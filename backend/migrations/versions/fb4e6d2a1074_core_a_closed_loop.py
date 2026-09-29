"""Core Closure A durable closed-loop brain owners.

Revision ID: fb4e6d2a1074
Revises: fa07d50b2163
Create Date: 2026-09-26 09:20:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fb4e6d2a1074"
down_revision: str | None = "fa07d50b2163"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _indexes(table: str, columns: tuple[str, ...]) -> None:
    for column in columns:
        op.create_index(op.f(f"ix_{table}_{column}"), table, [column])


def upgrade() -> None:
    op.create_table(
        "action_work",
        sa.Column("action_work_id", sa.String(), nullable=False),
        sa.Column("root_action_work_id", sa.String(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("parent_action_work_id", sa.String(), nullable=True),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("decision_brief_id", sa.String(), nullable=False),
        sa.Column("decision_brief_fingerprint", sa.String(), nullable=False),
        sa.Column("decision_adoption_id", sa.String(), nullable=False),
        sa.Column("decision_adoption_fingerprint", sa.String(), nullable=False),
        sa.Column("action_authorization_id", sa.String(), nullable=True),
        sa.Column("action_authorization_fingerprint", sa.String(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("work_intent_json", sa.Text(), nullable=False),
        sa.Column("owner_user_id", sa.String(), nullable=False),
        sa.Column("owner_context_json", sa.Text(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("blocker_reason", sa.Text(), nullable=True),
        sa.Column("completion_reference", sa.Text(), nullable=True),
        sa.Column("transition_history_json", sa.Text(), nullable=False),
        sa.Column("source_fingerprint", sa.String(), nullable=False),
        sa.Column("work_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_action_work_id"], ["action_work.action_work_id"]
        ),
        sa.ForeignKeyConstraint(
            ["decision_brief_id"], ["p21_decision_brief.decision_brief_id"]
        ),
        sa.ForeignKeyConstraint(
            ["decision_adoption_id"], ["decision_adoption.adoption_id"]
        ),
        sa.ForeignKeyConstraint(
            ["action_authorization_id"], ["action_authorization.authorization_id"]
        ),
        sa.PrimaryKeyConstraint("action_work_id"),
        sa.UniqueConstraint(
            "root_action_work_id",
            "revision",
            name="uq_action_work_root_revision",
        ),
        sa.UniqueConstraint(
            "work_fingerprint",
            name="uq_action_work_fingerprint",
        ),
    )
    _indexes(
        "action_work",
        (
            "root_action_work_id",
            "revision",
            "parent_action_work_id",
            "tenant_binding",
            "decision_brief_id",
            "decision_brief_fingerprint",
            "decision_adoption_id",
            "decision_adoption_fingerprint",
            "action_authorization_id",
            "action_authorization_fingerprint",
            "owner_user_id",
            "due_at",
            "status",
            "source_fingerprint",
            "work_fingerprint",
            "created_at",
        ),
    )

    op.create_table(
        "outcome_observation",
        sa.Column("outcome_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("action_work_id", sa.String(), nullable=False),
        sa.Column("action_work_fingerprint", sa.String(), nullable=False),
        sa.Column("decision_brief_id", sa.String(), nullable=False),
        sa.Column("decision_adoption_id", sa.String(), nullable=False),
        sa.Column("evidence_refs_json", sa.Text(), nullable=False),
        sa.Column("claim_ids_json", sa.Text(), nullable=False),
        sa.Column("report_id", sa.String(), nullable=True),
        sa.Column("report_fingerprint", sa.String(), nullable=True),
        sa.Column("baseline_definition", sa.Text(), nullable=False),
        sa.Column("baseline_window", sa.Text(), nullable=False),
        sa.Column("observation_window", sa.Text(), nullable=False),
        sa.Column("expected_target_ref", sa.Text(), nullable=True),
        sa.Column("observed_result_refs_json", sa.Text(), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=False),
        sa.Column("classification", sa.String(), nullable=False),
        sa.Column("source_fingerprint", sa.String(), nullable=False),
        sa.Column("outcome_fingerprint", sa.String(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorder_user_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["action_work_id"], ["action_work.action_work_id"]),
        sa.ForeignKeyConstraint(
            ["decision_brief_id"], ["p21_decision_brief.decision_brief_id"]
        ),
        sa.ForeignKeyConstraint(
            ["decision_adoption_id"], ["decision_adoption.adoption_id"]
        ),
        sa.ForeignKeyConstraint(["report_id"], ["p20_report_document.report_id"]),
        sa.PrimaryKeyConstraint("outcome_id"),
        sa.UniqueConstraint(
            "outcome_fingerprint",
            name="uq_outcome_observation_fingerprint",
        ),
    )
    _indexes(
        "outcome_observation",
        (
            "tenant_binding",
            "action_work_id",
            "action_work_fingerprint",
            "decision_brief_id",
            "decision_adoption_id",
            "report_id",
            "report_fingerprint",
            "classification",
            "source_fingerprint",
            "outcome_fingerprint",
            "observed_at",
            "recorder_user_id",
        ),
    )

    op.create_table(
        "institutional_memory_entry",
        sa.Column("memory_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("problem_type", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("entity_refs_json", sa.Text(), nullable=False),
        sa.Column("metric_refs_json", sa.Text(), nullable=False),
        sa.Column("source_refs_json", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("limitations_json", sa.Text(), nullable=False),
        sa.Column("precedent_of_memory_id", sa.String(), nullable=True),
        sa.Column("source_set_fingerprint", sa.String(), nullable=False),
        sa.Column("memory_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("indexed_by_user_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["precedent_of_memory_id"],
            ["institutional_memory_entry.memory_id"],
        ),
        sa.PrimaryKeyConstraint("memory_id"),
        sa.UniqueConstraint(
            "memory_fingerprint",
            name="uq_institutional_memory_fingerprint",
        ),
    )
    _indexes(
        "institutional_memory_entry",
        (
            "tenant_binding",
            "role",
            "problem_type",
            "domain",
            "precedent_of_memory_id",
            "source_set_fingerprint",
            "memory_fingerprint",
            "created_at",
            "indexed_by_user_id",
        ),
    )

    op.create_table(
        "watch",
        sa.Column("watch_id", sa.String(), nullable=False),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("source_contract_ref", sa.Text(), nullable=False),
        sa.Column("criterion_ref", sa.Text(), nullable=False),
        sa.Column("entity_refs_json", sa.Text(), nullable=False),
        sa.Column("metric_refs_json", sa.Text(), nullable=False),
        sa.Column("context_refs_json", sa.Text(), nullable=False),
        sa.Column("watch_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_user_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("watch_id"),
        sa.UniqueConstraint("watch_fingerprint", name="uq_watch_fingerprint"),
    )
    _indexes(
        "watch",
        (
            "tenant_binding",
            "kind",
            "watch_fingerprint",
            "created_at",
            "created_by_user_id",
        ),
    )

    op.create_table(
        "signal",
        sa.Column("signal_id", sa.String(), nullable=False),
        sa.Column("root_signal_id", sa.String(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("parent_signal_id", sa.String(), nullable=True),
        sa.Column("tenant_binding", sa.String(), nullable=False),
        sa.Column("watch_id", sa.String(), nullable=False),
        sa.Column("source_occurrence_id", sa.String(), nullable=False),
        sa.Column("occurrence_fingerprint", sa.String(), nullable=False),
        sa.Column("source_kind", sa.String(), nullable=False),
        sa.Column("source_ref", sa.Text(), nullable=False),
        sa.Column("evidence_ref_json", sa.Text(), nullable=True),
        sa.Column("entity_refs_json", sa.Text(), nullable=False),
        sa.Column("metric_refs_json", sa.Text(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("business_significance", sa.Text(), nullable=False),
        sa.Column("memory_entry_id", sa.String(), nullable=True),
        sa.Column("action_work_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("research_session_id", sa.String(), nullable=True),
        sa.Column("resolution_ref", sa.Text(), nullable=True),
        sa.Column("transition_history_json", sa.Text(), nullable=False),
        sa.Column("signal_fingerprint", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["parent_signal_id"], ["signal.signal_id"]),
        sa.ForeignKeyConstraint(["watch_id"], ["watch.watch_id"]),
        sa.ForeignKeyConstraint(
            ["memory_entry_id"], ["institutional_memory_entry.memory_id"]
        ),
        sa.ForeignKeyConstraint(["action_work_id"], ["action_work.action_work_id"]),
        sa.ForeignKeyConstraint(
            ["research_session_id"], ["research_session.session_id"]
        ),
        sa.PrimaryKeyConstraint("signal_id"),
        sa.UniqueConstraint(
            "root_signal_id",
            "revision",
            name="uq_signal_root_revision",
        ),
        sa.UniqueConstraint(
            "signal_fingerprint",
            name="uq_signal_fingerprint",
        ),
    )
    _indexes(
        "signal",
        (
            "root_signal_id",
            "revision",
            "parent_signal_id",
            "tenant_binding",
            "watch_id",
            "source_occurrence_id",
            "occurrence_fingerprint",
            "source_kind",
            "observed_at",
            "severity",
            "memory_entry_id",
            "action_work_id",
            "status",
            "research_session_id",
            "signal_fingerprint",
            "created_at",
        ),
    )


def downgrade() -> None:
    op.drop_table("signal")
    op.drop_table("watch")
    op.drop_table("institutional_memory_entry")
    op.drop_table("outcome_observation")
    op.drop_table("action_work")
