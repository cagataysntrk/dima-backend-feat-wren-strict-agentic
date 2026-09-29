from __future__ import annotations

import inspect

import pytest
from types import SimpleNamespace
from uuid import UUID

from app.v3.business_relationship_policy import RelationshipPolicyResolutionStatus
from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductCompositionTerminal,
)
from app.v3.product.execution_mode import ProductExecutionMode
from app.v3.business_relationship_v1 import RelationshipLayerState
from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.research import ObligationState
from app.v3.research_analytical_scope import analytical_scope_contract
from app.v3.root_cause_candidate_contract import (
    RootCauseCandidateRelation,
    RootCauseCandidateSemantics,
    embed_root_cause_candidate_semantics,
)
from app.v3.research_contracts import (
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    RankingSurface,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeVersion,
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
    def __init__(self, *, limited_goal_ids=()):
        self.sessions = {}
        self.counter = 0
        self.run_calls = []
        self.limited_goal_ids = set(limited_goal_ids)

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
        session = SimpleNamespace(
            session_id=sid,
            obligations=tuple(obligations),
            evidence_refs=(),
            context_version=brief.context_version,
            lineage_id="atl_" + f"{self.counter:020x}",
            authority_id="atc_fake_" + f"{self.counter:020x}",
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
        # P14 verifies analytical material, not business-relationship truth.
        # P18 remains the sole relationship-policy owner downstream.
        # OTHER represents a typed unresolved recursive product obligation.
        target = (
            ObligationState.LIMITED
            if (
                goal.goal_id in self.limited_goal_ids
                or goal.kind == ResearchGoalKind.OTHER
            )
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
    def __init__(self, *, research, claim_on_calls=None):
        self.states = {}
        self.research = research
        self.claim_on_calls = (
            None if claim_on_calls is None else set(claim_on_calls)
        )

    def _state(self, session_id):
        return self.states.setdefault(
            session_id,
            {"steps": [], "claims": [], "calls": 0},
        )

    def snapshot(self, *, session_id, principal):
        del principal
        state = self._state(session_id)
        session = self.research.sessions[session_id]
        return SimpleNamespace(
            source_revision=state["calls"] + 1,
            parent_obligations=tuple(
                SimpleNamespace(
                    obligation_id=item.obligation_id,
                    state=item.state,
                )
                for item in session.obligations
            ),
            completed_reasoning_steps=tuple(state["steps"]),
            pending_reasoning_steps=(),
            claims=tuple(state["claims"]),
            terminal_stop_reason=None,
            remaining_reasoning_steps=max(0, 8 - state["calls"]),
            action_profile=SimpleNamespace(
                rules=(
                    SimpleNamespace(
                        intent=SimpleNamespace(value="INVESTIGATE_GAP"),
                        legal_parent_step_ids=tuple(state["steps"]),
                        allow_parentless=True,
                    ),
                ),
                legal_intents=("INVESTIGATE_GAP",),
            ),
        )

    def run_one(
        self,
        *,
        session_id,
        principal,
        manager,
        native_session_token,
        downstream_reentry_intent=None,
    ):
        del principal, native_session_token, downstream_reentry_intent
        state = self._state(session_id)
        state["obligation"] = getattr(
            manager,
            "target_parent_obligation",
            FakeReasoning.current_obligation_by_session.get(
                session_id,
                "g_root",
            ),
        )
        state["calls"] += 1
        n = state["calls"]
        step_id = f"rrs_{session_id[-8:]}{n:016x}"[-28:]
        if not step_id.startswith("rrs_"):
            step_id = "rrs_" + f"{n:024x}"
        state["steps"].append(step_id)
        if self.claim_on_calls is None or n in self.claim_on_calls:
            session = self.research.sessions[session_id]
            evidence = tuple(
                item
                for item in session.evidence_refs
                if item.obligation_id == self._obligation(session_id)
            )
            state["claims"].append(
                SimpleNamespace(
                    claim_id="clm_" + f"{n:024x}",
                    research_session_id=session_id,
                    obligation_id=self._obligation(session_id),
                    claim_text=f"Sealed P17 claim {n}",
                    proposition=(
                        embed_root_cause_candidate_semantics(
                            {"subject": "observed-scope"},
                            RootCauseCandidateSemantics(
                                explanatory_subject_ref=self._obligation(session_id),
                                relation_kind=(
                                    RootCauseCandidateRelation.EXPLANATORY_CANDIDATE
                                ),
                                mechanism_ref=f"ibr_fake_{n}",
                                scope_lineage_id=session.lineage_id,
                                scope_version_id=(
                                    session.accepted_brief.scope.scope_version.version_id
                                ),
                            ),
                        )
                        if getattr(
                            manager,
                            "_claim_semantic_contract",
                            None,
                        )
                        is not None
                        else {"relationship_kind": "ASSOCIATION"}
                    ),
                    epistemic_state=SimpleNamespace(value="SUPPORTED"),
                    limitations=(),
                    evidence_links=tuple(
                        SimpleNamespace(
                            evidence_id=item.evidence_id,
                            receipt_id=item.receipt_id,
                            relation="SUPPORTS",
                        )
                        for item in evidence
                    ),
                )
            )
        return SimpleNamespace(step_id=step_id), None

    def _obligation(self, session_id):
        state = self._state(session_id)
        return state.get(
            "obligation",
            FakeReasoning.current_obligation_by_session.get(
                session_id,
                "g_root",
            ),
        )


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
        obligation = state.get(
            "obligation",
            self.current_obligation_by_session.get(session_id, "g_root"),
        )
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
            policy_id=(None if self.blocked else "brp_" + "2" * 24),
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
        candidate_identity_ref=None,
    ):
        del principal, candidate_identity_ref
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
    def __init__(self, research):
        self.research = research
        self.drafts = []

    def draft_from_governed_research(
        self,
        *,
        research_session_id,
        report_key,
        principal,
        explicit_limitations=(),
    ):
        del report_key, principal
        session = self.research.sessions[research_session_id]
        explicit = {item.obligation_id: item for item in explicit_limitations}
        coverage = []
        for question in session.accepted_brief.questions:
            if question.goal_id in explicit:
                coverage.append(
                    SimpleNamespace(
                        obligation_id=question.goal_id,
                        coverage_status=SimpleNamespace(value="LIMITED"),
                        limitation_ids=(explicit[question.goal_id].limitation_id,),
                        statement_ids=(),
                    )
                )
            else:
                coverage.append(
                    SimpleNamespace(
                        obligation_id=question.goal_id,
                        coverage_status=SimpleNamespace(value="REPRESENTED"),
                        limitation_ids=(),
                        statement_ids=("p20s_" + "4" * 24,),
                    )
                )
        return SimpleNamespace(
            research_session_id=research_session_id,
            coverage=tuple(coverage),
            statements=(),
            limitations=tuple(explicit_limitations),
        )

    def seal(self, *, draft, principal):
        del principal
        self.drafts.append(draft)
        return SimpleNamespace(report_id="p20r_" + "3" * 24)


def composer(
    *,
    relationship_blocked=True,
    limited_goal_ids=(),
    claim_on_calls=None,
):
    research = FakeResearch(limited_goal_ids=limited_goal_ids)
    investigation = FakeInvestigation(
        research=research,
        claim_on_calls=claim_on_calls,
    )
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
            reports=FakeReports(research),
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
    assert result.execution_mode == ProductExecutionMode.FAST


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

    # Fake P17 needs the accepted relationship obligation identity.
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
    assert result.child_research_session_ids == ()
    assert result.p17_step_refs
    assert result.p18_policy_use_refs == ("bru_" + "1" * 24,)
    assert result.p20_report_ref == "p20r_" + "3" * 24
    assert result.terminal_state == ProductCompositionTerminal.REPORT
    assert "P18" in result.owner_calls
    assert "P19" not in result.owner_calls
    assert result.execution_mode == ProductExecutionMode.GUIDED
    assert len(result.relationship_results) == 1
    relationship = result.relationship_results[0]
    assert relationship.policy_use_id == "bru_" + "1" * 24
    assert relationship.supporting_evidence_refs
    assert relationship.association_state == RelationshipLayerState.SUPPORTED
    assert relationship.business_relationship_state == RelationshipLayerState.BLOCKED
    assert "P18_RELATIONSHIP_POLICY_MISSING" in relationship.limitation_codes
    assert relationship.causality_state == RelationshipLayerState.NOT_ESTABLISHED
    assert relationship.contribution_state == RelationshipLayerState.NOT_ESTABLISHED


def test_r8_relationship_reuses_parent_r1_scope_contract_without_child_root():
    event_date = ResearchSemanticRef(
        source_mention="event date",
        candidate_id="dimension.event_date",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Event Date",
        cube_names=("machine_operations",),
    )
    assembly = ResearchSemanticRef(
        source_mention="Assembly",
        candidate_id="entity.department.assembly",
        target_kind=SemanticTargetKind.ENTITY_VALUE,
        canonical_name="Assembly",
        dimension_name="department",
        value="Assembly",
        cube_names=("machine_operations",),
    )
    period = ResearchTimePeriod(
        source_text="June 2026",
        time_dimension_candidate_id=event_date.candidate_id,
        start="2026-06-01",
        end="2026-07-01",
    )
    goal = question(
        "g_relationship_scoped",
        ResearchGoalKind.RELATIONSHIP,
        subjects=(DOWNTIME, FAULTS),
        related=(DEPT,),
    )
    parent = ResearchBrief(
        brief_id="rb-r8-parent",
        objective="Scoped relationship material.",
        scope=ResearchScope(
            semantic_refs=(DOWNTIME, FAULTS, DEPT, event_date, assembly),
            time_surfaces=("June 2026",),
            periods=(period,),
            temporal_dimension_ids=(event_date.candidate_id,),
            scope_version=ScopeVersion(
                version_id="scope_v2",
                ordinal=2,
                parent_version_id="scope_v1",
            ),
        ),
        questions=(goal,),
        must_requirement_ids=(goal.goal_id,),
        context_version="ctx-r8",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )

    c, research, _, reasoning = composer()
    original = c._resolve_relationship

    def wrapped(**kwargs):
        reasoning.current_obligation_by_session[kwargs["material_session_id"]] = (
            kwargs["material_goal"].goal_id
        )
        return original(**kwargs)

    c._resolve_relationship = wrapped
    result = c.compose(
        brief=parent,
        principal=principal(),
        request_ref="r8-parent-authority",
        source_message_hash="8" * 64,
        native_session_token=None,
    )

    assert result.child_research_session_ids == ()
    assert len(research.sessions) == 1
    material_session = research.sessions[result.research_session_id]
    assert material_session.accepted_brief.scope == parent.scope
    assert material_session.accepted_brief.questions == (goal,)

    contract = analytical_scope_contract(
        session=material_session,
        obligation_id=goal.goal_id,
    )
    assert contract.scope_identity.version_id == "scope_v2"
    assert contract.period is not None
    assert contract.period.start == "2026-06-01"
    assert contract.period.end == "2026-07-01"
    assert tuple(item.value for item in contract.filters) == ("Assembly",)


def test_r4_exact_active_p18_policy_promotes_only_business_relationship_layer():
    c, _, _, reasoning = composer(relationship_blocked=False)
    b = brief(
        question(
            "g_relationship",
            ResearchGoalKind.RELATIONSHIP,
            subjects=(DOWNTIME, FAULTS),
            related=(DEPT,),
        ),
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
        request_ref="r4-active-policy",
        source_message_hash="4" * 64,
        native_session_token=None,
    )
    assert len(result.relationship_results) == 1
    relationship = result.relationship_results[0]
    assert relationship.association_state == RelationshipLayerState.SUPPORTED
    assert (
        relationship.business_relationship_state
        == RelationshipLayerState.SATISFIED
    )
    assert relationship.contribution_state == RelationshipLayerState.NOT_ESTABLISHED
    assert relationship.causality_state == RelationshipLayerState.NOT_ESTABLISHED
    assert not any(
        item.code == "P18_RELATIONSHIP_POLICY_MISSING"
        for item in result.limitations
    )


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
    assert result.execution_mode == ProductExecutionMode.INVESTIGATION


def test_adaptive_requirement_roots_p17_in_exact_verified_source_obligation():
    c, research, investigation, reasoning = composer()
    b = brief(
        question("g_base", ResearchGoalKind.BREAKDOWN),
        report=True,
    )
    requirement = ProductInvestigationRequirement(
        requirement_id="pir_" + "a" * 20,
        kind=ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL,
        source_goal_id="g_base",
        source_text="Follow a new material direction only if verified evidence warrants it.",
    )

    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="adaptive",
        source_message_hash="d" * 64,
        native_session_token=None,
        investigation_requirements=(requirement,),
    )

    assert result.p17_required_goal_ids == ("g_base",)
    assert result.investigation_requirement_ids == (requirement.requirement_id,)
    assert result.fulfilled_investigation_requirement_ids == (
        requirement.requirement_id,
    )
    assert result.p17_step_refs
    steps = reasoning.steps(result.research_session_id)
    assert steps
    assert {step.parent_obligation_id for step in steps} == {"g_base"}
    assert result.p18_policy_use_refs == ()
    assert result.p19_assessment_refs == ()
    assert result.p20_report_ref is not None
    assert result.execution_mode == ProductExecutionMode.INVESTIGATION


def test_verified_evidence_does_not_auto_route_unrelated_unverified_goal_to_p17():
    c, research, investigation, reasoning = composer()
    b = brief(
        question("g_base", ResearchGoalKind.BREAKDOWN),
        question("g_unrelated", ResearchGoalKind.OTHER),
    )

    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="no-adaptive-edge",
        source_message_hash="7" * 64,
        native_session_token=None,
    )

    assert result.p17_required_goal_ids == ()
    assert result.investigation_requirement_ids == ()
    assert result.p17_step_refs == ()
    assert investigation._state(result.research_session_id)["calls"] == 0


