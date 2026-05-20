import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = (
        CheckConstraint(
            "name IN ('Base','Optimistic','Pessimistic')",
            name="scenarios_name_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    storefront: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    marketing: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ops: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    distribution_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    simulation: Mapped["Simulation"] = relationship("Simulation", back_populates="scenarios")  # noqa: F821
    results: Mapped[list["Result"]] = relationship(  # noqa: F821
        "Result", back_populates="scenario", cascade="all, delete-orphan", lazy="selectin"
    )
