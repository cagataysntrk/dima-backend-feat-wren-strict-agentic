from __future__ import annotations

import hashlib
import os
from collections import Counter

import pytest
from psycopg import connect

from app.v3.brain_v2.activities import (
    CanonicalizeActivityResult,
    CompletionActivityResult,
    EvidenceActivityResult,
    IntakeActivityResult,
    MaterialActivityDisposition,
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


class WaitingThenEvidenceActivities(OnePassActivities):
    """Direct-analytics fixture with one durable observation wait then Evidence."""

    def __init__(self) -> None:
        self.calls: Counter[str] = Counter()
        self.occurrence_identity = (
            "execution-link-fixed",
            "native-query-fixed",
            "query-fingerprint-fixed",
            "result-hash-fixed",
        )
        self.observed_occurrence_identities: list[tuple[str, str, str, str]] = []

    def intake(self, state):
        self.calls["intake"] += 1
        return super().intake(state)

    def canonicalize(self, state):
        self.calls["canonicalize"] += 1
        return super().canonicalize(state)

    def plan_requirements(self, state):
        self.calls["requirements_plan"] += 1
        return RequirementPlanActivityResult(
            material_group_ids=("mg_" + "a" * 24,),
            direct_requirement_ids=("g1",),
            activity_fingerprint=_fp("requirements-plan-direct"),
        )

    def acquire_material_group(self, state):
        self.calls["material_group"] += 1
        self.observed_occurrence_identities.append(self.occurrence_identity)
        if self.calls["material_group"] == 1:
            return MaterialGroupActivityResult(
                material_group_id="mg_" + "a" * 24,
                consumer_requirement_ids=("g1",),
                disposition=MaterialActivityDisposition.WAITING,
                limitation_code="R1_NATIVE_MATERIAL_OBSERVATION_UNAVAILABLE",
                activity_fingerprint=_fp("material-group-waiting"),
            )
        return MaterialGroupActivityResult(
            material_group_id="mg_" + "a" * 24,
            consumer_requirement_ids=("g1",),
            produced_evidence_ids=("evi_" + "c" * 24,),
            produced_receipt_refs=("dqr_" + "d" * 24,),
            activity_fingerprint=_fp("material-group-observed"),
        )

    def admit_evidence(self, state):
        self.calls["evidence"] += 1
        return EvidenceActivityResult(
            evidence_revision=1,
            evidence_ids=("evi_" + "c" * 24,),
            hypothesis_revision=0,
            hypothesis_ids=(),
            discovery_required=False,
            activity_fingerprint=_fp("evidence-direct"),
        )

    def evaluate_completion(self, state):
        self.calls["completion"] += 1
        return CompletionActivityResult(
            completion_revision=state.completion_revision + 1,
            terminal_requirement_ids=("g1",),
            analytical_complete=True,
            all_requirements_terminal=True,
            requirement_complete=True,
            report_required=False,
            activity_fingerprint=_fp("completion-direct"),
        )


def test_postgres_wait_checkpoint_survives_restart_and_resumes_same_occurrence():
    schema = "dima_brain_v2_test_wait_resume"
    thread_id = "postgres-wait-resume"

    with connect(DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')

    activities = WaitingThenEvidenceActivities()
    with postgres_checkpoint_saver(DSN, schema=schema, setup=True) as saver:
        service = BrainV2Service(activities=activities, checkpointer=saver)
        waiting = service.run(
            BrainGraphState(
                thread_id=thread_id,
                tenant_binding="id:tenant",
                principal_ref="user-1",
                current_user_input="Run governed direct analytics.",
            )
        )
        assert waiting.workflow_status == BrainWorkflowStatus.WAITING
        assert waiting.last_completed_node == "MATERIAL_GROUP_WAITING"
        assert waiting.active_material_group_id == "mg_" + "a" * 24
        assert activities.calls["intake"] == 1
        assert activities.calls["material_group"] == 1
        snapshot = service.graph.get_state(
            {"configurable": {"thread_id": thread_id}}
        )
        assert tuple(snapshot.next) == ("wait_material_group",)

    # Reopen the durable checkpointer and reconstruct the service. This is the
    # required process/service restart boundary; resume is not a new user turn.
    with postgres_checkpoint_saver(DSN, schema=schema) as saver:
        restarted = BrainV2Service(activities=activities, checkpointer=saver)
        restored = restarted.state(thread_id=thread_id)
        assert restored is not None
        assert restored.workflow_status == BrainWorkflowStatus.WAITING
        resumed = restarted.resume_waiting(
            thread_id=thread_id,
            tenant_binding="id:tenant",
            principal_ref="user-1",
        )

    assert resumed.workflow_status == BrainWorkflowStatus.COMPLETE
    assert resumed.thread_id == waiting.thread_id
    assert resumed.research_session_id == waiting.research_session_id
    assert resumed.scope_version_id == waiting.scope_version_id == "scope_v1"
    assert resumed.evidence_ids == ("evi_" + "c" * 24,)
    assert resumed.terminal_requirement_ids == ("g1",)
    assert activities.calls["intake"] == 1
    assert activities.calls["canonicalize"] == 1
    assert activities.calls["requirements_plan"] == 1
    assert activities.calls["material_group"] == 2
    assert activities.calls["evidence"] == 1
    assert activities.calls["completion"] == 1
    assert len(activities.observed_occurrence_identities) == 2
    assert set(activities.observed_occurrence_identities) == {
        activities.occurrence_identity
    }



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