def test_adaptive_requirement_does_not_open_p17_when_source_is_limited():
    c, research, investigation, reasoning = composer(
        limited_goal_ids=("g_base",),
    )
    b = brief(
        question("g_base", ResearchGoalKind.BREAKDOWN),
        report=True,
    )
    requirement = ProductInvestigationRequirement(
        requirement_id="pir_" + "b" * 20,
        kind=ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL,
        source_goal_id="g_base",
        source_text="Follow only verified material.",
    )

    result = c.compose(
        brief=b,
        principal=principal(),
        request_ref="adaptive-limited",
        source_message_hash="8" * 64,
        native_session_token=None,
        investigation_requirements=(requirement,),
    )

    assert result.p17_required_goal_ids == ("g_base",)
    assert result.p17_step_refs == ()
    assert result.fulfilled_investigation_requirement_ids == ()
    assert investigation._state(result.research_session_id)["calls"] == 0
    assert any(
        item.code == "PRODUCT_ADAPTIVE_SOURCE_NOT_VERIFIED"
        and item.obligation_id == "g_base"
        for item in result.limitations
    )


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
    assert {item.obligation_id for item in drafts[0].coverage} == {
        item.goal_id for item in b.questions
    }
    assert "d_report" not in {
        item.obligation_id for item in drafts[0].coverage
    }
    assert result.p20_report_ref
    fulfillment = {
        item.requirement_id: item
        for item in result.user_must_fulfillment
    }
    assert fulfillment["g_breakdown"].state.value == "VERIFIED"
    assert fulfillment["d_report"].state.value == "FULFILLED"
    assert fulfillment["d_report"].fulfilled_by_ref == result.p20_report_ref
    assert result.user_must_total == 2
    assert result.user_must_accounted == 2
    assert result.user_must_fulfilled == 2


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


