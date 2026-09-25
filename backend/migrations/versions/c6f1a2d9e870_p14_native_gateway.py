"""P14 thin native subject/resource binding seams.

Revision ID: c6f1a2d9e870
Revises: c4d9e2a7f160
Create Date: 2026-09-25 07:00:00.000000
"""
from __future__ import annotations
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "c6f1a2d9e870"
down_revision: str | None = "c4d9e2a7f160"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table(
        "native_subject_binding",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("dima_user_id", sa.Uuid(), nullable=False),
        sa.Column("metabase_user_id", sa.Integer(), nullable=False),
        sa.Column("security_profile", sa.String(), nullable=False),
        sa.Column("policy_version", sa.String(), nullable=False),
        sa.Column("approved_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["dima_user_id"], ["app_user.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "dima_user_id", name="uq_native_subject_binding_dima_user"),
        sa.UniqueConstraint("tenant_id", "metabase_user_id", name="uq_native_subject_binding_metabase_user"),
    )
    for column in ("tenant_id", "dima_user_id", "metabase_user_id", "enabled"):
        op.create_index(op.f(f"ix_native_subject_binding_{column}"), "native_subject_binding", [column])
    op.create_table(
        "native_resource_binding",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("candidate_id", sa.String(), nullable=False),
        sa.Column("candidate_kind", sa.String(), nullable=False),
        sa.Column("semantic_id", sa.String(), nullable=False),
        sa.Column("canonical_name", sa.String(), nullable=False),
        sa.Column("locator_kind", sa.String(), nullable=False),
        sa.Column("metabase_database_id", sa.Integer(), nullable=False),
        sa.Column("metabase_table_id", sa.Integer(), nullable=True),
        sa.Column("metabase_field_id", sa.Integer(), nullable=True),
        sa.Column("metabase_metric_id", sa.Integer(), nullable=True),
        sa.Column("metabase_entity_id", sa.String(), nullable=True),
        sa.Column("resource_entity_id", sa.String(), nullable=False),
        sa.Column("resource_fingerprint", sa.String(), nullable=False),
        sa.Column("resource_version", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "semantic_context_version", "candidate_id", "candidate_kind",
            name="uq_native_resource_binding_candidate",
        ),
    )
    for column in ("tenant_id", "semantic_context_version", "candidate_id", "semantic_id", "resource_entity_id", "resource_fingerprint", "enabled"):
        op.create_index(op.f(f"ix_native_resource_binding_{column}"), "native_resource_binding", [column])

def downgrade() -> None:
    for column in ("enabled", "resource_fingerprint", "resource_entity_id", "semantic_id", "candidate_id", "semantic_context_version", "tenant_id"):
        op.drop_index(op.f(f"ix_native_resource_binding_{column}"), table_name="native_resource_binding")
    op.drop_table("native_resource_binding")
    for column in ("enabled", "metabase_user_id", "dima_user_id", "tenant_id"):
        op.drop_index(op.f(f"ix_native_subject_binding_{column}"), table_name="native_subject_binding")
    op.drop_table("native_subject_binding")
