"""Durable exact-execution facts snapshot.

Revision ID: 0d7e4b2a9c61
Revises: ff5b8e2c1a73
Create Date: 2026-10-08 15:50:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0d7e4b2a9c61"
down_revision: str | None = "ff5b8e2c1a73"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("research_execution_link") as batch:
        batch.add_column(
            sa.Column("execution_facts_json", sa.Text(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("research_execution_link") as batch:
        batch.drop_column("execution_facts_json")