def test_relationship_waits_for_p17_owned_fifth_turn_without_product_shadow_budget():
    c, research, investigation, reasoning = composer(claim_on_calls={5})
    b = brief(question("g_relationship", ResearchGoalKind.RELATIONSHIP,
                       subjects=(DOWNTIME, FAULTS), related=(DEPT,)))
    original = c._resolve_relationship
    def wrapped(**kwargs):
        reasoning.current_obligation_by_session[kwargs["material_session_id"]] = kwargs["material_goal"].goal_id
        return original(**kwargs)
    c._resolve_relationship = wrapped
    result = c.compose(brief=b, principal=principal(), request_ref="rel-fifth",
                       source_message_hash="9"*64, native_session_token=None)
    assert result.child_research_session_ids == ()
    assert investigation._state(result.research_session_id)["calls"] == 5
    assert result.p18_policy_use_refs

def test_root_waits_for_p17_owned_seventh_turn_for_second_candidate():
    c, research, investigation, reasoning = composer(claim_on_calls={3, 7})
    b = brief(question("g_root", ResearchGoalKind.ROOT_CAUSE))
    original = c._assess_root_cause
    def wrapped(**kwargs):
        reasoning.current_obligation_by_session[kwargs["session_id"]] = kwargs["goal"].goal_id
        return original(**kwargs)
    c._assess_root_cause = wrapped
    result = c.compose(brief=b, principal=principal(), request_ref="root-seventh",
                       source_message_hash="6"*64, native_session_token=None)
    assert investigation._state(result.research_session_id)["calls"] == 7
    assert result.p19_assessment_refs
    p19_snapshot = c._epistemics.snapshot(
        research_session_id=result.research_session_id,
        obligation_id="g_root",
        principal=principal(),
    )
    assert len(p19_snapshot.hypotheses) == 2

