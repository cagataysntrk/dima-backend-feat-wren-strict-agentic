"""R1 durable P17 child analytical scope.

Revision ID: fd2a7c9e4b61
Revises: fc8a1d0e3b42
Create Date: 2026-09-28 13:55:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fd2a7c9e4b61"
down_revision: str | None = "fc8a1d0e3b42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Historical completed tasks remain readable. Every newly created P17 native
    # child is required by application code to persist its typed scope contract.
    with op.batch_alter_table("research_investigation_task") as batch:
        batch.add_column(
            sa.Column("analytical_scope_json", sa.Text(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("research_investigation_task") as batch:
        batch.drop_column("analytical_scope_json")
