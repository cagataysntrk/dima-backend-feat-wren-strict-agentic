"""P14 durable Research session and exact-occurrence correlation.

Revision ID: c4d9e2a7f160
Revises: b3e9f1a7c840
Create Date: 2026-09-24 23:00:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4d9e2a7f160"
down_revision: str | None = "b3e9f1a7c840"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "research_session",
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("principal_subject", sa.String(), nullable=False),
        sa.Column("authority_id", sa.String(), nullable=False),
        sa.Column("context_version", sa.String(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("checkpoint_json", sa.Text(), nullable=False),
        sa.Column("checkpoint_fingerprint", sa.String(), nullable=False),
        sa.Column("delegatable_ids_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("session_id"),
    )
    for column in (
        "tenant_binding",
        "principal_subject",
        "authority_id",
        "checkpoint_fingerprint",
    ):
        op.create_index(
            op.f(f"ix_research_session_{column}"),
            "research_session",
            [column],
        )

    op.create_table(
        "research_execution_link",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("obligation_id", sa.String(), nullable=False),
        sa.Column("dima_request_id", sa.String(), nullable=False),
        sa.Column("dima_trace_id", sa.String(), nullable=False),
        sa.Column("native_conversation_id", sa.Uuid(), nullable=False),
        sa.Column("native_query_id", sa.String(), nullable=True),
        sa.Column("attestation_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("receipt_id", sa.String(), nullable=True),
        sa.Column("evidence_id", sa.String(), nullable=True),
        sa.Column("limitation_code", sa.String(), nullable=True),
        sa.Column("limitation_detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["research_session.session_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dima_request_id",
            name="uq_research_execution_link_request",
        ),
    )
    for column in (
        "session_id",
        "obligation_id",
        "dima_request_id",
        "native_query_id",
        "status",
        "receipt_id",
        "evidence_id",
    ):
        op.create_index(
            op.f(f"ix_research_execution_link_{column}"),
            "research_execution_link",
            [column],
        )


def downgrade() -> None:
    for column in (
        "evidence_id",
        "receipt_id",
        "status",
        "native_query_id",
        "dima_request_id",
        "obligation_id",
        "session_id",
    ):
        op.drop_index(
            op.f(f"ix_research_execution_link_{column}"),
            table_name="research_execution_link",
        )
    op.drop_table("research_execution_link")
    for column in (
        "checkpoint_fingerprint",
        "authority_id",
        "principal_subject",
        "tenant_binding",
    ):
        op.drop_index(
            op.f(f"ix_research_session_{column}"),
            table_name="research_session",
        )
    op.drop_table("research_session")
