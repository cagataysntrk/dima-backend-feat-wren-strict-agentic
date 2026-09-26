"""Minimal ActionPlan / ActionAuthorization authority.

Revision ID: fa07d50b2163
Revises: f9e6c4fa1052
Create Date: 2026-09-26 06:18:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fa07d50b2163"
down_revision: str | None = "f9e6c4fa1052"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "action_authorization",
        sa.Column("authorization_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),

        sa.Column("decision_brief_id", sa.String(), nullable=False),
        sa.Column("decision_brief_fingerprint", sa.String(), nullable=False),
        sa.Column("decision_adoption_id", sa.String(), nullable=False),
        sa.Column("decision_adoption_fingerprint", sa.String(), nullable=False),

        sa.Column("report_id", sa.String(), nullable=False),
        sa.Column("report_fingerprint", sa.String(), nullable=False),

        sa.Column("action_kind", sa.String(), nullable=False),
        sa.Column("target_system", sa.String(), nullable=False),
        sa.Column("target_resource", sa.String(), nullable=False),

        sa.Column("canonical_plan_json", sa.Text(), nullable=False),
        sa.Column("plan_fingerprint", sa.String(), nullable=False),

        sa.Column("capability_key", sa.String(), nullable=False),
        sa.Column("capability_version", sa.String(), nullable=False),
        sa.Column("capability_fingerprint", sa.String(), nullable=False),

        sa.Column("risk_class", sa.String(), nullable=False),
        sa.Column("reversibility", sa.String(), nullable=False),
        sa.Column("confirmation_requirement", sa.String(), nullable=False),
        sa.Column("idempotency_strategy", sa.String(), nullable=False),

        sa.Column("authorization_policy_id", sa.String(), nullable=False),
        sa.Column("authorization_policy_version", sa.String(), nullable=False),

        sa.Column("authorizer_user_id", sa.String(), nullable=False),
        sa.Column("authorizer_context_json", sa.Text(), nullable=False),

        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("supersedes_authorization_id", sa.String(), nullable=True),
        sa.Column("authorization_fingerprint", sa.String(), nullable=False),

        sa.ForeignKeyConstraint(
            ["decision_brief_id"],
            ["p21_decision_brief.decision_brief_id"],
        ),
        sa.ForeignKeyConstraint(
            ["decision_adoption_id"],
            ["decision_adoption.adoption_id"],
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["p20_report_document.report_id"],
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_authorization_id"],
            ["action_authorization.authorization_id"],
        ),
        sa.PrimaryKeyConstraint("authorization_id"),
        sa.UniqueConstraint(
            "authorization_fingerprint",
            name="uq_action_authorization_fingerprint",
        ),
    )

    for column in (
        "tenant_binding",
        "decision_brief_id",
        "decision_brief_fingerprint",
        "decision_adoption_id",
        "decision_adoption_fingerprint",
        "report_id",
        "report_fingerprint",
        "action_kind",
        "target_system",
        "target_resource",
        "plan_fingerprint",
        "capability_key",
        "capability_version",
        "capability_fingerprint",
        "risk_class",
        "authorization_policy_id",
        "authorization_policy_version",
        "authorizer_user_id",
        "issued_at",
        "expires_at",
        "supersedes_authorization_id",
        "authorization_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_action_authorization_{column}"),
            "action_authorization",
            [column],
        )


def downgrade() -> None:
    for column in (
        "authorization_fingerprint",
        "supersedes_authorization_id",
        "expires_at",
        "issued_at",
        "authorizer_user_id",
        "authorization_policy_version",
        "authorization_policy_id",
        "risk_class",
        "capability_fingerprint",
        "capability_version",
        "capability_key",
        "plan_fingerprint",
        "target_resource",
        "target_system",
        "action_kind",
        "report_fingerprint",
        "report_id",
        "decision_adoption_fingerprint",
        "decision_adoption_id",
        "decision_brief_fingerprint",
        "decision_brief_id",
        "tenant_binding",
    ):
        op.drop_index(
            op.f(f"ix_action_authorization_{column}"),
            table_name="action_authorization",
        )
    op.drop_table("action_authorization")
