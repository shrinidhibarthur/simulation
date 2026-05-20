import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateSimulationRequest(BaseModel):
    request_text: str = Field(..., min_length=10)
    mvt: str | None = None
    budget: float | None = None
    sla_limit: float | None = Field(None, ge=0.0, le=1.0)


class SimulationSchema(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    step: int
    request_text: str
    use_case_brief: dict | None = None
    mvt: str | None = None
    budget: float | None = None
    sla_limit: float | None = None
    seed: int | None = None
    csv_path: str | None = None
    csv_profile: dict | None = None
    data_lock: dict | None = None
    rollout_plan: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SimulationListResponse(BaseModel):
    items: list[SimulationSchema]
    total: int


class ClarifyRequest(BaseModel):
    answers: dict[str, str] | None = None


class ClarifyResponse(BaseModel):
    questions: list[str]
    use_case_brief: dict | None = None
    complete: bool


class LockRequest(BaseModel):
    data_sources: list[dict]


class LockResponse(BaseModel):
    locked: bool
    seed: int
    validation_summary: dict


class RunRequest(BaseModel):
    scenario_ids: list[uuid.UUID]
    n_iterations: int = Field(default=10000, ge=100, le=100000)


class RunResponse(BaseModel):
    task_id: str
    status: str


class StatusResponse(BaseModel):
    step: int
    status: str
    task_id: str | None = None
    progress: float | None = None
    current_scenario: str | None = None
    eta_seconds: int | None = None