def test_product_composition_has_no_independent_p17_budget_or_output_quota():
    source = inspect.getsource(__import__(
        "app.v3.product.composition",
        fromlist=["HeadlessProductComposer"],
    ))
    for forbidden in (
        "max_turns",
        "minimum_claims",
        "ProductInvestigationOutputNeed",
        "RELATIONSHIP_INTERPRETATION_INPUT",
        "COMPETING_EXPLANATION_INPUTS",
    ):
        assert forbidden not in source



def test_relationship_unexpected_owner_error_fails_closed_instead_of_sealing_report():
    c, _, _, _ = composer()
    b = brief(
        question(
            "g_relationship",
            ResearchGoalKind.RELATIONSHIP,
            subjects=(DOWNTIME, FAULTS),
            related=(DEPT,),
        ),
        report=True,
    )

    def explode(**_kwargs):
        raise ValueError("unexpected upstream owner/transport contract failure")

    c._resolve_relationship = explode
    with pytest.raises(
        ValueError,
        match="unexpected upstream owner/transport contract failure",
    ):
        c.compose(
            brief=b,
            principal=principal(),
            request_ref="relationship-fail-closed",
            source_message_hash="f" * 64,
            native_session_token=None,
        )



def test_root_does_not_enter_p17_when_p14_parent_is_limited():
    """Root investigation is callable only from VERIFIED durable P14 material."""

    c, research, investigation, reasoning = composer(
        limited_goal_ids=("g_root",),
    )
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
        request_ref="root-limited-proof",
        source_message_hash="e" * 64,
        native_session_token=None,
    )

    state = next(
        item.state
        for item in research.sessions[result.research_session_id].obligations
        if item.obligation_id == "g_root"
    )
    assert state == ObligationState.LIMITED
    assert investigation._state(result.research_session_id)["calls"] == 0
    assert result.p17_step_refs == ()
    assert result.p19_assessment_refs == ()
    assert any(
        item.code == "P17_NO_LEGAL_MOVE"
        and item.obligation_id == "g_root"
        for item in result.limitations
    )


