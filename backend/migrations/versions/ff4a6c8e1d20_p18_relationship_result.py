"""Immutable P18 relationship-result terminal artifact.

Revision ID: ff4a6c8e1d20
Revises: fe3b7d1a9c42
Create Date: 2026-10-02 12:50:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ff4a6c8e1d20"
down_revision: str | None = "fe3b7d1a9c42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "p18_relationship_result",
        sa.Column("result_id", sa.String(), nullable=False),
        sa.Column("research_session_id", sa.String(), nullable=False),
        sa.Column("obligation_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("scope_lineage_id", sa.String(), nullable=False),
        sa.Column("scope_version_id", sa.String(), nullable=False),
        sa.Column("disposition", sa.String(), nullable=False),
        sa.Column("projection_json", sa.Text(), nullable=False),
        sa.Column("result_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["research_session_id"],
            ["research_session.session_id"],
        ),
        sa.PrimaryKeyConstraint("result_id"),
        sa.UniqueConstraint(
            "result_fingerprint",
            name="uq_p18_relationship_result_fingerprint",
        ),
    )
    for column in (
        "research_session_id",
        "obligation_id",
        "tenant_binding",
        "semantic_context_version",
        "scope_lineage_id",
        "scope_version_id",
        "disposition",
        "result_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_p18_relationship_result_{column}"),
            "p18_relationship_result",
            [column],
        )


def downgrade() -> None:
    for column in (
        "result_fingerprint",
        "disposition",
        "scope_version_id",
        "scope_lineage_id",
        "semantic_context_version",
        "tenant_binding",
        "obligation_id",
        "research_session_id",
    ):
        op.drop_index(
            op.f(f"ix_p18_relationship_result_{column}"),
            table_name="p18_relationship_result",
        )
    op.drop_table("p18_relationship_result")
