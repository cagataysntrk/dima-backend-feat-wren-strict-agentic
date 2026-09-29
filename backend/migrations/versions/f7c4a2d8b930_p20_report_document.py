"""P20 immutable governed ReportDocument authority.

Revision ID: f7c4a2d8b930
Revises: f6b2e8c4a917
Create Date: 2026-09-26 00:30:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "f7c4a2d8b930"
down_revision: str | None = "f6b2e8c4a917"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "p20_report_document",
        sa.Column("report_id", sa.String(), nullable=False),
        sa.Column("research_session_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("semantic_context_version", sa.String(), nullable=False),
        sa.Column("report_key", sa.String(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("parent_report_id", sa.String(), nullable=True),
        sa.Column("coverage_json", sa.Text(), nullable=False),
        sa.Column("statements_json", sa.Text(), nullable=False),
        sa.Column("source_refs_json", sa.Text(), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=False),
        sa.Column("source_set_fingerprint", sa.String(), nullable=False),
        sa.Column("report_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["research_session_id"], ["research_session.session_id"]),
        sa.ForeignKeyConstraint(["parent_report_id"], ["p20_report_document.report_id"]),
        sa.PrimaryKeyConstraint("report_id"),
        sa.UniqueConstraint("research_session_id", "report_key", "revision", name="uq_p20_report_document_revision"),
        sa.UniqueConstraint("report_fingerprint", name="uq_p20_report_document_fingerprint"),
    )
    for column in (
        "research_session_id",
        "tenant_binding",
        "semantic_context_version",
        "report_key",
        "revision",
        "parent_report_id",
        "source_set_fingerprint",
        "report_fingerprint",
    ):
        op.create_index(op.f(f"ix_p20_report_document_{column}"), "p20_report_document", [column])


def downgrade() -> None:
    for column in (
        "report_fingerprint",
        "source_set_fingerprint",
        "parent_report_id",
        "revision",
        "report_key",
        "semantic_context_version",
        "tenant_binding",
        "research_session_id",
    ):
        op.drop_index(op.f(f"ix_p20_report_document_{column}"), table_name="p20_report_document")
    op.drop_table("p20_report_document")
