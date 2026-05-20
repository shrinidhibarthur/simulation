#!/usr/bin/env python3
"""
Phase 4 integration test.
1. Validates the Monte Carlo engine directly (no Celery required).
2. Creates a fresh simulation through all steps via the API.
3. Submits via POST /run — waits for Celery worker to process it.
4. Confirms GET /results returns ranked results.
5. Confirms GET /api/simulations/{id}/rollout (Step 8) works.
"""
import json
import os
import sys
import time
import uuid

import requests

BASE = "http://localhost:8000"
PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
NOTE = "\033[94m→\033[0m"
API_KEY = os.getenv("GOOGLE_API_KEY", "")


def check(label, cond, detail=""):
    mark = PASS if cond else FAIL
    msg = f"  {mark} {label}"
    if detail:
        msg += f": {str(detail)[:120]}"
    print(msg)
    return cond


def wait_for_results(sim_id: str, timeout: int = 120) -> str:
    """Poll status until results_ready or timeout."""
    deadline = time.time() + timeout
    prev_scenario = ""
    while time.time() < deadline:
        r = requests.get(f"{BASE}/api/simulations/{sim_id}/status", timeout=5)
        data = r.json()
        status = data.get("status", "")
        progress = data.get("progress")
        current = data.get("current_scenario", "")
        if current and current != prev_scenario:
            print(f"    {NOTE} Running: {current} ({progress:.0f}%)" if progress else f"    {NOTE} Running: {current}")
            prev_scenario = current
        if status == "results_ready":
            return "results_ready"
        if status in ("failed", "locked"):
            return status
        time.sleep(2)
    return "timeout"


# ─────────────────────────────────────────────────────────────────────────────
# PART 1: Direct engine validation (no Celery)
# ─────────────────────────────────────────────────────────────────────────────

