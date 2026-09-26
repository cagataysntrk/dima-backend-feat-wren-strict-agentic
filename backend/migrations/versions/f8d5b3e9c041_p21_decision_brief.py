"""P21 immutable advisory DecisionBrief authority.

Revision ID: f8d5b3e9c041
Revises: f7c4a2d8b930
Create Date: 2026-09-26 05:05:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f8d5b3e9c041"
down_revision: str | None = "f7c4a2d8b930"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "p21_decision_brief",
        sa.Column("decision_brief_id", sa.String(), nullable=False),
        sa.Column("report_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("brief_key", sa.String(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("parent_decision_brief_id", sa.String(), nullable=True),
        sa.Column("objective_json", sa.Text(), nullable=False),
        sa.Column("constraints_json", sa.Text(), nullable=False),
        sa.Column("options_json", sa.Text(), nullable=False),
        sa.Column("tradeoffs_json", sa.Text(), nullable=False),
        sa.Column("recommendation_json", sa.Text(), nullable=False),
        sa.Column("premise_refs_json", sa.Text(), nullable=False),
        sa.Column("assumptions_json", sa.Text(), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=False),
        sa.Column("model_provenance_json", sa.Text(), nullable=True),
        sa.Column("source_report_fingerprint", sa.String(), nullable=False),
        sa.Column("decision_source_fingerprint", sa.String(), nullable=False),
        sa.Column("brief_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["p20_report_document.report_id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_decision_brief_id"],
            ["p21_decision_brief.decision_brief_id"],
        ),
        sa.PrimaryKeyConstraint("decision_brief_id"),
        sa.UniqueConstraint(
            "tenant_binding",
            "brief_key",
            "revision",
            name="uq_p21_decision_brief_revision",
        ),
        sa.UniqueConstraint(
            "brief_fingerprint",
            name="uq_p21_decision_brief_fingerprint",
        ),
    )
    for column in (
        "report_id",
        "tenant_binding",
        "semantic_context_version",
        "brief_key",
        "revision",
        "parent_decision_brief_id",
        "source_report_fingerprint",
        "decision_source_fingerprint",
        "brief_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_p21_decision_brief_{column}"),
            "p21_decision_brief",
            [column],
        )


def downgrade() -> None:
    for column in (
        "brief_fingerprint",
        "decision_source_fingerprint",
        "source_report_fingerprint",
        "parent_decision_brief_id",
        "revision",
        "brief_key",
        "semantic_context_version",
        "tenant_binding",
        "report_id",
    ):
        op.drop_index(
            op.f(f"ix_p21_decision_brief_{column}"),
            table_name="p21_decision_brief",
        )
    op.drop_table("p21_decision_brief")
