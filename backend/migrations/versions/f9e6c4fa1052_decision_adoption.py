"""Minimal modern Human Adoption authority.

Revision ID: f9e6c4fa1052
Revises: f8d5b3e9c041
Create Date: 2026-09-26 05:44:00.000000
"""
from __future__ import annotations
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "f9e6c4fa1052"
down_revision: str | None = "f8d5b3e9c041"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table(
        "decision_adoption",
        sa.Column("adoption_id", sa.String(), nullable=False),
        sa.Column("decision_brief_id", sa.String(), nullable=False),
        sa.Column("source_brief_fingerprint", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=False),
        sa.Column("actor_authorization_context_json", sa.Text(), nullable=False),
        sa.Column("disposition", sa.String(), nullable=False),
        sa.Column("selected_option_ids_json", sa.Text(), nullable=False),
        sa.Column("human_rationale", sa.Text(), nullable=True),
        sa.Column("human_conditions_json", sa.Text(), nullable=False),
        sa.Column("supersedes_adoption_id", sa.String(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("adoption_fingerprint", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["decision_brief_id"], ["p21_decision_brief.decision_brief_id"]),
        sa.ForeignKeyConstraint(["supersedes_adoption_id"], ["decision_adoption.adoption_id"]),
        sa.PrimaryKeyConstraint("adoption_id"),
        sa.UniqueConstraint("adoption_fingerprint", name="uq_decision_adoption_fingerprint"),
    )
    for column in (
        "decision_brief_id","source_brief_fingerprint","tenant_binding","actor_user_id",
        "disposition","supersedes_adoption_id","recorded_at","adoption_fingerprint",
    ):
        op.create_index(op.f(f"ix_decision_adoption_{column}"), "decision_adoption", [column])

def downgrade() -> None:
    for column in (
        "adoption_fingerprint","recorded_at","supersedes_adoption_id","disposition",
        "actor_user_id","tenant_binding","source_brief_fingerprint","decision_brief_id",
    ):
        op.drop_index(op.f(f"ix_decision_adoption_{column}"), table_name="decision_adoption")
    op.drop_table("decision_adoption")
