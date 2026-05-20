import uuid
from datetime import datetime

from pydantic import BaseModel


class ScenarioSchema(BaseModel):
    id: uuid.UUID
    simulation_id: uuid.UUID
    name: str
    storefront: dict
    marketing: dict
    ops: dict
    notes: str | None = None
    distribution_params: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScenariosResponse(BaseModel):
    scenarios: list[ScenarioSchema]
