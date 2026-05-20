"""Fix win_probability column precision (NUMERIC(5,4) → NUMERIC(6,2) to hold 0–100)

Revision ID: 0002
Revises: 0001
Create Date: 2025-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "results",
        "win_probability",
        type_=sa.Numeric(6, 2),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "results",
        "win_probability",
        type_=sa.Numeric(5, 4),
        existing_nullable=True,
    )
