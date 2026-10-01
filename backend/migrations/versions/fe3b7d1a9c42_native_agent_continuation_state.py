"""Durable native Metabot continuation state provenance.

Revision ID: fe3b7d1a9c42
Revises: fd2a7c9e4b61
Create Date: 2026-10-01 07:05:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fe3b7d1a9c42"
down_revision: str | None = "fd2a7c9e4b61"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("research_execution_link") as batch:
        batch.add_column(
            sa.Column("native_agent_state_json", sa.Text(), nullable=True)
        )
        batch.add_column(
            sa.Column(
                "native_agent_state_fingerprint",
                sa.String(),
                nullable=True,
            )
        )
        batch.create_index(
            op.f(
                "ix_research_execution_link_native_agent_state_fingerprint"
            ),
            ["native_agent_state_fingerprint"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("research_execution_link") as batch:
        batch.drop_index(
            op.f(
                "ix_research_execution_link_native_agent_state_fingerprint"
            )
        )
        batch.drop_column("native_agent_state_fingerprint")
        batch.drop_column("native_agent_state_json")
