import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger_event import LedgerEvent


async def log_event(
    db: AsyncSession,
    simulation_id: uuid.UUID,
    step: int,
    event_type: str,
    actor: str = "system",
    payload: dict | None = None,
) -> LedgerEvent:
    event = LedgerEvent(
        simulation_id=simulation_id,
        step=step,
        event_type=event_type,
        actor=actor,
        payload=payload,
    )
    db.add(event)
    await db.flush()
    return event
