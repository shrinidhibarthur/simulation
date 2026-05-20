import uuid
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Simulation(Base):
    __tablename__ = "simulations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','clarifying','scenarios_ready','configured',"
            "'locked','running','results_ready','rollout_ready','complete')",
            name="simulations_status_check",
        ),
        CheckConstraint("step BETWEEN 1 AND 9", name="simulations_step_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    request_text: Mapped[str] = mapped_column(Text, nullable=False)
    use_case_brief: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    mvt: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    sla_limit: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    seed: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    csv_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    csv_profile: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    data_lock: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    rollout_plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    scenarios: Mapped[list["Scenario"]] = relationship(  # noqa: F821
        "Scenario", back_populates="simulation", cascade="all, delete-orphan", lazy="selectin"
    )
    results: Mapped[list["Result"]] = relationship(  # noqa: F821
        "Result", back_populates="simulation", cascade="all, delete-orphan", lazy="selectin"
    )
    ledger_events: Mapped[list["LedgerEvent"]] = relationship(  # noqa: F821
        "LedgerEvent", back_populates="simulation", cascade="all, delete-orphan", lazy="selectin"
    )
