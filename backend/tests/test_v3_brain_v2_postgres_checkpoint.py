from __future__ import annotations

import hashlib
import os

import pytest
from psycopg import connect

from app.v3.brain_v2.activities import (
    CanonicalizeActivityResult,
    CompletionActivityResult,
    EvidenceActivityResult,
    IntakeActivityResult,
    MaterialActivityResult,
    MaterialGroupActivityResult,
    P18ActivityResult,
    RequirementPlanActivityResult,
    P19ActivityResult,
    ReportActivityResult,
)
from app.v3.brain_v2.checkpoint import postgres_checkpoint_saver
from app.v3.brain_v2.service import BrainV2Service
from app.v3.brain_v2.state import (
    BrainGraphState,
    BrainP19Route,
    BrainWorkflowStatus,
)


DSN = os.environ.get("DIMA_BRAIN_V2_TEST_POSTGRES_DSN", "").strip()
pytestmark = pytest.mark.skipif(not DSN, reason="Brain V2 Postgres DSN not configured")


def _fp(name: str) -> str:
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


class OnePassActivities:
    def intake(self, state):
        return IntakeActivityResult(
            research_session_id="rs_" + "1" * 24,
            accepted_brief_ref="brief:postgres",
            scope_version_id="scope_v1",
            open_requirement_ids=("g1",),
            material_requirement_ids=("g1",),
            discovery_required=False,
            activity_fingerprint=_fp("intake"),
        )

    def canonicalize(self, state):
        return CanonicalizeActivityResult(
            research_session_id="rs_" + "1" * 24,
            scope_version_id="scope_v1",
            open_requirement_ids=("g1",),
            material_requirement_ids=("g1",),
            hypothesis_ids=("p19h_" + "a" * 24, "p19h_" + "b" * 24),
            discovery_required=False,
            activity_fingerprint=_fp("canonicalize"),
        )

    def plan_requirements(self, state):
        return RequirementPlanActivityResult(
            material_group_ids=("mg_" + "a" * 24,),
            root_cause_requirement_ids=("g1",),
            activity_fingerprint=_fp("requirements-plan"),
        )

    def acquire_material_group(self, state):
        return MaterialGroupActivityResult(
            material_group_id="mg_" + "a" * 24,
            consumer_requirement_ids=("g1",),
            produced_evidence_ids=("evi_" + "c" * 24,),
            produced_receipt_refs=("dqr_" + "d" * 24,),
            activity_fingerprint=_fp("material-group"),
        )

    def adjudicate_relationship(self, state):
        raise AssertionError("ONE_PASS must not invoke P18")

    def evaluate_completion(self, state):
        return CompletionActivityResult(
            completion_revision=state.completion_revision + 1,
            terminal_requirement_ids=("g1",),
            analytical_complete=True,
            all_requirements_terminal=True,
            requirement_complete=True,
            report_required=False,
            activity_fingerprint=_fp("completion"),
        )

    def acquire_material(self, state):
        return MaterialActivityResult(
            material_requirement_ids=("g1",),
            produced_evidence_ids=("evi_" + "c" * 24,),
            produced_receipt_refs=("dqr_" + "d" * 24,),
            activity_fingerprint=_fp("material"),
        )

    def admit_evidence(self, state):
        return EvidenceActivityResult(
            evidence_revision=1,
            evidence_ids=("evi_" + "c" * 24,),
            hypothesis_revision=0,
            hypothesis_ids=state.hypothesis_ids,
            discovery_required=False,
            activity_fingerprint=_fp("evidence"),
        )

    def assess_p19(self, state):
        return P19ActivityResult(
            assessment_ref="p19a_" + "e" * 24,
            route=BrainP19Route.SUFFICIENT,
            hypothesis_revision=1,
            hypothesis_ids=state.hypothesis_ids,
            activity_fingerprint=_fp("p19"),
        )

    def discover_hypotheses(self, state):
        raise AssertionError("ONE_PASS must not discover hypotheses")

    def design_next_test(self, state):
        raise AssertionError("ONE_PASS must not design a next test")

    def synthesize_report(self, state):
        return ReportActivityResult(
            report_ref="p20r_" + "f" * 24,
            activity_fingerprint=_fp("report"),
        )


def test_postgres_checkpoint_survives_service_reconstruction_and_is_schema_isolated():
    schema = "dima_brain_v2_test_orchestration"
    thread_id = "postgres-checkpoint-restart"

    with connect(DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')

    activities = OnePassActivities()
    with postgres_checkpoint_saver(DSN, schema=schema, setup=True) as saver:
        service = BrainV2Service(activities=activities, checkpointer=saver)
        completed = service.run(
            BrainGraphState(
                thread_id=thread_id,
                tenant_binding="id:tenant",
                principal_ref="user-1",
                current_user_input="Checkpoint provider-free proof.",
            )
        )
        assert completed.workflow_status == BrainWorkflowStatus.COMPLETE

    # Simulate process/service reconstruction over the same durable checkpoint DB.
    with postgres_checkpoint_saver(DSN, schema=schema) as saver:
        restarted = BrainV2Service(activities=activities, checkpointer=saver)
        restored = restarted.state(thread_id=thread_id)
        assert restored is not None
        assert restored.workflow_status == BrainWorkflowStatus.COMPLETE
        # This fixture has no presentation requirement. Durable checkpointing
        # must not manufacture a P20 artifact merely because RCA is terminal.
        assert restored.report_ref is None
        assert restored.last_completed_node == "COMPLETE"

    with connect(DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name
                """,
                (schema,),
            )
            isolated_tables = {row[0] for row in cur.fetchall()}
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name LIKE 'checkpoint%%'
                """
            )
            public_checkpoint_tables = {row[0] for row in cur.fetchall()}

    assert "checkpoints" in isolated_tables
    assert "checkpoint_writes" in isolated_tables
    assert not public_checkpoint_tables
