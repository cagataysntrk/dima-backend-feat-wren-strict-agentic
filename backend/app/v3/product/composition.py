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

from app.v3.business_relationship_policy import (
    BusinessRelationshipPolicyStore,
    RelationshipPolicyRequirement,
)
from app.v3.hypothesis_root_cause import (
    GroundingRelation,
    GroundingSourceKind,
    HypothesisRootCauseStore,
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
from app.v3.research_contracts import (
    ComparisonSurface,
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    SemanticTargetKind,
)
from app.v3.research_manager import (
    ResearchInvestigationManager,
    ResearchManagerMaturationError,
    ResearchReasoningStore,
)
from app.v3.research_product import ResearchAskOrchestrator


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProductCompositionTerminal(StrEnum):
    ANSWER = "ANSWER"
    REPORT = "REPORT"
    DECISION = "DECISION"
    LIMITED = "LIMITED"
    INCONCLUSIVE = "INCONCLUSIVE"


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
    p20_report_ref: str | None = None
    p21_decision_ref: str | None = None
    evidence_refs: tuple[str, ...] = ()
    limitations: tuple[CompositionLimitation, ...] = ()
    owner_calls: tuple[str, ...] = ()
    p17_required_goal_ids: tuple[str, ...] = ()
    user_must_fulfillment: tuple[ProductRequirementFulfillment, ...] = ()
    user_must_total: int = 0
    user_must_accounted: int = 0
    user_must_fulfilled: int = 0
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
    ) -> None:
        self._research = research
        self._investigation = investigation
        self._investigation_manager = investigation_manager
        self._reasoning = reasoning
        self._relationships = relationships
        self._epistemics = epistemics
        self._epistemic_manager = epistemic_manager
        self._reports = reports

    @staticmethod
    def _run_p14(
        *,
        research: ResearchAskOrchestrator,
        session_id: str,
        brief: ResearchBrief,
        principal: Principal,
        native_session_token: str | None,
        owner_calls: list[str],
    ):
        for question in brief.questions:
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
    def _relationship_material_brief(
        *,
        parent_session_id: str,
        parent: ResearchBrief,
        goal: ResearchQuestion,
    ) -> ResearchBrief:
        refs = tuple(dict.fromkeys((*goal.subject_refs, *goal.related_refs)))
        measures = tuple(
            item for item in refs
            if item.target_kind
            in {
                SemanticTargetKind.METRIC,
                SemanticTargetKind.KPI,
            }
        )
        dimensions = tuple(
            item for item in refs
            if item.target_kind == SemanticTargetKind.DIMENSION
        )
        if len(measures) < 2:
            raise ValueError(
                "relationship material requires at least two governed measure refs"
            )

        names = " and ".join(item.canonical_name for item in measures)
        if dimensions:
            dimension_names = ", ".join(item.canonical_name for item in dimensions)
            source_text = (
                f"Compare {names} by {dimension_names}. "
                "Return governed analytical material only; do not claim causality."
            )
        else:
            source_text = (
                f"Compare {names}. Return governed analytical material only; "
                "do not claim causality."
            )

        seed = {
            "parent_session_id": parent_session_id,
            "goal_id": goal.goal_id,
            "refs": [item.candidate_id for item in refs],
        }
        child_goal_id = _stable("gpc_", seed)
        child_goal = ResearchQuestion(
            goal_id=child_goal_id,
            kind=ResearchGoalKind.COMPARISON,
            source_text=source_text,
            subject_refs=measures,
            related_refs=dimensions,
            comparisons=(
                ComparisonSurface(
                    text="Governed comparative material for relationship policy evaluation."
                ),
            ),
            status=ResearchGoalStatus.RESOLVED,
        )
        return ResearchBrief(
            brief_id=_stable("rbpc_", seed, 24),
            objective=source_text,
            scope=ResearchScope(semantic_refs=refs),
            required_domains=parent.required_domains,
            questions=(child_goal,),
            deliverables=(),
            must_requirement_ids=(child_goal_id,),
            blocking_goal_ids=(),
            context_version=parent.context_version,
            status=ResearchBriefStatus.READY_FOR_RESEARCH,
        )

    def _material_session_for_relationship(
        self,
        *,
        parent_session_id: str,
        brief: ResearchBrief,
        goal: ResearchQuestion,
        principal: Principal,
        native_session_token: str | None,
        owner_calls: list[str],
    ) -> tuple[str, ResearchQuestion]:
        child = self._relationship_material_brief(
            parent_session_id=parent_session_id,
            parent=brief,
            goal=goal,
        )
        source_hash = hashlib.sha256(
            _canonical(child.model_dump(mode="json")).encode("utf-8")
        ).hexdigest()
        session = self._research.start_from_brief(
            brief=child,
            request_ref=(
                f"product-composition:{parent_session_id}:{goal.goal_id}:relationship-material"
            ),
            source_message_hash=source_hash,
            principal=principal,
        )
        owner_calls.append("P14")
        final = self._run_p14(
            research=self._research,
            session_id=session.session_id,
            brief=child,
            principal=principal,
            native_session_token=native_session_token,
            owner_calls=owner_calls,
        )
        child_goal = child.questions[0]
        match = next(
            item for item in final.obligations
            if item.obligation_id == child_goal.goal_id
        )
        if _state_value(match.state) != ObligationState.VERIFIED.value:
            raise RuntimeError(
                "relationship comparison material did not reach VERIFIED P14 state"
            )
        return final.session_id, child_goal

    def _run_p17(
        self,
        *,
        session_id: str,
        principal: Principal,
        native_session_token: str | None,
        minimum_claims: int,
        owner_calls: list[str],
        max_turns: int = 4,
    ):
        executed = 0
        last_error: Exception | None = None
        for _ in range(max_turns):
            snapshot = self._investigation.snapshot(
                session_id=session_id,
                principal=principal,
            )
            if (
                len(snapshot.completed_reasoning_steps) >= 1
                and len(snapshot.claims) >= minimum_claims
            ):
                return snapshot, executed, last_error
            if snapshot.terminal_stop_reason is not None:
                return snapshot, executed, last_error
            try:
                self._investigation.run_one(
                    session_id=session_id,
                    principal=principal,
                    manager=self._investigation_manager,
                    native_session_token=native_session_token,
                )
                owner_calls.append("P17")
                executed += 1
            except ResearchManagerMaturationError as exc:
                last_error = exc
                if exc.code == "P17_INVESTIGATION_TERMINAL":
                    break
                raise
        return (
            self._investigation.snapshot(
                session_id=session_id,
                principal=principal,
            ),
            executed,
            last_error,
        )

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
        snapshot, _, _ = self._run_p17(
            session_id=material_session_id,
            principal=principal,
            native_session_token=native_session_token,
            minimum_claims=1,
            owner_calls=owner_calls,
        )
        claims = tuple(
            item for item in snapshot.claims
            if item.obligation_id == material_goal.goal_id
        )
        steps = tuple(
            item for item in self._reasoning.steps(material_session_id)
            if item.parent_obligation_id == material_goal.goal_id
        )
        if not claims or not steps:
            return None, snapshot, "PRODUCT_RELATIONSHIP_LINEAGE_INCOMPLETE"

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
        return decision, snapshot, None

    def _assess_root_cause(
        self,
        *,
        session_id: str,
        goal: ResearchQuestion,
        principal: Principal,
        native_session_token: str | None,
        owner_calls: list[str],
    ):
        snapshot, _, _ = self._run_p17(
            session_id=session_id,
            principal=principal,
            native_session_token=native_session_token,
            minimum_claims=2,
            owner_calls=owner_calls,
        )
        claims = tuple(
            item for item in snapshot.claims
            if item.obligation_id == goal.goal_id
        )
        if len(claims) < 2:
            return None, snapshot, "PRODUCT_P19_COMPETING_HYPOTHESES_INCOMPLETE"

        for claim in claims:
            hypothesis = self._epistemics.create_hypothesis(
                research_session_id=session_id,
                obligation_id=goal.goal_id,
                statement=claim.claim_text,
                principal=principal,
            )
            self._epistemics.create_grounding(
                hypothesis_id=hypothesis.hypothesis_id,
                source_kind=GroundingSourceKind.P16_CLAIM,
                source_ref=claim.claim_id,
                relation=GroundingRelation.CONTEXT,
                principal=principal,
            )
        p19_snapshot = self._epistemics.snapshot(
            research_session_id=session_id,
            obligation_id=goal.goal_id,
            principal=principal,
        )
        draft = self._epistemic_manager.propose(
            p19_snapshot,
            policy_statuses={},
        )
        assessment = self._epistemics.assess(
            draft=draft,
            principal=principal,
        )
        owner_calls.append("P19")
        return assessment, snapshot, None

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
    ) -> tuple[tuple[ProductRequirementFulfillment, ...], int, int, int]:
        obligation_map = {item.obligation_id: item for item in session.obligations}
        projected: list[ProductRequirementFulfillment] = []

        for question in brief.questions:
            obligation = obligation_map.get(question.goal_id)
            raw_state = (
                _state_value(obligation.state)
                if obligation is not None
                else ProductRequirementState.PENDING.value
            )
            if raw_state == ObligationState.VERIFIED.value:
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

    def compose(
        self,
        *,
        brief: ResearchBrief,
        principal: Principal,
        request_ref: str,
        source_message_hash: str,
        native_session_token: str | None,
    ) -> ProductCompositionResult:
        if brief.status != ResearchBriefStatus.READY_FOR_RESEARCH:
            raise ValueError("Product Composition requires accepted READY ResearchBrief")

        owner_calls: list[str] = []
        child_sessions: list[str] = []
        p17_refs: list[str] = []
        p18_refs: list[str] = []
        p19_refs: list[str] = []
        limitations: list[CompositionLimitation] = []
        p17_required: list[str] = []
        correlated_evidence_refs: list[str] = []
        limitation_codes: dict[str, str] = {}

        session = self._research.start_from_brief(
            brief=brief,
            request_ref=request_ref,
            source_message_hash=source_message_hash,
            principal=principal,
        )
        owner_calls.append("P14")
        session = self._run_p14(
            research=self._research,
            session_id=session.session_id,
            brief=brief,
            principal=principal,
            native_session_token=native_session_token,
            owner_calls=owner_calls,
        )

        goal_by_id = _question_map(brief)
        verified_exists = any(
            _state_value(item.state) == ObligationState.VERIFIED.value
            for item in session.obligations
            if item.obligation_id in goal_by_id
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
            needs_investigation = (
                goal.kind in {
                    ResearchGoalKind.RELATIONSHIP,
                    ResearchGoalKind.ROOT_CAUSE,
                }
                or (
                    verified_exists
                    and state != ObligationState.VERIFIED.value
                )
            )
            if needs_investigation:
                p17_required.append(goal.goal_id)

            if goal.kind == ResearchGoalKind.RELATIONSHIP:
                try:
                    material_session_id, material_goal = (
                        self._material_session_for_relationship(
                            parent_session_id=session.session_id,
                            brief=brief,
                            goal=goal,
                            principal=principal,
                            native_session_token=native_session_token,
                            owner_calls=owner_calls,
                        )
                    )
                    child_sessions.append(material_session_id)
                    material_session = self._research.resume_state(
                        session_id=material_session_id,
                        principal=principal,
                    )
                    correlated_evidence_refs.extend(
                        item.evidence_id for item in material_session.evidence_refs
                    )
                    decision, p17_snapshot, error = self._resolve_relationship(
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
                                detail="Relationship authority reached a governed limited terminal.",
                                owner="P18",
                            )
                        )
                except (RuntimeError, ValueError) as exc:
                    code = getattr(
                        exc,
                        "code",
                        "PRODUCT_RELATIONSHIP_COMPOSITION_INCONCLUSIVE",
                    )
                    limitation_codes[goal.goal_id] = str(code)
                    limitations.append(
                        CompositionLimitation(
                            obligation_id=goal.goal_id,
                            code=str(code),
                            detail="Relationship composition did not reach a publishable governed terminal.",
                            owner="PRODUCT",
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

            if needs_investigation:
                p17_snapshot, _, error = self._run_p17(
                    session_id=session.session_id,
                    principal=principal,
                    native_session_token=native_session_token,
                    minimum_claims=0,
                    owner_calls=owner_calls,
                )
                p17_refs.extend(p17_snapshot.completed_reasoning_steps)
                if not p17_snapshot.completed_reasoning_steps:
                    code = (
                        getattr(error, "code", None)
                        or "PRODUCT_P17_INCONCLUSIVE"
                    )
                    limitation_codes[goal.goal_id] = str(code)
                    limitations.append(
                        CompositionLimitation(
                            obligation_id=goal.goal_id,
                            code=str(code),
                            detail="P17 bounded investigation reached no completed reasoning step.",
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

        advanced_incomplete = (
            any(
                goal.kind == ResearchGoalKind.RELATIONSHIP
                for goal in brief.questions
            )
            and not p18_refs
        ) or (
            any(
                goal.kind == ResearchGoalKind.ROOT_CAUSE
                for goal in brief.questions
            )
            and not p19_refs
        ) or (
            bool(p17_required) and not p17_refs
        )

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
            )
        )

        return ProductCompositionResult(
            research_session_id=session.session_id,
            child_research_session_ids=tuple(child_sessions),
            p17_step_refs=tuple(p17_refs),
            p18_policy_use_refs=tuple(p18_refs),
            p19_assessment_refs=tuple(p19_refs),
            p20_report_ref=(report.report_id if report is not None else None),
            evidence_refs=evidence_refs,
            limitations=tuple(limitations),
            owner_calls=tuple(owner_calls),
            p17_required_goal_ids=tuple(p17_required),
            user_must_fulfillment=user_must,
            user_must_total=user_must_total,
            user_must_accounted=user_must_accounted,
            user_must_fulfilled=user_must_fulfilled,
            terminal_state=terminal,
        )
