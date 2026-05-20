import uuid
from datetime import datetime

from pydantic import BaseModel


class ResultSchema(BaseModel):
    id: uuid.UUID
    simulation_id: uuid.UUID
    scenario_id: uuid.UUID
    conversion_lift: float
    aov_delta: float
    rpv_lift: float
    margin_impact: float
    stockout_change: float
    markdown_change: float
    cost_to_serve_delta: float
    sla_risk: float
    confidence: float
    composite_score: float
    kde_x_values: list[float]
    kde_y_values: list[float]
    win_probability: float | None = None
    demand_momentum: float | None = None
    visibility_budget: float | None = None
    raw_summary: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResultsResponse(BaseModel):
    results: list[ResultSchema]
    ranked: list[ResultSchema]
