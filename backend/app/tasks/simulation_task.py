"""
Vectorized Monte Carlo simulation task.
Ports the simulation engine from simulation_lab_demo_streamlit_app.py
to a production Celery worker using numpy/scipy with seeded reproducibility.
"""
import json
import time
import uuid
from datetime import datetime, timezone

import numpy as np
import redis
from scipy.stats import gaussian_kde, norm

from app.config import settings
from app.tasks.celery_app import celery_app

# ── Sync DB helpers (Celery is synchronous — uses psycopg2, not asyncpg) ─────

def _get_sync_engine():
    from sqlalchemy import create_engine
    return create_engine(settings.sync_database_url, pool_pre_ping=True)


def _get_sync_session():
    from sqlalchemy.orm import Session
    engine = _get_sync_engine()
    return Session(engine)


def _push_progress(r_client, simulation_id: str, progress: float, current_scenario: str, n_iterations: int):
    payload = {
        "progress": round(progress, 1),
        "current_scenario": current_scenario,
        "iterations_complete": int(progress / 100 * n_iterations),
        "total_iterations": n_iterations,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    r_client.setex(f"sim_progress:{simulation_id}", 3600, json.dumps(payload))


# ── Albertsons baseline constants ─────────────────────────────────────────────

BASELINE_CVR = 0.028
BASELINE_AOV = 87.50
BASELINE_RPV = BASELINE_CVR * BASELINE_AOV  # 2.45
BASELINE_MARGIN = 0.421

# Default distribution params per scenario name (overridden by Gemini suggestions from Step 4)
DEFAULT_PARAMS = {
    "Base":        {"cvr": (2.8,  97.2,  0.0),   "aov": (4.47, 0.35), "margin": (4.47, 0.20)},
    "Optimistic":  {"cvr": (4.2,  95.8,  0.05),  "aov": (4.60, 0.30), "margin": (4.50, 0.18)},
    "Pessimistic": {"cvr": (1.8,  98.2, -0.03),  "aov": (4.34, 0.40), "margin": (4.43, 0.22)},
}


def _run_scenario(rng: np.random.Generator, name: str, dist_params: dict | None, n: int) -> dict:
    params = dist_params or DEFAULT_PARAMS.get(name, DEFAULT_PARAMS["Base"])

    cvr_alpha, cvr_beta, _ = params["cvr"]
    aov_mu, aov_sigma = params["aov"]
    margin_mu, margin_sigma = params["margin"]

    cvr_samples = rng.beta(cvr_alpha, cvr_beta, size=n)
    aov_samples = rng.lognormal(aov_mu, aov_sigma, size=n)
    margin_samples = rng.lognormal(margin_mu, margin_sigma, size=n)
    rpv_samples = cvr_samples * aov_samples

    conversion_lift = (cvr_samples - BASELINE_CVR) / BASELINE_CVR
    aov_delta = aov_samples - BASELINE_AOV
    rpv_lift = (rpv_samples - BASELINE_RPV) / BASELINE_RPV
    margin_impact = margin_samples - BASELINE_MARGIN

    # Synthetic stockout / markdown / cost-to-serve from the aov distribution
    stockout_samples = rng.beta(2.0, 23.0, size=n)  # baseline ~8%
    markdown_samples = rng.beta(3.0, 22.0, size=n)  # baseline ~12%
    cost_samples = rng.lognormal(2.65, 0.15, size=n)  # baseline ~$14.20

    stockout_change = stockout_samples - 0.042
    markdown_change = markdown_samples - 0.123
    cost_to_serve_delta = cost_samples - 14.20

    sla_risk_rate = float(np.mean(stockout_samples > 0.08))
    confidence = float(np.mean(rpv_samples > BASELINE_RPV))
    sla_factor = 1.0 - sla_risk_rate

    # Composite score: confidence×0.25 + rpv_lift×0.3 + conversion_lift×0.2 + margin_impact×0.15 + sla_factor×0.05
    composite_score = (
        confidence * 0.25
        + float(np.mean(rpv_lift)) * 0.3
        + float(np.mean(conversion_lift)) * 0.2
        + float(np.mean(margin_impact)) * 0.15
        + sla_factor * 0.05
    )

    # Beacon metrics (ported from simulation_lab_beacon_integrated.py)
    cvr_vol = float(np.std(cvr_samples) / (np.mean(cvr_samples) + 1e-9))
    cvr_mean = float(np.mean(cvr_samples))
    d1 = (np.log(cvr_mean / BASELINE_CVR + 1e-9) + 0.5 * cvr_vol**2) / (cvr_vol + 1e-9)
    win_probability = float(np.clip(norm.cdf(d1) * 100, 0, 100))
    demand_momentum = float(np.clip(cvr_mean * np.sqrt(365 / 30) * 100, 0, 200))
    visibility_budget = float(np.clip((win_probability / 100) * (1 + float(np.mean(rpv_lift))) * 100_000, 0, 100_000))

    # KDE for chart (512 points, bw=0.3 to avoid over-smoothing tails)
    try:
        kde = gaussian_kde(rpv_samples, bw_method=0.3)
        x_grid = np.linspace(float(np.percentile(rpv_samples, 1)), float(np.percentile(rpv_samples, 99)), 512)
        y_values = kde(x_grid)
    except Exception:
        x_grid = np.linspace(0, 5, 512)
        y_values = np.zeros(512)

    return {
        "conversion_lift": float(np.mean(conversion_lift)),
        "aov_delta": float(np.mean(aov_delta)),
        "rpv_lift": float(np.mean(rpv_lift)),
        "margin_impact": float(np.mean(margin_impact)),
        "stockout_change": float(np.mean(stockout_change)),
        "markdown_change": float(np.mean(markdown_change)),
        "cost_to_serve_delta": float(np.mean(cost_to_serve_delta)),
        "sla_risk": sla_risk_rate,
        "confidence": confidence,
        "composite_score": composite_score,
        "kde_x_values": x_grid.tolist(),
        "kde_y_values": y_values.tolist(),
        "win_probability": win_probability,
        "demand_momentum": demand_momentum,
        "visibility_budget": visibility_budget,
        "raw_summary": {
            "cvr_mean": cvr_mean,
            "cvr_std": float(np.std(cvr_samples)),
            "aov_mean": float(np.mean(aov_samples)),
            "aov_std": float(np.std(aov_samples)),
            "rpv_p5": float(np.percentile(rpv_samples, 5)),
            "rpv_p95": float(np.percentile(rpv_samples, 95)),
            "n_iterations": n,
        },
    }


@celery_app.task(bind=True, name="tasks.run_simulation")
def run_simulation_task(self, simulation_id: str, scenario_ids: list[str], n_iterations: int = 10_000):
    from app.models.result import Result
    from app.models.scenario import Scenario
    from app.models.simulation import Simulation

    r_client = redis.from_url(settings.redis_url, decode_responses=True)
    session = _get_sync_session()

    try:
        sim_uuid = uuid.UUID(simulation_id)
        sim = session.get(Simulation, sim_uuid)
        if not sim:
            return {"error": "Simulation not found"}

        # Idempotency check
        existing = session.query(Result).filter(Result.simulation_id == sim_uuid).first()
        if existing:
            return {"status": "already_complete", "simulation_id": simulation_id}

        seed = sim.seed
        if seed is None:
            return {"error": "No seed — CSV profiling not complete"}

        rng = np.random.default_rng(seed)

        scenarios_to_run = []
        for sc_id_str in scenario_ids:
            sc = session.get(Scenario, uuid.UUID(sc_id_str))
            if sc:
                scenarios_to_run.append(sc)

        if not scenarios_to_run:
            # Fall back: run all scenarios linked to simulation
            scenarios_to_run = session.query(Scenario).filter(Scenario.simulation_id == sim_uuid).all()

        total = len(scenarios_to_run)
        results_created = []

        for i, sc in enumerate(scenarios_to_run):
            self.update_state(state="PROGRESS", meta={"progress": (i / total) * 100, "current_scenario": sc.name})
            _push_progress(r_client, simulation_id, (i / total) * 100, sc.name, n_iterations)

            kpi_data = _run_scenario(rng, sc.name, sc.distribution_params, n_iterations)

            result = Result(
                simulation_id=sim_uuid,
                scenario_id=sc.id,
                **kpi_data,
            )
            session.add(result)
            results_created.append(result)

        sim.status = "results_ready"
        sim.step = 7
        session.commit()

        _push_progress(r_client, simulation_id, 100.0, "complete", n_iterations)
        return {"status": "complete", "simulation_id": simulation_id, "results_count": len(results_created)}

    except Exception as exc:
        session.rollback()
        sim = session.get(Simulation, uuid.UUID(simulation_id))
        if sim:
            sim.status = "locked"  # revert to allow re-run
            session.commit()
        raise exc
    finally:
        session.close()
        r_client.close()