def test_r3_product_root_candidate_projection_has_no_hidden_predicate_object_contract():
    source = inspect.getsource(
        __import__(
            "app.v3.product.composition",
            fromlist=["HeadlessProductComposer"],
        )
    )
    assert 'proposition.get("predicate")' not in source
    assert 'proposition.get("object")' not in source
    assert "decode_root_cause_candidate_semantics" in source


def test_r3_stale_scope_candidate_is_not_current_p19_input():
    claim = SimpleNamespace(
        claim_id="clm_" + "a" * 24,
        proposition=embed_root_cause_candidate_semantics(
            {"provider_note": "historical"},
            RootCauseCandidateSemantics(
                explanatory_subject_ref="g_root",
                relation_kind=(
                    RootCauseCandidateRelation.EXPLANATORY_CANDIDATE
                ),
                mechanism_ref="ibr_historical",
                scope_lineage_id="atl_historical",
                scope_version_id="scope_v1",
            ),
        ),
        evidence_links=(
            SimpleNamespace(
                evidence_id="evi_" + "b" * 24,
                receipt_id="dqr_" + "c" * 24,
                relation="SUPPORTS",
            ),
        ),
    )
    candidate = HeadlessProductComposer._root_cause_candidate(
        claim,
        expected_subject_ref="g_root",
        expected_scope_lineage_id="atl_current",
        expected_scope_version_id="scope_v2",
    )
    assert candidate is None


