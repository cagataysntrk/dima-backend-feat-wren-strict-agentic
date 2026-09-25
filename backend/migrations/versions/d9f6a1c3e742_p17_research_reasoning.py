"""P17 durable Research reasoning-step and investigation-task ledger.

Revision ID: d9f6a1c3e742
Revises: c8b4d7e1a295
Create Date: 2026-09-25 12:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d9f6a1c3e742"
down_revision: str | None = "c8b4d7e1a295"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "research_reasoning_step",
        sa.Column("step_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column("source_snapshot_fingerprint", sa.String(), nullable=False),
        sa.Column("parent_obligation_id", sa.String(), nullable=False),
        sa.Column("proposal_id", sa.String(), nullable=False),
        sa.Column("proposal_json", sa.Text(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("objective_key", sa.String(), nullable=False),
        sa.Column("bounded_objective", sa.Text(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("inspected_evidence_refs_json", sa.Text(), nullable=False),
        sa.Column("inspected_claim_refs_json", sa.Text(), nullable=False),
        sa.Column("inspected_material_refs_json", sa.Text(), nullable=False),
        sa.Column("proposal_fingerprint", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("stop_reason", sa.String(), nullable=True),
        sa.Column("result_refs_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["research_session.session_id"]),
        sa.PrimaryKeyConstraint("step_id"),
    )
    for column in (
        "session_id",
        "source_revision",
        "source_snapshot_fingerprint",
        "parent_obligation_id",
        "proposal_id",
        "action",
        "objective_key",
        "proposal_fingerprint",
        "status",
        "stop_reason",
    ):
        op.create_index(
            op.f(f"ix_research_reasoning_step_{column}"),
            "research_reasoning_step",
            [column],
        )

    op.create_table(
        "research_investigation_task",
        sa.Column("task_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("reasoning_step_id", sa.String(), nullable=False),
        sa.Column("parent_obligation_id", sa.String(), nullable=False),
        sa.Column("bounded_objective", sa.Text(), nullable=False),
        sa.Column("counter_to_claim_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("native_execution_refs_json", sa.Text(), nullable=False),
        sa.Column("material_refs_json", sa.Text(), nullable=False),
        sa.Column("evidence_refs_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["research_session.session_id"]),
        sa.ForeignKeyConstraint(
            ["reasoning_step_id"],
            ["research_reasoning_step.step_id"],
        ),
        sa.PrimaryKeyConstraint("task_id"),
        sa.UniqueConstraint(
            "reasoning_step_id",
            name="uq_research_investigation_task_reasoning_step",
        ),
    )
    for column in (
        "session_id",
        "reasoning_step_id",
        "parent_obligation_id",
        "counter_to_claim_id",
        "status",
    ):
        op.create_index(
            op.f(f"ix_research_investigation_task_{column}"),
            "research_investigation_task",
            [column],
        )


def downgrade() -> None:
    for column in (
        "status",
        "counter_to_claim_id",
        "parent_obligation_id",
        "reasoning_step_id",
        "session_id",
    ):
        op.drop_index(
            op.f(f"ix_research_investigation_task_{column}"),
            table_name="research_investigation_task",
        )
    op.drop_table("research_investigation_task")

    for column in (
        "stop_reason",
        "status",
        "proposal_fingerprint",
        "objective_key",
        "action",
        "proposal_id",
        "parent_obligation_id",
        "source_snapshot_fingerprint",
        "source_revision",
        "session_id",
    ):
        op.drop_index(
            op.f(f"ix_research_reasoning_step_{column}"),
            table_name="research_reasoning_step",
        )
    op.drop_table("research_reasoning_step")
