"""P19 minimal hypothesis/root-cause epistemic authority.

Revision ID: f6b2e8c4a917
Revises: f5a1d7c9e2b4
Create Date: 2026-09-25 20:20:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f6b2e8c4a917"
down_revision: str | None = "f5a1d7c9e2b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "p19_hypothesis",
        sa.Column("hypothesis_id", sa.String(), nullable=False),
        sa.Column("research_session_id", sa.String(), nullable=False),
        sa.Column("obligation_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("identity_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["research_session_id"],
            ["research_session.session_id"],
        ),
        sa.PrimaryKeyConstraint("hypothesis_id"),
        sa.UniqueConstraint(
            "identity_fingerprint",
            name="uq_p19_hypothesis_identity_fingerprint",
        ),
    )
    for column in (
        "research_session_id",
        "obligation_id",
        "tenant_binding",
        "semantic_context_version",
        "identity_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_p19_hypothesis_{column}"),
            "p19_hypothesis",
            [column],
        )

    op.create_table(
        "p19_hypothesis_grounding",
        sa.Column("grounding_link_id", sa.String(), nullable=False),
        sa.Column("hypothesis_id", sa.String(), nullable=False),
        sa.Column("source_kind", sa.String(), nullable=False),
        sa.Column("source_ref", sa.String(), nullable=False),
        sa.Column("source_receipt_id", sa.String(), nullable=True),
        sa.Column("relation", sa.String(), nullable=False),
        sa.Column("link_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["hypothesis_id"],
            ["p19_hypothesis.hypothesis_id"],
        ),
        sa.PrimaryKeyConstraint("grounding_link_id"),
        sa.UniqueConstraint(
            "link_fingerprint",
            name="uq_p19_hypothesis_grounding_fingerprint",
        ),
    )
    for column in (
        "hypothesis_id",
        "source_kind",
        "source_ref",
        "source_receipt_id",
        "relation",
        "link_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_p19_hypothesis_grounding_{column}"),
            "p19_hypothesis_grounding",
            [column],
        )

    op.create_table(
        "p19_root_cause_assessment",
        sa.Column("assessment_id", sa.String(), nullable=False),
        sa.Column("research_session_id", sa.String(), nullable=False),
        sa.Column("obligation_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("candidate_assessments_json", sa.Text(), nullable=False),
        sa.Column("root_cause_hypothesis_ids_json", sa.Text(), nullable=False),
        sa.Column("aggregate_outcome", sa.String(), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=False),
        sa.Column("numeric_provenance_json", sa.Text(), nullable=False),
        sa.Column("mediation_annotations_json", sa.Text(), nullable=False),
        sa.Column("assessment_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["research_session_id"],
            ["research_session.session_id"],
        ),
        sa.PrimaryKeyConstraint("assessment_id"),
        sa.UniqueConstraint(
            "assessment_fingerprint",
            name="uq_p19_root_cause_assessment_fingerprint",
        ),
    )
    for column in (
        "research_session_id",
        "obligation_id",
        "tenant_binding",
        "semantic_context_version",
        "aggregate_outcome",
        "assessment_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_p19_root_cause_assessment_{column}"),
            "p19_root_cause_assessment",
            [column],
        )


def downgrade() -> None:
    for column in (
        "assessment_fingerprint",
        "aggregate_outcome",
        "semantic_context_version",
        "tenant_binding",
        "obligation_id",
        "research_session_id",
    ):
        op.drop_index(
            op.f(f"ix_p19_root_cause_assessment_{column}"),
            table_name="p19_root_cause_assessment",
        )
    op.drop_table("p19_root_cause_assessment")

    for column in (
        "link_fingerprint",
        "relation",
        "source_receipt_id",
        "source_ref",
        "source_kind",
        "hypothesis_id",
    ):
        op.drop_index(
            op.f(f"ix_p19_hypothesis_grounding_{column}"),
            table_name="p19_hypothesis_grounding",
        )
    op.drop_table("p19_hypothesis_grounding")

    for column in (
        "identity_fingerprint",
        "semantic_context_version",
        "tenant_binding",
        "obligation_id",
        "research_session_id",
    ):
        op.drop_index(
            op.f(f"ix_p19_hypothesis_{column}"),
            table_name="p19_hypothesis",
        )
    op.drop_table("p19_hypothesis")
