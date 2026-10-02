from __future__ import annotations

import hashlib
from contextlib import contextmanager
from collections import Counter

from app.v3.brain_v2.activities import (
    CandidateProjectionActivityResult,
    CanonicalizeActivityResult,
    EvidenceActivityResult,
    IntakeActivityResult,
    CompletionActivityResult,
    MaterialActivityResult,
    MaterialGroupActivityResult,
    P18ActivityResult,
    RequirementPlanActivityResult,
    P17ActivityResult,
    P19ActivityResult,
    ReportActivityResult,
)
import pytest

from app.v3.brain_v2.service import BrainV2Service, BrainV2ThreadError
from app.v3.brain_v2.state import (
    BrainGraphState,
    BrainP19Route,
    BrainWorkflowStatus,
)


class FakeActivities:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.calls: Counter[str] = Counter()

    def _fp(self, name: str, state: BrainGraphState) -> str:
        raw = "|".join(
            (
                name,
                state.scope_version_id or "none",
                str(state.evidence_revision),
                str(state.hypothesis_revision),
                state.pending_next_test_ref or "none",
                str(state.adaptive_reentries),
            )
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def intake(self, state: BrainGraphState) -> IntakeActivityResult:
        self.calls["intake"] += 1
        continuing = state.research_session_id is not None
        return IntakeActivityResult(
            research_session_id="rs_" + ("d" if continuing else "c") * 24,
            accepted_brief_ref=("brief:fixture:v2" if continuing else "brief:fixture:v1"),
            scope_version_id=("scope_v2" if continuing else "scope_v1"),
            open_requirement_ids=("goal-1",),
            material_requirement_ids=("goal-1",),
            discovery_required=self.mode.startswith("discovery"),
            activity_fingerprint=self._fp("intake", state),
        )

    def canonicalize(self, state: BrainGraphState) -> CanonicalizeActivityResult:
        self.calls["canonicalize"] += 1
        hypotheses = (
            ()
            if self.mode.startswith("discovery")
            else ("p19h_" + "a" * 24, "p19h_" + "b" * 24)
        )
        assert state.research_session_id is not None
        assert state.scope_version_id is not None
        return CanonicalizeActivityResult(
            research_session_id=state.research_session_id,
            scope_version_id=state.scope_version_id,
            open_requirement_ids=("goal-1",),
            material_requirement_ids=("goal-1",),
            hypothesis_ids=hypotheses,
            discovery_required=self.mode.startswith("discovery"),
            activity_fingerprint=self._fp("canonicalize", state),
        )

    def plan_requirements(
        self, state: BrainGraphState
    ) -> RequirementPlanActivityResult:
        self.calls["requirements_plan"] += 1
        return RequirementPlanActivityResult(
            material_group_ids=("mg_" + "a" * 24,),
            root_cause_requirement_ids=("goal-1",),
            activity_fingerprint=self._fp("requirements-plan", state),
        )

    def acquire_material_group(
        self, state: BrainGraphState
    ) -> MaterialGroupActivityResult:
        self.calls["material_group"] += 1
        return MaterialGroupActivityResult(
            material_group_id="mg_" + "a" * 24,
            consumer_requirement_ids=("goal-1",),
            produced_evidence_ids=("evi_" + "9" * 24,),
            produced_receipt_refs=("dqr_" + "9" * 24,),
            activity_fingerprint=self._fp("material-group", state),
        )

    def adjudicate_relationship(
        self, state: BrainGraphState
    ) -> P18ActivityResult:
        raise AssertionError("pure RCA fixture must not invoke P18")

    def evaluate_completion(
        self, state: BrainGraphState
    ) -> CompletionActivityResult:
        self.calls["completion"] += 1
        return CompletionActivityResult(
            completion_revision=state.completion_revision + 1,
            terminal_requirement_ids=("goal-1",),
            analytical_complete=True,
            requirement_complete=True,
            report_required=False,
            activity_fingerprint=self._fp("completion", state),
        )

    def acquire_material(self, state: BrainGraphState) -> MaterialActivityResult:
        self.calls["material"] += 1
        ordinal = self.calls["material"]
        return MaterialActivityResult(
            material_requirement_ids=state.material_requirement_ids,
            produced_evidence_ids=("evi_" + (str(ordinal) * 24),),
            produced_receipt_refs=("dqr_" + (str(ordinal) * 24),),
            activity_fingerprint=self._fp("material", state),
        )

    def admit_evidence(self, state: BrainGraphState) -> EvidenceActivityResult:
        self.calls["evidence"] += 1
        revision = state.evidence_revision + len(state.pending_evidence_ids)
        seeded = state.hypothesis_ids
        discovery_required = state.discovery_required
        return EvidenceActivityResult(
            evidence_revision=revision,
            evidence_ids=tuple(dict.fromkeys((*state.evidence_ids, *state.pending_evidence_ids))),
            hypothesis_revision=state.hypothesis_revision,
            hypothesis_ids=seeded,
            discovery_required=discovery_required,
            activity_fingerprint=self._fp("evidence", state),
        )

    def assess_p19(self, state: BrainGraphState) -> P19ActivityResult:
        self.calls["p19"] += 1
        ordinal = self.calls["p19"]
        if self.mode == "fail_p19_once" and ordinal == 1:
            raise RuntimeError("simulated provider interruption before durable P19 result")
        if self.mode in {"inconclusive", "discovery_one"}:
            route = BrainP19Route.INCONCLUSIVE
            next_ref = None
        elif self.mode in {"adaptive", "always_next"} and ordinal == 1:
            route = BrainP19Route.NEXT_TEST_REQUIRED
            next_ref = "ntr_" + "d" * 24
        elif self.mode == "always_next":
            route = BrainP19Route.NEXT_TEST_REQUIRED
            next_ref = "ntr_" + "e" * 24
        else:
            route = BrainP19Route.SUFFICIENT
            next_ref = None
        return P19ActivityResult(
            assessment_ref="p19a_" + (str(ordinal) * 24),
            route=route,
            hypothesis_revision=state.hypothesis_revision + 1,
            hypothesis_ids=state.hypothesis_ids,
            pending_next_test_ref=next_ref,
            activity_fingerprint=self._fp("p19", state),
        )

    def project_candidates(
        self, state: BrainGraphState
    ) -> CandidateProjectionActivityResult:
        self.calls["project_candidates"] += 1
        if self.mode == "discovery_zero":
            hypotheses = ()
        elif self.mode == "discovery_one":
            hypotheses = ("p19h_" + "a" * 24,)
        else:
            hypotheses = ("p19h_" + "a" * 24, "p19h_" + "b" * 24)
        semantics = tuple(
            f"metric.candidate_{index}"
            for index, _ in enumerate(hypotheses, start=1)
        )
        return CandidateProjectionActivityResult(
            hypothesis_revision=state.hypothesis_revision + (1 if hypotheses else 0),
            hypothesis_ids=hypotheses,
            candidate_semantic_ids=semantics,
            candidate_count=len(hypotheses),
            activity_fingerprint=self._fp("project-candidates", state),
        )

    def discover_hypotheses(self, state: BrainGraphState) -> P17ActivityResult:
        self.calls["p17_discovery"] += 1
        return P17ActivityResult(
            hypothesis_revision=state.hypothesis_revision + 1,
            hypothesis_ids=("p19h_" + "a" * 24, "p19h_" + "b" * 24),
            material_requirement_ids=state.material_requirement_ids,
            discovery_required=False,
            activity_fingerprint=self._fp("p17-discovery", state),
        )

    def design_next_test(self, state: BrainGraphState) -> P17ActivityResult:
        self.calls["p17_next_test"] += 1
        self.calls["native_followup"] += 1
        ordinal = self.calls["native_followup"] + self.calls["material"]
        return P17ActivityResult(
            hypothesis_revision=state.hypothesis_revision,
            hypothesis_ids=state.hypothesis_ids,
            material_requirement_ids=("goal-1:discriminating",),
            discovery_required=False,
            produced_evidence_ids=("evi_" + (str(ordinal) * 24),),
            produced_receipt_refs=("dqr_" + (str(ordinal) * 24),),
            activity_fingerprint=self._fp("p17-next-test", state),
        )

    def synthesize_report(self, state: BrainGraphState) -> ReportActivityResult:
        self.calls["report"] += 1
        return ReportActivityResult(
            report_ref="p20r_" + "f" * 24,
            activity_fingerprint=self._fp("report", state),
        )


def _run(mode: str) -> tuple[BrainGraphState, FakeActivities]:
    activities = FakeActivities(mode)
    service = BrainV2Service(activities=activities)
    result = service.run(
        BrainGraphState(
            thread_id=f"thread-{mode}",
            tenant_binding="id:tenant",
            principal_ref="user-1",
            current_user_input="Investigate the accepted governed question.",
        )
    )
    return result, activities


def test_one_pass_skips_p17_and_executes_one_material_acquisition() -> None:
    result, activities = _run("one_pass")

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert activities.calls["material"] == 1
    assert activities.calls["p17_discovery"] == 0
    assert activities.calls["p17_next_test"] == 0
    assert activities.calls["p19"] == 1
    assert activities.calls["report"] == 1
    assert result.adaptive_reentries == 0


def test_adaptive_runs_exactly_one_discriminating_reentry() -> None:
    result, activities = _run("adaptive")

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert activities.calls["material"] == 1
    assert activities.calls["native_followup"] == 1
    assert activities.calls["evidence"] == 2
    assert activities.calls["p17_discovery"] == 0
    assert activities.calls["p17_next_test"] == 1
    assert activities.calls["p19"] == 2
    assert result.adaptive_reentries == 1


def test_discovery_projects_candidates_without_p17_provider() -> None:
    result, activities = _run("discovery")

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert activities.calls["material"] == 1
    assert activities.calls["project_candidates"] == 1
    assert activities.calls["p17_discovery"] == 0
    assert activities.calls["p17_next_test"] == 0
    assert activities.calls["p19"] == 1
    assert len(result.hypothesis_ids) == 2
    assert result.candidate_semantic_ids == (
        "metric.candidate_1",
        "metric.candidate_2",
    )


def test_discovery_zero_candidate_set_stops_before_p19() -> None:
    result, activities = _run("discovery_zero")

    assert result.workflow_status == BrainWorkflowStatus.INCONCLUSIVE
    assert result.last_completed_node == "HONEST_STOP"
    assert activities.calls["material"] == 1
    assert activities.calls["project_candidates"] == 1
    assert activities.calls["p17_discovery"] == 0
    assert activities.calls["p19"] == 0
    assert activities.calls["report"] == 0


def test_discovery_single_real_candidate_reaches_p19_without_fake_competitor() -> None:
    result, activities = _run("discovery_one")

    assert result.workflow_status == BrainWorkflowStatus.INCONCLUSIVE
    assert result.last_completed_node == "HONEST_STOP"
    assert activities.calls["material"] == 1
    assert activities.calls["project_candidates"] == 1
    assert activities.calls["p17_discovery"] == 0
    assert activities.calls["p19"] == 1
    assert activities.calls["report"] == 0
    assert result.hypothesis_ids == ("p19h_" + "a" * 24,)
    assert result.candidate_semantic_ids == ("metric.candidate_1",)


def test_inconclusive_is_an_honest_terminal_without_extra_work() -> None:
    result, activities = _run("inconclusive")

    assert result.workflow_status == BrainWorkflowStatus.INCONCLUSIVE
    assert result.last_completed_node == "HONEST_STOP"
    assert activities.calls["material"] == 1
    assert activities.calls["p17_next_test"] == 0
    assert activities.calls["report"] == 0


def test_reentry_bound_stops_second_next_test_instead_of_looping() -> None:
    result, activities = _run("always_next")

    assert result.workflow_status == BrainWorkflowStatus.INCONCLUSIVE
    assert activities.calls["material"] == 1
    assert activities.calls["native_followup"] == 1
    assert activities.calls["p17_next_test"] == 1
    assert activities.calls["p19"] == 2
    assert result.adaptive_reentries == 1



def test_continue_turn_advances_scope_without_reusing_old_current_evidence() -> None:
    activities = FakeActivities("one_pass")
    service = BrainV2Service(activities=activities)
    first = service.run(
        BrainGraphState(
            thread_id="thread-scope-repair",
            tenant_binding="id:tenant",
            principal_ref="user-1",
            current_user_input="Initial governed question.",
        )
    )
    first_evidence = first.evidence_ids

    second = service.continue_turn(
        thread_id="thread-scope-repair",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        user_input="Narrow the accepted scope.",
    )

    assert first.scope_version_id == "scope_v1"
    assert second.scope_version_id == "scope_v2"
    assert second.research_session_id == "rs_" + "d" * 24
    assert first_evidence
    assert second.evidence_ids
    assert set(first_evidence).isdisjoint(second.evidence_ids)
    assert activities.calls["intake"] == 2
    assert activities.calls["material"] == 2


def test_foreign_principal_cannot_resume_or_trigger_activities() -> None:
    activities = FakeActivities("one_pass")
    service = BrainV2Service(activities=activities)
    service.run(
        BrainGraphState(
            thread_id="thread-secure",
            tenant_binding="id:tenant",
            principal_ref="user-1",
            current_user_input="Initial governed question.",
        )
    )
    before = activities.calls.copy()

    with pytest.raises(BrainV2ThreadError):
        service.continue_turn(
            thread_id="thread-secure",
            tenant_binding="id:foreign",
            principal_ref="user-foreign",
            user_input="Try to continue another tenant's thread.",
        )

    assert activities.calls == before



def test_interrupted_graph_resumes_without_repeating_completed_activities() -> None:
    activities = FakeActivities("fail_p19_once")
    service = BrainV2Service(activities=activities)
    initial = BrainGraphState(
        thread_id="thread-crash-resume",
        tenant_binding="id:tenant",
        principal_ref="user-1",
        current_user_input="Investigate the accepted governed question.",
    )

    with pytest.raises(RuntimeError, match="simulated provider interruption"):
        service.run(initial)

    checkpoint = service.state(thread_id="thread-crash-resume")
    assert checkpoint is not None
    assert checkpoint.last_completed_node == "ADMIT_EVIDENCE"
    before = activities.calls.copy()

    resumed = service.resume_interrupted(
        thread_id="thread-crash-resume",
        tenant_binding="id:tenant",
        principal_ref="user-1",
    )

    assert resumed.workflow_status == BrainWorkflowStatus.COMPLETE
    assert activities.calls["intake"] == before["intake"] == 1
    assert activities.calls["canonicalize"] == before["canonicalize"] == 1
    assert activities.calls["material"] == before["material"] == 1
    assert activities.calls["evidence"] == before["evidence"] == 1
    assert activities.calls["p19"] == before["p19"] + 1 == 2
    assert activities.calls["report"] == 1


class _CapturedBoundarySpan:
    def __init__(self, record):
        self._record = record

    def set_attributes(self, **values):
        self._record["attributes"].update(
            {key: value for key, value in values.items() if value is not None}
        )


class _CapturedBoundaryBridge:
    def __init__(self):
        self.records = []

    @contextmanager
    def operation(self, boundary, *, state=None, **attributes):
        name = getattr(boundary, "value", str(boundary))
        record = {"name": name, "attributes": dict(attributes)}
        self.records.append(record)
        yield _CapturedBoundarySpan(record)


def test_discovery_graph_emits_governed_boundary_span_sequence() -> None:
    activities = FakeActivities("discovery")
    bridge = _CapturedBoundaryBridge()
    activities.otel_bridge = bridge
    service = BrainV2Service(activities=activities)

    result = service.run(
        BrainGraphState(
            thread_id="thread-discovery-otel",
            tenant_binding="id:tenant",
            principal_ref="user-1",
            current_user_input="Governed discovery.",
        )
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert [item["name"] for item in bridge.records] == [
        "dima.intent.interpret",
        "dima.scope.resolve",
        "dima.requirements.plan",
        "dima.material.compile",
        "dima.evidence.admit",
        "dima.discovery.project_candidates",
        "dima.p19.assess",
        "dima.completion.evaluate",
        "dima.p20.report",
        "dima.completion.evaluate",
    ]
    projection = next(
        item
        for item in bridge.records
        if item["name"] == "dima.discovery.project_candidates"
    )
    assert projection["attributes"]["candidate_count"] == 2
