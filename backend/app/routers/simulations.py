import json
import uuid
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.ledger_event import LedgerEvent
from app.models.result import Result
from app.models.scenario import Scenario
from app.models.simulation import Simulation
from app.schemas.ledger import LedgerEventSchema, LedgerResponse
from app.schemas.result import ResultSchema, ResultsResponse
from app.schemas.scenario import ScenarioSchema, ScenariosResponse
from app.schemas.simulation import (
    ClarifyRequest,
    ClarifyResponse,
    CreateSimulationRequest,
    LockRequest,
    LockResponse,
    RunRequest,
    RunResponse,
    SimulationListResponse,
    SimulationSchema,
    StatusResponse,
)
from app.services.ledger_service import log_event

router = APIRouter(prefix="/api/simulations", tags=["simulations"])

DB = Annotated[AsyncSession, Depends(get_db)]


# ── helpers ──────────────────────────────────────────────────────────────────

async def _get_simulation_or_404(db: AsyncSession, simulation_id: uuid.UUID) -> Simulation:
    result = await db.execute(select(Simulation).where(Simulation.id == simulation_id))
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim


# ── Step 1: create simulation ─────────────────────────────────────────────────

@router.post("", response_model=SimulationSchema, status_code=201)
async def create_simulation(body: CreateSimulationRequest, db: DB):
    title = body.request_text[:80].strip()
    sim = Simulation(
        title=title,
        request_text=body.request_text,
        mvt=body.mvt,
        budget=body.budget,
        sla_limit=body.sla_limit,
        status="draft",
        step=1,
    )
    db.add(sim)
    await db.flush()
    await log_event(db, sim.id, 1, "simulation_created", payload={"title": title})
    await db.commit()
    await db.refresh(sim)
    return sim


# ── List & get ────────────────────────────────────────────────────────────────

@router.get("", response_model=SimulationListResponse)
async def list_simulations(db: DB, status: str | None = None, page: int = 1, per_page: int = 20):
    q = select(Simulation).order_by(Simulation.created_at.desc())
    if status:
        q = q.where(Simulation.status == status)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar_one()
    items_result = await db.execute(q.offset((page - 1) * per_page).limit(per_page))
    return SimulationListResponse(items=items_result.scalars().all(), total=total)


@router.get("/{simulation_id}", response_model=SimulationSchema)
async def get_simulation(simulation_id: uuid.UUID, db: DB):
    return await _get_simulation_or_404(db, simulation_id)


# ── Step 2: AI clarifier ──────────────────────────────────────────────────────

@router.post("/{simulation_id}/clarify", response_model=ClarifyResponse)
async def clarify_simulation(simulation_id: uuid.UUID, body: ClarifyRequest, db: DB):
    sim = await _get_simulation_or_404(db, simulation_id)

    try:
        from app.agents.clarifier_agent import run_clarifier
        result = await run_clarifier(sim, body.answers)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini error: {exc}") from exc

    if result["complete"]:
        sim.use_case_brief = result["use_case_brief"]
        sim.status = "clarifying"
        sim.step = 2
        await log_event(db, sim.id, 2, "clarification_complete", payload={"brief_keys": list(result["use_case_brief"].keys())})
    else:
        await log_event(db, sim.id, 2, "clarification_questions_sent", payload={"question_count": len(result["questions"])})

    await db.commit()
    return ClarifyResponse(**result)


# ── Step 3: scenario generation ───────────────────────────────────────────────

@router.post("/{simulation_id}/scenarios", response_model=ScenariosResponse)
async def generate_scenarios(simulation_id: uuid.UUID, db: DB):
    sim = await _get_simulation_or_404(db, simulation_id)
    if not sim.use_case_brief:
        raise HTTPException(status_code=400, detail="UseCaseBrief not yet generated — complete clarification first")

    try:
        from app.agents.scenario_agent import generate_scenarios as _gen
        raw_scenarios = await _gen(sim)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini error: {exc}") from exc

    created = []
    for sc_data in raw_scenarios:
        sc = Scenario(
            simulation_id=sim.id,
            name=sc_data["name"],
            storefront=sc_data.get("storefront", {}),
            marketing=sc_data.get("marketing", {}),
            ops=sc_data.get("ops", {}),
            notes=sc_data.get("notes"),
        )
        db.add(sc)
        created.append(sc)

    sim.status = "scenarios_ready"
    sim.step = 3
    await db.flush()
    await log_event(db, sim.id, 3, "scenarios_generated", payload={"count": len(created)})
    await db.commit()
    for sc in created:
        await db.refresh(sc)
    return ScenariosResponse(scenarios=created)


# ── Step 4: CSV profile ───────────────────────────────────────────────────────

@router.post("/{simulation_id}/profile-csv")
async def profile_csv(simulation_id: uuid.UUID, db: DB, file: UploadFile = File(...)):
    sim = await _get_simulation_or_404(db, simulation_id)

    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV file exceeds 10 MB limit")

    import hashlib
    import os
    import aiofiles

    upload_dir = f"/app/uploads/{simulation_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"

    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    try:
        from app.agents.csv_profiler_agent import profile_csv as _profile
        profile_result = await _profile(sim, file_path, content)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CSV profiling error: {exc}") from exc

    # Compute seed now that all parameters are known
    seed_input = f"{sim.request_text}{sim.mvt or ''}{sim.budget or ''}{sim.sla_limit or ''}"
    seed = int(hashlib.md5(seed_input.encode()).hexdigest(), 16) % (2**32 - 1)

    sim.csv_path = file_path
    sim.csv_profile = profile_result
    sim.seed = seed
    sim.status = "configured"
    sim.step = 4

    await log_event(db, sim.id, 4, "csv_uploaded", payload={"filename": file.filename})
    await log_event(db, sim.id, 4, "seed_computed", payload={"seed": seed})
    await db.commit()

    return {"csv_profile": profile_result, "seed": seed}


