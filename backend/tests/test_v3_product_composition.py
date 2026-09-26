from __future__ import annotations

import inspect
from types import SimpleNamespace
from uuid import UUID

from app.v3.business_relationship_policy import RelationshipPolicyResolutionStatus
from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductCompositionTerminal,
)
from app.v3.research import ObligationState
from app.v3.research_contracts import (
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from control_plane.authorize import Principal


TENANT = UUID("00000000-0000-4000-8000-000000006801")
USER = UUID("00000000-0000-4000-8000-000000006802")


def principal():
    return Principal(
        user_id=str(USER),
        tenant_id=str(TENANT),
        tenant_slug="composition",
        roles=["analyst"],
    )


def metric(cid: str, name: str):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def dim(cid: str, name: str):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


DOWNTIME = metric("metric.downtime", "Machine Downtime Minutes")
FAULTS = metric("metric.faults", "Fault Count")
DEPT = dim("dimension.department", "Department")


def question(
    goal_id: str,
    kind: ResearchGoalKind,
    *,
    subjects=(DOWNTIME,),
    related=(DEPT,),
):
    return ResearchQuestion(
        goal_id=goal_id,
        kind=kind,
        source_text=f"Governed {kind.value} request.",
        subject_refs=subjects,
        related_refs=related,
        status=ResearchGoalStatus.RESOLVED,
    )


def brief(*questions, report=False):
    deliverables = (
        (
            ResearchDeliverableRequirement(
                requirement_id="d_report",
                kind=PresentationKind.REPORT,
                source_text="Produce a governed report.",
            ),
        )
        if report
        else ()
    )
    refs = {}
    for item in questions:
        for ref in (*item.subject_refs, *item.related_refs):
            refs[ref.candidate_id] = ref
    return ResearchBrief(
        brief_id="rb-composition",
        objective="Compose governed product authorities.",
        scope=ResearchScope(semantic_refs=tuple(refs.values())),
        questions=tuple(questions),
        deliverables=deliverables,
        must_requirement_ids=tuple(
            [item.goal_id for item in questions]
            + [item.requirement_id for item in deliverables]
        ),
        context_version="ctx-composition-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


class FakeResearch:
    def __init__(self):
        self.sessions = {}
        self.counter = 0
        self.run_calls = []

    def start_from_brief(
        self,
        *,
        brief,
        request_ref,
        source_message_hash,
        principal,
    ):
        del request_ref, source_message_hash, principal
        self.counter += 1
        sid = f"rs_{self.counter:024x}"
        obligations = [
            SimpleNamespace(
                obligation_id=item.goal_id,
                state=ObligationState.READY,
            )
            for item in brief.questions
        ]
        obligations.extend(
            SimpleNamespace(
                obligation_id=item.requirement_id,
                state=ObligationState.READY,
            )
            for item in brief.deliverables
        )
        session = SimpleNamespace(
            session_id=sid,
            obligations=tuple(obligations),
            evidence_refs=(),
            context_version=brief.context_version,
            accepted_brief=brief,
        )
        self.sessions[sid] = session
        return session

    def resume_state(self, *, session_id, principal):
        del principal
        return self.sessions[session_id]

    def run_next(
        self,
        *,
        session_id,
        principal,
        obligation_id,
        native_session_token,
    ):
        del principal, native_session_token
        self.run_calls.append((session_id, obligation_id))
        session = self.sessions[session_id]
        brief = session.accepted_brief
        goal = next(item for item in brief.questions if item.goal_id == obligation_id)

        # Provider-free owner behavior fixture:
        # - direct RELATIONSHIP cannot manufacture analytical relationship truth;
        # - OTHER represents a typed unresolved recursive product obligation;
        # - every ordinary/comparison/root analytical request can yield P14 Evidence.
        target = (
            ObligationState.LIMITED
            if goal.kind in {ResearchGoalKind.RELATIONSHIP, ResearchGoalKind.OTHER}
            else ObligationState.VERIFIED
        )
        obligations = tuple(
            SimpleNamespace(
                obligation_id=item.obligation_id,
                state=(target if item.obligation_id == obligation_id else item.state),
            )
            for item in session.obligations
        )
        evidence = session.evidence_refs
        if target == ObligationState.VERIFIED:
            evidence = (
                *evidence,
                SimpleNamespace(
                    evidence_id=f"evi_{len(evidence)+1:024x}",
                    receipt_id=f"dqr_{len(evidence)+1:024x}",
                    obligation_id=obligation_id,
                ),
            )
        self.sessions[session_id] = SimpleNamespace(
            **{
                **session.__dict__,
                "obligations": obligations,
                "evidence_refs": evidence,
            }
        )
        return SimpleNamespace(evidence_id=(evidence[-1].evidence_id if evidence else None))


class FakeInvestigation:
    def __init__(self):
        self.states = {}

    def _state(self, session_id):
        return self.states.setdefault(
            session_id,
            {"steps": [], "claims": [], "calls": 0},
        )

    def snapshot(self, *, session_id, principal):
        del principal
        state = self._state(session_id)
        return SimpleNamespace(
            completed_reasoning_steps=tuple(state["steps"]),
            claims=tuple(state["claims"]),
            terminal_stop_reason=None,
        )

    def run_one(
        self,
        *,
        session_id,
        principal,
        manager,
        native_session_token,
    ):
        del principal, manager, native_session_token
        state = self._state(session_id)
        state["calls"] += 1
        n = state["calls"]
        step_id = f"rrs_{session_id[-8:]}{n:016x}"[-28:]
        if not step_id.startswith("rrs_"):
            step_id = "rrs_" + f"{n:024x}"
        state["steps"].append(step_id)
        state["claims"].append(
            SimpleNamespace(
                claim_id="clm_" + f"{n:024x}",
                obligation_id=self._obligation(session_id),
                claim_text=f"Sealed P17 claim {n}",
            )
        )
        return SimpleNamespace(step_id=step_id), None

    def _obligation(self, session_id):
        # Test reasoning store sets this before each composition branch.
        return FakeReasoning.current_obligation_by_session.get(session_id, "g_root")


class FakeProposalManager:
    def __init__(self):
        self.call_count = 0

    def propose(self, snapshot):
        self.call_count += 1
        return snapshot


class FakeReasoning:
    current_obligation_by_session = {}

    def __init__(self, investigation):
        self.investigation = investigation

    def steps(self, session_id):
        state = self.investigation._state(session_id)
        obligation = self.current_obligation_by_session.get(session_id, "g_root")
        return tuple(
            SimpleNamespace(
                step_id=item,
                parent_obligation_id=obligation,
            )
            for item in state["steps"]
        )


class FakeRelationshipStore:
    def __init__(self, *, blocked=True):
        self.calls = []
        self.blocked = blocked

    def resolve(self, *, requirement, principal):
        del principal
        self.calls.append(requirement)
        return SimpleNamespace(
            policy_use_id="bru_" + "1" * 24,
            resolution_status=(
                RelationshipPolicyResolutionStatus.BLOCKED_MISSING
                if self.blocked
                else RelationshipPolicyResolutionStatus.SATISFIED
            ),
            limitation_code=(
                "P18_RELATIONSHIP_POLICY_MISSING" if self.blocked else None
            ),
        )


class FakeP19:
    def __init__(self):
        self.hypotheses = []
        self.groundings = []
        self.assess_calls = 0

    def create_hypothesis(
        self,
        *,
        research_session_id,
        obligation_id,
        statement,
        principal,
    ):
        del principal
        item = SimpleNamespace(
            hypothesis_id="p19h_" + f"{len(self.hypotheses)+1:024x}",
            research_session_id=research_session_id,
            obligation_id=obligation_id,
            statement=statement,
        )
        self.hypotheses.append(item)
        return item

    def create_grounding(self, **kwargs):
        self.groundings.append(kwargs)
        return SimpleNamespace(
            grounding_link_id="p19g_" + f"{len(self.groundings):024x}"
        )

    def snapshot(self, *, research_session_id, obligation_id, principal):
        del principal
        return SimpleNamespace(
            research_session_id=research_session_id,
            obligation_id=obligation_id,
            hypotheses=tuple(
                SimpleNamespace(hypothesis=item, groundings=())
                for item in self.hypotheses
                if item.research_session_id == research_session_id
                and item.obligation_id == obligation_id
            ),
        )

    def assess(self, *, draft, principal):
        del draft, principal
        self.assess_calls += 1
        return SimpleNamespace(
            assessment_id="p19a_" + "2" * 24,
            aggregate_outcome=SimpleNamespace(
                value="NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED"
            ),
            limitations=("ASSOCIATION_ONLY",),
        )


class FakeP19Manager:
    def __init__(self):
        self.call_count = 0

    def propose(self, snapshot, *, policy_statuses=None, deterministic_feedback_code=None):
        del snapshot, policy_statuses, deterministic_feedback_code
        self.call_count += 1
        return object()


class FakeReports:
    def __init__(self):
        self.drafts = []

    def seal(self, *, draft, principal):
        del principal
        self.drafts.append(draft)
        return SimpleNamespace(report_id="p20r_" + "3" * 24)


def composer(*, relationship_blocked=True):
    research = FakeResearch()
    investigation = FakeInvestigation()
    reasoning = FakeReasoning(investigation)
    return (
        HeadlessProductComposer(
            research=research,
            investigation=investigation,
            investigation_manager=FakeProposalManager(),
            reasoning=reasoning,
            relationships=FakeRelationshipStore(blocked=relationship_blocked),
            epistemics=FakeP19(),
            epistemic_manager=FakeP19Manager(),
            reports=FakeReports(),
        ),
        research,
        investigation,
        reasoning,
    )


def _prime_reasoning_target(research, reasoning):
    # The provider-free fake maps each created session to its single analytical
    # obligation. Product code itself never uses this helper or case metadata.
    for sid, session in research.sessions.items():
        if session.accepted_brief.questions:
            reasoning.current_obligation_by_session[sid] = (
                session.accepted_brief.questions[0].goal_id
            )


def test_ordinary_composition_uses_p14_only():
    c, research, _, reasoning = composer()
    b = brief(question("g_breakdown", ResearchGoalKind.BREAKDOWN))
    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="ordinary",
        source_message_hash="a" * 64,
        native_session_token=None,
    )
    _prime_reasoning_target(research, reasoning)
    assert result.terminal_state == ProductCompositionTerminal.ANSWER
    assert result.evidence_refs
    assert result.p17_step_refs == ()
    assert result.p18_policy_use_refs == ()
    assert result.p19_assessment_refs == ()
    assert result.p20_report_ref is None


def test_relationship_composes_p14_material_p17_and_p18_without_creating_policy():
    c, research, investigation, reasoning = composer()
    b = brief(
        question(
            "g_relationship",
            ResearchGoalKind.RELATIONSHIP,
            subjects=(DOWNTIME, FAULTS),
            related=(DEPT,),
        ),
        report=True,
    )

    # Fake P17 needs the child obligation identity after child creation.
    original = c._resolve_relationship
    def wrapped(**kwargs):
        reasoning.current_obligation_by_session[kwargs["material_session_id"]] = (
            kwargs["material_goal"].goal_id
        )
        return original(**kwargs)
    c._resolve_relationship = wrapped

    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="relationship",
        source_message_hash="b" * 64,
        native_session_token=None,
    )
    assert result.child_research_session_ids
    assert result.p17_step_refs
    assert result.p18_policy_use_refs == ("bru_" + "1" * 24,)
    assert result.p20_report_ref == "p20r_" + "3" * 24
    assert result.terminal_state == ProductCompositionTerminal.REPORT
    assert "P18" in result.owner_calls
    assert "P19" not in result.owner_calls


