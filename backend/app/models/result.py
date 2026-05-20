import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Result(Base):
    __tablename__ = "results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False
    )

    # Core KPIs (ported from SimResult in simulation_lab_demo_streamlit_app.py)
    conversion_lift: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    aov_delta: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    rpv_lift: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    margin_impact: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    stockout_change: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    markdown_change: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    cost_to_serve_delta: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    sla_risk: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)

    # Composite score: confidence×0.25 + rpv_lift×0.3 + conversion_lift×0.2 + margin_impact×0.15 + sla_factor×0.05
    composite_score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)

    # KDE arrays for chart rendering (512 points, zipped client-side)
    kde_x_values: Mapped[list] = mapped_column(ARRAY(Numeric), nullable=False, default=list)
    kde_y_values: Mapped[list] = mapped_column(ARRAY(Numeric), nullable=False, default=list)

    # Beacon metrics (ported from simulation_lab_beacon_integrated.py)
    win_probability: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)  # 0.00–100.00
    demand_momentum: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    visibility_budget: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Summary stats only — not 10k raw rows
    raw_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    simulation: Mapped["Simulation"] = relationship("Simulation", back_populates="results")  # noqa: F821
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="results")  # noqa: F821
