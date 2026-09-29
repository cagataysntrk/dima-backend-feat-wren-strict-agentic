"""Core-B typed product investigation routing.

Revision ID: fc8a1d0e3b42
Revises: fb4e6d2a1074
Create Date: 2026-09-27 02:18:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fc8a1d0e3b42"
down_revision: str | None = "fb4e6d2a1074"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_investigation_requirement",
        sa.Column("routing_record_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("research_session_id", sa.String(), nullable=False),
        sa.Column("brief_id", sa.String(), nullable=False),
        sa.Column("requirement_id", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("source_goal_id", sa.String(), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("requirement_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["research_session_id"],
            ["research_session.session_id"],
        ),
        sa.PrimaryKeyConstraint("routing_record_id"),
        sa.UniqueConstraint(
            "tenant_binding",
            "research_session_id",
            "requirement_id",
            name="uq_product_investigation_requirement_scope",
        ),
        sa.UniqueConstraint(
            "requirement_fingerprint",
            name="uq_product_investigation_requirement_fingerprint",
        ),
    )
    for column in (
        "tenant_binding",
        "research_session_id",
        "brief_id",
        "requirement_id",
        "kind",
        "source_goal_id",
        "requirement_fingerprint",
        "created_at",
    ):
        op.create_index(
            op.f(f"ix_product_investigation_requirement_{column}"),
            "product_investigation_requirement",
            [column],
        )


def downgrade() -> None:
    for column in (
        "created_at",
        "requirement_fingerprint",
        "source_goal_id",
        "kind",
        "requirement_id",
        "brief_id",
        "research_session_id",
        "tenant_binding",
    ):
        op.drop_index(
            op.f(f"ix_product_investigation_requirement_{column}"),
            table_name="product_investigation_requirement",
        )
    op.drop_table("product_investigation_requirement")