def test_root_cause_composes_p17_then_p19_and_preserves_inconclusive_outcome():
    c, research, investigation, reasoning = composer()
    b = brief(
        question("g_root", ResearchGoalKind.ROOT_CAUSE),
        report=True,
    )
    original = c._assess_root_cause
    def wrapped(**kwargs):
        reasoning.current_obligation_by_session[kwargs["session_id"]] = (
            kwargs["goal"].goal_id
        )
        return original(**kwargs)
    c._assess_root_cause = wrapped

    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="root",
        source_message_hash="c" * 64,
        native_session_token=None,
    )
    assert len(result.p17_step_refs) >= 2
    assert result.p19_assessment_refs == ("p19a_" + "2" * 24,)
    assert result.p20_report_ref == "p20r_" + "3" * 24
    assert any(
        item.code == "NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED"
        for item in result.limitations
    )


def test_adaptive_route_comes_from_typed_unresolved_state_not_raw_text():
    c, research, investigation, reasoning = composer()
    b = brief(
        question("g_base", ResearchGoalKind.BREAKDOWN),
        question("g_followup", ResearchGoalKind.OTHER),
        report=True,
    )
    original = c._run_p17
    def wrapped(**kwargs):
        reasoning.current_obligation_by_session[kwargs["session_id"]] = "g_base"
        return original(**kwargs)
    c._run_p17 = wrapped

    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="adaptive",
        source_message_hash="d" * 64,
        native_session_token=None,
    )
    assert "g_followup" in result.p17_required_goal_ids
    assert result.p17_step_refs
    assert result.p18_policy_use_refs == ()
    assert result.p19_assessment_refs == ()
    assert result.p20_report_ref is not None


