"""P17 durable Research investigation manager.

P17 owns bounded investigation reasoning and restart durability only. Metabase/Metabot
remain the analytical owners; P14/P15/P16 remain sealed authorities for execution,
Research material, and claim/Evidence epistemics.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.analytical_request_contract import (
    AnalyticalRequestContract,
    AnalyticalRequestMismatch,
    assert_child_request_scope,
)
from app.v3.claim_lineage import (
    ClaimEvidenceRelation,
    ClaimFreshness,
    ClaimLineageStore,
)
from app.v3.research import ObligationState, ResearchManager, ResearchSession, ResearchStateError
from app.v3.research_analytical_scope import analytical_scope_contract
from app.v3.root_cause_candidate_contract import (
    RootCauseCandidateRelation,
    RootCauseCandidateSemantics,
    embed_root_cause_candidate_semantics,
)
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import (
    ResearchClaimRecord,
    ResearchExecutionLink,
    ResearchExplorationMaterial,
    ResearchInvestigationTaskRecord,
    ResearchReasoningStepRecord,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchManagerMaturationError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ManagerAction(StrEnum):
    RECORD_INVESTIGATION = "RECORD_INVESTIGATION"
    EXPLORE_NATIVE = "EXPLORE_NATIVE"
    FORM_CLAIM = "FORM_CLAIM"
    SEEK_COUNTER_EVIDENCE = "SEEK_COUNTER_EVIDENCE"
    STOP = "STOP"


class InvestigationIntent(StrEnum):
    """Investigation semantics; these are never analytical operators."""

    LEGACY = "LEGACY"
    INVESTIGATE_GAP = "INVESTIGATE_GAP"
    EXPLORE_ALTERNATIVES = "EXPLORE_ALTERNATIVES"
    SEEK_COUNTER_EVIDENCE = "SEEK_COUNTER_EVIDENCE"
    DEEPEN_EXPLANATION = "DEEPEN_EXPLANATION"
    TEST_DISCRIMINATING_EVIDENCE = "TEST_DISCRIMINATING_EVIDENCE"
    REPLAN = "REPLAN"
    FORM_CLAIM = "FORM_CLAIM"
    STOP_BRANCH = "STOP_BRANCH"
    STOP_INVESTIGATION = "STOP_INVESTIGATION"


class InvestigationTargetKind(StrEnum):
    QUESTION = "QUESTION"
    GAP = "GAP"
    CLAIM = "CLAIM"
    EFFECT = "EFFECT"
    EXPLANATION = "EXPLANATION"
    ALTERNATIVE = "ALTERNATIVE"


class StopScope(StrEnum):
    BRANCH = "BRANCH"
    INVESTIGATION = "INVESTIGATION"


class ManagerStopReason(StrEnum):
    OBJECTIVE_SATISFIED = "OBJECTIVE_SATISFIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    NO_PROGRESS = "NO_PROGRESS"
    BLOCKED = "BLOCKED"
    NO_NEW_EVIDENCE = "NO_NEW_EVIDENCE"
    NO_MEANINGFUL_GAIN = "NO_MEANINGFUL_GAIN"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    CONTRADICTED = "CONTRADICTED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    ROOT_EXTERNAL_TO_AVAILABLE_DATA = "ROOT_EXTERNAL_TO_AVAILABLE_DATA"
    CAUSAL_IDENTIFICATION_LIMIT = "CAUSAL_IDENTIFICATION_LIMIT"


class ClaimSemanticContract(StrEnum):
    ROOT_CAUSE_CANDIDATE = "ROOT_CAUSE_CANDIDATE"


class ReasoningStepStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    NO_PROGRESS = "NO_PROGRESS"


class InvestigationTaskStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    LIMITED = "LIMITED"


class ResearchReasoningBudget(Frozen):
    max_reasoning_steps: int = Field(default=8, ge=1, le=64)
    max_followup_native_turns: int = Field(default=4, ge=0, le=32)
    max_counter_evidence_attempts: int = Field(default=2, ge=0, le=16)
    # V1 contract depth is one-based: persisted root depth 0 == contract depth 1.
    max_depth: int = Field(default=3, ge=1, le=3)


class ProposedClaimEvidenceLink(Frozen):
    evidence_id: str = Field(min_length=1)
    relation: ClaimEvidenceRelation


class ProposedClaimDraft(Frozen):
    claim_text: str = Field(min_length=1)
    proposition: dict[str, Any]
    scope: dict[str, Any]
    freshness: ClaimFreshness
    origin_material_refs: tuple[str, ...] = ()
    evidence_links: tuple[ProposedClaimEvidenceLink, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def structured(self):
        if not self.proposition:
            raise ValueError("FORM_CLAIM requires a structured proposition")
        if not self.scope:
            raise ValueError("FORM_CLAIM requires an explicit scope")
        evidence_ids = [item.evidence_id for item in self.evidence_links]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("FORM_CLAIM Evidence links must be unique")
        return self


class ManagerProposal(Frozen):
    proposal_id: str = Field(min_length=1, max_length=160)
    source_revision: int = Field(ge=1)
    target_parent_obligation: str = Field(min_length=1)
    action: ManagerAction
    intent: InvestigationIntent | None = None
    parent_step_id: str | None = Field(
        default=None,
        pattern=r"^rrs_[a-f0-9]{24}$",
    )
    branch_key: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$",
    )
    target_kind: InvestigationTargetKind = InvestigationTargetKind.GAP
    target_ref: str | None = Field(default=None, max_length=512)
    # Stable manager-supplied identity for the bounded investigative target.
    # This, rather than free-form prose, participates in no-progress identity.
    objective_key: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
    bounded_objective: str | None = Field(default=None, max_length=2000)
    rationale: str = Field(min_length=1, max_length=4000)
    inspected_evidence_refs: tuple[str, ...] = ()
    inspected_claim_refs: tuple[str, ...] = ()
    inspected_material_refs: tuple[str, ...] = ()
    expected_information_gain: str | None = Field(default=None, max_length=2000)
    stop_reason: ManagerStopReason | None = None
    counter_to_claim_id: str | None = None
    claim: ProposedClaimDraft | None = None
    mechanism_semantic_ref: str | None = Field(default=None, max_length=512)
    claim_semantic_contract: ClaimSemanticContract | None = None
    child_analytical_scope: AnalyticalRequestContract | None = None

    @property
    def effective_intent(self) -> InvestigationIntent:
        if self.intent is not None:
            return self.intent
        return {
            ManagerAction.RECORD_INVESTIGATION: InvestigationIntent.REPLAN,
            ManagerAction.EXPLORE_NATIVE: InvestigationIntent.INVESTIGATE_GAP,
            ManagerAction.FORM_CLAIM: InvestigationIntent.FORM_CLAIM,
            ManagerAction.SEEK_COUNTER_EVIDENCE: (
                InvestigationIntent.SEEK_COUNTER_EVIDENCE
            ),
            ManagerAction.STOP: InvestigationIntent.STOP_INVESTIGATION,
        }[self.action]

    @model_validator(mode="after")
    def coherent(self):
        intent = self.effective_intent
        compatible = {
            ManagerAction.RECORD_INVESTIGATION: {
                InvestigationIntent.EXPLORE_ALTERNATIVES,
                InvestigationIntent.DEEPEN_EXPLANATION,
                InvestigationIntent.REPLAN,
            },
            ManagerAction.EXPLORE_NATIVE: {
                InvestigationIntent.INVESTIGATE_GAP,
                InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            },
            ManagerAction.FORM_CLAIM: {InvestigationIntent.FORM_CLAIM},
            ManagerAction.SEEK_COUNTER_EVIDENCE: {
                InvestigationIntent.SEEK_COUNTER_EVIDENCE
            },
            ManagerAction.STOP: {
                InvestigationIntent.STOP_BRANCH,
                InvestigationIntent.STOP_INVESTIGATION,
            },
        }
        if intent not in compatible[self.action]:
            raise ValueError(
                f"{intent.value} is incompatible with {self.action.value}"
            )
        for name, refs in (
            ("Evidence", self.inspected_evidence_refs),
            ("claim", self.inspected_claim_refs),
            ("material", self.inspected_material_refs),
        ):
            if len(refs) != len(set(refs)):
                raise ValueError(f"{name} refs must be unique")

        if (
            self.claim_semantic_contract is not None
            and self.action != ManagerAction.FORM_CLAIM
        ):
            raise ValueError(
                "claim semantic contract is only valid for FORM_CLAIM"
            )
        if (
            self.mechanism_semantic_ref is not None
            and self.action != ManagerAction.FORM_CLAIM
        ):
            raise ValueError(
                "mechanism semantic ref is only valid for FORM_CLAIM"
            )

        if self.action == ManagerAction.STOP:
            if self.stop_reason is None:
                raise ValueError("STOP requires stop_reason")
            if self.claim is not None or self.counter_to_claim_id is not None:
                raise ValueError("STOP cannot carry follow-up payload")
            return self

        if not self.bounded_objective or not self.bounded_objective.strip():
            raise ValueError("non-STOP proposal requires bounded_objective")
        if (
            not self.expected_information_gain
            or not self.expected_information_gain.strip()
        ):
            raise ValueError("non-STOP proposal requires expected_information_gain")
        if self.stop_reason is not None:
            raise ValueError("non-STOP proposal cannot carry stop_reason")

        if self.action == ManagerAction.FORM_CLAIM and self.claim is None:
            raise ValueError("FORM_CLAIM requires claim draft")
        if self.action != ManagerAction.FORM_CLAIM and self.claim is not None:
            raise ValueError("claim draft is only valid for FORM_CLAIM")

        if self.action == ManagerAction.SEEK_COUNTER_EVIDENCE:
            if self.counter_to_claim_id is None:
                raise ValueError(
                    "SEEK_COUNTER_EVIDENCE requires counter_to_claim_id"
                )
        elif self.counter_to_claim_id is not None:
            raise ValueError(
                "counter_to_claim_id is only valid for SEEK_COUNTER_EVIDENCE"
            )
        return self


class ResolvedInvestigationTopology(Frozen):
    parent_step_id: str | None
    depth: int = Field(ge=0)
    branch_id: str = Field(min_length=1)
    intent: InvestigationIntent
    target_kind: InvestigationTargetKind
    target_ref: str | None = None
    stop_scope: StopScope | None = None


class InvestigationBranchBehavior(StrEnum):
    ROOT_OR_INHERIT = "ROOT_OR_INHERIT"
    OPEN_CHILD_BRANCH = "OPEN_CHILD_BRANCH"
    INHERIT_BRANCH = "INHERIT_BRANCH"
    GLOBAL_CONTROL = "GLOBAL_CONTROL"


class InvestigationGainRequirement(StrEnum):
    NONE = "NONE"
    POSITIVE_EXPECTED_GAIN = "POSITIVE_EXPECTED_GAIN"


class InvestigationBranchKeyPolicy(StrEnum):
    REQUIRED = "REQUIRED"
    FORBIDDEN = "FORBIDDEN"


class InvestigationActionRule(Frozen):
    intent: InvestigationIntent
    legal_parent_step_ids: tuple[str, ...] = ()
    allow_parentless: bool = False
    branch_behavior: InvestigationBranchBehavior
    branch_key_policy: InvestigationBranchKeyPolicy
    depth_delta: int = Field(default=0, ge=0, le=1)
    gain_requirement: InvestigationGainRequirement = (
        InvestigationGainRequirement.NONE
    )


class InvestigationActionProfile(Frozen):
    """Pure state projection of legal P17 moves; never a next-step planner."""

    rules: tuple[InvestigationActionRule, ...]
    max_depth: int = Field(ge=0)

    @property
    def legal_intents(self) -> tuple[InvestigationIntent, ...]:
        return tuple(rule.intent for rule in self.rules)

    def rule_for(
        self,
        intent: InvestigationIntent,
    ) -> InvestigationActionRule | None:
        return next(
            (rule for rule in self.rules if rule.intent == intent),
            None,
        )


class InvestigationNodeView(Frozen):
    step_id: str
    parent_step_id: str | None
    root_obligation_id: str
    depth: int = Field(ge=0)
    branch_id: str
    intent: InvestigationIntent
    target_kind: InvestigationTargetKind
    target_ref: str | None
    objective_key: str
    bounded_objective: str | None
    status: ReasoningStepStatus
    evidence_refs: tuple[str, ...] = ()
    counter_evidence_refs: tuple[str, ...] = ()
    native_material_refs: tuple[str, ...] = ()
    child_step_ids: tuple[str, ...] = ()
    stop_reason: ManagerStopReason | None = None
    stop_scope: StopScope | None = None

    @property
    def contract_depth(self) -> int:
        return self.depth + 1


class InvestigationGraph(Frozen):
    nodes: tuple[InvestigationNodeView, ...]
    root_step_ids: tuple[str, ...]
    open_branch_ids: tuple[str, ...]
    stopped_branch_ids: tuple[str, ...]
    max_observed_depth: int = Field(ge=0)

    @property
    def max_contract_depth(self) -> int:
        if not self.nodes:
            return 0
        return max(item.contract_depth for item in self.nodes)


class ParentObligationView(Frozen):
    obligation_id: str
    objective: str
    state: str


class ClaimEvidenceCognitionView(Frozen):
    evidence_id: str
    receipt_id: str
    relation: str


class ClaimView(Frozen):
    claim_id: str
    obligation_id: str
    claim_text: str
    proposition: dict[str, Any]
    scope: dict[str, Any]
    epistemic_state: str
    origin_material_refs: tuple[str, ...] = ()
    evidence_relations: tuple[str, ...] = ()
    evidence_links: tuple[ClaimEvidenceCognitionView, ...] = ()
    limitations: tuple[str, ...] = ()


class NativeDashcardCognitionView(Frozen):
    dashcard_id: str | int | None = None
    card_id: str | int | None = None
    title: str | None = None


class MaterialCognitionView(Frozen):
    """Thin read projection over durable P15 material; never a second truth copy."""

    lead_id: str
    obligation_id: str
    execution_link_id: str
    native_conversation_id: str
    native_query_id: str
    query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    material_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_evidence_refs: tuple[str, ...]
    exploration_kind: str
    native_name: str | None = None
    native_title: str | None = None
    native_description: str | None = None
    dashcards: tuple[NativeDashcardCognitionView, ...] = ()


class EvidenceResultCognitionView(Frozen):
    """Bounded read projection of one already VERIFIED native result.

    The durable ResearchExecutionLink remains authority. This view deliberately
    excludes query/SQL/MBQL and exposes only result values plus exact Evidence
    lineage so P17 can interpret existing material without reopening analytics.
    """

    evidence_id: str = Field(min_length=1)
    receipt_id: str = Field(min_length=1)
    obligation_id: str = Field(min_length=1)
    execution_link_id: str = Field(min_length=1)
    result_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    row_count: int = Field(ge=0)
    columns: tuple[str, ...] = ()
    rows: tuple[tuple[Any, ...], ...] = ()
    truncated: bool = False


class ResearchManagerSnapshot(Frozen):
    research_session_id: str
    research_authority_id: str
    source_revision: int
    objective: str
    parent_obligations: tuple[ParentObligationView, ...]
    evidence_refs: tuple[str, ...]
    material_refs: tuple[str, ...]
    materials: tuple[MaterialCognitionView, ...]
    evidence_results: tuple[EvidenceResultCognitionView, ...] = ()
    action_profile: InvestigationActionProfile
    claims: tuple[ClaimView, ...]
    investigation: InvestigationGraph
    limitation_refs: tuple[str, ...]
    completed_reasoning_steps: tuple[str, ...]
    pending_reasoning_steps: tuple[str, ...]
    remaining_reasoning_steps: int = Field(ge=0)
    remaining_followup_native_turns: int = Field(ge=0)
    remaining_counter_evidence_attempts: int = Field(ge=0)
    terminal_stop_reason: ManagerStopReason | None = None

    @property
    def fingerprint(self) -> str:
        return _json(
            self.model_dump(mode="json"),
            code="P17_SNAPSHOT_NOT_CANONICAL",
        )[1]


class ResearchReasoningStep(Frozen):
    step_id: str = Field(pattern=r"^rrs_[a-f0-9]{24}$")
    research_session_id: str
    source_revision: int
    source_snapshot_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    parent_obligation_id: str
    parent_step_id: str | None = None
    depth: int = Field(ge=0)
    branch_id: str
    intent: InvestigationIntent
    target_kind: InvestigationTargetKind
    target_ref: str | None = None
    stop_scope: StopScope | None = None
    proposal_id: str
    action: ManagerAction
    objective_key: str
    bounded_objective: str | None
    rationale: str
    inspected_evidence_refs: tuple[str, ...]
    inspected_claim_refs: tuple[str, ...]
    inspected_material_refs: tuple[str, ...]
    proposal_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    status: ReasoningStepStatus
    stop_reason: ManagerStopReason | None = None
    result_refs: tuple[str, ...] = ()
    created_at: datetime
    completed_at: datetime | None = None

    @property
    def contract_depth(self) -> int:
        return self.depth + 1


class ResearchInvestigationTask(Frozen):
    task_id: str = Field(pattern=r"^rit_[a-f0-9]{24}$")
    research_session_id: str
    reasoning_step_id: str
    parent_obligation_id: str
    bounded_objective: str
    analytical_scope: AnalyticalRequestContract | None = None
    counter_to_claim_id: str | None = None
    status: InvestigationTaskStatus
    native_execution_refs: tuple[str, ...] = ()
    material_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    created_at: datetime
    completed_at: datetime | None = None


class FollowupResult(Frozen):
    native_execution_refs: tuple[str, ...] = ()
    material_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


class ResearchProposalManager(Protocol):
    def propose(self, snapshot: ResearchManagerSnapshot) -> ManagerProposal: ...


class ResearchFollowupExecutor(Protocol):
    """Adapter seam to the single sealed P14 native-direct mechanics."""

    def execute(
        self,
        *,
        session: ResearchSession,
        step: ResearchReasoningStep,
        task: ResearchInvestigationTask,
        principal: Principal,
        native_session_token: str | None,
    ) -> FollowupResult: ...


def _now(value: datetime | None = None) -> datetime:
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("P17 timestamps must be timezone-aware")
    return value


def _json(value: Any, *, code: str) -> tuple[str, str]:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
    except (TypeError, ValueError) as exc:
        raise ResearchManagerMaturationError(
            code,
            "value is not deterministic JSON",
        ) from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_list(raw: str, *, code: str) -> tuple[str, ...]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ResearchManagerMaturationError(
            code,
            "persisted JSON is invalid",
        ) from exc
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise ResearchManagerMaturationError(
            code,
            "persisted list has invalid shape",
        )
    return tuple(value)


def _load_analytical_scope(
    raw: str | None,
) -> AnalyticalRequestContract | None:
    if raw is None:
        return None
    try:
        return AnalyticalRequestContract.model_validate_json(raw)
    except ValueError as exc:
        raise ResearchManagerMaturationError(
            "P17_TASK_ANALYTICAL_SCOPE_INVALID",
            "persisted child analytical scope is invalid",
        ) from exc


def _resolved_child_scope(
    *,
    session: ResearchSession,
    obligation_id: str,
    child: AnalyticalRequestContract | None,
) -> AnalyticalRequestContract:
    parent = analytical_scope_contract(
        session=session,
        obligation_id=obligation_id,
    )
    if child is None:
        return parent
    try:
        assert_child_request_scope(parent, child)
    except AnalyticalRequestMismatch as exc:
        raise ResearchManagerMaturationError(
            exc.code,
            exc.detail,
        ) from exc

    brief = session.accepted_brief
    if brief is None:
        raise ResearchManagerMaturationError(
            "P17_ACCEPTED_BRIEF_REQUIRED",
            "child analytical scope requires accepted Research authority",
        )
    known = {item.candidate_id for item in brief.scope.semantic_refs}
    used = set(child.metric_refs)
    used.update(child.dimension_refs)
    used.update(child.grain_constraints)
    for item in child.filters:
        used.add(item.semantic_ref)
        used.add(item.source_candidate_id)
    if child.period is not None:
        used.add(child.period.time_dimension)
    if child.comparison is not None:
        used.add(child.comparison.base_period.time_dimension)
        used.add(child.comparison.reference_period.time_dimension)
    if child.ranking is not None:
        used.add(child.ranking.measure)
    unknown = sorted(used - known)
    if unknown:
        raise ResearchManagerMaturationError(
            "P17_CHILD_SCOPE_SEMANTIC_REF_OUT_OF_SCOPE",
            ",".join(unknown),
        )
    return child


def _id(prefix: str) -> str:
    return prefix + uuid4().hex[:24]


def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise ResearchManagerMaturationError(
        "P17_TENANT_REQUIRED",
        "Research reasoning requires an explicit tenant binding",
    )


class ResearchReasoningStore:
    """Durable P17 reasoning/task ledger. It never mutates P14 obligations."""

    def __init__(self, db_engine=None) -> None:
        self._engine = db_engine or control_plane_engine

    @staticmethod
    def _step(record: ResearchReasoningStepRecord) -> ResearchReasoningStep:
        return ResearchReasoningStep(
            step_id=record.step_id,
            research_session_id=record.session_id,
            source_revision=record.source_revision,
            source_snapshot_fingerprint=record.source_snapshot_fingerprint,
            parent_obligation_id=record.parent_obligation_id,
            parent_step_id=record.parent_step_id,
            depth=record.depth,
            branch_id=record.branch_id,
            intent=InvestigationIntent(record.intent),
            target_kind=InvestigationTargetKind(record.target_kind),
            target_ref=record.target_ref,
            stop_scope=(
                StopScope(record.stop_scope)
                if record.stop_scope is not None
                else None
            ),
            proposal_id=record.proposal_id,
            action=ManagerAction(record.action),
            objective_key=record.objective_key,
            bounded_objective=record.bounded_objective,
            rationale=record.rationale,
            inspected_evidence_refs=_load_list(
                record.inspected_evidence_refs_json,
                code="P17_EVIDENCE_REFS_INVALID",
            ),
            inspected_claim_refs=_load_list(
                record.inspected_claim_refs_json,
                code="P17_CLAIM_REFS_INVALID",
            ),
            inspected_material_refs=_load_list(
                record.inspected_material_refs_json,
                code="P17_MATERIAL_REFS_INVALID",
            ),
            proposal_fingerprint=record.proposal_fingerprint,
            status=ReasoningStepStatus(record.status),
            stop_reason=(
                ManagerStopReason(record.stop_reason)
                if record.stop_reason is not None
                else None
            ),
            result_refs=_load_list(
                record.result_refs_json,
                code="P17_RESULT_REFS_INVALID",
            ),
            created_at=record.created_at,
            completed_at=record.completed_at,
        )

    @staticmethod
    def _task(
        record: ResearchInvestigationTaskRecord,
    ) -> ResearchInvestigationTask:
        return ResearchInvestigationTask(
            task_id=record.task_id,
            research_session_id=record.session_id,
            reasoning_step_id=record.reasoning_step_id,
            parent_obligation_id=record.parent_obligation_id,
            bounded_objective=record.bounded_objective,
            analytical_scope=_load_analytical_scope(
                record.analytical_scope_json
            ),
            counter_to_claim_id=record.counter_to_claim_id,
            status=InvestigationTaskStatus(record.status),
            native_execution_refs=_load_list(
                record.native_execution_refs_json,
                code="P17_NATIVE_REFS_INVALID",
            ),
            material_refs=_load_list(
                record.material_refs_json,
                code="P17_TASK_MATERIAL_REFS_INVALID",
            ),
            evidence_refs=_load_list(
                record.evidence_refs_json,
                code="P17_TASK_EVIDENCE_REFS_INVALID",
            ),
            created_at=record.created_at,
            completed_at=record.completed_at,
        )

    def proposal(self, step_id: str) -> ManagerProposal:
        with Session(self._engine) as db:
            record = db.get(ResearchReasoningStepRecord, step_id)
            if record is None:
                raise ResearchManagerMaturationError(
                    "P17_STEP_NOT_FOUND",
                    step_id,
                )
            try:
                return ManagerProposal.model_validate_json(record.proposal_json)
            except ValueError as exc:
                raise ResearchManagerMaturationError(
                    "P17_PROPOSAL_PERSISTENCE_INVALID",
                    step_id,
                ) from exc

    def steps(self, session_id: str) -> tuple[ResearchReasoningStep, ...]:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(ResearchReasoningStepRecord)
                    .where(ResearchReasoningStepRecord.session_id == session_id)
                    .order_by(
                        ResearchReasoningStepRecord.created_at,
                        ResearchReasoningStepRecord.step_id,
                    )
                ).all()
            )
        return tuple(self._step(x) for x in rows)

    def tasks(self, session_id: str) -> tuple[ResearchInvestigationTask, ...]:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(ResearchInvestigationTaskRecord)
                    .where(
                        ResearchInvestigationTaskRecord.session_id == session_id
                    )
                    .order_by(
                        ResearchInvestigationTaskRecord.created_at,
                        ResearchInvestigationTaskRecord.task_id,
                    )
                ).all()
            )
        return tuple(self._task(x) for x in rows)

    def task_for_step(self, step_id: str) -> ResearchInvestigationTask | None:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(ResearchInvestigationTaskRecord).where(
                        ResearchInvestigationTaskRecord.reasoning_step_id
                        == step_id
                    )
                ).all()
            )
        if len(rows) > 1:
            raise ResearchManagerMaturationError(
                "P17_STEP_TASK_DUPLICATE",
                step_id,
            )
        return self._task(rows[0]) if rows else None

    def step(self, step_id: str) -> ResearchReasoningStep:
        with Session(self._engine) as db:
            record = db.get(ResearchReasoningStepRecord, step_id)
            if record is None:
                raise ResearchManagerMaturationError(
                    "P17_STEP_NOT_FOUND",
                    step_id,
                )
        return self._step(record)

    def create_step(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        proposal: ManagerProposal,
        topology: ResolvedInvestigationTopology,
        proposal_fingerprint: str,
        status: ReasoningStepStatus = ReasoningStepStatus.PENDING,
        stop_reason: ManagerStopReason | None = None,
        stop_scope_override: StopScope | None = None,
        now: datetime | None = None,
    ) -> ResearchReasoningStep:
        when = _now(now)
        evidence_json, _ = _json(
            sorted(proposal.inspected_evidence_refs),
            code="P17_EVIDENCE_REFS_NOT_CANONICAL",
        )
        claim_json, _ = _json(
            sorted(proposal.inspected_claim_refs),
            code="P17_CLAIM_REFS_NOT_CANONICAL",
        )
        material_json, _ = _json(
            sorted(proposal.inspected_material_refs),
            code="P17_MATERIAL_REFS_NOT_CANONICAL",
        )
        result_json, _ = _json(
            [],
            code="P17_RESULT_REFS_NOT_CANONICAL",
        )
        record = ResearchReasoningStepRecord(
            step_id=_id("rrs_"),
            session_id=session.session_id,
            source_revision=proposal.source_revision,
            source_snapshot_fingerprint=snapshot.fingerprint,
            parent_obligation_id=proposal.target_parent_obligation,
            parent_step_id=topology.parent_step_id,
            depth=topology.depth,
            branch_id=topology.branch_id,
            intent=topology.intent.value,
            target_kind=topology.target_kind.value,
            target_ref=topology.target_ref,
            stop_scope=(
                (stop_scope_override or topology.stop_scope).value
                if (stop_scope_override or topology.stop_scope)
                else None
            ),
            proposal_id=proposal.proposal_id,
            proposal_json=proposal.model_dump_json(),
            action=proposal.action.value,
            objective_key=proposal.objective_key,
            bounded_objective=proposal.bounded_objective,
            rationale=proposal.rationale,
            inspected_evidence_refs_json=evidence_json,
            inspected_claim_refs_json=claim_json,
            inspected_material_refs_json=material_json,
            proposal_fingerprint=proposal_fingerprint,
            status=status.value,
            stop_reason=(
                stop_reason.value if stop_reason is not None else None
            ),
            result_refs_json=result_json,
            created_at=when,
            completed_at=(
                when if status != ReasoningStepStatus.PENDING else None
            ),
        )
        with Session(self._engine) as db:
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._step(record)

    def create_task(
        self,
        *,
        session: ResearchSession,
        step: ResearchReasoningStep,
        proposal: ManagerProposal,
        now: datetime | None = None,
    ) -> ResearchInvestigationTask:
        if not proposal.bounded_objective:
            raise ResearchManagerMaturationError(
                "P17_TASK_OBJECTIVE_REQUIRED",
                "follow-up task requires bounded objective",
            )
        empty, _ = _json([], code="P17_TASK_REFS_NOT_CANONICAL")
        task_id = _id("rit_")
        analytical_scope = _resolved_child_scope(
            session=session,
            obligation_id=proposal.target_parent_obligation,
            child=proposal.child_analytical_scope,
        ).model_copy(
            update={
                "request_ref": (
                    f"{session.session_id}:"
                    f"{proposal.target_parent_obligation}:{task_id}"
                )
            }
        )
        record = ResearchInvestigationTaskRecord(
            task_id=task_id,
            session_id=session.session_id,
            reasoning_step_id=step.step_id,
            parent_obligation_id=proposal.target_parent_obligation,
            bounded_objective=proposal.bounded_objective,
            analytical_scope_json=analytical_scope.model_dump_json(),
            counter_to_claim_id=proposal.counter_to_claim_id,
            status=InvestigationTaskStatus.PENDING.value,
            native_execution_refs_json=empty,
            material_refs_json=empty,
            evidence_refs_json=empty,
            created_at=_now(now),
            completed_at=None,
        )
        with Session(self._engine) as db:
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._task(record)

    def complete_task(
        self,
        task_id: str,
        *,
        result: FollowupResult,
        now: datetime | None = None,
    ) -> ResearchInvestigationTask:
        native, _ = _json(
            sorted(set(result.native_execution_refs)),
            code="P17_NATIVE_REFS_NOT_CANONICAL",
        )
        material, _ = _json(
            sorted(set(result.material_refs)),
            code="P17_TASK_MATERIAL_REFS_NOT_CANONICAL",
        )
        evidence, _ = _json(
            sorted(set(result.evidence_refs)),
            code="P17_TASK_EVIDENCE_REFS_NOT_CANONICAL",
        )
        with Session(self._engine) as db:
            record = db.get(ResearchInvestigationTaskRecord, task_id)
            if record is None:
                raise ResearchManagerMaturationError(
                    "P17_TASK_NOT_FOUND",
                    task_id,
                )
            if record.status != InvestigationTaskStatus.PENDING.value:
                raise ResearchManagerMaturationError(
                    "P17_TASK_NOT_PENDING",
                    task_id,
                )
            record.status = InvestigationTaskStatus.COMPLETED.value
            record.native_execution_refs_json = native
            record.material_refs_json = material
            record.evidence_refs_json = evidence
            record.completed_at = _now(now)
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._task(record)

    def complete_step(
        self,
        step_id: str,
        *,
        result_refs: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> ResearchReasoningStep:
        raw, _ = _json(
            sorted(set(result_refs)),
            code="P17_RESULT_REFS_NOT_CANONICAL",
        )
        with Session(self._engine) as db:
            record = db.get(ResearchReasoningStepRecord, step_id)
            if record is None:
                raise ResearchManagerMaturationError(
                    "P17_STEP_NOT_FOUND",
                    step_id,
                )
            if record.status != ReasoningStepStatus.PENDING.value:
                raise ResearchManagerMaturationError(
                    "P17_STEP_NOT_PENDING",
                    step_id,
                )
            record.status = ReasoningStepStatus.COMPLETED.value
            record.result_refs_json = raw
            record.completed_at = _now(now)
            db.add(record)
            db.commit()
            db.refresh(record)
        return self._step(record)

    def prior_fingerprint(
        self,
        *,
        session_id: str,
        proposal_fingerprint: str,
    ) -> ResearchReasoningStep | None:
        with Session(self._engine) as db:
            record = db.exec(
                select(ResearchReasoningStepRecord)
                .where(ResearchReasoningStepRecord.session_id == session_id)
                .where(
                    ResearchReasoningStepRecord.proposal_fingerprint
                    == proposal_fingerprint
                )
                .order_by(ResearchReasoningStepRecord.created_at.desc())
            ).first()
        return self._step(record) if record is not None else None


def _project_investigation_graph(
    *,
    steps: tuple[ResearchReasoningStep, ...],
    tasks: tuple[ResearchInvestigationTask, ...],
) -> InvestigationGraph:
    task_by_step = {x.reasoning_step_id: x for x in tasks}
    children: dict[str, list[str]] = {}
    for step in steps:
        if step.parent_step_id is not None:
            children.setdefault(step.parent_step_id, []).append(step.step_id)

    branch_ids = {
        x.branch_id
        for x in steps
        if x.stop_scope != StopScope.INVESTIGATION
    }
    stopped_branches: set[str] = set()
    nodes = []
    for step in steps:
        task = task_by_step.get(step.step_id)
        evidence = task.evidence_refs if task is not None else ()
        materials = task.material_refs if task is not None else ()
        counter = (
            evidence
            if step.intent == InvestigationIntent.SEEK_COUNTER_EVIDENCE
            else ()
        )
        if (
            step.stop_scope == StopScope.BRANCH
            or (
                step.status == ReasoningStepStatus.NO_PROGRESS
                and step.intent != InvestigationIntent.LEGACY
            )
        ):
            stopped_branches.add(step.branch_id)
        nodes.append(
            InvestigationNodeView(
                step_id=step.step_id,
                parent_step_id=step.parent_step_id,
                root_obligation_id=step.parent_obligation_id,
                depth=step.depth,
                branch_id=step.branch_id,
                intent=step.intent,
                target_kind=step.target_kind,
                target_ref=step.target_ref,
                objective_key=step.objective_key,
                bounded_objective=step.bounded_objective,
                status=step.status,
                evidence_refs=evidence,
                counter_evidence_refs=counter,
                native_material_refs=materials,
                child_step_ids=tuple(sorted(children.get(step.step_id, ()))),
                stop_reason=step.stop_reason,
                stop_scope=step.stop_scope,
            )
        )

    return InvestigationGraph(
        nodes=tuple(nodes),
        root_step_ids=tuple(
            x.step_id for x in steps if x.parent_step_id is None
        ),
        open_branch_ids=tuple(sorted(branch_ids - stopped_branches)),
        stopped_branch_ids=tuple(sorted(stopped_branches)),
        max_observed_depth=max((x.depth for x in steps), default=0),
    )


def _open_investigation_nodes(
    graph: InvestigationGraph,
) -> tuple[InvestigationNodeView, ...]:
    open_branches = set(graph.open_branch_ids)
    return tuple(
        node
        for node in graph.nodes
        if node.branch_id in open_branches
        and node.stop_scope != StopScope.INVESTIGATION
    )


def _build_action_profile(
    *,
    graph: InvestigationGraph,
    claims: tuple[ClaimView, ...],
    materials: tuple[MaterialCognitionView, ...],
    evidence_results: tuple[EvidenceResultCognitionView, ...] = (),
    remaining_followup_native_turns: int,
    remaining_counter_evidence_attempts: int,
    max_depth: int,
) -> InvestigationActionProfile:
    """Project legal moves from current state without choosing among them."""

    open_nodes = _open_investigation_nodes(graph)
    advancing = tuple(
        node.step_id
        for node in open_nodes
        if node.contract_depth < max_depth
    )
    open_ids = tuple(node.step_id for node in open_nodes)
    candidate_branches = {
        node.branch_id
        for node in graph.nodes
        if node.intent == InvestigationIntent.EXPLORE_ALTERNATIVES
    }
    candidate_advancing = tuple(
        node.step_id
        for node in open_nodes
        if node.branch_id in candidate_branches
        and node.contract_depth < max_depth
    )
    rules: list[InvestigationActionRule] = []

    def add(
        intent: InvestigationIntent,
        *,
        parents: tuple[str, ...] = (),
        allow_parentless: bool = False,
        behavior: InvestigationBranchBehavior,
        branch_key: InvestigationBranchKeyPolicy,
        depth_delta: int = 0,
    ) -> None:
        if not allow_parentless and not parents:
            return
        rules.append(
            InvestigationActionRule(
                intent=intent,
                legal_parent_step_ids=parents,
                allow_parentless=allow_parentless,
                branch_behavior=behavior,
                branch_key_policy=branch_key,
                depth_delta=depth_delta,
                gain_requirement=(
                    InvestigationGainRequirement.POSITIVE_EXPECTED_GAIN
                    if depth_delta > 0
                    else InvestigationGainRequirement.NONE
                ),
            )
        )

    if remaining_followup_native_turns > 0:
        add(
            InvestigationIntent.INVESTIGATE_GAP,
            parents=advancing if graph.nodes else (),
            allow_parentless=not graph.nodes,
            behavior=InvestigationBranchBehavior.ROOT_OR_INHERIT,
            branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
            depth_delta=1,
        )

    add(
        InvestigationIntent.EXPLORE_ALTERNATIVES,
        parents=advancing,
        behavior=InvestigationBranchBehavior.OPEN_CHILD_BRANCH,
        branch_key=InvestigationBranchKeyPolicy.REQUIRED,
        depth_delta=1,
    )
    add(
        InvestigationIntent.DEEPEN_EXPLANATION,
        parents=advancing,
        behavior=InvestigationBranchBehavior.INHERIT_BRANCH,
        branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
        depth_delta=1,
    )
    if remaining_followup_native_turns > 0:
        add(
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            parents=candidate_advancing,
            behavior=InvestigationBranchBehavior.INHERIT_BRANCH,
            branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
            depth_delta=1,
        )
    add(
        InvestigationIntent.REPLAN,
        parents=open_ids,
        behavior=InvestigationBranchBehavior.INHERIT_BRANCH,
        branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
        depth_delta=0,
    )
    if (
        claims
        and remaining_followup_native_turns > 0
        and remaining_counter_evidence_attempts > 0
    ):
        add(
            InvestigationIntent.SEEK_COUNTER_EVIDENCE,
            parents=advancing,
            allow_parentless=not graph.nodes,
            behavior=InvestigationBranchBehavior.ROOT_OR_INHERIT,
            branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
            depth_delta=1,
        )
    # VERIFIED native Evidence is already governed analytical material.
    # P17 may synthesize a typed claim from its bounded read-only result view
    # without opening another native acquisition merely to make FORM_CLAIM legal.
    if materials or evidence_results:
        add(
            InvestigationIntent.FORM_CLAIM,
            parents=advancing,
            behavior=InvestigationBranchBehavior.INHERIT_BRANCH,
            branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
            depth_delta=1,
        )
    add(
        InvestigationIntent.STOP_BRANCH,
        parents=open_ids,
        behavior=InvestigationBranchBehavior.INHERIT_BRANCH,
        branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
        depth_delta=0,
    )
    add(
        InvestigationIntent.STOP_INVESTIGATION,
        parents=open_ids,
        allow_parentless=True,
        behavior=InvestigationBranchBehavior.GLOBAL_CONTROL,
        branch_key=InvestigationBranchKeyPolicy.FORBIDDEN,
        depth_delta=0,
    )
    return InvestigationActionProfile(
        rules=tuple(rules),
        max_depth=max_depth,
    )


def project_discriminating_test_reentry_rule(
    *,
    snapshot: ResearchManagerSnapshot,
    obligation_id: str,
) -> InvestigationActionRule | None:
    """Project the single legal typed P19 -> P17 NextTest move.

    Generic P17 state does not gain TEST_DISCRIMINATING_EVIDENCE merely because
    Evidence exists. The move becomes legal only when P19 supplies the exact
    downstream obligation. This projector is then shared by P19 capacity checks
    and P17 execution, eliminating duplicate adaptive authorization.
    """

    if snapshot.remaining_followup_native_turns <= 0:
        return None

    parent = next(
        (
            item
            for item in snapshot.parent_obligations
            if item.obligation_id == obligation_id
        ),
        None,
    )
    if (
        parent is None
        or str(getattr(parent.state, "value", parent.state)) != "VERIFIED"
    ):
        return None

    current_evidence = set(snapshot.evidence_refs)
    if not any(
        item.obligation_id == obligation_id
        and item.evidence_id in current_evidence
        for item in snapshot.evidence_results
    ):
        return None

    open_branches = set(snapshot.investigation.open_branch_ids)
    scoped_open = tuple(
        node
        for node in snapshot.investigation.nodes
        if (
            node.root_obligation_id == obligation_id
            and node.branch_id in open_branches
            and node.stop_scope != StopScope.INVESTIGATION
        )
    )
    compatible = tuple(
        node
        for node in scoped_open
        if node.intent
        in {
            InvestigationIntent.EXPLORE_ALTERNATIVES,
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
        }
    )
    advancing = tuple(
        node.step_id
        for node in compatible
        if node.contract_depth < snapshot.action_profile.max_depth
    )

    if not scoped_open:
        allow_parentless = True
    elif advancing:
        allow_parentless = False
    else:
        return None

    return InvestigationActionRule(
        intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
        legal_parent_step_ids=advancing,
        allow_parentless=allow_parentless,
        branch_behavior=InvestigationBranchBehavior.ROOT_OR_INHERIT,
        branch_key_policy=InvestigationBranchKeyPolicy.FORBIDDEN,
        depth_delta=1,
        gain_requirement=InvestigationGainRequirement.POSITIVE_EXPECTED_GAIN,
    )


def _branch_id(seed: str) -> str:
    return "ibr_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]


def resolve_investigation_topology(
    *,
    snapshot: ResearchManagerSnapshot,
    proposal: ManagerProposal,
) -> ResolvedInvestigationTopology:
    """Resolve dynamic P17 legality exactly once from state + typed proposal."""

    intent = proposal.effective_intent
    node_by_id = {
        node.step_id: node for node in snapshot.investigation.nodes
    }
    parent = (
        node_by_id.get(proposal.parent_step_id)
        if proposal.parent_step_id is not None
        else None
    )
    rule = snapshot.action_profile.rule_for(intent)
    if rule is None:
        depth_advancing = {
            InvestigationIntent.INVESTIGATE_GAP,
            InvestigationIntent.EXPLORE_ALTERNATIVES,
            InvestigationIntent.SEEK_COUNTER_EVIDENCE,
            InvestigationIntent.DEEPEN_EXPLANATION,
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            InvestigationIntent.FORM_CLAIM,
        }
        if (
            parent is not None
            and intent in depth_advancing
            and parent.contract_depth >= snapshot.action_profile.max_depth
        ):
            raise ResearchManagerMaturationError(
                "P17_DEPTH_BUDGET_EXHAUSTED",
                (
                    f"parent contract depth {parent.contract_depth} reached "
                    f"max_depth={snapshot.action_profile.max_depth}"
                ),
            )
        if proposal.parent_step_id is not None:
            raise ResearchManagerMaturationError(
                "P17_PARENT_STEP_NOT_LEGAL",
                proposal.parent_step_id,
            )
        raise ResearchManagerMaturationError(
            "P17_INTENT_NOT_LEGAL_IN_STATE",
            intent.value,
        )

    if rule.branch_key_policy == InvestigationBranchKeyPolicy.REQUIRED:
        if proposal.branch_key is None:
            raise ResearchManagerMaturationError(
                "P17_BRANCH_KEY_REQUIRED",
                intent.value,
            )
    elif proposal.branch_key is not None:
        raise ResearchManagerMaturationError(
            "P17_BRANCH_KEY_FORBIDDEN",
            intent.value,
        )

    if proposal.parent_step_id is None:
        if not rule.allow_parentless:
            raise ResearchManagerMaturationError(
                "P17_PARENT_STEP_REQUIRED",
                intent.value,
            )
    else:
        depth_advancing = {
            InvestigationIntent.INVESTIGATE_GAP,
            InvestigationIntent.EXPLORE_ALTERNATIVES,
            InvestigationIntent.SEEK_COUNTER_EVIDENCE,
            InvestigationIntent.DEEPEN_EXPLANATION,
            InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            InvestigationIntent.FORM_CLAIM,
        }
        if (
            parent is not None
            and intent in depth_advancing
            and parent.contract_depth >= snapshot.action_profile.max_depth
        ):
            raise ResearchManagerMaturationError(
                "P17_DEPTH_BUDGET_EXHAUSTED",
                (
                    f"parent contract depth {parent.contract_depth} reached "
                    f"max_depth={snapshot.action_profile.max_depth}"
                ),
            )
        if (
            parent is None
            or proposal.parent_step_id not in rule.legal_parent_step_ids
        ):
            raise ResearchManagerMaturationError(
                "P17_PARENT_STEP_NOT_LEGAL",
                proposal.parent_step_id,
            )
        if (
            parent.root_obligation_id
            != proposal.target_parent_obligation
        ):
            raise ResearchManagerMaturationError(
                "P17_PARENT_STEP_OBLIGATION_MISMATCH",
                proposal.parent_step_id,
            )

    if rule.branch_behavior == InvestigationBranchBehavior.ROOT_OR_INHERIT:
        if parent is None:
            depth = 0
            branch_id = _branch_id(
                f"{snapshot.research_session_id}|"
                f"{proposal.target_parent_obligation}|root"
            )
        else:
            depth = parent.depth + rule.depth_delta
            branch_id = parent.branch_id
    elif rule.branch_behavior == InvestigationBranchBehavior.OPEN_CHILD_BRANCH:
        assert parent is not None
        assert proposal.branch_key is not None
        depth = parent.depth + rule.depth_delta
        branch_id = _branch_id(
            f"{snapshot.research_session_id}|"
            f"{parent.step_id}|{proposal.branch_key}"
        )
    elif rule.branch_behavior == InvestigationBranchBehavior.INHERIT_BRANCH:
        assert parent is not None
        depth = parent.depth + rule.depth_delta
        branch_id = parent.branch_id
    else:
        # Global control is not an investigation branch. A compatibility branch
        # value is persisted only because the existing row contract requires it.
        depth = parent.depth if parent is not None else 0
        if parent is not None:
            branch_id = parent.branch_id
        else:
            roots = [
                node
                for node in snapshot.investigation.nodes
                if node.parent_step_id is None
                and node.stop_scope != StopScope.INVESTIGATION
            ]
            branch_id = (
                roots[0].branch_id
                if roots
                else _branch_id(
                    f"{snapshot.research_session_id}|"
                    f"{proposal.target_parent_obligation}|global-control"
                )
            )

    contract_depth = depth + 1
    if contract_depth > snapshot.action_profile.max_depth:
        raise ResearchManagerMaturationError(
            "P17_DEPTH_BUDGET_EXHAUSTED",
            (
                f"resolved contract depth {contract_depth} exceeds "
                f"max depth {snapshot.action_profile.max_depth}"
            ),
        )
    if (
        rule.gain_requirement
        == InvestigationGainRequirement.POSITIVE_EXPECTED_GAIN
        and not (proposal.expected_information_gain or "").strip()
    ):
        raise ResearchManagerMaturationError(
            "P17_POSITIVE_EXPECTED_GAIN_REQUIRED",
            "depth-increasing investigation move requires typed positive expected gain",
        )

    stop_scope = None
    if intent == InvestigationIntent.STOP_BRANCH:
        stop_scope = StopScope.BRANCH
    elif intent == InvestigationIntent.STOP_INVESTIGATION:
        stop_scope = StopScope.INVESTIGATION

    return ResolvedInvestigationTopology(
        parent_step_id=proposal.parent_step_id,
        depth=depth,
        branch_id=branch_id,
        intent=intent,
        target_kind=proposal.target_kind,
        target_ref=proposal.target_ref,
        stop_scope=stop_scope,
    )


class ResearchInvestigationManager:
    """Validate, persist, and execute one bounded P17 investigation transition."""

    def __init__(
        self,
        *,
        research_store: ResearchSessionStore,
        claim_store: ClaimLineageStore,
        reasoning_store: ResearchReasoningStore | None = None,
        followup_executor: ResearchFollowupExecutor | None = None,
        budget: ResearchReasoningBudget | None = None,
        db_engine=None,
    ) -> None:
        self._research = research_store
        self._claims = claim_store
        self._engine = db_engine or control_plane_engine
        self._ledger = reasoning_store or ResearchReasoningStore(self._engine)
        self._followup = followup_executor
        self._budget = budget or ResearchReasoningBudget()

    def _session(
        self,
        session_id: str,
        principal: Principal,
    ) -> ResearchSession:
        return self._research.load(
            session_id,
            tenant=_tenant(principal),
            principal=str(principal.user_id),
        )

    def _claim_views(
        self,
        session: ResearchSession,
        principal: Principal,
    ) -> tuple[ClaimView, ...]:
        with Session(self._engine) as db:
            claim_ids = tuple(
                x.claim_id
                for x in db.exec(
                    select(ResearchClaimRecord)
                    .where(
                        ResearchClaimRecord.session_id == session.session_id
                    )
                    .where(
                        ResearchClaimRecord.tenant_binding
                        == session.tenant_binding
                    )
                    .where(
                        ResearchClaimRecord.principal_subject
                        == session.principal_subject
                    )
                    .where(
                        ResearchClaimRecord.semantic_context_version
                        == session.context_version
                    )
                    .order_by(
                        ResearchClaimRecord.created_at,
                        ResearchClaimRecord.claim_id,
                    )
                ).all()
            )

        views = []
        for claim_id in claim_ids:
            claim = self._claims.load_claim(
                session_id=session.session_id,
                claim_id=claim_id,
                principal=principal,
            )
            views.append(
                ClaimView(
                    claim_id=claim.claim_id,
                    obligation_id=claim.obligation_id,
                    claim_text=claim.claim_text,
                    proposition=claim.proposition,
                    scope=claim.scope,
                    epistemic_state=claim.epistemic_state.value,
                    origin_material_refs=claim.origin_material_refs,
                    evidence_relations=tuple(
                        x.relation.value for x in claim.evidence_links
                    ),
                    evidence_links=tuple(
                        ClaimEvidenceCognitionView(
                            evidence_id=x.evidence_id,
                            receipt_id=x.receipt_id,
                            relation=x.relation.value,
                        )
                        for x in claim.evidence_links
                    ),
                    limitations=claim.limitations,
                )
            )
        return tuple(views)

    def snapshot(
        self,
        *,
        session_id: str,
        principal: Principal,
    ) -> ResearchManagerSnapshot:
        session = self._session(session_id, principal)
        steps = self._ledger.steps(session.session_id)
        tasks = self._ledger.tasks(session.session_id)

        with Session(self._engine) as db:
            material_rows = tuple(
                db.exec(
                    select(ResearchExplorationMaterial)
                    .where(
                        ResearchExplorationMaterial.session_id
                        == session.session_id
                    )
                    .where(
                        ResearchExplorationMaterial.epistemic_state
                        == "RESEARCH_MATERIAL"
                    )
                    .order_by(
                        ResearchExplorationMaterial.created_at,
                        ResearchExplorationMaterial.lead_id,
                    )
                ).all()
            )
            followup_rows = tuple(
                db.exec(
                    select(ResearchExecutionLink)
                    .where(ResearchExecutionLink.session_id == session.session_id)
                    .where(ResearchExecutionLink.execution_kind == "P17_FOLLOWUP")
                    .where(ResearchExecutionLink.status == "VERIFIED")
                    .order_by(
                        ResearchExecutionLink.created_at,
                        ResearchExecutionLink.id,
                    )
                ).all()
            )
            verified_result_rows = tuple(
                db.exec(
                    select(ResearchExecutionLink)
                    .where(ResearchExecutionLink.session_id == session.session_id)
                    .where(ResearchExecutionLink.status == "VERIFIED")
                    .order_by(
                        ResearchExecutionLink.created_at,
                        ResearchExecutionLink.id,
                    )
                ).all()
            )

        materials = []
        for row in material_rows:
            try:
                source_refs = json.loads(row.source_evidence_refs_json)
                payload = json.loads(row.native_payload_json)
            except json.JSONDecodeError as exc:
                raise ResearchManagerMaturationError(
                    "P17_MATERIAL_PERSISTENCE_INVALID",
                    row.lead_id,
                ) from exc
            if (
                not isinstance(source_refs, list)
                or any(not isinstance(x, str) for x in source_refs)
                or not isinstance(payload, dict)
            ):
                raise ResearchManagerMaturationError(
                    "P17_MATERIAL_PERSISTENCE_INVALID",
                    row.lead_id,
                )

            def text_field(key: str) -> str | None:
                value = payload.get(key)
                return value if isinstance(value, str) else None

            dashcards = []
            raw_dashcards = payload.get("dashcards")
            if isinstance(raw_dashcards, list):
                for item in raw_dashcards:
                    if not isinstance(item, dict):
                        continue
                    dashcard_id = item.get("id")
                    card_id = item.get("card_id")
                    title = item.get("title")
                    if not isinstance(title, str):
                        name = item.get("name")
                        title = name if isinstance(name, str) else None
                    if not isinstance(dashcard_id, (str, int)):
                        dashcard_id = None
                    if not isinstance(card_id, (str, int)):
                        card_id = None
                    dashcards.append(
                        NativeDashcardCognitionView(
                            dashcard_id=dashcard_id,
                            card_id=card_id,
                            title=title,
                        )
                    )

            materials.append(
                MaterialCognitionView(
                    lead_id=row.lead_id,
                    obligation_id=row.obligation_id,
                    execution_link_id=str(row.execution_link_id),
                    native_conversation_id=str(row.native_conversation_id),
                    native_query_id=row.native_query_id,
                    query_fingerprint=row.query_fingerprint,
                    material_fingerprint=row.payload_fingerprint,
                    source_evidence_refs=tuple(source_refs),
                    exploration_kind=row.exploration_kind,
                    native_name=text_field("name"),
                    native_title=text_field("title"),
                    native_description=text_field("description"),
                    dashcards=tuple(dashcards),
                )
            )

        evidence_results: list[EvidenceResultCognitionView] = []
        seen_evidence_results: set[str] = set()
        max_cognition_rows = 100
        for row in verified_result_rows:
            if (
                not row.evidence_id
                or not row.receipt_id
                or not row.native_result_json
                or not row.result_hash
            ):
                continue
            if row.evidence_id in seen_evidence_results:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_RESULT_DUPLICATE",
                    row.evidence_id,
                )
            try:
                payload = json.loads(row.native_result_json)
            except json.JSONDecodeError as exc:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_RESULT_INVALID",
                    str(row.id),
                ) from exc
            if not isinstance(payload, dict):
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_RESULT_INVALID",
                    str(row.id),
                )
            canonical = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != row.result_hash:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_RESULT_FINGERPRINT_MISMATCH",
                    str(row.id),
                )

            data = payload.get("data")
            raw_rows = data.get("rows") if isinstance(data, dict) else None
            raw_cols = data.get("cols") if isinstance(data, dict) else None
            projected_rows: list[tuple[Any, ...]] = []
            if isinstance(raw_rows, list):
                for item in raw_rows[:max_cognition_rows]:
                    if isinstance(item, (list, tuple)):
                        projected_rows.append(tuple(item))
            columns: list[str] = []
            if isinstance(raw_cols, list):
                for item in raw_cols:
                    if not isinstance(item, dict):
                        continue
                    label = item.get("display_name")
                    if not isinstance(label, str):
                        label = item.get("name")
                    if isinstance(label, str) and label.strip():
                        columns.append(label.strip())

            raw_count = payload.get("row_count")
            row_count = (
                raw_count
                if isinstance(raw_count, int) and raw_count >= 0
                else len(raw_rows)
                if isinstance(raw_rows, list)
                else len(projected_rows)
            )
            evidence_results.append(
                EvidenceResultCognitionView(
                    evidence_id=row.evidence_id,
                    receipt_id=row.receipt_id,
                    obligation_id=row.obligation_id,
                    execution_link_id=str(row.id),
                    result_hash=row.result_hash,
                    row_count=row_count,
                    columns=tuple(columns),
                    rows=tuple(projected_rows),
                    truncated=(
                        isinstance(raw_rows, list)
                        and len(raw_rows) > len(projected_rows)
                    ),
                )
            )
            seen_evidence_results.add(row.evidence_id)

        claims = self._claim_views(session, principal)
        completed = tuple(
            x.step_id
            for x in steps
            if x.status
            in {
                ReasoningStepStatus.COMPLETED,
                ReasoningStepStatus.STOPPED,
                ReasoningStepStatus.NO_PROGRESS,
            }
        )
        pending = tuple(
            x.step_id
            for x in steps
            if x.status == ReasoningStepStatus.PENDING
        )
        followups = len(tasks)
        counters = sum(
            1 for x in tasks if x.counter_to_claim_id is not None
        )
        graph = _project_investigation_graph(
            steps=steps,
            tasks=tasks,
        )
        remaining_reasoning_steps = max(
            0,
            self._budget.max_reasoning_steps - len(steps),
        )
        remaining_followup_native_turns = max(
            0,
            self._budget.max_followup_native_turns - followups,
        )
        remaining_counter_evidence_attempts = max(
            0,
            self._budget.max_counter_evidence_attempts - counters,
        )
        action_profile = _build_action_profile(
            graph=graph,
            claims=claims,
            materials=tuple(materials),
            evidence_results=tuple(evidence_results),
            remaining_followup_native_turns=remaining_followup_native_turns,
            remaining_counter_evidence_attempts=(
                remaining_counter_evidence_attempts
            ),
            max_depth=self._budget.max_depth,
        )
        terminal = next(
            (
                x.stop_reason
                for x in reversed(steps)
                if x.status
                in {
                    ReasoningStepStatus.STOPPED,
                    ReasoningStepStatus.NO_PROGRESS,
                }
                and (
                    x.stop_scope == StopScope.INVESTIGATION
                    or (
                        x.intent == InvestigationIntent.LEGACY
                        and x.stop_scope is None
                    )
                )
            ),
            None,
        )
        return ResearchManagerSnapshot(
            research_session_id=session.session_id,
            research_authority_id=session.authority_id,
            source_revision=session.revision,
            objective=session.objective,
            parent_obligations=tuple(
                ParentObligationView(
                    obligation_id=x.obligation_id,
                    objective=x.objective,
                    state=x.state.value,
                )
                for x in session.obligations
            ),
            evidence_refs=tuple(
                sorted(
                    {
                        *(x.evidence_id for x in session.evidence_refs),
                        *(
                            x.evidence_id
                            for x in followup_rows
                            if x.evidence_id is not None
                        ),
                    }
                )
            ),
            material_refs=tuple(
                sorted(x.lead_id for x in material_rows)
            ),
            materials=tuple(materials),
            evidence_results=tuple(evidence_results),
            claims=claims,
            investigation=graph,
            action_profile=action_profile,
            limitation_refs=tuple(
                sorted(x.limitation_id for x in session.limitations)
            ),
            completed_reasoning_steps=completed,
            pending_reasoning_steps=pending,
            remaining_reasoning_steps=remaining_reasoning_steps,
            remaining_followup_native_turns=remaining_followup_native_turns,
            remaining_counter_evidence_attempts=(
                remaining_counter_evidence_attempts
            ),
            terminal_stop_reason=terminal,
        )

    @staticmethod
    def _fingerprint(
        session: ResearchSession,
        proposal: ManagerProposal,
    ) -> str:
        claim_identity = None
        if proposal.claim is not None:
            claim_identity = {
                "proposition": proposal.claim.proposition,
                "scope": proposal.claim.scope,
                "freshness": proposal.claim.freshness.model_dump(mode="json"),
                "origin_material_refs": sorted(
                    proposal.claim.origin_material_refs
                ),
                "evidence_links": sorted(
                    (
                        item.evidence_id,
                        item.relation.value,
                    )
                    for item in proposal.claim.evidence_links
                ),
                "limitations": sorted(proposal.claim.limitations),
            }
        child_scope_identity = None
        if proposal.child_analytical_scope is not None:
            child_scope_identity = proposal.child_analytical_scope.model_dump(
                mode="json"
            )
            child_scope_identity.pop("request_ref", None)
        identity = {
            "research_authority_id": session.authority_id,
            "research_session_id": session.session_id,
            "parent_obligation_id": proposal.target_parent_obligation,
            "parent_step_id": proposal.parent_step_id,
            "branch_key": proposal.branch_key,
            "intent": proposal.effective_intent.value,
            "target_kind": proposal.target_kind.value,
            "target_ref": proposal.target_ref,
            "action": proposal.action.value,
            # objective_key is the normalized bounded target identity.
            # rationale/bounded_objective prose is intentionally excluded.
            "objective_key": proposal.objective_key,
            "counter_to_claim_id": proposal.counter_to_claim_id,
            "inspected_evidence_refs": sorted(
                proposal.inspected_evidence_refs
            ),
            "inspected_claim_refs": sorted(proposal.inspected_claim_refs),
            "inspected_material_refs": sorted(
                proposal.inspected_material_refs
            ),
            "claim_identity": claim_identity,
            "claim_semantic_contract": (
                proposal.claim_semantic_contract.value
                if proposal.claim_semantic_contract is not None
                else None
            ),
            "child_analytical_scope": child_scope_identity,
            "stop_reason": (
                proposal.stop_reason.value
                if proposal.stop_reason is not None
                else None
            ),
        }
        return _json(
            identity,
            code="P17_PROPOSAL_NOT_CANONICAL",
        )[1]

    def _validate(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        proposal: ManagerProposal,
        topology: ResolvedInvestigationTopology,
    ) -> None:
        if proposal.source_revision != session.revision:
            raise ResearchManagerMaturationError(
                "P17_SOURCE_REVISION_MISMATCH",
                "manager proposal was formed against another Research revision",
            )

        obligation = next(
            (
                x
                for x in session.obligations
                if x.obligation_id == proposal.target_parent_obligation
            ),
            None,
        )
        if obligation is None:
            raise ResearchManagerMaturationError(
                "P17_PARENT_OBLIGATION_OUT_OF_SCOPE",
                proposal.target_parent_obligation,
            )

        if proposal.child_analytical_scope is not None:
            _resolved_child_scope(
                session=session,
                obligation_id=proposal.target_parent_obligation,
                child=proposal.child_analytical_scope,
            )

        if topology.depth + 1 > self._budget.max_depth:
            raise ResearchManagerMaturationError(
                "P17_DEPTH_BUDGET_EXHAUSTED",
                (
                    f"requested contract depth {topology.depth + 1} exceeds "
                    f"max_depth={self._budget.max_depth}"
                ),
            )
        rule = snapshot.action_profile.rule_for(
            proposal.effective_intent
        )
        if rule is None:
            raise ResearchManagerMaturationError(
                "P17_INTENT_NOT_LEGAL_IN_STATE",
                proposal.effective_intent.value,
            )
        if (
            rule.branch_behavior
            != InvestigationBranchBehavior.GLOBAL_CONTROL
            and topology.branch_id
            in snapshot.investigation.stopped_branch_ids
        ):
            raise ResearchManagerMaturationError(
                "P17_BRANCH_TERMINAL",
                topology.branch_id,
            )

        evidence_scope = {
            x.evidence_id: x.obligation_id for x in session.evidence_refs
        }
        claim_by_id = {x.claim_id: x for x in snapshot.claims}
        with Session(self._engine) as db:
            followup_rows = tuple(
                db.exec(
                    select(ResearchExecutionLink)
                    .where(ResearchExecutionLink.session_id == session.session_id)
                    .where(ResearchExecutionLink.execution_kind == "P17_FOLLOWUP")
                    .where(ResearchExecutionLink.status == "VERIFIED")
                ).all()
            )
            material_rows = tuple(
                db.exec(
                    select(ResearchExplorationMaterial)
                    .where(
                        ResearchExplorationMaterial.session_id
                        == session.session_id
                    )
                    .where(
                        ResearchExplorationMaterial.epistemic_state
                        == "RESEARCH_MATERIAL"
                    )
                ).all()
            )
        for link in followup_rows:
            if (
                link.evidence_id is None
                or link.receipt_id is None
                or not link.reasoning_step_id
                or not link.investigation_task_id
            ):
                raise ResearchManagerMaturationError(
                    "P17_FOLLOWUP_EVIDENCE_LINEAGE_INVALID",
                    str(link.id),
                )
            prior = evidence_scope.get(link.evidence_id)
            if prior is not None and prior != link.obligation_id:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_ID_SCOPE_CONFLICT",
                    link.evidence_id,
                )
            evidence_scope[link.evidence_id] = link.obligation_id

        material_by_id = {x.lead_id: x for x in material_rows}

        for evidence_id in proposal.inspected_evidence_refs:
            obligation_id = evidence_scope.get(evidence_id)
            if obligation_id is None:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_REF_UNKNOWN",
                    evidence_id,
                )
            if obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_EVIDENCE_REF_SCOPE_MISMATCH",
                    evidence_id,
                )

        for claim_id in proposal.inspected_claim_refs:
            claim = claim_by_id.get(claim_id)
            if claim is None:
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_REF_UNKNOWN",
                    claim_id,
                )
            if claim.obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_REF_SCOPE_MISMATCH",
                    claim_id,
                )

        for material_id in proposal.inspected_material_refs:
            material = material_by_id.get(material_id)
            if material is None:
                raise ResearchManagerMaturationError(
                    "P17_MATERIAL_REF_UNKNOWN",
                    material_id,
                )
            if material.obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_MATERIAL_REF_SCOPE_MISMATCH",
                    material_id,
                )

        if proposal.action == ManagerAction.SEEK_COUNTER_EVIDENCE:
            claim = claim_by_id.get(proposal.counter_to_claim_id or "")
            if claim is None:
                raise ResearchManagerMaturationError(
                    "P17_COUNTER_CLAIM_UNKNOWN",
                    proposal.counter_to_claim_id or "",
                )
            if claim.obligation_id != proposal.target_parent_obligation:
                raise ResearchManagerMaturationError(
                    "P17_COUNTER_CLAIM_SCOPE_MISMATCH",
                    claim.claim_id,
                )
            if claim.claim_id not in proposal.inspected_claim_refs:
                raise ResearchManagerMaturationError(
                    "P17_COUNTER_CLAIM_NOT_INSPECTED",
                    claim.claim_id,
                )

        if (
            proposal.action == ManagerAction.FORM_CLAIM
            and proposal.claim is not None
        ):
            if any(
                ref not in material_by_id
                for ref in proposal.claim.origin_material_refs
            ):
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_ORIGIN_UNKNOWN",
                    "FORM_CLAIM references unknown P15 material",
                )
            if any(
                material_by_id[ref].obligation_id
                != proposal.target_parent_obligation
                for ref in proposal.claim.origin_material_refs
            ):
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_ORIGIN_SCOPE_MISMATCH",
                    "FORM_CLAIM origin belongs to another obligation",
                )
            inspected = set(proposal.inspected_evidence_refs)
            for link in proposal.claim.evidence_links:
                if link.evidence_id not in inspected:
                    raise ResearchManagerMaturationError(
                        "P17_CLAIM_EVIDENCE_NOT_INSPECTED",
                        link.evidence_id,
                    )

    def _system_stop(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        reason: ManagerStopReason,
        detail: str,
    ) -> ResearchReasoningStep:
        proposal = ManagerProposal(
            proposal_id=f"p17-system-{reason.value.lower()}",
            source_revision=session.revision,
            target_parent_obligation=session.obligations[0].obligation_id,
            action=ManagerAction.STOP,
            objective_key=f"system.{reason.value.lower()}",
            rationale=detail,
            stop_reason=reason,
        )
        fingerprint = self._fingerprint(session, proposal)
        topology = resolve_investigation_topology(
            snapshot=snapshot,
            proposal=proposal,
        )
        return self._ledger.create_step(
            session=session,
            snapshot=snapshot,
            proposal=proposal,
            topology=topology,
            proposal_fingerprint=fingerprint,
            status=(
                ReasoningStepStatus.NO_PROGRESS
                if reason == ManagerStopReason.NO_PROGRESS
                else ReasoningStepStatus.STOPPED
            ),
            stop_reason=reason,
        )

    def _resume_pending(
        self,
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        step: ResearchReasoningStep,
        principal: Principal,
        native_session_token: str | None,
    ) -> tuple[ResearchReasoningStep, ResearchInvestigationTask | None]:
        proposal = self._ledger.proposal(step.step_id)
        if proposal.source_revision != session.revision:
            raise ResearchManagerMaturationError(
                "P17_PENDING_STEP_REVISION_DRIFT",
                step.step_id,
            )

        if proposal.action == ManagerAction.RECORD_INVESTIGATION:
            return (
                self._ledger.complete_step(step.step_id),
                None,
            )

        if proposal.action == ManagerAction.FORM_CLAIM:
            assert proposal.claim is not None
            proposition = proposal.claim.proposition
            if (
                proposal.claim_semantic_contract
                == ClaimSemanticContract.ROOT_CAUSE_CANDIDATE
            ):
                if session.accepted_brief is None:
                    raise ResearchManagerMaturationError(
                        "P17_ROOT_CANDIDATE_SCOPE_REQUIRED",
                        "typed root candidate requires accepted Research scope",
                    )
                mechanism_ref = proposal.mechanism_semantic_ref
                if mechanism_ref is None:
                    raise ResearchManagerMaturationError(
                        "P17_ROOT_CANDIDATE_MECHANISM_REQUIRED",
                        "typed root candidate requires a governed mechanism semantic ref",
                    )
                accepted_refs = {
                    item.candidate_id
                    for item in session.accepted_brief.scope.semantic_refs
                }
                if mechanism_ref not in accepted_refs:
                    raise ResearchManagerMaturationError(
                        "P17_ROOT_CANDIDATE_MECHANISM_OUT_OF_SCOPE",
                        mechanism_ref,
                    )
                semantics = RootCauseCandidateSemantics(
                    explanatory_subject_ref=proposal.target_parent_obligation,
                    relation_kind=(
                        RootCauseCandidateRelation.EXPLANATORY_CANDIDATE
                    ),
                    mechanism_ref=mechanism_ref,
                    scope_lineage_id=session.lineage_id,
                    scope_version_id=(
                        session.accepted_brief.scope.scope_version.version_id
                    ),
                )
                try:
                    proposition = embed_root_cause_candidate_semantics(
                        proposition,
                        semantics,
                    )
                except ValueError as exc:
                    raise ResearchManagerMaturationError(
                        "P17_ROOT_CANDIDATE_CONTRACT_INVALID",
                        str(exc),
                    ) from exc
            claim = self._claims.create_claim(
                session_id=session.session_id,
                obligation_id=proposal.target_parent_obligation,
                principal=principal,
                claim_text=proposal.claim.claim_text,
                proposition=proposition,
                scope=proposal.claim.scope,
                freshness=proposal.claim.freshness,
                origin_material_refs=proposal.claim.origin_material_refs,
                limitations=proposal.claim.limitations,
            )
            for evidence_link in proposal.claim.evidence_links:
                claim = self._claims.link_evidence(
                    session_id=session.session_id,
                    claim_id=claim.claim_id,
                    evidence_id=evidence_link.evidence_id,
                    relation=evidence_link.relation,
                    principal=principal,
                )
            return (
                self._ledger.complete_step(
                    step.step_id,
                    result_refs=(claim.claim_id,),
                ),
                None,
            )

        if proposal.action not in {
            ManagerAction.EXPLORE_NATIVE,
            ManagerAction.SEEK_COUNTER_EVIDENCE,
        }:
            raise ResearchManagerMaturationError(
                "P17_PENDING_ACTION_INVALID",
                proposal.action.value,
            )
        if self._followup is None:
            raise ResearchManagerMaturationError(
                "P17_FOLLOWUP_EXECUTOR_REQUIRED",
                "pending follow-up requires the single sealed native-direct adapter",
            )

        task = self._ledger.task_for_step(step.step_id)
        if task is None:
            task = self._ledger.create_task(
                session=session,
                step=step,
                proposal=proposal,
            )

        if task.status == InvestigationTaskStatus.PENDING:
            result = self._followup.execute(
                session=session,
                step=step,
                task=task,
                principal=principal,
                native_session_token=native_session_token,
            )
            task = self._ledger.complete_task(
                task.task_id,
                result=result,
            )

        result_refs = tuple(
            dict.fromkeys(
                (
                    *task.native_execution_refs,
                    *task.material_refs,
                    *task.evidence_refs,
                )
            )
        )
        return (
            self._ledger.complete_step(
                step.step_id,
                result_refs=result_refs,
            ),
            task,
        )

    @staticmethod
    def _verified_evidence_claim_reentry_snapshot(
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        obligation_id: str,
    ) -> ResearchManagerSnapshot:
        """Authorize one claim-only P17 root from already VERIFIED P14 Evidence.

        This is a downstream re-entry legality projection, not a new analytical
        material source. It never creates material, never executes native work,
        and only exists for the exact verified obligation/evidence scope.
        """

        obligation = ResearchManager.obligation(session, obligation_id)
        if obligation.state != ObligationState.VERIFIED:
            raise ResearchManagerMaturationError(
                "P17_CLAIM_REENTRY_VERIFIED_OBLIGATION_REQUIRED",
                obligation_id,
            )
        evidence_refs = tuple(
            item.evidence_id
            for item in session.evidence_refs
            if item.obligation_id == obligation_id
        )
        if not evidence_refs:
            raise ResearchManagerMaturationError(
                "P17_CLAIM_REENTRY_EVIDENCE_REQUIRED",
                obligation_id,
            )

        open_branches = set(snapshot.investigation.open_branch_ids)
        scoped_open = tuple(
            node
            for node in snapshot.investigation.nodes
            if (
                node.root_obligation_id == obligation_id
                and node.branch_id in open_branches
                and node.stop_scope != StopScope.INVESTIGATION
            )
        )
        advancing = tuple(
            node.step_id
            for node in scoped_open
            if node.contract_depth < snapshot.action_profile.max_depth
        )
        if scoped_open and not advancing:
            raise ResearchManagerMaturationError(
                "P17_CLAIM_REENTRY_DEPTH_EXHAUSTED",
                obligation_id,
            )

        claim_rule = InvestigationActionRule(
            intent=InvestigationIntent.FORM_CLAIM,
            legal_parent_step_ids=advancing,
            allow_parentless=not scoped_open,
            branch_behavior=InvestigationBranchBehavior.ROOT_OR_INHERIT,
            branch_key_policy=InvestigationBranchKeyPolicy.FORBIDDEN,
            depth_delta=1,
            gain_requirement=InvestigationGainRequirement.POSITIVE_EXPECTED_GAIN,
        )
        rules = tuple(
            rule
            for rule in snapshot.action_profile.rules
            if rule.intent != InvestigationIntent.FORM_CLAIM
        )
        return snapshot.model_copy(
            update={
                "action_profile": InvestigationActionProfile(
                    rules=(*rules, claim_rule),
                    max_depth=snapshot.action_profile.max_depth,
                )
            }
        )

    @staticmethod
    def _verified_evidence_discriminating_reentry_snapshot(
        *,
        session: ResearchSession,
        snapshot: ResearchManagerSnapshot,
        obligation_id: str,
    ) -> ResearchManagerSnapshot:
        """Authorize one typed P19 -> P17 discriminating native re-entry.

        Direct P19 may be reached without any prior P17 node when the user
        supplied the competing hypotheses. A typed NextTestRequest must still
        be able to request exactly one high-information P17 test without
        inventing a synthetic discovery step.

        This projection is fail-closed: it requires the exact VERIFIED parent
        obligation and governed Evidence, preserves the existing depth/native
        budgets, and adds only TEST_DISCRIMINATING_EVIDENCE legality.
        """

        try:
            obligation = ResearchManager.obligation(session, obligation_id)
        except ResearchStateError as exc:
            raise ResearchManagerMaturationError(
                "P17_TEST_REENTRY_OBLIGATION_INVALID",
                obligation_id,
            ) from exc
        if obligation.state != ObligationState.VERIFIED:
            raise ResearchManagerMaturationError(
                "P17_TEST_REENTRY_VERIFIED_OBLIGATION_REQUIRED",
                obligation_id,
            )
        evidence_refs = tuple(
            item.evidence_id
            for item in session.evidence_refs
            if item.obligation_id == obligation_id
        )
        if not evidence_refs:
            raise ResearchManagerMaturationError(
                "P17_TEST_REENTRY_EVIDENCE_REQUIRED",
                obligation_id,
            )
        if snapshot.remaining_followup_native_turns <= 0:
            raise ResearchManagerMaturationError(
                "P17_TEST_REENTRY_NATIVE_BUDGET_EXHAUSTED",
                obligation_id,
            )

        test_rule = project_discriminating_test_reentry_rule(
            snapshot=snapshot,
            obligation_id=obligation_id,
        )
        if test_rule is None:
            raise ResearchManagerMaturationError(
                "P17_TEST_REENTRY_NOT_CALLABLE",
                obligation_id,
            )
        rules = tuple(
            rule
            for rule in snapshot.action_profile.rules
            if rule.intent != InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
        )
        return snapshot.model_copy(
            update={
                "action_profile": InvestigationActionProfile(
                    rules=(*rules, test_rule),
                    max_depth=snapshot.action_profile.max_depth,
                )
            }
        )

    def run_one(
        self,
        *,
        session_id: str,
        principal: Principal,
        manager: ResearchProposalManager,
        native_session_token: str | None = None,
        downstream_reentry_intent: InvestigationIntent | None = None,
        downstream_reentry_intents: tuple[InvestigationIntent, ...] | None = None,
        downstream_reentry_obligation_id: str | None = None,
        child_analytical_scope: AnalyticalRequestContract | None = None,
    ) -> tuple[ResearchReasoningStep, ResearchInvestigationTask | None]:
        session = self._session(session_id, principal)
        snapshot = self.snapshot(
            session_id=session_id,
            principal=principal,
        )
        if (
            downstream_reentry_intent is not None
            and downstream_reentry_intents is not None
        ):
            raise ResearchManagerMaturationError(
                "P17_DOWNSTREAM_REENTRY_CONTRACT_CONFLICT",
                "use either one strict reentry intent or one typed allowed-intent set",
            )
        if downstream_reentry_intents is not None:
            authorized_reentry_intents = tuple(
                dict.fromkeys(downstream_reentry_intents)
            )
            if not authorized_reentry_intents:
                raise ResearchManagerMaturationError(
                    "P17_DOWNSTREAM_REENTRY_INTENTS_EMPTY",
                    "typed allowed-intent set cannot be empty",
                )
        elif downstream_reentry_intent is not None:
            authorized_reentry_intents = (downstream_reentry_intent,)
        else:
            authorized_reentry_intents = ()

        projection_intents = tuple(
            intent
            for intent in authorized_reentry_intents
            if intent
            in {
                InvestigationIntent.FORM_CLAIM,
                InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            }
        )
        if len(projection_intents) > 1:
            raise ResearchManagerMaturationError(
                "P17_DOWNSTREAM_REENTRY_PROJECTION_AMBIGUOUS",
                ",".join(intent.value for intent in projection_intents),
            )
        projection_intent = (
            projection_intents[0] if projection_intents else None
        )

        if projection_intent == InvestigationIntent.FORM_CLAIM:
            if not downstream_reentry_obligation_id:
                raise ResearchManagerMaturationError(
                    "P17_CLAIM_REENTRY_OBLIGATION_REQUIRED",
                    "FORM_CLAIM downstream reentry requires one exact obligation",
                )
            snapshot = self._verified_evidence_claim_reentry_snapshot(
                session=session,
                snapshot=snapshot,
                obligation_id=downstream_reentry_obligation_id,
            )
        elif (
            projection_intent
            == InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
            and downstream_reentry_obligation_id is not None
        ):
            # Brain V2 direct-P19 re-entry supplies the exact obligation and may
            # need a typed parentless projection because no prior P17 node
            # exists. Historical P17 callers that omit the exact obligation
            # retain the pre-existing action-profile/terminal legality below.
            snapshot = self._verified_evidence_discriminating_reentry_snapshot(
                session=session,
                snapshot=snapshot,
                obligation_id=downstream_reentry_obligation_id,
            )
        elif downstream_reentry_obligation_id is not None:
            raise ResearchManagerMaturationError(
                "P17_DOWNSTREAM_REENTRY_OBLIGATION_UNEXPECTED",
                downstream_reentry_obligation_id,
            )

        if snapshot.terminal_stop_reason is not None:
            legal_reentry = (
                snapshot.terminal_stop_reason
                == ManagerStopReason.OBJECTIVE_SATISFIED
                and projection_intent is not None
                and snapshot.action_profile.rule_for(
                    projection_intent
                )
                is not None
            )
            if not legal_reentry:
                raise ResearchManagerMaturationError(
                    "P17_INVESTIGATION_TERMINAL",
                    snapshot.terminal_stop_reason.value,
                )

        if len(snapshot.pending_reasoning_steps) > 1:
            raise ResearchManagerMaturationError(
                "P17_MULTIPLE_PENDING_STEPS",
                "bounded manager permits at most one pending reasoning step",
            )

        if snapshot.pending_reasoning_steps:
            pending = next(
                x
                for x in self._ledger.steps(session.session_id)
                if x.step_id == snapshot.pending_reasoning_steps[0]
            )
            if child_analytical_scope is not None:
                persisted = self._ledger.proposal(pending.step_id)
                if (
                    persisted.child_analytical_scope
                    != child_analytical_scope
                ):
                    raise ResearchManagerMaturationError(
                        "P17_PENDING_CHILD_SCOPE_MISMATCH",
                        "restart cannot replace persisted child analytical scope",
                    )
            return self._resume_pending(
                session=session,
                snapshot=snapshot,
                step=pending,
                principal=principal,
                native_session_token=native_session_token,
            )

        if snapshot.remaining_reasoning_steps == 0:
            return (
                self._system_stop(
                    session=session,
                    snapshot=snapshot,
                    reason=ManagerStopReason.BUDGET_EXHAUSTED,
                    detail="P17 reasoning budget exhausted",
                ),
                None,
            )

        proposal = manager.propose(snapshot)
        if proposal.child_analytical_scope is not None:
            raise ResearchManagerMaturationError(
                "P17_MANAGER_CHILD_SCOPE_AUTHORITY_FORBIDDEN",
                (
                    "manager/provider proposal cannot author analytical scope; "
                    "Dima must bind typed child scope state"
                ),
            )
        if child_analytical_scope is not None:
            proposal = proposal.model_copy(
                update={
                    "child_analytical_scope": child_analytical_scope,
                }
            )
        if (
            authorized_reentry_intents
            and proposal.effective_intent not in authorized_reentry_intents
        ):
            raise ResearchManagerMaturationError(
                "P17_DOWNSTREAM_REENTRY_INTENT_MISMATCH",
                (
                    "authorized "
                    + ",".join(
                        intent.value for intent in authorized_reentry_intents
                    )
                    + f", received {proposal.effective_intent.value}"
                ),
            )
        topology = resolve_investigation_topology(
            snapshot=snapshot,
            proposal=proposal,
        )
        self._validate(
            session=session,
            snapshot=snapshot,
            proposal=proposal,
            topology=topology,
        )
        fingerprint = self._fingerprint(session, proposal)
        prior = self._ledger.prior_fingerprint(
            session_id=session.session_id,
            proposal_fingerprint=fingerprint,
        )
        if prior is not None:
            step = self._ledger.create_step(
                session=session,
                snapshot=snapshot,
                proposal=proposal,
                topology=topology,
                proposal_fingerprint=fingerprint,
                status=ReasoningStepStatus.NO_PROGRESS,
                stop_reason=ManagerStopReason.NO_PROGRESS,
                stop_scope_override=StopScope.BRANCH,
            )
            return step, None

        if proposal.action == ManagerAction.STOP:
            step = self._ledger.create_step(
                session=session,
                snapshot=snapshot,
                proposal=proposal,
                topology=topology,
                proposal_fingerprint=fingerprint,
                status=ReasoningStepStatus.STOPPED,
                stop_reason=proposal.stop_reason,
            )
            return step, None

        if (
            proposal.action
            in {
                ManagerAction.EXPLORE_NATIVE,
                ManagerAction.SEEK_COUNTER_EVIDENCE,
            }
            and snapshot.remaining_followup_native_turns == 0
        ):
            return (
                self._system_stop(
                    session=session,
                    snapshot=snapshot,
                    reason=ManagerStopReason.BUDGET_EXHAUSTED,
                    detail="P17 native follow-up budget exhausted",
                ),
                None,
            )

        if (
            proposal.action == ManagerAction.SEEK_COUNTER_EVIDENCE
            and snapshot.remaining_counter_evidence_attempts == 0
        ):
            return (
                self._system_stop(
                    session=session,
                    snapshot=snapshot,
                    reason=ManagerStopReason.BUDGET_EXHAUSTED,
                    detail="P17 counter-evidence budget exhausted",
                ),
                None,
            )

        if (
            proposal.action
            in {
                ManagerAction.EXPLORE_NATIVE,
                ManagerAction.SEEK_COUNTER_EVIDENCE,
            }
            and self._followup is None
        ):
            raise ResearchManagerMaturationError(
                "P17_FOLLOWUP_EXECUTOR_REQUIRED",
                "native follow-up proposal requires the single sealed native-direct adapter",
            )

        # Persist the accepted manager proposal before any follow-on work.
        step = self._ledger.create_step(
            session=session,
            snapshot=snapshot,
            proposal=proposal,
            topology=topology,
            proposal_fingerprint=fingerprint,
        )
        return self._resume_pending(
            session=session,
            snapshot=snapshot,
            step=step,
            principal=principal,
            native_session_token=native_session_token,
        )
