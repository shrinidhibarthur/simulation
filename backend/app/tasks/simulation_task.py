"""
Vectorized Monte Carlo simulation task.
Ports the simulation engine from simulation_lab_demo_streamlit_app.py
to a production Celery worker using numpy/scipy with seeded reproducibility.

Key contracts:
- Seed is computed ONCE at Step 4 (data lock) and never changes.
- np.random.default_rng(seed) is constructed fresh per task run — same seed → same samples.
- All 10k iterations are sampled at once (no Python loop per iteration).
- Idempotency: if results already exist for a simulation_id, return early.
"""
import json
import uuid
from datetime import datetime, timezone

import numpy as np
import redis as redis_lib
from scipy.stats import gaussian_kde, norm
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.tasks.celery_app import celery_app

# ── Module-level sync engine (reused across task calls on the same worker process) ─
_sync_engine = None


def _get_engine():
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(
            settings.sync_database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _sync_engine


def _get_session() -> Session:
    return Session(_get_engine())


def _get_redis() -> redis_lib.Redis:
    return redis_lib.from_url(settings.redis_url, decode_responses=True)


def _push_progress(r: redis_lib.Redis, simulation_id: str, progress: float, current_scenario: str, n: int):
    payload = {
        "progress": round(progress, 1),
        "current_scenario": current_scenario,
        "iterations_complete": int(progress / 100 * n),
        "total_iterations": n,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        r.setex(f"sim_progress:{simulation_id}", 3600, json.dumps(payload))
    except Exception:
        pass  # Redis unavailable — progress reporting is best-effort


def _ledger(session: Session, simulation_id: uuid.UUID, step: int, event_type: str, payload: dict | None = None):
    """Write an audit event from within the Celery worker (sync)."""
    from app.models.ledger_event import LedgerEvent
    event = LedgerEvent(
        simulation_id=simulation_id,
        step=step,
        event_type=event_type,
        actor="celery-worker",
        payload=payload,
    )
    session.add(event)


# ── Albertsons baseline constants ─────────────────────────────────────────────

BASELINE_CVR = 0.028
BASELINE_AOV = 87.50
BASELINE_RPV = BASELINE_CVR * BASELINE_AOV   # 2.45
BASELINE_MARGIN = 0.421

# Default Beta/Lognormal params per scenario name
# Overridden by Gemini's csv_profile distribution_suggestions when available
DEFAULT_PARAMS = {
    "Base": {
        "cvr": {"dist": "Beta", "alpha": 2.8, "beta": 97.2},
        "aov": {"dist": "Lognormal", "mu": 4.47, "sigma": 0.35},
        "margin": {"dist": "Lognormal", "mu": -0.866, "sigma": 0.20},
        "stockout": {"dist": "Beta", "alpha": 2.0, "beta": 23.0},
    },
    "Optimistic": {
        "cvr": {"dist": "Beta", "alpha": 4.2, "beta": 95.8},
        "aov": {"dist": "Lognormal", "mu": 4.60, "sigma": 0.30},
        "margin": {"dist": "Lognormal", "mu": -0.799, "sigma": 0.18},
        "stockout": {"dist": "Beta", "alpha": 1.5, "beta": 28.5},
    },
    "Pessimistic": {
        "cvr": {"dist": "Beta", "alpha": 1.8, "beta": 98.2},
        "aov": {"dist": "Lognormal", "mu": 4.34, "sigma": 0.40},
        "margin": {"dist": "Lognormal", "mu": -0.916, "sigma": 0.22},
        "stockout": {"dist": "Beta", "alpha": 3.0, "beta": 19.0},
    },
}

# Lift multipliers applied on top of Base params for Optimistic/Pessimistic
LIFT_MULTIPLIERS = {
    "Base": 1.0,
    "Optimistic": 1.0,   # params already encode uplift
    "Pessimistic": 1.0,
}


def _merge_gemini_params(scenario_name: str, csv_profile: dict | None) -> dict:
    """
    Merge Gemini's per-column distribution suggestions (from Step 4 CSV profiling)
    into the scenario parameters. Falls back to DEFAULT_PARAMS if no profile exists
    or if Gemini did not suggest distributions for the relevant columns.
    """
    base = dict(DEFAULT_PARAMS.get(scenario_name, DEFAULT_PARAMS["Base"]))

    if not csv_profile:
        return base

    kpi_map = csv_profile.get("kpi_column_map", {})
    suggestions = {s["column_name"]: s for s in csv_profile.get("distribution_suggestions", [])}

    def _get_params(col_key: str, default_key: str):
        col = kpi_map.get(col_key)
        if col and col in suggestions:
            s = suggestions[col]
            dtype = s.get("distribution_type", "")
            params = s.get("params", {})
            if dtype == "Beta" and "alpha" in params and "beta" in params:
                return {"dist": "Beta", "alpha": float(params["alpha"]), "beta": float(params["beta"])}
            if dtype == "Lognormal" and "mu" in params and "sigma" in params:
                return {"dist": "Lognormal", "mu": float(params["mu"]), "sigma": float(params["sigma"])}
        return base[default_key]

    merged = {
        "cvr": _get_params("cvr_column", "cvr"),
        "aov": _get_params("aov_column", "aov"),
        "margin": _get_params("margin_column", "margin"),
        "stockout": base["stockout"],  # rarely in CSV — keep default
    }

    # Scale Optimistic/Pessimistic relative to the merged Base params
    if scenario_name == "Optimistic" and merged["cvr"]["dist"] == "Beta":
        merged["cvr"] = {**merged["cvr"], "alpha": merged["cvr"]["alpha"] * 1.5}
    elif scenario_name == "Pessimistic" and merged["cvr"]["dist"] == "Beta":
        merged["cvr"] = {**merged["cvr"], "alpha": merged["cvr"]["alpha"] * 0.65}

    return merged


def _sample(rng: np.random.Generator, param: dict, n: int) -> np.ndarray:
    """Sample n values from a named distribution."""
    dist = param.get("dist", "Normal")
    if dist == "Beta":
        return rng.beta(param["alpha"], param["beta"], size=n)
    if dist == "Lognormal":
        return rng.lognormal(param["mu"], param["sigma"], size=n)
    if dist == "Normal":
        return rng.normal(param.get("mu", 0), param.get("sigma", 1), size=n)
    # Fallback: uniform
    return rng.uniform(param.get("low", 0), param.get("high", 1), size=n)


def _run_scenario(rng: np.random.Generator, name: str, params: dict, n: int) -> dict:
    """
    Fully vectorized: all n iterations sampled in one numpy call per distribution.
    Composite score formula (ported from simulation_lab_demo_streamlit_app.py lines 430-436):
      score = confidence×0.25 + rpv_lift×0.3 + conversion_lift×0.2 + margin_impact×0.15 + sla_factor×0.05
    """
    cvr_samples     = np.clip(_sample(rng, params["cvr"], n), 1e-6, 0.999)
    aov_samples     = np.clip(_sample(rng, params["aov"], n), 1.0, None)
    margin_samples  = np.clip(_sample(rng, params["margin"], n), 1e-6, None)
    stockout_samples = np.clip(_sample(rng, params["stockout"], n), 0.0, 1.0)
    markdown_samples = rng.beta(3.0, 22.0, size=n)
    cost_samples     = np.clip(rng.lognormal(2.65, 0.15, size=n), 1.0, None)

    rpv_samples = cvr_samples * aov_samples

    # KPI deltas
    conversion_lift     = (cvr_samples - BASELINE_CVR) / BASELINE_CVR
    aov_delta           = aov_samples - BASELINE_AOV
    rpv_lift            = (rpv_samples - BASELINE_RPV) / BASELINE_RPV
    margin_impact       = margin_samples - BASELINE_MARGIN
    stockout_change     = stockout_samples - 0.042
    markdown_change     = markdown_samples - 0.123
    cost_to_serve_delta = cost_samples - 14.20

    # Aggregate metrics
    sla_risk_rate = float(np.mean(stockout_samples > 0.08))
    confidence    = float(np.mean(rpv_samples > BASELINE_RPV))
    sla_factor    = 1.0 - sla_risk_rate

    composite_score = (
        confidence                    * 0.25
        + float(np.mean(rpv_lift))    * 0.30
        + float(np.mean(conversion_lift)) * 0.20
        + float(np.mean(margin_impact))   * 0.15
        + sla_factor                  * 0.05
    )

    # Beacon metrics (ported from simulation_lab_beacon_integrated.py)
    cvr_mean = float(np.mean(cvr_samples))
    cvr_vol  = float(np.std(cvr_samples)) / (cvr_mean + 1e-9)
    d1 = (np.log(max(cvr_mean / BASELINE_CVR, 1e-9)) + 0.5 * cvr_vol ** 2) / (cvr_vol + 1e-9)
    win_probability  = float(np.clip(norm.cdf(d1) * 100, 0, 100))
    demand_momentum  = float(np.clip(cvr_mean * np.sqrt(365 / 30) * 100, 0, 200))
    visibility_budget = float(np.clip(
        (win_probability / 100) * (1 + float(np.mean(rpv_lift))) * 100_000, 0, 100_000
    ))

    # KDE — 512 points, bw=0.3 avoids over-smoothing long e-commerce tails
    try:
        kde    = gaussian_kde(rpv_samples, bw_method=0.3)
        x_grid = np.linspace(float(np.percentile(rpv_samples, 1)), float(np.percentile(rpv_samples, 99)), 512)
        y_vals = kde(x_grid)
    except Exception:
        x_grid = np.linspace(0.0, 5.0, 512)
        y_vals = np.zeros(512)

    return {
        "conversion_lift":     float(np.mean(conversion_lift)),
        "aov_delta":           float(np.mean(aov_delta)),
        "rpv_lift":            float(np.mean(rpv_lift)),
        "margin_impact":       float(np.mean(margin_impact)),
        "stockout_change":     float(np.mean(stockout_change)),
        "markdown_change":     float(np.mean(markdown_change)),
        "cost_to_serve_delta": float(np.mean(cost_to_serve_delta)),
        "sla_risk":            sla_risk_rate,
        "confidence":          confidence,
        "composite_score":     composite_score,
        "kde_x_values":        x_grid.tolist(),
        "kde_y_values":        y_vals.tolist(),
        "win_probability":     win_probability,
        "demand_momentum":     demand_momentum,
        "visibility_budget":   visibility_budget,
        "raw_summary": {
            "cvr_mean":   cvr_mean,
            "cvr_std":    float(np.std(cvr_samples)),
            "aov_mean":   float(np.mean(aov_samples)),
            "aov_std":    float(np.std(aov_samples)),
            "rpv_mean":   float(np.mean(rpv_samples)),
            "rpv_p5":     float(np.percentile(rpv_samples, 5)),
            "rpv_p95":    float(np.percentile(rpv_samples, 95)),
            "n_iterations": n,
        },
    }


# ── Celery task ────────────────────────────────────────────────────────────────

@celery_app.task(bind=True, name="tasks.run_simulation", max_retries=3)
def run_simulation_task(self, simulation_id: str, scenario_ids: list[str], n_iterations: int = 10_000):
    from app.models.result import Result
    from app.models.scenario import Scenario
    from app.models.simulation import Simulation

    sim_uuid = uuid.UUID(simulation_id)
    r = _get_redis()
    session = _get_session()

    try:
        sim = session.get(Simulation, sim_uuid)
        if not sim:
            return {"error": "Simulation not found", "simulation_id": simulation_id}

        # ── Idempotency guard ────────────────────────────────────────────────
        existing_count = session.query(Result).filter(Result.simulation_id == sim_uuid).count()
        if existing_count > 0:
            return {"status": "already_complete", "simulation_id": simulation_id, "results": existing_count}

        if sim.seed is None:
            return {"error": "No seed — complete Step 4 (CSV profile) first"}

        # ── Construct RNG from immutable seed ────────────────────────────────
        # Same seed always → same samples → reproducible audit trail
        rng = np.random.default_rng(sim.seed)

        # ── Resolve scenarios ────────────────────────────────────────────────
        scenarios_to_run: list[Scenario] = []
        for sc_id_str in scenario_ids:
            sc = session.get(Scenario, uuid.UUID(sc_id_str))
            if sc:
                scenarios_to_run.append(sc)

        if not scenarios_to_run:
            # Fallback: run all scenarios linked to this simulation
            scenarios_to_run = (
                session.query(Scenario)
                .filter(Scenario.simulation_id == sim_uuid)
                .all()
            )

        if not scenarios_to_run:
            return {"error": "No scenarios found for this simulation"}

        total = len(scenarios_to_run)
        _ledger(session, sim_uuid, 6, "simulation_engine_started",
                {"seed": sim.seed, "n_iterations": n_iterations, "scenario_count": total})
        session.commit()

        # ── Run each scenario ────────────────────────────────────────────────
        results_created = []
        for i, sc in enumerate(scenarios_to_run):
            pct = round((i / total) * 100, 1)
            self.update_state(state="PROGRESS", meta={"progress": pct, "current_scenario": sc.name})
            _push_progress(r, simulation_id, pct, sc.name, n_iterations)

            # Merge Gemini distribution suggestions from Step 4 CSV profiling
            params = _merge_gemini_params(sc.name, sim.csv_profile)
            kpi_data = _run_scenario(rng, sc.name, params, n_iterations)

            result = Result(simulation_id=sim_uuid, scenario_id=sc.id, **kpi_data)
            session.add(result)
            results_created.append(result)
            session.flush()  # get the result.id before commit

            _ledger(session, sim_uuid, 6, "scenario_complete", {
                "scenario": sc.name,
                "composite_score": round(kpi_data["composite_score"], 6),
                "rpv_lift": round(kpi_data["rpv_lift"], 6),
                "confidence": round(kpi_data["confidence"], 4),
            })

        # ── Advance simulation state ─────────────────────────────────────────
        winner = max(results_created, key=lambda r: r.composite_score)
        winner_scenario = next((s for s in scenarios_to_run if s.id == winner.scenario_id), None)

        sim.status = "results_ready"
        sim.step = 7
        _ledger(session, sim_uuid, 7, "results_ready", {
            "winner": winner_scenario.name if winner_scenario else None,
            "winner_score": round(float(winner.composite_score), 6),
            "winner_rpv_lift": round(float(winner.rpv_lift), 4),
            "winner_confidence": round(float(winner.confidence), 4),
        })
        session.commit()

        _push_progress(r, simulation_id, 100.0, "complete", n_iterations)
        self.update_state(state="SUCCESS", meta={"progress": 100, "current_scenario": "complete"})

        return {
            "status": "complete",
            "simulation_id": simulation_id,
            "results_count": len(results_created),
            "winner": winner_scenario.name if winner_scenario else None,
            "winner_composite_score": round(float(winner.composite_score), 6),
        }

    except Exception as exc:
        session.rollback()
        # Revert simulation to "locked" so it can be re-triggered
        try:
            sim = session.get(Simulation, sim_uuid)
            if sim and sim.status == "running":
                sim.status = "locked"
                sim.step = 5
                _ledger(session, sim_uuid, 6, "simulation_failed", {"error": str(exc)})
                session.commit()
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=5) if self.request.retries < self.max_retries else exc
    finally:
        session.close()
        try:
            r.close()
        except Exception:
            pass
