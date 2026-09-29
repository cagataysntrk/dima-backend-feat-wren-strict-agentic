"""P16 durable claim-lineage and Evidence edges.

Revision ID: c8b4d7e1a295
Revises: c7e5a9d2b610
Create Date: 2026-09-25 10:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c8b4d7e1a295"
down_revision: str | None = "c7e5a9d2b610"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "research_claim",
        sa.Column("claim_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("obligation_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("principal_subject", sa.String(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("proposition_json", sa.Text(), nullable=False),
        sa.Column("scope_json", sa.Text(), nullable=False),
        sa.Column("freshness_json", sa.Text(), nullable=False),
        sa.Column("origin_material_refs_json", sa.Text(), nullable=False),
        sa.Column("epistemic_state", sa.String(), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=False),
        sa.Column("claim_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["research_session.session_id"]),
        sa.PrimaryKeyConstraint("claim_id"),
    )
    for column in (
        "session_id",
        "obligation_id",
        "tenant_binding",
        "principal_subject",
        "semantic_context_version",
        "epistemic_state",
        "claim_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_research_claim_{column}"),
            "research_claim",
            [column],
        )

    op.create_table(
        "claim_evidence_link",
        sa.Column("link_id", sa.String(), nullable=False),
        sa.Column("claim_id", sa.String(), nullable=False),
        sa.Column("evidence_id", sa.String(), nullable=False),
        sa.Column("receipt_id", sa.String(), nullable=False),
        sa.Column("execution_link_id", sa.Uuid(), nullable=False),
        sa.Column("relation", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["research_claim.claim_id"]),
        sa.ForeignKeyConstraint(["execution_link_id"], ["research_execution_link.id"]),
        sa.PrimaryKeyConstraint("link_id"),
        sa.UniqueConstraint(
            "claim_id",
            "evidence_id",
            name="uq_claim_evidence_link_claim_evidence",
        ),
    )
    for column in (
        "claim_id",
        "evidence_id",
        "receipt_id",
        "execution_link_id",
        "relation",
    ):
        op.create_index(
            op.f(f"ix_claim_evidence_link_{column}"),
            "claim_evidence_link",
            [column],
        )


def downgrade() -> None:
    for column in (
        "relation",
        "execution_link_id",
        "receipt_id",
        "evidence_id",
        "claim_id",
    ):
        op.drop_index(
            op.f(f"ix_claim_evidence_link_{column}"),
            table_name="claim_evidence_link",
        )
    op.drop_table("claim_evidence_link")

    for column in (
        "claim_fingerprint",
        "epistemic_state",
        "semantic_context_version",
        "principal_subject",
        "tenant_binding",
        "obligation_id",
        "session_id",
    ):
        op.drop_index(
            op.f(f"ix_research_claim_{column}"),
            table_name="research_claim",
        )
    op.drop_table("research_claim")