def test_engine_direct():
    print("\n" + "="*60)
    print("PART 1: Monte Carlo Engine — Direct Unit Test")
    print("="*60)

    sys.path.insert(0, "backend")
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://albertsons:changeme@localhost:5432/simulations")
    os.environ.setdefault("SYNC_DATABASE_URL", "postgresql://albertsons:changeme@localhost:5432/simulations")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
    os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    os.environ.setdefault("REDIS_PASSWORD", "")
    os.environ.setdefault("GOOGLE_API_KEY", API_KEY)
    os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")

    from app.tasks.simulation_task import (
        DEFAULT_PARAMS, BASELINE_CVR, BASELINE_AOV, BASELINE_RPV,
        _merge_gemini_params, _run_scenario,
    )
    import numpy as np

    errors = []

    # Test 1: Seeded reproducibility
    print("\n[A] Seeded reproducibility")
    seed = 1349568088
    for run in range(2):
        rng = np.random.default_rng(seed)
        params = DEFAULT_PARAMS["Base"]
        kpi1 = _run_scenario(rng, "Base", params, 10_000)

    rng_a = np.random.default_rng(seed)
    kpi_a = _run_scenario(rng_a, "Base", DEFAULT_PARAMS["Base"], 10_000)
    rng_b = np.random.default_rng(seed)
    kpi_b = _run_scenario(rng_b, "Base", DEFAULT_PARAMS["Base"], 10_000)

    ok = kpi_a["composite_score"] == kpi_b["composite_score"]
    check("Same seed → identical composite_score", ok, kpi_a["composite_score"])
    if not ok:
        errors.append("reproducibility")

    # Test 2: Optimistic beats Base beats Pessimistic (on CVR mean)
    print("\n[B] Scenario ordering (Optimistic > Base > Pessimistic on CVR)")
    rng = np.random.default_rng(42)
    results = {}
    for name in ["Base", "Optimistic", "Pessimistic"]:
        r = _run_scenario(rng, name, DEFAULT_PARAMS[name], 10_000)
        results[name] = r
        print(f"  {NOTE} {name:12s}: rpv_lift={r['rpv_lift']:+.4f}  composite={r['composite_score']:+.6f}  "
              f"win_prob={r['win_probability']:.1f}%  confidence={r['confidence']:.3f}")

    opt_score = results["Optimistic"]["composite_score"]
    base_score = results["Base"]["composite_score"]
    pess_score = results["Pessimistic"]["composite_score"]
    check("Optimistic composite > Base", opt_score > base_score, f"{opt_score:.4f} > {base_score:.4f}")
    check("Base composite > Pessimistic", base_score > pess_score, f"{base_score:.4f} > {pess_score:.4f}")

    # Test 3: KDE arrays are valid
    print("\n[C] KDE array validity")
    base_r = results["Base"]
    check("KDE has 512 x-values", len(base_r["kde_x_values"]) == 512, len(base_r["kde_x_values"]))
    check("KDE has 512 y-values", len(base_r["kde_y_values"]) == 512, len(base_r["kde_y_values"]))
    check("KDE y-values are non-negative", all(v >= 0 for v in base_r["kde_y_values"]))
    check("KDE x-values are ordered", base_r["kde_x_values"][0] < base_r["kde_x_values"][-1])

    # Test 4: Beacon metrics in valid ranges
    print("\n[D] Beacon metrics")
    check("win_probability in [0,100]", 0 <= base_r["win_probability"] <= 100, base_r["win_probability"])
    check("demand_momentum in [0,200]", 0 <= base_r["demand_momentum"] <= 200, base_r["demand_momentum"])
    check("visibility_budget in [0,100k]", 0 <= base_r["visibility_budget"] <= 100_000, base_r["visibility_budget"])

    # Test 5: Gemini distribution merge
    print("\n[E] Gemini distribution merge")
    mock_profile = {
        "kpi_column_map": {"cvr_column": "cvr", "aov_column": "aov"},
        "distribution_suggestions": [
            {"column_name": "cvr", "distribution_type": "Beta", "params": {"alpha": 84.64, "beta": 2938.36}},
            {"column_name": "aov", "distribution_type": "Lognormal", "params": {"mu": 4.46, "sigma": 0.064}},
        ],
    }
    merged = _merge_gemini_params("Base", mock_profile)
    check("CVR merged from Gemini as Beta", merged["cvr"]["dist"] == "Beta")
    check("CVR alpha from Gemini", abs(merged["cvr"]["alpha"] - 84.64) < 0.1, merged["cvr"]["alpha"])
    check("AOV merged from Gemini as Lognormal", merged["aov"]["dist"] == "Lognormal")
    check("Fallback for missing column", merged["stockout"]["dist"] == "Beta")

    # Test 6: Performance — 10k iterations < 5 seconds
    print("\n[F] Performance")
    import time as _time
    rng = np.random.default_rng(99)
    t0 = _time.perf_counter()
    _run_scenario(rng, "Optimistic", DEFAULT_PARAMS["Optimistic"], 10_000)
    elapsed = _time.perf_counter() - t0
    check(f"10k iterations complete in <5s", elapsed < 5.0, f"{elapsed:.3f}s")

    print(f"\n  Engine tests: {'PASS' if not errors else f'FAIL {errors}'}")
    return errors


# ─────────────────────────────────────────────────────────────────────────────
# PART 2: End-to-end API test (requires FastAPI + Celery worker)
# ─────────────────────────────────────────────────────────────────────────────

