"""Decouple forward P18 policy-use lineage from P17 reasoning steps.

Revision ID: ff5b8e2c1a73
Revises: ff4a6c8e1d20
Create Date: 2026-10-02 15:45:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ff5b8e2c1a73"
down_revision: str | None = "ff4a6c8e1d20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "business_relationship_policy_use",
        sa.Column("interpretation_ref", sa.String(), nullable=True),
    )
    op.create_index(
        op.f("ix_business_relationship_policy_use_interpretation_ref"),
        "business_relationship_policy_use",
        ["interpretation_ref"],
    )
    op.alter_column(
        "business_relationship_policy_use",
        "reasoning_step_id",
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade() -> None:
    connection = op.get_bind()
    forward_rows = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM business_relationship_policy_use "
            "WHERE reasoning_step_id IS NULL"
        )
    ).scalar_one()
    if forward_rows:
        raise RuntimeError(
            "cannot downgrade P18 interpretation provenance while forward rows exist"
        )
    op.alter_column(
        "business_relationship_policy_use",
        "reasoning_step_id",
        existing_type=sa.String(),
        nullable=False,
    )
    op.drop_index(
        op.f("ix_business_relationship_policy_use_interpretation_ref"),
        table_name="business_relationship_policy_use",
    )
    op.drop_column(
        "business_relationship_policy_use",
        "interpretation_ref",
    )