def test_r3_missing_evidence_does_not_create_p19_candidate():
    claim = SimpleNamespace(
        claim_id="clm_" + "d" * 24,
        proposition=embed_root_cause_candidate_semantics(
            {"provider_note": "current"},
            RootCauseCandidateSemantics(
                explanatory_subject_ref="g_root",
                relation_kind=(
                    RootCauseCandidateRelation.EXPLANATORY_CANDIDATE
                ),
                mechanism_ref="ibr_current",
                scope_lineage_id="atl_current",
                scope_version_id="scope_v1",
            ),
        ),
        evidence_links=(),
    )
    candidate = HeadlessProductComposer._root_cause_candidate(
        claim,
        expected_subject_ref="g_root",
        expected_scope_lineage_id="atl_current",
        expected_scope_version_id="scope_v1",
    )
    assert candidate is None



def test_r8_a_coorigin_relationship_reuses_verified_sibling_material_without_second_p14_turn():
    fragment_identity = "fragment-sha256:" + "a" * 64
    ranking = ResearchQuestion(
        goal_id="g_r8_rank",
        kind=ResearchGoalKind.RANKING,
        source_text="Inspect the two highest downtime departments.",
        source_fragment_identity=fragment_identity,
        subject_refs=(DEPT, DOWNTIME),
        related_refs=(),
        ranking=RankingSurface(
            text="top 2 by downtime",
            direction="desc",
            limit=2,
            measure_semantic_id=DOWNTIME.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    relationship = ResearchQuestion(
        goal_id="g_r8_relationship",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text=(
            "Inspect the two highest downtime departments together with fault count."
        ),
        source_fragment_identity=fragment_identity,
        subject_refs=(DOWNTIME, FAULTS),
        related_refs=(DEPT,),
        status=ResearchGoalStatus.RESOLVED,
    )
    b = brief(ranking, relationship)
    c, research, _, reasoning = composer(relationship_blocked=False)

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
        request_ref="r8-a-coorigin-material",
        source_message_hash="a" * 64,
        native_session_token=None,
    )

    # One VERIFIED sibling material occurrence is enough for the downstream
    # relationship authority; Product must not open a duplicate P14 material turn.
    assert research.run_calls == [(result.research_session_id, ranking.goal_id)]
    assert result.child_research_session_ids == ()
    assert result.p18_policy_use_refs == ("bru_" + "1" * 24,)
    assert len(result.relationship_results) == 1
    projected = result.relationship_results[0]
    assert projected.obligation_id == ranking.goal_id
    assert (
        projected.applicability_scope["accepted_relationship_goal_id"]
        == relationship.goal_id
    )

    # The Research relationship obligation is deliberately not forged VERIFIED;
    # its USER_MUST is fulfilled by the governed P18 result at Product level.
    session = research.sessions[result.research_session_id]
    relationship_obligation = next(
        item
        for item in session.obligations
        if item.obligation_id == relationship.goal_id
    )
    assert relationship_obligation.state == ObligationState.READY
    fulfillment = {
        item.requirement_id: item
        for item in result.user_must_fulfillment
    }
    assert fulfillment[relationship.goal_id].state.value == "FULFILLED"
    assert (
        fulfillment[relationship.goal_id].fulfilled_by_ref
        == result.p18_policy_use_refs[0]
    )
    assert result.user_must_accounted == 2
    assert result.user_must_fulfilled == 2
