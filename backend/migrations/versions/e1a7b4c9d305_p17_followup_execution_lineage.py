"""P17 distinguish sealed P14 base occurrences from subordinate follow-ups.

Revision ID: e1a7b4c9d305
Revises: d9f6a1c3e742
Create Date: 2026-09-25 13:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e1a7b4c9d305"
down_revision: str | None = "d9f6a1c3e742"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("research_execution_link") as batch:
        batch.add_column(
            sa.Column(
                "execution_kind",
                sa.String(),
                nullable=False,
                server_default="P14_BASE",
            )
        )
        batch.add_column(
            sa.Column("reasoning_step_id", sa.String(), nullable=True)
        )
        batch.add_column(
            sa.Column("investigation_task_id", sa.String(), nullable=True)
        )
        batch.create_index(
            op.f("ix_research_execution_link_execution_kind"),
            ["execution_kind"],
        )
        batch.create_index(
            op.f("ix_research_execution_link_reasoning_step_id"),
            ["reasoning_step_id"],
        )
        batch.create_index(
            op.f("ix_research_execution_link_investigation_task_id"),
            ["investigation_task_id"],
        )
        batch.create_foreign_key(
            "fk_research_execution_link_reasoning_step",
            "research_reasoning_step",
            ["reasoning_step_id"],
            ["step_id"],
        )
        batch.create_foreign_key(
            "fk_research_execution_link_investigation_task",
            "research_investigation_task",
            ["investigation_task_id"],
            ["task_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("research_execution_link") as batch:
        batch.drop_constraint(
            "fk_research_execution_link_investigation_task",
            type_="foreignkey",
        )
        batch.drop_constraint(
            "fk_research_execution_link_reasoning_step",
            type_="foreignkey",
        )
        batch.drop_index(
            op.f("ix_research_execution_link_investigation_task_id")
        )
        batch.drop_index(
            op.f("ix_research_execution_link_reasoning_step_id")
        )
        batch.drop_index(
            op.f("ix_research_execution_link_execution_kind")
        )
        batch.drop_column("investigation_task_id")
        batch.drop_column("reasoning_step_id")
        batch.drop_column("execution_kind")
