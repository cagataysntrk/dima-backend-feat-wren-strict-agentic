"""P15 durable native exploration material.

Revision ID: c7e5a9d2b610
Revises: c6f1a2d9e870
Create Date: 2026-09-25 09:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c7e5a9d2b610"
down_revision: str | None = "c6f1a2d9e870"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "research_exploration_material",
        sa.Column("lead_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("obligation_id", sa.String(), nullable=False),
        sa.Column("execution_link_id", sa.Uuid(), nullable=False),
        sa.Column("native_conversation_id", sa.Uuid(), nullable=False),
        sa.Column("native_query_id", sa.String(), nullable=False),
        sa.Column("query_fingerprint", sa.String(), nullable=False),
        sa.Column("source_evidence_refs_json", sa.Text(), nullable=False),
        sa.Column("exploration_kind", sa.String(), nullable=False),
        sa.Column("native_payload_json", sa.Text(), nullable=False),
        sa.Column("payload_fingerprint", sa.String(), nullable=False),
        sa.Column("epistemic_state", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["research_session.session_id"]),
        sa.ForeignKeyConstraint(["execution_link_id"], ["research_execution_link.id"]),
        sa.PrimaryKeyConstraint("lead_id"),
        sa.UniqueConstraint(
            "execution_link_id",
            name="uq_research_exploration_material_execution_link",
        ),
    )
    for column in (
        "session_id",
        "obligation_id",
        "execution_link_id",
        "native_query_id",
        "query_fingerprint",
        "exploration_kind",
        "payload_fingerprint",
        "epistemic_state",
    ):
        op.create_index(
            op.f(f"ix_research_exploration_material_{column}"),
            "research_exploration_material",
            [column],
        )


def downgrade() -> None:
    for column in (
        "epistemic_state",
        "payload_fingerprint",
        "exploration_kind",
        "query_fingerprint",
        "native_query_id",
        "execution_link_id",
        "obligation_id",
        "session_id",
    ):
        op.drop_index(
            op.f(f"ix_research_exploration_material_{column}"),
            table_name="research_exploration_material",
        )
    op.drop_table("research_exploration_material")