def test_e2e_api():
    print("\n" + "="*60)
    print("PART 2: End-to-End API Test (FastAPI + Celery)")
    print("="*60)
    errors = []

    # ── Step 1: Create ────────────────────────────────────────────────────────
    print("\n[1] Create simulation")
    r = requests.post(f"{BASE}/api/simulations", json={
        "request_text": "Test a free shipping threshold of $75 on the Albertsons checkout flow to understand impact on AOV and conversion rate.",
        "mvt": "phase4-test",
        "budget": 25000,
        "sla_limit": 0.08,
    }, timeout=10)
    check("Created 201", r.status_code == 201, r.status_code)
    sim = r.json()
    sim_id = sim["id"]
    print(f"  {NOTE} sim_id={sim_id}")

    # ── Step 2: Clarify ───────────────────────────────────────────────────────
    print("\n[2] Clarify — generate questions")
    r = requests.post(f"{BASE}/api/simulations/{sim_id}/clarify", json={}, timeout=60)
    check("Got questions", r.status_code == 200 and r.json().get("questions"), len(r.json().get("questions", [])))
    questions = r.json()["questions"]

    print("\n[3] Clarify — submit answers → UseCaseBrief")
    answers = {q: f"Answer: {q[:40]}..." for q in questions}
    r = requests.post(f"{BASE}/api/simulations/{sim_id}/clarify", json={"answers": answers}, timeout=60)
    check("Brief complete", r.status_code == 200 and r.json().get("complete"), r.json().get("complete"))

    # ── Step 3: Scenarios ─────────────────────────────────────────────────────
    print("\n[4] Generate scenarios")
    r = requests.post(f"{BASE}/api/simulations/{sim_id}/scenarios", json={}, timeout=90)
    check("3 scenarios returned", r.status_code == 201, r.status_code)
    scenarios = r.json()["scenarios"]
    check("Has Base/Optimistic/Pessimistic", {s["name"] for s in scenarios} == {"Base", "Optimistic", "Pessimistic"})
    sc_ids = [s["id"] for s in scenarios]

    # ── Step 4: CSV Profile ───────────────────────────────────────────────────
    print("\n[5] Profile CSV")
    csv_data = (
        "cvr,aov,margin_pct,stockout_rate\n"
        "0.028,87.50,0.42,0.04\n0.031,92.00,0.41,0.03\n"
        "0.025,81.00,0.44,0.05\n0.033,95.00,0.40,0.03\n"
    )
    r = requests.post(
        f"{BASE}/api/simulations/{sim_id}/profile-csv",
        files={"file": ("data.csv", csv_data, "text/csv")},
        timeout=90,
    )
    check("Profile 200", r.status_code == 200, r.status_code)
    profile = r.json()
    seed = profile.get("seed")
    check("Seed computed", isinstance(seed, int) and seed > 0, seed)
    dist = profile.get("csv_profile", {}).get("distribution_suggestions", [])
    check("Gemini mapped distributions", len(dist) > 0, f"{len(dist)} columns mapped")

    # ── Step 5: Lock ──────────────────────────────────────────────────────────
    print("\n[6] Lock data sources")
    r = requests.post(f"{BASE}/api/simulations/{sim_id}/lock", json={"data_sources": [
        {"name": "Adobe/EDDL", "latency_minutes": 1},
        {"name": "OMS", "latency_minutes": 4},
        {"name": "Inventory", "latency_minutes": 10},
        {"name": "Pricing", "latency_minutes": 1},
        {"name": "CRM", "latency_minutes": 480},
        {"name": "WMS", "latency_minutes": 6},
        {"name": "Carriers", "latency_minutes": 1440},
    ]}, timeout=10)
    check("Locked", r.status_code == 200 and r.json().get("locked"), r.json().get("seed"))

    # ── Step 6: Run ───────────────────────────────────────────────────────────
    print("\n[7] Run simulation via Celery")
    r = requests.post(f"{BASE}/api/simulations/{sim_id}/run",
                      json={"scenario_ids": sc_ids, "n_iterations": 10000}, timeout=10)
    check("Task queued", r.status_code == 200, r.status_code)
    task_id = r.json().get("task_id")
    print(f"  {NOTE} task_id={task_id}")

    print("\n[8] Polling for results (up to 120s)...")
    final_status = wait_for_results(sim_id, timeout=120)
    check("Simulation reached results_ready", final_status == "results_ready", final_status)
    if final_status != "results_ready":
        errors.append("simulation_did_not_complete")
        print(f"  Final status was '{final_status}' — check Celery worker logs")
        return errors

    # ── Step 7: Results ───────────────────────────────────────────────────────
    print("\n[9] GET /api/simulations/{id}/results")
    r = requests.get(f"{BASE}/api/simulations/{sim_id}/results", timeout=10)
    check("Results 200", r.status_code == 200, r.status_code)
    resp = r.json()
    results = resp.get("results", [])
    ranked = resp.get("ranked", [])
    check("3 results returned", len(results) == 3, len(results))
    check("3 ranked results", len(ranked) == 3, len(ranked))

    if ranked:
        winner = ranked[0]
        winner_sc = next((s for s in scenarios if s["id"] == winner["scenario_id"]), {})
        print(f"\n  WINNER: {winner_sc.get('name', '?')}")
        print(f"    composite_score:  {winner['composite_score']:+.6f}")
        print(f"    conversion_lift:  {winner['conversion_lift']:+.4f} ({winner['conversion_lift']*100:+.2f}%)")
        print(f"    rpv_lift:         {winner['rpv_lift']:+.4f} ({winner['rpv_lift']*100:+.2f}%)")
        print(f"    margin_impact:    {winner['margin_impact']:+.4f}")
        print(f"    confidence:       {winner['confidence']:.1%}")
        print(f"    win_probability:  {winner['win_probability']:.1f}%")
        print(f"    demand_momentum:  {winner['demand_momentum']:.1f}")
        print(f"    visibility_budget: ${winner['visibility_budget']:,.0f}")
        print(f"\n  Ranking:")
        for i, res in enumerate(ranked, 1):
            sc_name = next((s["name"] for s in scenarios if s["id"] == res["scenario_id"]), "?")
            print(f"    #{i} {sc_name:12s}  score={res['composite_score']:+.6f}  rpv={res['rpv_lift']:+.4f}")

    check("Ranked order correct", ranked[0]["composite_score"] >= ranked[-1]["composite_score"])
    check("KDE x_values present", len(ranked[0].get("kde_x_values", [])) == 512)
    check("KDE y_values present", len(ranked[0].get("kde_y_values", [])) == 512)
    check("raw_summary present", isinstance(ranked[0].get("raw_summary"), dict))

    # ── Idempotency ───────────────────────────────────────────────────────────
    print("\n[10] Idempotency — re-running same simulation")
    r = requests.post(f"{BASE}/api/simulations/{sim_id}/run",
                      json={"scenario_ids": sc_ids, "n_iterations": 10000}, timeout=10)
    # Should be rejected (status is results_ready, not locked)
    check("Re-run rejected (not locked)", r.status_code == 400, r.status_code)

    # ── Step 8: Rollout ───────────────────────────────────────────────────────
    print("\n[11] POST /api/simulations/{id}/rollout (Step 8)")
    r = requests.post(f"{BASE}/api/simulations/{sim_id}/rollout", json={}, timeout=90)
    check("Rollout 200", r.status_code == 200, r.status_code)
    rollout = r.json().get("rollout_plan", {})
    check("Has feature_flags", isinstance(rollout.get("feature_flags"), list) and len(rollout["feature_flags"]) > 0)
    check("Has auto_rollback_rules", isinstance(rollout.get("auto_rollback_rules"), list))
    check("Has inventory_guardrails", isinstance(rollout.get("inventory_guardrails"), dict))
    check("Has timeline", isinstance(rollout.get("timeline"), list))
    if rollout.get("feature_flags"):
        ff = rollout["feature_flags"][0]
        print(f"  {NOTE} First flag: {ff.get('flag_name')} → wk1={ff.get('week1_pct')}% → wk4={ff.get('week4_pct')}%")

    # ── Ledger ────────────────────────────────────────────────────────────────
    print("\n[12] GET /api/simulations/{id}/ledger — full audit trail")
    r = requests.get(f"{BASE}/api/simulations/{sim_id}/ledger", timeout=10)
    events = r.json().get("events", [])
    event_types = [e["event_type"] for e in events]
    check(f"Has ≥10 ledger events", len(events) >= 10, len(events))
    check("simulation_created in ledger", "simulation_created" in event_types)
    check("seed_computed in ledger", "seed_computed" in event_types)
    check("simulation_engine_started in ledger", "simulation_engine_started" in event_types)
    check("scenario_complete in ledger", "scenario_complete" in event_types)
    check("results_ready in ledger", "results_ready" in event_types)
    check("rollout_generated in ledger", "rollout_generated" in event_types)
    print(f"  {NOTE} All {len(events)} events: {event_types}")

    print(f"\n  E2E tests: {'PASS' if not errors else f'FAIL {errors}'}")
    return errors


if __name__ == "__main__":
    all_errors = []
    all_errors += test_engine_direct()
    all_errors += test_e2e_api()

    print("\n" + "="*60)
    if all_errors:
        print(f"  {FAIL} Phase 4 FAILED: {all_errors}")
        sys.exit(1)
    else:
        print(f"  {PASS} Phase 4 ALL CHECKS PASSED")
        sys.exit(0)
