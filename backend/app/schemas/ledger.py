import uuid
from datetime import datetime

from pydantic import BaseModel


class LedgerEventSchema(BaseModel):
    id: uuid.UUID
    simulation_id: uuid.UUID
    step: int
    event_type: str
    actor: str
    payload: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LedgerResponse(BaseModel):
    events: list[LedgerEventSchema]
    total: int
