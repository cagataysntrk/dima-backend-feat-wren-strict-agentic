from __future__ import annotations

import hashlib
from collections import Counter

from app.v3.brain_v2.activities import (
    CandidateProjectionActivityResult,
    CanonicalizeActivityResult,
    CompletionActivityResult,
    EvidenceActivityResult,
    IntakeActivityResult,
    MaterialActivityResult,
    MaterialGroupActivityResult,
    P17ActivityResult,
    P18ActivityResult,
    P19ActivityResult,
    ReportActivityResult,
    RequirementPlanActivityResult,
)
from app.v3.brain_v2.service import BrainV2Service
from app.v3.brain_v2.state import BrainGraphState, BrainWorkflowStatus


REL = "g_relationship"
RANK = "g_ranking"
REPORT = "d_report"
GROUP = "mg_" + "a" * 24


class ForwardPhase2Activities:
    """Pure orchestration fixture: no provider/native/network work."""

    def __init__(self, mode: str) -> None:
        if mode not in {"relationship", "multi_intent"}:
            raise ValueError(mode)
        self.mode = mode
        self.calls: Counter[str] = Counter()

    @staticmethod
    def _fp(name: str, state: BrainGraphState) -> str:
        raw = "|".join(
            (
                name,
                state.scope_version_id or "none",
                str(state.evidence_revision),
                str(state.completion_revision),
                str(state.presentation_revision),
            )
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def _requirements(self):
        if self.mode == "relationship":
            return (REL,), (REL,), ()
        return (RANK, REL, REPORT), (REL,), (RANK,)

    def intake(self, state):
        self.calls["intake"] += 1
        must, _, _ = self._requirements()
        return IntakeActivityResult(
            research_session_id="rs_" + "1" * 24,
            accepted_brief_ref="brief:forward-phase2",
            scope_version_id="scope_v1",
            open_requirement_ids=must,
            material_requirement_ids=tuple(
                item for item in must if item != REPORT
            ),
            discovery_required=False,
            activity_fingerprint=self._fp("intake", state),
        )

    def canonicalize(self, state):
        self.calls["canonicalize"] += 1
        must, _, _ = self._requirements()
        return CanonicalizeActivityResult(
            research_session_id=state.research_session_id,
            scope_version_id=state.scope_version_id,
            open_requirement_ids=must,
            material_requirement_ids=tuple(
                item for item in must if item != REPORT
            ),
            hypothesis_ids=(),
            discovery_required=False,
            activity_fingerprint=self._fp("canonicalize", state),
        )

    def plan_requirements(self, state):
        self.calls["requirements_plan"] += 1
        must, relationships, direct = self._requirements()
        return RequirementPlanActivityResult(
            material_group_ids=(GROUP,),
            direct_requirement_ids=direct,
            relationship_requirement_ids=relationships,
            root_cause_requirement_ids=(),
            report_requirement_ids=(
                (REPORT,) if REPORT in must else ()
            ),
            activity_fingerprint=self._fp("requirements-plan", state),
        )

    def acquire_material_group(self, state):
        self.calls["material_group"] += 1
        consumers = (
            (REL,) if self.mode == "relationship" else (RANK, REL)
        )
        return MaterialGroupActivityResult(
            material_group_id=GROUP,
            consumer_requirement_ids=consumers,
            produced_evidence_ids=("evi_" + "2" * 24,),
            produced_receipt_refs=("dqr_" + "3" * 24,),
            activity_fingerprint=self._fp("material-group", state),
        )

    def acquire_material(self, state):
        raise AssertionError("phase-2 forward path must use MaterialGroup execution")

    def admit_evidence(self, state):
        self.calls["evidence"] += 1
        return EvidenceActivityResult(
            evidence_revision=state.evidence_revision + 1,
            evidence_ids=tuple(
                dict.fromkeys((*state.evidence_ids, *state.pending_evidence_ids))
            ),
            hypothesis_revision=state.hypothesis_revision,
            hypothesis_ids=state.hypothesis_ids,
            discovery_required=False,
            activity_fingerprint=self._fp("evidence", state),
        )

    def adjudicate_relationship(self, state):
        self.calls["p18"] += 1
        assert state.active_requirement_id == REL
        assert state.completed_material_group_ids == (GROUP,)
        assert len(state.evidence_ids) == 1
        return P18ActivityResult(
            requirement_id=REL,
            claim_ref="clm_" + "4" * 24,
            policy_use_ref="bru_" + "5" * 24,
            activity_fingerprint=self._fp("p18", state),
        )

    def evaluate_completion(self, state):
        self.calls["completion"] += 1
        terminal = []
        if self.mode == "multi_intent":
            terminal.append(RANK)
        if REL in state.p18_requirement_ids:
            terminal.append(REL)
        if state.report_ref is not None:
            terminal.extend(state.report_requirement_ids)
        terminal = tuple(dict.fromkeys(terminal))
        analytical = set(
            (
                *state.direct_requirement_ids,
                *state.relationship_requirement_ids,
                *state.root_cause_requirement_ids,
            )
        )
        return CompletionActivityResult(
            completion_revision=state.completion_revision + 1,
            terminal_requirement_ids=terminal,
            analytical_complete=analytical.issubset(set(terminal)),
            requirement_complete=set(state.open_requirement_ids).issubset(
                set(terminal)
            ),
            report_required=bool(
                set(state.report_requirement_ids) - set(terminal)
            ),
            activity_fingerprint=self._fp("completion", state),
        )

    def synthesize_report(self, state):
        self.calls["report"] += 1
        assert set(
            (
                *state.direct_requirement_ids,
                *state.relationship_requirement_ids,
                *state.root_cause_requirement_ids,
            )
        ).issubset(set(state.terminal_requirement_ids))
        return ReportActivityResult(
            report_ref="p20r_" + "6" * 24,
            activity_fingerprint=self._fp("report", state),
        )

    def project_candidates(self, state) -> CandidateProjectionActivityResult:
        raise AssertionError("relationship/direct composition must not call P19 candidate projection")

    def assess_p19(self, state) -> P19ActivityResult:
        raise AssertionError("relationship/direct composition must not call P19")

    def discover_hypotheses(self, state) -> P17ActivityResult:
        raise AssertionError("normal relationship path must not call P17 discovery")

    def design_next_test(self, state) -> P17ActivityResult:
        raise AssertionError("relationship/direct composition must not call P17 NextTest")


def _initial(thread_id: str):
    return BrainGraphState(
        thread_id=thread_id,
        tenant_binding="id:tenant",
        principal_ref="user",
        current_user_input="typed provider-free request",
    )


def test_observational_relationship_uses_one_material_then_p18_only():
    activities = ForwardPhase2Activities("relationship")
    result = BrainV2Service(activities=activities).run(
        _initial("forward-relationship")
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert activities.calls["material_group"] == 1
    assert activities.calls["evidence"] == 1
    assert activities.calls["p18"] == 1
    assert activities.calls["report"] == 0
    assert activities.calls["p19"] == 0
    assert result.p18_requirement_ids == (REL,)
    assert result.terminal_requirement_ids == (REL,)
    assert result.report_ref is None


def test_relationship_report_continuation_reuses_terminal_authority_zero_reanalysis():
    activities = ForwardPhase2Activities("relationship")
    service = BrainV2Service(activities=activities)
    first = service.run(_initial("forward-relationship-report"))
    before = activities.calls.copy()

    second = service.continue_report_turn(
        thread_id=first.thread_id,
        tenant_binding=first.tenant_binding,
        principal_ref=first.principal_ref,
        user_input="present current governed relationship as a report",
    )

    assert second.workflow_status == BrainWorkflowStatus.COMPLETE
    assert second.research_session_id == first.research_session_id
    assert second.scope_version_id == first.scope_version_id
    assert second.presentation_revision == first.presentation_revision + 1
    assert second.report_ref is not None
    assert activities.calls["intake"] == before["intake"]
    assert activities.calls["canonicalize"] == before["canonicalize"]
    assert activities.calls["requirements_plan"] == before["requirements_plan"]
    assert activities.calls["material_group"] == before["material_group"]
    assert activities.calls["evidence"] == before["evidence"]
    assert activities.calls["p18"] == before["p18"]
    assert activities.calls["p19"] == 0
    assert activities.calls["report"] == before["report"] + 1
    assert set(second.report_requirement_ids).issubset(
        set(second.terminal_requirement_ids)
    )


def test_multi_intent_ranking_relationship_report_shares_one_material_group():
    activities = ForwardPhase2Activities("multi_intent")
    result = BrainV2Service(activities=activities).run(
        _initial("forward-multi-intent")
    )

    assert result.workflow_status == BrainWorkflowStatus.COMPLETE
    assert result.material_group_ids == (GROUP,)
    assert result.completed_material_group_ids == (GROUP,)
    assert activities.calls["material_group"] == 1
    assert activities.calls["evidence"] == 1
    assert activities.calls["p18"] == 1
    assert activities.calls["p19"] == 0
    assert activities.calls["report"] == 1
    assert set(result.terminal_requirement_ids) == {RANK, REL, REPORT}
    assert result.report_ref is not None
