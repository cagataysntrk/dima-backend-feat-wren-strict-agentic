"""P18 minimal business relationship policy authority and use lineage.

Revision ID: f5a1d7c9e2b4
Revises: f3c9d6e2a814
Create Date: 2026-09-25 20:20:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f5a1d7c9e2b4"
down_revision: str | None = "f3c9d6e2a814"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "business_relationship_policy",
        sa.Column("policy_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("policy_key", sa.String(), nullable=False),
        sa.Column("source_business_ref", sa.String(), nullable=False),
        sa.Column("target_business_ref", sa.String(), nullable=False),
        sa.Column("business_relationship_statement", sa.Text(), nullable=False),
        sa.Column("applicability_scope_json", sa.Text(), nullable=False),
        sa.Column(
            "applicability_scope_fingerprint",
            sa.String(),
            nullable=False,
        ),
        sa.Column("policy_fingerprint", sa.String(), nullable=False),
        sa.Column("provenance_ref", sa.String(), nullable=False),
        sa.Column("approved_by_subject", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "retired_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("policy_id"),
        sa.UniqueConstraint(
            "policy_fingerprint",
            name="uq_business_relationship_policy_fingerprint",
        ),
    )
    for column in (
        "tenant_binding",
        "semantic_context_version",
        "policy_key",
        "source_business_ref",
        "target_business_ref",
        "applicability_scope_fingerprint",
        "policy_fingerprint",
        "provenance_ref",
        "approved_by_subject",
        "status",
    ):
        op.create_index(
            op.f(f"ix_business_relationship_policy_{column}"),
            "business_relationship_policy",
            [column],
        )

    op.create_table(
        "business_relationship_policy_use",
        sa.Column("policy_use_id", sa.String(), nullable=False),
        sa.Column("research_session_id", sa.String(), nullable=False),
        sa.Column("obligation_id", sa.String(), nullable=False),
        sa.Column("claim_id", sa.String(), nullable=False),
        sa.Column("reasoning_step_id", sa.String(), nullable=False),
        sa.Column("requirement_fingerprint", sa.String(), nullable=False),
        sa.Column("policy_id", sa.String(), nullable=True),
        sa.Column("policy_fingerprint", sa.String(), nullable=True),
        sa.Column("resolution_status", sa.String(), nullable=False),
        sa.Column("limitation_code", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["research_session_id"],
            ["research_session.session_id"],
        ),
        sa.ForeignKeyConstraint(
            ["claim_id"],
            ["research_claim.claim_id"],
        ),
        sa.ForeignKeyConstraint(
            ["reasoning_step_id"],
            ["research_reasoning_step.step_id"],
        ),
        sa.ForeignKeyConstraint(
            ["policy_id"],
            ["business_relationship_policy.policy_id"],
        ),
        sa.PrimaryKeyConstraint("policy_use_id"),
    )
    for column in (
        "research_session_id",
        "obligation_id",
        "claim_id",
        "reasoning_step_id",
        "requirement_fingerprint",
        "policy_id",
        "policy_fingerprint",
        "resolution_status",
        "limitation_code",
    ):
        op.create_index(
            op.f(f"ix_business_relationship_policy_use_{column}"),
            "business_relationship_policy_use",
            [column],
        )


def downgrade() -> None:
    for column in (
        "limitation_code",
        "resolution_status",
        "policy_fingerprint",
        "policy_id",
        "requirement_fingerprint",
        "reasoning_step_id",
        "claim_id",
        "obligation_id",
        "research_session_id",
    ):
        op.drop_index(
            op.f(f"ix_business_relationship_policy_use_{column}"),
            table_name="business_relationship_policy_use",
        )
    op.drop_table("business_relationship_policy_use")

    for column in (
        "status",
        "approved_by_subject",
        "provenance_ref",
        "policy_fingerprint",
        "applicability_scope_fingerprint",
        "target_business_ref",
        "source_business_ref",
        "policy_key",
        "semantic_context_version",
        "tenant_binding",
    ):
        op.drop_index(
            op.f(f"ix_business_relationship_policy_{column}"),
            table_name="business_relationship_policy",
        )
    op.drop_table("business_relationship_policy")