# ── Step 5: data lock ─────────────────────────────────────────────────────────

@router.post("/{simulation_id}/lock", response_model=LockResponse)
async def lock_simulation(simulation_id: uuid.UUID, body: LockRequest, db: DB):
    sim = await _get_simulation_or_404(db, simulation_id)
    if sim.seed is None:
        raise HTTPException(status_code=400, detail="Seed not yet computed — complete CSV profiling first")

    # Acceptable latency thresholds (minutes)
    thresholds = {
        "Adobe/EDDL": 5, "OMS": 10, "Inventory": 30,
        "Pricing": 5, "CRM": 1500, "WMS": 20, "Carriers": 11520,
    }

    validation_results = []
    all_ok = True
    for src in body.data_sources:
        name = src.get("name", "")
        latency_min = src.get("latency_minutes", 0)
        threshold = thresholds.get(name, 60)
        ok = latency_min <= threshold
        if not ok:
            all_ok = False
        validation_results.append({"name": name, "latency_minutes": latency_min, "ok": ok, "threshold": threshold})

    data_lock = {"sources": validation_results, "all_ok": all_ok, "override": not all_ok}
    sim.data_lock = data_lock
    sim.status = "locked"
    sim.step = 5

    await log_event(db, sim.id, 5, "data_locked", payload={"all_ok": all_ok})
    await db.commit()

    return LockResponse(locked=True, seed=sim.seed, validation_summary={"all_ok": all_ok, "sources": len(validation_results)})


# ── Step 6: run simulation ────────────────────────────────────────────────────

@router.post("/{simulation_id}/run", response_model=RunResponse)
async def run_simulation(simulation_id: uuid.UUID, body: RunRequest, db: DB):
    sim = await _get_simulation_or_404(db, simulation_id)
    if sim.status != "locked":
        raise HTTPException(status_code=400, detail="Simulation must be in 'locked' status to run")

    from app.tasks.simulation_task import run_simulation_task
    task = run_simulation_task.delay(str(simulation_id), [str(sid) for sid in body.scenario_ids], body.n_iterations)

    sim.status = "running"
    sim.step = 6
    await log_event(db, sim.id, 6, "simulation_started", payload={"task_id": task.id, "n_iterations": body.n_iterations})
    await db.commit()

    return RunResponse(task_id=task.id, status="queued")


# ── Step 6: status polling ────────────────────────────────────────────────────

@router.get("/{simulation_id}/status", response_model=StatusResponse)
async def get_status(simulation_id: uuid.UUID, db: DB):
    sim = await _get_simulation_or_404(db, simulation_id)

    progress = None
    current_scenario = None
    eta_seconds = None

    if sim.status == "running":
        try:
            r = aioredis.from_url(settings.redis_url, decode_responses=True)
            raw = await r.get(f"sim_progress:{simulation_id}")
            await r.aclose()
            if raw:
                prog_data = json.loads(raw)
                progress = prog_data.get("progress")
                current_scenario = prog_data.get("current_scenario")
        except Exception:
            pass

    return StatusResponse(
        step=sim.step,
        status=sim.status,
        progress=progress,
        current_scenario=current_scenario,
        eta_seconds=eta_seconds,
    )


# ── Step 7: results ───────────────────────────────────────────────────────────

@router.get("/{simulation_id}/results", response_model=ResultsResponse)
async def get_results(simulation_id: uuid.UUID, db: DB):
    result = await db.execute(select(Result).where(Result.simulation_id == simulation_id))
    results = result.scalars().all()
    ranked = sorted(results, key=lambda r: float(r.composite_score), reverse=True)
    return ResultsResponse(results=list(results), ranked=ranked)


# ── Step 8: rollout plan ──────────────────────────────────────────────────────

@router.post("/{simulation_id}/rollout")
async def generate_rollout(simulation_id: uuid.UUID, db: DB):
    sim = await _get_simulation_or_404(db, simulation_id)
    if sim.status not in ("results_ready", "rollout_ready", "complete"):
        raise HTTPException(status_code=400, detail="Results must be ready before generating rollout plan")

    result = await db.execute(select(Result).where(Result.simulation_id == simulation_id))
    all_results = result.scalars().all()
    if not all_results:
        raise HTTPException(status_code=400, detail="No simulation results found")

    winner = max(all_results, key=lambda r: float(r.composite_score))
    winner_scenario = await db.get(Scenario, winner.scenario_id)

    try:
        from app.agents.rollout_agent import generate_rollout as _rollout
        rollout_plan = await _rollout(sim, winner, winner_scenario)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini error: {exc}") from exc

    sim.rollout_plan = rollout_plan
    sim.status = "rollout_ready"
    sim.step = 8
    await log_event(db, sim.id, 8, "rollout_generated", payload={"winner_scenario": winner_scenario.name if winner_scenario else None})
    await db.commit()

    return {"rollout_plan": rollout_plan}


# ── Step 9: ledger ────────────────────────────────────────────────────────────

@router.get("/{simulation_id}/ledger", response_model=LedgerResponse)
async def get_ledger(simulation_id: uuid.UUID, db: DB, page: int = 1, per_page: int = 50):
    q = select(LedgerEvent).where(LedgerEvent.simulation_id == simulation_id).order_by(LedgerEvent.created_at.desc())
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar_one()
    events_result = await db.execute(q.offset((page - 1) * per_page).limit(per_page))
    return LedgerResponse(events=events_result.scalars().all(), total=total)
