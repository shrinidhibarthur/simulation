"""Initial schema — 4 tables: simulations, scenarios, results, ledger_events

Revision ID: 0001
Revises:
Create Date: 2025-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── simulations ───────────────────────────────────────────────────────────
    op.create_table(
        "simulations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="draft"),
        sa.Column("step", sa.Integer, nullable=False, server_default="1"),
        sa.Column("request_text", sa.Text, nullable=False),
        sa.Column("use_case_brief", postgresql.JSONB, nullable=True),
        sa.Column("mvt", sa.Text, nullable=True),
        sa.Column("budget", sa.Numeric(12, 2), nullable=True),
        sa.Column("sla_limit", sa.Numeric(5, 4), nullable=True),
        sa.Column("seed", sa.BigInteger, nullable=True),
        sa.Column("csv_path", sa.Text, nullable=True),
        sa.Column("csv_profile", postgresql.JSONB, nullable=True),
        sa.Column("data_lock", postgresql.JSONB, nullable=True),
        sa.Column("rollout_plan", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "status IN ('draft','clarifying','scenarios_ready','configured','locked','running','results_ready','rollout_ready','complete')",
            name="simulations_status_check",
        ),
        sa.CheckConstraint("step BETWEEN 1 AND 9", name="simulations_step_check"),
    )
    op.create_index("ix_simulations_status_created", "simulations", ["status", sa.text("created_at DESC")])

    # updated_at auto-update trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER simulations_updated_at
        BEFORE UPDATE ON simulations
        FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    """)

    # ── scenarios ─────────────────────────────────────────────────────────────
    op.create_table(
        "scenarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("simulation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("storefront", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("marketing", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("ops", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("distribution_params", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("name IN ('Base','Optimistic','Pessimistic')", name="scenarios_name_check"),
    )
    op.create_index("ix_scenarios_simulation_id", "scenarios", ["simulation_id"])

    # ── results ───────────────────────────────────────────────────────────────
    op.create_table(
        "results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("simulation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversion_lift", sa.Numeric(8, 6), nullable=False),
        sa.Column("aov_delta", sa.Numeric(10, 4), nullable=False),
        sa.Column("rpv_lift", sa.Numeric(8, 6), nullable=False),
        sa.Column("margin_impact", sa.Numeric(8, 6), nullable=False),
        sa.Column("stockout_change", sa.Numeric(8, 6), nullable=False),
        sa.Column("markdown_change", sa.Numeric(8, 6), nullable=False),
        sa.Column("cost_to_serve_delta", sa.Numeric(8, 6), nullable=False),
        sa.Column("sla_risk", sa.Numeric(5, 4), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("composite_score", sa.Numeric(8, 6), nullable=False),
        sa.Column("kde_x_values", postgresql.ARRAY(sa.Numeric), nullable=False),
        sa.Column("kde_y_values", postgresql.ARRAY(sa.Numeric), nullable=False),
        sa.Column("win_probability", sa.Numeric(5, 4), nullable=True),
        sa.Column("demand_momentum", sa.Numeric(10, 4), nullable=True),
        sa.Column("visibility_budget", sa.Numeric(12, 2), nullable=True),
        sa.Column("raw_summary", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_results_simulation_scenario", "results", ["simulation_id", "scenario_id"])

    # ── ledger_events ─────────────────────────────────────────────────────────
    op.create_table(
        "ledger_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("simulation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("simulations.id"), nullable=False),
        sa.Column("step", sa.Integer, nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("actor", sa.Text, nullable=False, server_default="system"),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_ledger_simulation_created", "ledger_events", ["simulation_id", sa.text("created_at DESC")])


def downgrade() -> None:
    op.drop_table("ledger_events")
    op.drop_table("results")
    op.drop_table("scenarios")
    op.execute("DROP TRIGGER IF EXISTS simulations_updated_at ON simulations")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at")
    op.drop_table("simulations")
