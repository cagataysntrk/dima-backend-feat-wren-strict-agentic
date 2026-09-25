"""P17 minimal recursive investigation topology on the existing reasoning ledger.

Revision ID: f3c9d6e2a814
Revises: e1a7b4c9d305
Create Date: 2026-09-25 13:45:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f3c9d6e2a814"
down_revision: str | None = "e1a7b4c9d305"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Additive compatibility migration only. Existing flat P17 rows remain valid
    # as depth-0 legacy roots; no destructive rewrite of historical proposals.
    with op.batch_alter_table("research_reasoning_step") as batch:
        batch.add_column(
            sa.Column("parent_step_id", sa.String(), nullable=True)
        )
        batch.add_column(
            sa.Column(
                "depth",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch.add_column(
            sa.Column(
                "branch_id",
                sa.String(),
                nullable=False,
                server_default="legacy-root",
            )
        )
        batch.add_column(
            sa.Column(
                "intent",
                sa.String(),
                nullable=False,
                server_default="LEGACY",
            )
        )
        batch.add_column(
            sa.Column(
                "target_kind",
                sa.String(),
                nullable=False,
                server_default="GAP",
            )
        )
        batch.add_column(
            sa.Column("target_ref", sa.String(), nullable=True)
        )
        batch.add_column(
            sa.Column("stop_scope", sa.String(), nullable=True)
        )

        batch.create_index(
            op.f("ix_research_reasoning_step_parent_step_id"),
            ["parent_step_id"],
        )
        batch.create_index(
            op.f("ix_research_reasoning_step_depth"),
            ["depth"],
        )
        batch.create_index(
            op.f("ix_research_reasoning_step_branch_id"),
            ["branch_id"],
        )
        batch.create_index(
            op.f("ix_research_reasoning_step_intent"),
            ["intent"],
        )
        batch.create_index(
            op.f("ix_research_reasoning_step_target_kind"),
            ["target_kind"],
        )
        batch.create_index(
            op.f("ix_research_reasoning_step_target_ref"),
            ["target_ref"],
        )
        batch.create_index(
            op.f("ix_research_reasoning_step_stop_scope"),
            ["stop_scope"],
        )
        batch.create_foreign_key(
            "fk_research_reasoning_step_parent",
            "research_reasoning_step",
            ["parent_step_id"],
            ["step_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("research_reasoning_step") as batch:
        batch.drop_constraint(
            "fk_research_reasoning_step_parent",
            type_="foreignkey",
        )
        for column in (
            "stop_scope",
            "target_ref",
            "target_kind",
            "intent",
            "branch_id",
            "depth",
            "parent_step_id",
        ):
            batch.drop_index(
                op.f(f"ix_research_reasoning_step_{column}")
            )
        batch.drop_column("stop_scope")
        batch.drop_column("target_ref")
        batch.drop_column("target_kind")
        batch.drop_column("intent")
        batch.drop_column("branch_id")
        batch.drop_column("depth")
        batch.drop_column("parent_step_id")
