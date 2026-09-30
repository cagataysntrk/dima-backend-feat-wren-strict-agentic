"""Core-B headless product composition over sealed P14-P21 authorities.

Product Composition coordinates existing owners. It does not calculate analytics,
mint Evidence/claims, decide relationship legality, judge root cause, or bypass
P20/P21 legality.
"""
from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from control_plane.authorize import Principal

from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.product.execution_mode import (
    ProductExecutionMode,
    classify_execution_mode,
)
from app.v3.product.process_manager import (
    ProductProcessError,
    ProductProcessNext,
    ProductProcessObservation,
    ProductProcessPurpose,
    RootCauseCandidate,
    decide_next_owner,
)

from app.v3.business_relationship_policy import (
    BusinessRelationshipPolicyStore,
    RelationshipPolicyRequirement,
)
from app.v3.business_relationship_v1 import (
    RelationshipResultProjection,
    project_relationship_result,
)
from app.v3.hypothesis_root_cause import (
    GroundingRelation,
    GroundingSourceKind,
    HypothesisRootCauseStore,
)
from app.v3.hypothesis_root_cause_v1 import (
    NextTestRequest,
    discriminating_test_is_callable,
    next_test_request,
)
from app.v3.report_document import (
    CoverageEntry,
    CoverageStatus,
    ReportDocumentStore,
    ReportDraft,
    ReportLimitation,
    stable_limitation_id,
)
from app.v3.research import ObligationState
from app.v3.research_analytical_scope import (
    CoOriginMaterialRequirement,
    coorigin_material_requirements,
)
from app.v3.research_contracts import (
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchQuestion,
    SemanticTargetKind,
)
from app.v3.research_manager import (
    ClaimSemanticContract,
    InvestigationIntent,
    InvestigationTargetKind,
    ManagerAction,
    ManagerProposal,
    ResearchInvestigationManager,
    ResearchManagerMaturationError,
    ResearchReasoningStore,
)
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.root_cause_candidate_contract import (
    decode_root_cause_candidate_semantics,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProductCompositionTerminal(StrEnum):
    ANSWER = "ANSWER"
    REPORT = "REPORT"
    DECISION = "DECISION"
    LIMITED = "LIMITED"
    INCONCLUSIVE = "INCONCLUSIVE"


class RootCauseExecutionMode(StrEnum):
    ONE_PASS = "ONE_PASS"
    ADAPTIVE = "ADAPTIVE"
    GOVERNED_INCONCLUSIVE = "GOVERNED_INCONCLUSIVE"


class RootCauseModeResult(Frozen):
    obligation_id: str = Field(min_length=1)
    mode: RootCauseExecutionMode
    assessment_ref: str = Field(pattern=r"^p19a_[a-f0-9]{24}$")
    user_seeded_candidates: bool
    analytical_reentry_count: int = Field(ge=0)


class ProductCompositionCurrentness(StrEnum):
    CURRENT = "CURRENT"


class CompositionLimitation(Frozen):
    obligation_id: str | None = None
    code: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    owner: str = Field(min_length=1)


class ProductRequirementKind(StrEnum):
    ANALYTICAL = "ANALYTICAL"
    DELIVERABLE = "DELIVERABLE"


class ProductRequirementState(StrEnum):
    VERIFIED = "VERIFIED"
    LIMITED = "LIMITED"
    FULFILLED = "FULFILLED"
    PENDING = "PENDING"


class ProductRequirementDisposition(StrEnum):
    FULFILLED = "FULFILLED"
    LIMITED = "LIMITED"
    UNSUPPORTED = "UNSUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class ProductRequirementCompletion(Frozen):
    requirement_id: str = Field(min_length=1)
    disposition: ProductRequirementDisposition
    fulfilled_by_ref: str | None = None


class ProductCompletionLedger(Frozen):
    entries: tuple[ProductRequirementCompletion, ...]
    process_complete: bool
    requirement_complete: bool
    # Historical compatibility alias: terminal accounting, not fulfillment.
    trusted_complete: bool


class ProductRequirementFulfillment(Frozen):
    requirement_id: str = Field(min_length=1)
    requirement_kind: ProductRequirementKind
    state: ProductRequirementState
    fulfilled_by_ref: str | None = None


class ProductCompositionResult(Frozen):
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    child_research_session_ids: tuple[str, ...] = ()
    p17_step_refs: tuple[str, ...] = ()
    p18_policy_use_refs: tuple[str, ...] = ()
    p19_assessment_refs: tuple[str, ...] = ()
    root_cause_mode_results: tuple[RootCauseModeResult, ...] = ()
    p20_report_ref: str | None = None
    p21_decision_ref: str | None = None
    evidence_refs: tuple[str, ...] = ()
    limitations: tuple[CompositionLimitation, ...] = ()
    owner_calls: tuple[str, ...] = ()
    p17_required_goal_ids: tuple[str, ...] = ()
    investigation_requirement_ids: tuple[str, ...] = ()
    fulfilled_investigation_requirement_ids: tuple[str, ...] = ()
    user_must_fulfillment: tuple[ProductRequirementFulfillment, ...] = ()
    user_must_total: int = 0
    user_must_accounted: int = 0
    user_must_fulfilled: int = 0
    completion_ledger: ProductCompletionLedger | None = None
    execution_mode: ProductExecutionMode
    relationship_results: tuple[RelationshipResultProjection, ...] = ()
    terminal_state: ProductCompositionTerminal
    currentness: ProductCompositionCurrentness = ProductCompositionCurrentness.CURRENT


class ProposalManager(Protocol):
    call_count: int

    def propose(self, snapshot): ...


class P19ProposalManager(Protocol):
    call_count: int

    def propose(
        self,
        snapshot,
        *,
        policy_statuses: dict[str, str] | None = None,
        deterministic_feedback_code: str | None = None,
    ): ...


class ProductInvestigationRequirementStoreProtocol(Protocol):
    def persist(
        self,
        *,
        tenant_binding: str,
        research_session_id: str,
        brief_id: str,
        requirements: tuple[ProductInvestigationRequirement, ...],
        accepted_goal_ids: tuple[str, ...],
    ) -> tuple[ProductInvestigationRequirement, ...]: ...

    def load(
        self,
        *,
        tenant_binding: str,
        research_session_id: str,
    ) -> tuple[ProductInvestigationRequirement, ...]: ...


class _ObligationScopedProposalManager:
    """Provider-view adapter only; P17 domain validation remains final."""

    def __init__(
        self,
        *,
        inner: ProposalManager,
        target_parent_obligation: str,
        allowed_evidence_refs: tuple[str, ...],
        claim_semantic_contract: ClaimSemanticContract | None = None,
        allowed_mechanism_refs: tuple[str, ...] = (),
        allowed_intents: tuple[InvestigationIntent, ...] = (),
    ) -> None:
        self._inner = inner
        self.target_parent_obligation = target_parent_obligation
        self._allowed_evidence_refs = allowed_evidence_refs
        self._claim_semantic_contract = claim_semantic_contract
        self._allowed_mechanism_refs = allowed_mechanism_refs
        self._allowed_intents = allowed_intents

    @property
    def call_count(self) -> int:
        return int(getattr(self._inner, "call_count", 0))

    def propose(self, snapshot):
        if self._claim_semantic_contract == ClaimSemanticContract.ROOT_CAUSE_CANDIDATE:
            method_name = (
                "propose_root_candidate_for_obligation_with_constraints"
                if self._allowed_intents
                else "propose_root_candidate_for_obligation"
            )
            scoped = getattr(self._inner, method_name, None)
            if not callable(scoped):
                raise ValueError(
                    "root-cause provider lacks governed mechanism selection boundary"
                )
            kwargs = {
                "target_parent_obligation": self.target_parent_obligation,
                "allowed_evidence_refs": self._allowed_evidence_refs,
                "allowed_mechanism_refs": self._allowed_mechanism_refs,
            }
            if self._allowed_intents:
                kwargs["allowed_intents"] = self._allowed_intents
            proposal = scoped(snapshot, **kwargs)
        else:
            if self._allowed_intents:
                scoped = getattr(
                    self._inner,
                    "propose_for_obligation_with_constraints",
                    None,
                )
                if not callable(scoped):
                    raise ValueError(
                        "provider lacks scoped constrained P17 proposal boundary"
                    )
                proposal = scoped(
                    snapshot,
                    target_parent_obligation=self.target_parent_obligation,
                    allowed_evidence_refs=self._allowed_evidence_refs,
                    allowed_intents=self._allowed_intents,
                )
            else:
                scoped = getattr(self._inner, "propose_for_obligation", None)
                if callable(scoped):
                    proposal = scoped(
                        snapshot,
                        target_parent_obligation=self.target_parent_obligation,
                        allowed_evidence_refs=self._allowed_evidence_refs,
                    )
                else:
                    proposal = self._inner.propose(snapshot)
        target = getattr(proposal, "target_parent_obligation", None)
        if target is not None and target != self.target_parent_obligation:
            raise ValueError(
                "provider proposal escaped Core-B source-obligation scope"
            )
        if (
            self._claim_semantic_contract is not None
            and proposal.action == ManagerAction.FORM_CLAIM
        ):
            proposal = proposal.model_copy(
                update={
                    "claim_semantic_contract": self._claim_semantic_contract,
                }
            )
        return proposal


class _NextTestProposalManager:
    """Deterministic Product adapter: typed P19 need -> one legal P17 intent."""

    def __init__(
        self,
        *,
        request: NextTestRequest,
        target_parent_obligation: str,
    ) -> None:
        self.request = request
        self.target_parent_obligation = target_parent_obligation
        self.call_count = 0

    def propose(self, snapshot):
        self.call_count += 1
        rule = snapshot.action_profile.rule_for(
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
        )
        if rule is None:
            raise ProductProcessError(
                "PRODUCT_NEXT_TEST_NOT_STATE_LEGAL",
                self.request.request_id,
            )
        ordered = {
            node.step_id: index
            for index, node in enumerate(snapshot.investigation.nodes)
        }
        legal = tuple(
            step_id for step_id in rule.legal_parent_step_ids
            if next(
                (
                    node.root_obligation_id
                    for node in snapshot.investigation.nodes
                    if node.step_id == step_id
                ),
                None,
            )
            == self.target_parent_obligation
        )
        if not legal:
            raise ProductProcessError(
                "PRODUCT_NEXT_TEST_PARENT_MISSING",
                self.request.request_id,
            )
        parent = max(legal, key=lambda item: ordered.get(item, -1))
        return ManagerProposal(
            proposal_id="p17-next-" + self.request.request_id[4:],
            source_revision=snapshot.source_revision,
            target_parent_obligation=self.target_parent_obligation,
            action=ManagerAction.EXPLORE_NATIVE,
            intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            parent_step_id=parent,
            branch_key=None,
            target_kind=InvestigationTargetKind.EXPLANATION,
            target_ref=self.request.request_id,
            objective_key="next_test." + self.request.request_id[4:],
            bounded_objective=self.request.bounded_objective(),
            rationale=(
                "P19 exposed a typed unresolved ambiguity; Product routes only "
                "the governed test need and does not predict the result."
            ),
            inspected_evidence_refs=(),
            inspected_claim_refs=(),
            inspected_material_refs=(),
            expected_information_gain=(
                self.request.expected_discriminatory_value.value
            ),
        )


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def _stable(prefix: str, value: Any, length: int = 20) -> str:
    return prefix + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()[:length]


def _question_map(brief: ResearchBrief) -> dict[str, ResearchQuestion]:
    return {item.goal_id: item for item in brief.questions}


def _state_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _root_cause_execution_mode(
    *,
    aggregate_outcome: Any,
    analytical_reentry_count: int,
) -> RootCauseExecutionMode:
    if analytical_reentry_count > 0:
        return RootCauseExecutionMode.ADAPTIVE
    if _state_value(aggregate_outcome) in {
        "IN_PROGRESS",
        "NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED",
    }:
        return RootCauseExecutionMode.GOVERNED_INCONCLUSIVE
    return RootCauseExecutionMode.ONE_PASS


class HeadlessProductComposer:
    """One bounded orchestration owner; all truth remains in sealed owners."""

    def __init__(
        self,
        *,
        research: ResearchAskOrchestrator,
        investigation: ResearchInvestigationManager,
        investigation_manager: ProposalManager,
        reasoning: ResearchReasoningStore,
        relationships: BusinessRelationshipPolicyStore,
        epistemics: HypothesisRootCauseStore,
        epistemic_manager: P19ProposalManager,
        reports: ReportDocumentStore,
        investigation_requirements: (
            ProductInvestigationRequirementStoreProtocol | None
        ) = None,
    ) -> None:
        self._research = research
        self._investigation = investigation
        self._investigation_manager = investigation_manager
        self._reasoning = reasoning
        self._relationships = relationships
        self._epistemics = epistemics
        self._epistemic_manager = epistemic_manager
        self._reports = reports
        self._investigation_requirements = investigation_requirements

    @staticmethod
    def _run_p14(
        *,
        research: ResearchAskOrchestrator,
        session_id: str,
        brief: ResearchBrief,
        principal: Principal,
        native_session_token: str | None,
        owner_calls: list[str],
        skip_obligation_ids: frozenset[str] = frozenset(),
    ):
        for question in brief.questions:
            if question.goal_id in skip_obligation_ids:
                continue
            session = research.resume_state(
                session_id=session_id,
                principal=principal,
            )
            matches = tuple(
                item for item in session.obligations
                if item.obligation_id == question.goal_id
            )
            if len(matches) != 1:
                continue
            state = _state_value(matches[0].state)
            if state in {"VERIFIED", "LIMITED", "FAILED"}:
                continue
            research.run_next(
                session_id=session_id,
                principal=principal,
                obligation_id=question.goal_id,
                native_session_token=native_session_token,
            )
            owner_calls.append("P14")
        return research.resume_state(
            session_id=session_id,
            principal=principal,
        )

    @staticmethod
    def _relationship_material_requirement(
        *,
        requirements: tuple[CoOriginMaterialRequirement, ...],
        goal: ResearchQuestion,
    ) -> CoOriginMaterialRequirement | None:
        matches = tuple(
            item
            for item in requirements
            if (
                goal.goal_id in item.source_goal_ids
                and goal.goal_id != item.anchor_goal_id
            )
        )
        if len(matches) > 1:
            raise ValueError(
                "relationship goal belongs to multiple co-origin material requirements"
            )
        if not matches:
            return None
        requirement = matches[0]
        required = {
            item.candidate_id
            for item in (*goal.subject_refs, *goal.related_refs)
            if item.target_kind
            in {
                SemanticTargetKind.METRIC,
                SemanticTargetKind.KPI,
                SemanticTargetKind.DIMENSION,
            }
        }
        coverage = set(requirement.required_metric_refs) | set(
            requirement.required_dimension_refs
        )
        if not required.issubset(coverage):
            raise ValueError(
                "canonical co-origin material coverage cannot satisfy relationship refs"
            )
        return requirement

    @staticmethod
    def _root_cause_candidate(
        claim,
        *,
        expected_subject_ref: str,
        expected_scope_lineage_id: str,
        expected_scope_version_id: str,
    ) -> RootCauseCandidate | None:
        proposition = getattr(claim, "proposition", {}) or {}
        try:
            semantics = decode_root_cause_candidate_semantics(proposition)
        except ValueError as exc:
            raise ProductProcessError(
                "PRODUCT_ROOT_CANDIDATE_CONTRACT_INVALID",
                str(exc),
            ) from exc
        if semantics is None:
            return None
        if (
            semantics.explanatory_subject_ref != expected_subject_ref
            or semantics.scope_lineage_id != expected_scope_lineage_id
            or semantics.scope_version_id != expected_scope_version_id
        ):
            # Historical claims remain readable but cannot satisfy current scope.
            return None
        evidence_refs = tuple(
            dict.fromkeys(
                link.evidence_id
                for link in getattr(claim, "evidence_links", ())
            )
        )
        if not evidence_refs:
            return None
        return RootCauseCandidate(
            claim_id=claim.claim_id,
            semantics=semantics,
            evidence_refs=evidence_refs,
        )

    @staticmethod
    def _root_cause_mechanism_refs(
        *,
        goal: ResearchQuestion,
        source_session,
    ) -> tuple[tuple[str, ...], bool]:
        surface = goal.causal_competition
        goal_refs = tuple((*goal.subject_refs, *goal.related_refs))
        if surface is not None:
            if surface.candidate_mechanism_semantic_ids:
                return surface.candidate_mechanism_semantic_ids, True
            return (
                tuple(
                    dict.fromkeys(
                        item.candidate_id
                        for item in goal_refs
                        if (
                            item.target_kind
                            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                            and item.candidate_id != surface.effect_semantic_id
                        )
                    )
                ),
                False,
            )

        # Compatibility for historical accepted briefs that predate the typed
        # causal surface. Live Research Intake can no longer mint this shape.
        subject_refs = {item.candidate_id for item in goal.subject_refs}
        brief = getattr(source_session, "accepted_brief", None)
        return (
            tuple(
                sorted(
                    item.candidate_id
                    for item in (brief.scope.semantic_refs if brief else ())
                    if (
                        item.target_kind
                        in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                        and item.candidate_id not in subject_refs
                    )
                )
            ),
            False,
        )

    def _synthesize_root_candidates(
        self,
        *,
        session_id: str,
        goal: ResearchQuestion,
        principal: Principal,
        native_session_token: str | None,
        owner_calls: list[str],
        mechanism_refs: tuple[str, ...],
        evidence_refs: tuple[str, ...],
    ):
        """Interpret already VERIFIED Evidence for exact governed mechanisms.

        This is P17 claim synthesis only. FORM_CLAIM cannot execute analytics,
        so explicit user candidates do not trigger redundant Metabase re-entry.
        """
        if not evidence_refs:
            return self._investigation.snapshot(
                session_id=session_id,
                principal=principal,
            )
        for mechanism_ref in tuple(dict.fromkeys(mechanism_refs)):
            manager = _ObligationScopedProposalManager(
                inner=self._investigation_manager,
                target_parent_obligation=goal.goal_id,
                allowed_evidence_refs=evidence_refs,
                claim_semantic_contract=ClaimSemanticContract.ROOT_CAUSE_CANDIDATE,
                allowed_mechanism_refs=(mechanism_ref,),
                allowed_intents=(InvestigationIntent.FORM_CLAIM,),
            )
            self._investigation.run_one(
                session_id=session_id,
                principal=principal,
                manager=manager,
                native_session_token=native_session_token,
                downstream_reentry_intent=InvestigationIntent.FORM_CLAIM,
                downstream_reentry_obligation_id=goal.goal_id,
            )
            owner_calls.append("P17")
        return self._investigation.snapshot(
            session_id=session_id,
            principal=principal,
        )

    def _sync_root_candidates_to_p19(
        self,
        *,
        session_id: str,
        goal: ResearchQuestion,
        principal: Principal,
        source_session,
        claims: tuple[Any, ...],
    ) -> tuple[str, ...]:
        brief = source_session.accepted_brief
        if brief is None:
            return ()
        refs = {item.candidate_id: item for item in brief.scope.semantic_refs}
        relation_map = {
            "SUPPORTS": GroundingRelation.SUPPORTS,
            "CHALLENGES": GroundingRelation.CHALLENGES,
            "CONTEXTUALIZES": GroundingRelation.CONTEXT,
            "INSUFFICIENT": GroundingRelation.INSUFFICIENT,
        }
        mechanism_refs: list[str] = []
        for claim in claims:
            candidate = self._root_cause_candidate(
                claim,
                expected_subject_ref=goal.goal_id,
                expected_scope_lineage_id=source_session.lineage_id,
                expected_scope_version_id=brief.scope.scope_version.version_id,
            )
            if candidate is None:
                continue
            mechanism_ref = candidate.semantics.mechanism_ref
            mechanism_refs.append(mechanism_ref)
            semantic = refs.get(mechanism_ref)
            statement = (
                semantic.canonical_name
                if semantic is not None
                else mechanism_ref
            )
            hypothesis = self._epistemics.create_hypothesis(
                research_session_id=session_id,
                obligation_id=goal.goal_id,
                statement=statement,
                principal=principal,
                candidate_identity_ref=mechanism_ref,
            )
            self._epistemics.create_grounding(
                hypothesis_id=hypothesis.hypothesis_id,
                source_kind=GroundingSourceKind.P16_CLAIM,
                source_ref=claim.claim_id,
                relation=GroundingRelation.CONTEXT,
                principal=principal,
            )
            for link in claim.evidence_links:
                relation = relation_map.get(link.relation)
                if relation is None:
                    raise ProductProcessError(
                        "PRODUCT_P16_EVIDENCE_RELATION_UNKNOWN",
                        link.relation,
                    )
                self._epistemics.create_grounding(
                    hypothesis_id=hypothesis.hypothesis_id,
                    source_kind=GroundingSourceKind.P14_EVIDENCE,
                    source_ref=link.evidence_id,
                    source_receipt_id=link.receipt_id,
                    relation=relation,
                    principal=principal,
                )
        return tuple(dict.fromkeys(mechanism_refs))

    def _observe_p17_process(
        self,
        *,
        snapshot,
        session_id: str,
        target_obligation_id: str,
        principal: Principal,
        downstream_ref_present: bool = False,
    ) -> tuple[ProductProcessObservation, tuple[Any, ...], tuple[Any, ...]]:
        steps = tuple(
            step for step in self._reasoning.steps(session_id)
            if step.parent_obligation_id == target_obligation_id
        )
        scoped_step_ids = {step.step_id for step in steps}
        completed_ids = set(snapshot.completed_reasoning_steps)
        completed = tuple(
            step.step_id for step in steps
            if step.step_id in completed_ids
        )
        claims_by_id = {
            claim.claim_id: claim
            for claim in snapshot.claims
            if claim.obligation_id == target_obligation_id
        }
        claims = tuple(claims_by_id.values())

        parent_verified = any(
            item.obligation_id == target_obligation_id
            and _state_value(item.state) == ObligationState.VERIFIED.value
            for item in snapshot.parent_obligations
        )
        scoped_move_available = False
        if parent_verified:
            for rule in snapshot.action_profile.rules:
                legal_parents = set(rule.legal_parent_step_ids)
                if not (
                    rule.allow_parentless
                    or bool(legal_parents.intersection(scoped_step_ids))
                ):
                    continue
                if (
                    _state_value(rule.intent) == "SEEK_COUNTER_EVIDENCE"
                    and not claims
                ):
                    continue
                scoped_move_available = True
                break

        stop = getattr(snapshot, "terminal_stop_reason", None)
        current_session = self._research.resume_state(
            session_id=session_id,
            principal=principal,
        )
        accepted_brief = getattr(current_session, "accepted_brief", None)
        root_candidates = ()
        if accepted_brief is not None:
            root_candidates = tuple(
                candidate
                for claim in claims
                if (
                    candidate := self._root_cause_candidate(
                        claim,
                        expected_subject_ref=target_obligation_id,
                        expected_scope_lineage_id=current_session.lineage_id,
                        expected_scope_version_id=(
                            accepted_brief.scope.scope_version.version_id
                        ),
                    )
                )
                is not None
            )
        observation = ProductProcessObservation(
            claim_ids=tuple(claims_by_id),
            completed_step_ids=completed,
            root_cause_candidates=root_candidates,
            terminal_stop_reason=(
                _state_value(stop) if stop is not None else None
            ),
            remaining_reasoning_steps=int(snapshot.remaining_reasoning_steps),
            scoped_move_available=scoped_move_available,
            downstream_ref_present=downstream_ref_present,
        )
        return observation, claims, steps

    @staticmethod
    def _p17_progress_signature(
        snapshot,
        observation: ProductProcessObservation,
        steps: tuple[Any, ...],
    ) -> tuple[Any, ...]:
        return (
            getattr(snapshot, "source_revision", None),
            observation.claim_ids,
            observation.completed_step_ids,
            tuple(
                (
                    step.step_id,
                    _state_value(getattr(step, "status", "")),
                    tuple(getattr(step, "result_refs", ()) or ()),
                )
                for step in steps
            ),
            tuple(getattr(snapshot, "pending_reasoning_steps", ()) or ()),
            observation.terminal_stop_reason,
            observation.remaining_reasoning_steps,
        )

    @staticmethod
    def _p17_terminal_code(*, snapshot, last_error: Exception | None) -> str:
        if last_error is not None and getattr(last_error, "code", None):
            return str(last_error.code)
        stop = getattr(snapshot, "terminal_stop_reason", None)
        if stop is not None:
            return "P17_" + _state_value(stop)
        if int(getattr(snapshot, "remaining_reasoning_steps", 0)) <= 0:
            return "P17_BUDGET_EXHAUSTED"
        return "P17_NO_LEGAL_MOVE"

    def _run_p17(
        self,
        *,
        session_id: str,
        principal: Principal,
        native_session_token: str | None,
        purpose: ProductProcessPurpose,
        owner_calls: list[str],
        manager: ProposalManager | None = None,
        target_obligation_id: str,
        downstream_ref_present: bool = False,
        downstream_reentry_intent: InvestigationIntent | None = None,
        downstream_reentry_obligation_id: str | None = None,
    ):
        executed = 0
        last_error: Exception | None = None
        effective_manager = manager or self._investigation_manager

        while True:
            snapshot = self._investigation.snapshot(
                session_id=session_id,
                principal=principal,
            )
            observation, _, steps = self._observe_p17_process(
                snapshot=snapshot,
                session_id=session_id,
                target_obligation_id=target_obligation_id,
                principal=principal,
                downstream_ref_present=downstream_ref_present,
            )
            next_owner = decide_next_owner(purpose, observation)
            if next_owner != ProductProcessNext.P17:
                return snapshot, next_owner, executed, last_error

            before = self._p17_progress_signature(snapshot, observation, steps)
            try:
                self._investigation.run_one(
                    session_id=session_id,
                    principal=principal,
                    manager=effective_manager,
                    native_session_token=native_session_token,
                    downstream_reentry_intent=downstream_reentry_intent,
                    downstream_reentry_obligation_id=(
                        downstream_reentry_obligation_id
                    ),
                )
                owner_calls.append("P17")
                executed += 1
            except ResearchManagerMaturationError as exc:
                last_error = exc
                if exc.code == "P17_INVESTIGATION_TERMINAL":
                    terminal = self._investigation.snapshot(
                        session_id=session_id,
                        principal=principal,
                    )
                    return terminal, ProductProcessNext.TERMINAL, executed, last_error
                raise

            after = self._investigation.snapshot(
                session_id=session_id,
                principal=principal,
            )
            after_observation, _, after_steps = self._observe_p17_process(
                snapshot=after,
                session_id=session_id,
                target_obligation_id=target_obligation_id,
                principal=principal,
                downstream_ref_present=downstream_ref_present,
            )
            after_signature = self._p17_progress_signature(
                after,
                after_observation,
                after_steps,
            )
            if after_signature == before:
                last_error = ProductProcessError(
                    "PROCESS_NO_PROGRESS",
                    "P17 returned without durable state/revision progress",
                )
                return after, ProductProcessNext.TERMINAL, executed, last_error

    @staticmethod
    def _relationship_refs(goal: ResearchQuestion) -> tuple[str, str, tuple[str, ...]]:
        refs = tuple(dict.fromkeys((*goal.subject_refs, *goal.related_refs)))
        measures = tuple(
            item.candidate_id for item in refs
            if item.target_kind
            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
        if len(measures) < 2:
            raise ValueError("relationship goal has no governed measure pair")
        dimensions = tuple(
            item.candidate_id for item in refs
            if item.target_kind == SemanticTargetKind.DIMENSION
        )
        return measures[0], measures[1], dimensions

    def _resolve_relationship(
        self,
        *,
        original_goal: ResearchQuestion,
        material_session_id: str,
        material_goal: ResearchQuestion,
        principal: Principal,
        native_session_token: str | None,
        owner_calls: list[str],
    ):
        material_session = self._research.resume_state(
            session_id=material_session_id,
            principal=principal,
        )
        allowed_evidence_refs = tuple(
            item.evidence_id
            for item in material_session.evidence_refs
            if item.obligation_id == material_goal.goal_id
        )
        if not allowed_evidence_refs:
            raise ProductProcessError(
                "PRODUCT_RELATIONSHIP_MATERIAL_EVIDENCE_REQUIRED",
                "relationship handoff requires verified same-obligation Evidence",
            )
        scoped_manager = _ObligationScopedProposalManager(
            inner=self._investigation_manager,
            target_parent_obligation=material_goal.goal_id,
            allowed_evidence_refs=allowed_evidence_refs,
            allowed_intents=(InvestigationIntent.FORM_CLAIM,),
        )
        snapshot, next_owner, _, last_error = self._run_p17(
            session_id=material_session_id,
            principal=principal,
            native_session_token=native_session_token,
            purpose=ProductProcessPurpose.RELATIONSHIP,
            owner_calls=owner_calls,
            manager=scoped_manager,
            target_obligation_id=material_goal.goal_id,
            downstream_reentry_intent=InvestigationIntent.FORM_CLAIM,
            downstream_reentry_obligation_id=material_goal.goal_id,
        )
        observation, claims, all_steps = self._observe_p17_process(
            snapshot=snapshot,
            session_id=material_session_id,
            target_obligation_id=material_goal.goal_id,
            principal=principal,
        )
        completed = set(observation.completed_step_ids)
        steps = tuple(step for step in all_steps if step.step_id in completed)
        if next_owner != ProductProcessNext.P18:
            return None, None, snapshot, self._p17_terminal_code(
                snapshot=snapshot,
                last_error=last_error,
            )

        source_ref, target_ref, dimensions = self._relationship_refs(original_goal)
        scope = {
            "accepted_relationship_goal_id": original_goal.goal_id,
            "semantic_ref_ids": sorted(
                {
                    item.candidate_id
                    for item in (
                        *original_goal.subject_refs,
                        *original_goal.related_refs,
                    )
                }
            ),
            "dimension_ref_ids": list(dimensions),
        }
        key = "relationship:" + hashlib.sha256(
            _canonical(
                {
                    "source": source_ref,
                    "target": target_ref,
                    "scope": scope,
                }
            ).encode("utf-8")
        ).hexdigest()[:24]
        decision = self._relationships.resolve(
            requirement=RelationshipPolicyRequirement(
                research_session_id=material_session_id,
                obligation_id=material_goal.goal_id,
                claim_id=claims[-1].claim_id,
                reasoning_step_id=steps[-1].step_id,
                policy_key=key,
                source_business_ref=source_ref,
                target_business_ref=target_ref,
                semantic_context_version=(
                    self._research.resume_state(
                        session_id=material_session_id,
                        principal=principal,
                    ).context_version
                ),
                applicability_scope=scope,
                required=True,
            ),
            principal=principal,
        )
        owner_calls.append("P18")
        current_material = self._research.resume_state(
            session_id=material_session_id,
            principal=principal,
        )
        relationship_result = project_relationship_result(
            research_session_id=material_session_id,
            claim=claims[-1],
            decision=decision,
            scope_lineage_id=current_material.lineage_id,
            scope_version_id=(
                current_material.accepted_brief.scope.scope_version.version_id
            ),
            applicability_scope=scope,
        )
        return decision, relationship_result, snapshot, None

    def _assess_root_cause(
        self,
        *,
        session_id: str,
        goal: ResearchQuestion,
        principal: Principal,
        native_session_token: str | None,
        owner_calls: list[str],
    ):
        source_session = self._research.resume_state(
            session_id=session_id,
            principal=principal,
        )
        allowed_evidence_refs = tuple(
            item.evidence_id
            for item in source_session.evidence_refs
            if item.obligation_id == goal.goal_id
        )
        allowed_mechanism_refs, user_seeded = self._root_cause_mechanism_refs(
            goal=goal,
            source_session=source_session,
        )
        last_error = None
        if user_seeded:
            snapshot = self._synthesize_root_candidates(
                session_id=session_id,
                goal=goal,
                principal=principal,
                native_session_token=native_session_token,
                owner_calls=owner_calls,
                mechanism_refs=allowed_mechanism_refs,
                evidence_refs=allowed_evidence_refs,
            )
            observation, claims, _ = self._observe_p17_process(
                snapshot=snapshot,
                session_id=session_id,
                target_obligation_id=goal.goal_id,
                principal=principal,
            )
            next_owner = decide_next_owner(
                ProductProcessPurpose.ROOT_CAUSE,
                observation,
            )
        else:
            scoped_manager = _ObligationScopedProposalManager(
                inner=self._investigation_manager,
                target_parent_obligation=goal.goal_id,
                allowed_evidence_refs=allowed_evidence_refs,
                claim_semantic_contract=ClaimSemanticContract.ROOT_CAUSE_CANDIDATE,
                allowed_mechanism_refs=allowed_mechanism_refs,
            )
            snapshot, next_owner, _, last_error = self._run_p17(
                session_id=session_id,
                principal=principal,
                native_session_token=native_session_token,
                purpose=ProductProcessPurpose.ROOT_CAUSE,
                owner_calls=owner_calls,
                manager=scoped_manager,
                target_obligation_id=goal.goal_id,
            )
            observation, claims, _ = self._observe_p17_process(
                snapshot=snapshot,
                session_id=session_id,
                target_obligation_id=goal.goal_id,
                principal=principal,
            )
        if next_owner != ProductProcessNext.P19:
            return None, snapshot, self._p17_terminal_code(
                snapshot=snapshot,
                last_error=last_error,
            )

        active_mechanism_refs = self._sync_root_candidates_to_p19(
            session_id=session_id,
            goal=goal,
            principal=principal,
            source_session=source_session,
            claims=claims,
        )

        scope_version_id = (
            source_session.accepted_brief.scope.scope_version.version_id
            if source_session.accepted_brief is not None
            else "scope_v1"
        )
        scope_lineage_id = source_session.lineage_id
        feedback_code = None
        assessment = None

        while True:
            p19_snapshot = self._epistemics.snapshot(
                research_session_id=session_id,
                obligation_id=goal.goal_id,
                principal=principal,
            )
            draft = self._epistemic_manager.propose(
                p19_snapshot,
                policy_statuses={},
                deterministic_feedback_code=feedback_code,
            )
            assessment = self._epistemics.assess(
                draft=draft,
                principal=principal,
            )
            owner_calls.append("P19")

            request = next_test_request(
                snapshot=p19_snapshot,
                assessment=assessment,
                scope_lineage_id=scope_lineage_id,
                scope_version_id=scope_version_id,
            )
            if request is None:
                break

            latest = self._investigation.snapshot(
                session_id=session_id,
                principal=principal,
            )
            if not discriminating_test_is_callable(
                snapshot=latest,
                request=request,
                evidence_surface_available=bool(native_session_token),
            ):
                break

            before_evidence = {
                item.evidence_id
                for item in self._research.resume_state(
                    session_id=session_id,
                    principal=principal,
                ).evidence_refs
                if item.obligation_id == goal.goal_id
            }
            step, task = self._investigation.run_one(
                session_id=session_id,
                principal=principal,
                manager=_NextTestProposalManager(
                    request=request,
                    target_parent_obligation=goal.goal_id,
                ),
                native_session_token=native_session_token,
                downstream_reentry_intent=(
                    InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
                ),
            )
            owner_calls.append("P17")

            target_hypotheses = {
                item.hypothesis.hypothesis_id
                for item in p19_snapshot.hypotheses
                if item.hypothesis.hypothesis_id in request.hypothesis_ids
            }
            for hypothesis_id in target_hypotheses:
                self._epistemics.create_grounding(
                    hypothesis_id=hypothesis_id,
                    source_kind=GroundingSourceKind.P17_REASONING_STEP,
                    source_ref=step.step_id,
                    relation=GroundingRelation.CONTEXT,
                    principal=principal,
                )

            current = self._research.resume_state(
                session_id=session_id,
                principal=principal,
            )
            new_evidence = tuple(
                item for item in current.evidence_refs
                if (
                    item.obligation_id == goal.goal_id
                    and item.evidence_id not in before_evidence
                )
            )
            if new_evidence and active_mechanism_refs:
                synthesis_snapshot = self._synthesize_root_candidates(
                    session_id=session_id,
                    goal=goal,
                    principal=principal,
                    native_session_token=native_session_token,
                    owner_calls=owner_calls,
                    mechanism_refs=active_mechanism_refs,
                    evidence_refs=tuple(item.evidence_id for item in new_evidence),
                )
                _, refreshed_claims, _ = self._observe_p17_process(
                    snapshot=synthesis_snapshot,
                    session_id=session_id,
                    target_obligation_id=goal.goal_id,
                    principal=principal,
                )
                active_mechanism_refs = self._sync_root_candidates_to_p19(
                    session_id=session_id,
                    goal=goal,
                    principal=principal,
                    source_session=self._research.resume_state(
                        session_id=session_id,
                        principal=principal,
                    ),
                    claims=refreshed_claims,
                )
            else:
                for hypothesis_id in target_hypotheses:
                    for evidence in new_evidence:
                        self._epistemics.create_grounding(
                            hypothesis_id=hypothesis_id,
                            source_kind=GroundingSourceKind.P14_EVIDENCE,
                            source_ref=evidence.evidence_id,
                            source_receipt_id=evidence.receipt_id,
                            relation=GroundingRelation.CONTEXT,
                            principal=principal,
                        )
            feedback_code = "P19_DISCRIMINATING_TEST_COMPLETED"

        assert assessment is not None
        latest_snapshot = self._investigation.snapshot(
            session_id=session_id,
            principal=principal,
        )
        return assessment, latest_snapshot, None

    def _seal_report(
        self,
        *,
        session_id: str,
        brief: ResearchBrief,
        principal: Principal,
        composition_limitations: tuple[CompositionLimitation, ...],
        owner_calls: list[str],
    ):
        analytical_ids = {item.goal_id for item in brief.questions}
        grouped: dict[str, list[CompositionLimitation]] = {}
        for item in composition_limitations:
            if item.obligation_id in analytical_ids:
                grouped.setdefault(item.obligation_id, []).append(item)

        explicit: list[ReportLimitation] = []
        for obligation_id in tuple(item.goal_id for item in brief.questions):
            items = grouped.get(obligation_id, [])
            if not items:
                continue
            codes = tuple(dict.fromkeys(item.code for item in items))
            details = tuple(dict.fromkeys(item.detail for item in items))
            code = "|".join(codes)
            detail = " ".join(details)
            limitation_id = stable_limitation_id(
                {
                    "session_id": session_id,
                    "obligation_id": obligation_id,
                    "codes": codes,
                    "details": details,
                }
            )
            explicit.append(
                ReportLimitation(
                    limitation_id=limitation_id,
                    obligation_id=obligation_id,
                    code=code,
                    detail=detail,
                    source_refs=(),
                )
            )

        draft = self._reports.draft_from_governed_research(
            research_session_id=session_id,
            report_key="product-composition",
            principal=principal,
            explicit_limitations=tuple(explicit),
        )
        report = self._reports.seal(
            draft=draft,
            principal=principal,
        )
        owner_calls.append("P20")
        return report

    @staticmethod
    def _project_user_must(
        *,
        brief: ResearchBrief,
        session,
        report,
        relationship_results: tuple[RelationshipResultProjection, ...] = (),
        root_cause_assessments: dict[str, Any] | None = None,
    ) -> tuple[tuple[ProductRequirementFulfillment, ...], int, int, int]:
        obligation_map = {item.obligation_id: item for item in session.obligations}
        relationship_by_goal: dict[str, RelationshipResultProjection] = {}
        for result in relationship_results:
            goal_id = str(
                result.applicability_scope.get("accepted_relationship_goal_id") or ""
            ).strip()
            if not goal_id:
                continue
            if goal_id in relationship_by_goal:
                raise ValueError(
                    "multiple governed relationship results target one USER_MUST goal"
                )
            relationship_by_goal[goal_id] = result
        root_cause_by_goal = root_cause_assessments or {}
        projected: list[ProductRequirementFulfillment] = []

        for question in brief.questions:
            obligation = obligation_map.get(question.goal_id)
            raw_state = (
                _state_value(obligation.state)
                if obligation is not None
                else ProductRequirementState.PENDING.value
            )
            fulfilled_by_ref = None
            if question.kind == ResearchGoalKind.ROOT_CAUSE:
                assessment = root_cause_by_goal.get(question.goal_id)
                if (
                    assessment is not None
                    and _state_value(assessment.aggregate_outcome)
                    != "IN_PROGRESS"
                ):
                    state = ProductRequirementState.FULFILLED
                    fulfilled_by_ref = assessment.assessment_id
                elif raw_state == ObligationState.LIMITED.value:
                    state = ProductRequirementState.LIMITED
                else:
                    state = ProductRequirementState.PENDING
            elif question.kind == ResearchGoalKind.RELATIONSHIP:
                relationship = relationship_by_goal.get(question.goal_id)
                if relationship is not None:
                    fulfilled_by_ref = relationship.policy_use_id
                    if (
                        _state_value(relationship.business_relationship_state)
                        == "SATISFIED"
                        and not relationship.limitation_codes
                    ):
                        state = ProductRequirementState.FULFILLED
                    else:
                        state = ProductRequirementState.LIMITED
                elif raw_state == ObligationState.LIMITED.value:
                    state = ProductRequirementState.LIMITED
                else:
                    state = ProductRequirementState.PENDING
            elif raw_state == ObligationState.VERIFIED.value:
                state = ProductRequirementState.VERIFIED
            elif raw_state == ObligationState.LIMITED.value:
                state = ProductRequirementState.LIMITED
            else:
                state = ProductRequirementState.PENDING
            projected.append(
                ProductRequirementFulfillment(
                    requirement_id=question.goal_id,
                    requirement_kind=ProductRequirementKind.ANALYTICAL,
                    state=state,
                    fulfilled_by_ref=fulfilled_by_ref,
                )
            )

        for deliverable in brief.deliverables:
            if deliverable.kind == PresentationKind.REPORT and report is not None:
                state = ProductRequirementState.FULFILLED
                fulfilled_by_ref = report.report_id
            else:
                state = ProductRequirementState.PENDING
                fulfilled_by_ref = None
            projected.append(
                ProductRequirementFulfillment(
                    requirement_id=deliverable.requirement_id,
                    requirement_kind=ProductRequirementKind.DELIVERABLE,
                    state=state,
                    fulfilled_by_ref=fulfilled_by_ref,
                )
            )

        ids = tuple(item.requirement_id for item in projected)
        if ids != tuple(brief.must_requirement_ids):
            raise ValueError(
                "Product USER_MUST projection must preserve exact accepted requirement identity"
            )
        accounted = sum(
            item.state != ProductRequirementState.PENDING
            for item in projected
        )
        fulfilled = sum(
            item.state in {
                ProductRequirementState.VERIFIED,
                ProductRequirementState.FULFILLED,
            }
            for item in projected
        )
        return tuple(projected), len(projected), accounted, fulfilled

    @staticmethod
    def _completion_ledger(
        *,
        brief: ResearchBrief,
        projected: tuple[ProductRequirementFulfillment, ...],
        terminal: ProductCompositionTerminal,
    ) -> ProductCompletionLedger:
        unsupported = {
            item.requirement_id
            for item in brief.deliverables
            if item.kind != PresentationKind.REPORT
        }
        entries: list[ProductRequirementCompletion] = []
        for item in projected:
            if item.state in {
                ProductRequirementState.VERIFIED,
                ProductRequirementState.FULFILLED,
            }:
                disposition = ProductRequirementDisposition.FULFILLED
            elif item.state == ProductRequirementState.LIMITED:
                disposition = ProductRequirementDisposition.LIMITED
            elif item.requirement_id in unsupported:
                disposition = ProductRequirementDisposition.UNSUPPORTED
            elif terminal == ProductCompositionTerminal.INCONCLUSIVE:
                disposition = ProductRequirementDisposition.INCONCLUSIVE
            elif (
                terminal == ProductCompositionTerminal.REPORT
                and any(
                    question.goal_id == item.requirement_id
                    and question.kind
                    in {
                        ResearchGoalKind.RELATIONSHIP,
                        ResearchGoalKind.ROOT_CAUSE,
                    }
                    for question in brief.questions
                )
            ):
                disposition = ProductRequirementDisposition.INCONCLUSIVE
            elif terminal == ProductCompositionTerminal.LIMITED:
                disposition = ProductRequirementDisposition.LIMITED
            else:
                raise ValueError(
                    "trusted Product completion cannot hide a pending USER_MUST requirement"
                )
            entries.append(
                ProductRequirementCompletion(
                    requirement_id=item.requirement_id,
                    disposition=disposition,
                    fulfilled_by_ref=item.fulfilled_by_ref,
                )
            )

        ids = tuple(item.requirement_id for item in entries)
        if ids != tuple(brief.must_requirement_ids):
            raise ValueError(
                "Product Completion Ledger must preserve exact USER_MUST identity"
            )
        process_complete = (
            len(entries) == len(brief.must_requirement_ids)
            and all(
                item.disposition
                in {
                    ProductRequirementDisposition.FULFILLED,
                    ProductRequirementDisposition.LIMITED,
                    ProductRequirementDisposition.UNSUPPORTED,
                    ProductRequirementDisposition.INCONCLUSIVE,
                }
                for item in entries
            )
        )
        requirement_complete = (
            process_complete
            and all(
                item.disposition == ProductRequirementDisposition.FULFILLED
                for item in entries
            )
        )
        return ProductCompletionLedger(
            entries=tuple(entries),
            process_complete=process_complete,
            requirement_complete=requirement_complete,
            trusted_complete=process_complete,
        )

    def compose(
        self,
        *,
        brief: ResearchBrief,
        principal: Principal,
        request_ref: str,
        source_message_hash: str,
        native_session_token: str | None,
        investigation_requirements: (
            tuple[ProductInvestigationRequirement, ...] | None
        ) = None,
        prior_research_session_id: str | None = None,
    ) -> ProductCompositionResult:
        if brief.status != ResearchBriefStatus.READY_FOR_RESEARCH:
            raise ValueError("Product Composition requires accepted READY ResearchBrief")

        owner_calls: list[str] = []
        child_sessions: list[str] = []
        p17_refs: list[str] = []
        p18_refs: list[str] = []
        p19_refs: list[str] = []
        root_cause_assessments: dict[str, Any] = {}
        root_cause_complete_goal_ids: set[str] = set()
        root_cause_modes: list[RootCauseModeResult] = []
        relationship_results: list[RelationshipResultProjection] = []
        limitations: list[CompositionLimitation] = []
        p17_required: list[str] = []
        fulfilled_investigation_requirements: list[str] = []
        correlated_evidence_refs: list[str] = []
        limitation_codes: dict[str, str] = {}

        start_kwargs = {
            "brief": brief,
            "request_ref": request_ref,
            "source_message_hash": source_message_hash,
            "principal": principal,
        }
        if prior_research_session_id is not None:
            start_kwargs["prior_session_id"] = prior_research_session_id
        session = self._research.start_from_brief(**start_kwargs)
        owner_calls.append("P14")
        accepted_investigation_requirements = (
            tuple(investigation_requirements)
            if investigation_requirements is not None
            else ()
        )
        if self._investigation_requirements is not None:
            if investigation_requirements is not None:
                self._investigation_requirements.persist(
                    tenant_binding=session.tenant_binding,
                    research_session_id=session.session_id,
                    brief_id=brief.brief_id,
                    requirements=accepted_investigation_requirements,
                    accepted_goal_ids=tuple(
                        question.goal_id for question in brief.questions
                    ),
                )
            accepted_investigation_requirements = (
                self._investigation_requirements.load(
                    tenant_binding=session.tenant_binding,
                    research_session_id=session.session_id,
                )
            )
        execution_mode = classify_execution_mode(
            brief,
            investigation_requirements=accepted_investigation_requirements,
        ).mode

        goal_by_id = _question_map(brief)
        material_requirements = coorigin_material_requirements(session)
        deferred_relationship_ids = frozenset(
            goal_id
            for requirement in material_requirements
            for goal_id in requirement.source_goal_ids
            if (
                goal_id != requirement.anchor_goal_id
                and goal_by_id[goal_id].kind == ResearchGoalKind.RELATIONSHIP
            )
        )
        owner_calls.append("P14")
        session = self._run_p14(
            research=self._research,
            session_id=session.session_id,
            brief=brief,
            principal=principal,
            native_session_token=native_session_token,
            owner_calls=owner_calls,
            skip_obligation_ids=deferred_relationship_ids,
        )

        for goal in brief.questions:
            state = next(
                (
                    _state_value(item.state)
                    for item in session.obligations
                    if item.obligation_id == goal.goal_id
                ),
                "UNKNOWN",
            )
            needs_investigation = goal.kind in {
                ResearchGoalKind.RELATIONSHIP,
                ResearchGoalKind.ROOT_CAUSE,
            }
            if needs_investigation:
                p17_required.append(goal.goal_id)

            if goal.kind == ResearchGoalKind.RELATIONSHIP:
                # Relationship authority consumes either the one canonical co-origin
                # material anchor or its existing direct P14 material path. Accepted
                # relationship semantics are never rewritten into the anchor goal.
                material_session_id = session.session_id
                material_requirement = self._relationship_material_requirement(
                    requirements=material_requirements,
                    goal=goal,
                )
                if material_requirement is not None:
                    material_goal = goal_by_id[material_requirement.anchor_goal_id]
                    current = self._research.resume_state(
                        session_id=session.session_id,
                        principal=principal,
                    )
                    material_state = next(
                        (
                            _state_value(item.state)
                            for item in current.obligations
                            if item.obligation_id == material_goal.goal_id
                        ),
                        "UNKNOWN",
                    )
                    if material_state != ObligationState.VERIFIED.value:
                        code = "PRODUCT_COORIGIN_MATERIAL_NOT_VERIFIED"
                        limitation_codes[goal.goal_id] = code
                        limitations.append(
                            CompositionLimitation(
                                obligation_id=goal.goal_id,
                                code=code,
                                detail=(
                                    "Canonical co-origin analytical material did not "
                                    "reach VERIFIED; duplicate relationship acquisition "
                                    "was not opened."
                                ),
                                owner="PRODUCT",
                            )
                        )
                        continue
                else:
                    current = self._research.resume_state(
                        session_id=session.session_id,
                        principal=principal,
                    )
                    match = next(
                        (
                            item
                            for item in current.obligations
                            if item.obligation_id == goal.goal_id
                        ),
                        None,
                    )
                    if (
                        match is not None
                        and _state_value(match.state)
                        not in {"VERIFIED", "LIMITED", "FAILED"}
                    ):
                        self._research.run_next(
                            session_id=session.session_id,
                            principal=principal,
                            obligation_id=goal.goal_id,
                            native_session_token=native_session_token,
                        )
                        owner_calls.append("P14")
                    session = self._research.resume_state(
                        session_id=session.session_id,
                        principal=principal,
                    )
                    material_goal = goal
                decision, relationship_result, p17_snapshot, error = self._resolve_relationship(
                    original_goal=goal,
                    material_session_id=material_session_id,
                    material_goal=material_goal,
                    principal=principal,
                    native_session_token=native_session_token,
                    owner_calls=owner_calls,
                )
                p17_refs.extend(p17_snapshot.completed_reasoning_steps)
                if decision is None:
                    code = error or "PRODUCT_RELATIONSHIP_INCONCLUSIVE"
                else:
                    p18_refs.append(decision.policy_use_id)
                    if relationship_result is not None:
                        relationship_results.append(relationship_result)
                    code = (
                        decision.limitation_code
                        or f"P18_{decision.resolution_status.value}"
                    )
                limitation_codes[goal.goal_id] = code
                if decision is None or decision.limitation_code:
                    limitations.append(
                        CompositionLimitation(
                            obligation_id=goal.goal_id,
                            code=code,
                            detail=(
                                "Relationship authority reached a governed "
                                "limited terminal."
                            ),
                            owner="P18",
                        )
                    )
                continue

            if goal.kind == ResearchGoalKind.ROOT_CAUSE:
                assessment, p17_snapshot, error = self._assess_root_cause(
                    session_id=session.session_id,
                    goal=goal,
                    principal=principal,
                    native_session_token=native_session_token,
                    owner_calls=owner_calls,
                )
                p17_refs.extend(p17_snapshot.completed_reasoning_steps)
                if assessment is None:
                    code = error or "PRODUCT_P19_INCONCLUSIVE"
                    limitation_codes[goal.goal_id] = code
                    limitations.append(
                        CompositionLimitation(
                            obligation_id=goal.goal_id,
                            code=code,
                            detail="P19 did not receive enough governed competing hypotheses.",
                            owner="P19",
                        )
                    )
                else:
                    p19_refs.append(assessment.assessment_id)
                    root_cause_assessments[goal.goal_id] = assessment
                    if _state_value(assessment.aggregate_outcome) != "IN_PROGRESS":
                        root_cause_complete_goal_ids.add(goal.goal_id)
                    goal_steps = tuple(
                        step
                        for step in self._reasoning.steps(session.session_id)
                        if step.parent_obligation_id == goal.goal_id
                    )
                    analytical_reentry_count = sum(
                        _state_value(getattr(step, "action", ""))
                        in {
                            ManagerAction.EXPLORE_NATIVE.value,
                            ManagerAction.SEEK_COUNTER_EVIDENCE.value,
                        }
                        for step in goal_steps
                    )
                    surface = goal.causal_competition
                    root_cause_modes.append(
                        RootCauseModeResult(
                            obligation_id=goal.goal_id,
                            mode=_root_cause_execution_mode(
                                aggregate_outcome=assessment.aggregate_outcome,
                                analytical_reentry_count=analytical_reentry_count,
                            ),
                            assessment_ref=assessment.assessment_id,
                            user_seeded_candidates=bool(
                                surface is not None
                                and surface.candidate_mechanism_semantic_ids
                            ),
                            analytical_reentry_count=analytical_reentry_count,
                        )
                    )
                    limitation_codes[goal.goal_id] = assessment.aggregate_outcome.value
                    if assessment.limitations:
                        limitations.append(
                            CompositionLimitation(
                                obligation_id=goal.goal_id,
                                code=assessment.aggregate_outcome.value,
                                detail="P19 preserved an explicit epistemic limitation.",
                                owner="P19",
                            )
                        )
                continue

        for requirement in accepted_investigation_requirements:
            if (
                requirement.kind
                != ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL
            ):
                raise ValueError(
                    "unsupported Core-B investigation requirement kind"
                )
            source_goal = goal_by_id.get(requirement.source_goal_id)
            if source_goal is None:
                raise ValueError(
                    "Core-B investigation requirement references unknown goal"
                )
            p17_required.append(source_goal.goal_id)
            source_state = next(
                (
                    _state_value(item.state)
                    for item in session.obligations
                    if item.obligation_id == source_goal.goal_id
                ),
                "UNKNOWN",
            )
            if source_state != ObligationState.VERIFIED.value:
                code = "PRODUCT_ADAPTIVE_SOURCE_NOT_VERIFIED"
                limitation_codes[source_goal.goal_id] = code
                limitations.append(
                    CompositionLimitation(
                        obligation_id=source_goal.goal_id,
                        code=code,
                        detail=(
                            "Adaptive investigation was not opened because its "
                            "exact analytical source obligation was not VERIFIED."
                        ),
                        owner="PRODUCT",
                    )
                )
                continue

            current_session = self._research.resume_state(
                session_id=session.session_id,
                principal=principal,
            )
            source_evidence_refs = tuple(
                item.evidence_id
                for item in current_session.evidence_refs
                if item.obligation_id == source_goal.goal_id
            )
            scoped_manager = _ObligationScopedProposalManager(
                inner=self._investigation_manager,
                target_parent_obligation=source_goal.goal_id,
                allowed_evidence_refs=source_evidence_refs,
            )
            p17_snapshot, next_owner, _, error = self._run_p17(
                session_id=session.session_id,
                principal=principal,
                native_session_token=native_session_token,
                purpose=ProductProcessPurpose.ADAPTIVE_INVESTIGATION,
                owner_calls=owner_calls,
                manager=scoped_manager,
                target_obligation_id=source_goal.goal_id,
            )
            scoped_step_ids = {
                step.step_id
                for step in self._reasoning.steps(session.session_id)
                if step.parent_obligation_id == source_goal.goal_id
            }
            scoped_terminal_refs = tuple(
                step_id
                for step_id in p17_snapshot.completed_reasoning_steps
                if step_id in scoped_step_ids
            )
            p17_refs.extend(scoped_terminal_refs)
            if (
                next_owner == ProductProcessNext.COMPLETE
                and scoped_terminal_refs
            ):
                fulfilled_investigation_requirements.append(
                    requirement.requirement_id
                )
            else:
                code = (
                    getattr(error, "code", None)
                    or "PRODUCT_P17_INCONCLUSIVE"
                )
                limitation_codes[source_goal.goal_id] = str(code)
                limitations.append(
                    CompositionLimitation(
                        obligation_id=source_goal.goal_id,
                        code=str(code),
                        detail=(
                            "P17 did not reach a governed terminal for the "
                            "typed adaptive investigation requirement."
                        ),
                        owner="P17",
                    )
                )

        report_requested = any(
            item.kind == PresentationKind.REPORT
            for item in brief.deliverables
        )
        report = None
        if report_requested:
            report = self._seal_report(
                session_id=session.session_id,
                brief=brief,
                principal=principal,
                composition_limitations=tuple(limitations),
                owner_calls=owner_calls,
            )

        current = self._research.resume_state(
            session_id=session.session_id,
            principal=principal,
        )
        evidence_refs = tuple(
            dict.fromkeys(
                (
                    *(item.evidence_id for item in current.evidence_refs),
                    *correlated_evidence_refs,
                )
            )
        )
        p17_refs = list(dict.fromkeys(p17_refs))
        p18_refs = list(dict.fromkeys(p18_refs))
        p19_refs = list(dict.fromkeys(p19_refs))
        p17_required = list(dict.fromkeys(p17_required))

        adaptive_incomplete = (
            bool(accepted_investigation_requirements)
            and set(fulfilled_investigation_requirements)
            != {
                item.requirement_id
                for item in accepted_investigation_requirements
            }
        )
        relationship_goal_ids = {
            goal.goal_id
            for goal in brief.questions
            if goal.kind == ResearchGoalKind.RELATIONSHIP
        }
        root_cause_goal_ids = {
            goal.goal_id
            for goal in brief.questions
            if goal.kind == ResearchGoalKind.ROOT_CAUSE
        }
        relationship_completed_goal_ids = {
            str(
                result.applicability_scope.get(
                    "accepted_relationship_goal_id"
                )
                or ""
            )
            for result in relationship_results
        }
        advanced_incomplete = bool(
            relationship_goal_ids - relationship_completed_goal_ids
        ) or bool(
            root_cause_goal_ids - root_cause_complete_goal_ids
        ) or adaptive_incomplete

        if report is not None:
            terminal = ProductCompositionTerminal.REPORT
        elif advanced_incomplete:
            terminal = ProductCompositionTerminal.INCONCLUSIVE
        elif evidence_refs:
            terminal = ProductCompositionTerminal.ANSWER
        else:
            terminal = ProductCompositionTerminal.LIMITED

        user_must, user_must_total, user_must_accounted, user_must_fulfilled = (
            self._project_user_must(
                brief=brief,
                session=current,
                report=report,
                relationship_results=tuple(relationship_results),
                root_cause_assessments=root_cause_assessments,
            )
        )

        completion_ledger = self._completion_ledger(
            brief=brief,
            projected=user_must,
            terminal=terminal,
        )

        return ProductCompositionResult(
            research_session_id=session.session_id,
            child_research_session_ids=tuple(child_sessions),
            p17_step_refs=tuple(p17_refs),
            p18_policy_use_refs=tuple(p18_refs),
            p19_assessment_refs=tuple(p19_refs),
            root_cause_mode_results=tuple(root_cause_modes),
            p20_report_ref=(report.report_id if report is not None else None),
            evidence_refs=evidence_refs,
            limitations=tuple(limitations),
            owner_calls=tuple(owner_calls),
            p17_required_goal_ids=tuple(p17_required),
            investigation_requirement_ids=tuple(
                item.requirement_id
                for item in accepted_investigation_requirements
            ),
            fulfilled_investigation_requirement_ids=tuple(
                dict.fromkeys(fulfilled_investigation_requirements)
            ),
            user_must_fulfillment=user_must,
            user_must_total=user_must_total,
            user_must_accounted=user_must_accounted,
            user_must_fulfilled=user_must_fulfilled,
            completion_ledger=completion_ledger,
            execution_mode=execution_mode,
            relationship_results=tuple(relationship_results),
            terminal_state=terminal,
        )