def test_p18_blocked_resolution_is_preserved_as_limitation_not_fake_success():
    c, research, _, reasoning = composer(relationship_blocked=True)
    b = brief(
        question(
            "g_relationship",
            ResearchGoalKind.RELATIONSHIP,
            subjects=(DOWNTIME, FAULTS),
            related=(DEPT,),
        ),
        report=True,
    )
    original = c._resolve_relationship
    def wrapped(**kwargs):
        reasoning.current_obligation_by_session[kwargs["material_session_id"]] = (
            kwargs["material_goal"].goal_id
        )
        return original(**kwargs)
    c._resolve_relationship = wrapped
    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="blocked",
        source_message_hash="e" * 64,
        native_session_token=None,
    )
    assert result.p18_policy_use_refs
    assert any(
        item.code == "P18_RELATIONSHIP_POLICY_MISSING"
        and item.owner == "P18"
        for item in result.limitations
    )


def test_report_is_written_only_through_p20_seal_and_covers_every_user_must():
    c, research, _, reasoning = composer()
    b = brief(
        question("g_breakdown", ResearchGoalKind.BREAKDOWN),
        report=True,
    )
    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="report",
        source_message_hash="f" * 64,
        native_session_token=None,
    )
    drafts = c._reports.drafts
    assert len(drafts) == 1
    assert {item.obligation_id for item in drafts[0].coverage} == set(
        b.must_requirement_ids
    )
    assert all(
        item.coverage_status.value == "LIMITED"
        for item in drafts[0].coverage
    )
    assert result.p20_report_ref


def test_product_composition_has_no_direct_truth_store_or_text_case_routing():
    source = inspect.getsource(
        __import__(
            "app.v3.product.composition",
            fromlist=["HeadlessProductComposer"],
        )
    )
    for forbidden in (
        "sqlmodel",
        "sqlalchemy",
        "Session(",
        "ResearchClaimRecord(",
        "EvidenceArtifact(",
        "BusinessRelationshipPolicyRecord(",
        "RootCauseAssessmentRecord(",
        "ReportDocumentRecord(",
        "DecisionBriefRecord(",
        'if "root cause"',
        'if "relationship"',
        "adaptive_tr",
        "relationship_explicit_tr",
        "root_cause_tr",
        "askv2_case_id",
    ):
        assert forbidden not in source
