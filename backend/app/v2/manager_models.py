"""Day 6.5 bounded-Manager authority contracts.

These models do not execute analytics and do not expose canonical semantic identifiers
to the Manager. They separate probabilistic cognition from deterministic acceptance,
semantic binding, execution and completion authority.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from app.v2.models import FrozenModel


class ObligationOrigin(StrEnum):
    USER_MUST = "USER_MUST"
    USER_OPTIONAL = "USER_OPTIONAL"
    SYSTEM_REQUIRED = "SYSTEM_REQUIRED"
    AGENT_DERIVED = "AGENT_DERIVED"


class ObligationPriority(StrEnum):
    MUST = "MUST"
    SHOULD = "SHOULD"


class ObligationPolarity(StrEnum):
    REQUIRED = "REQUIRED"
    EXCLUDED = "EXCLUDED"


class ObligationStatus(StrEnum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"
    BLOCKED_DATA_GAP = "BLOCKED_DATA_GAP"
    LIMITED = "LIMITED"
    UNSUPPORTED = "UNSUPPORTED"
    SUPERSEDED = "SUPERSEDED"


class ManagerCapabilityKey(StrEnum):
    PERFORMANCE = "performance"
    BREAKDOWN = "breakdown"
    RANKING = "ranking"
    COMPARISON = "comparison"
    RELATIONSHIP = "relationship"
    ROOT_CAUSE = "root_cause"
    TREND = "trend"
    REPORT = "report"
    TABLE = "table"
    CHART = "chart"
    EXPLAIN = "explain"


class AcceptanceStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"


class RepresentabilityDecision(StrEnum):
    STANDARD_LOSSLESS = "STANDARD_LOSSLESS"
    STANDARD_BUILD_REQUIRED = "STANDARD_BUILD_REQUIRED"
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"


class ResearchRunTerminal(StrEnum):
    VERIFIED_COMPLETE = "VERIFIED_COMPLETE"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class ResearchDirectiveType(StrEnum):
    ADAPT_ON_EVIDENCE = "ADAPT_ON_EVIDENCE"
    BROADEN_WITHIN_BUDGET = "BROADEN_WITHIN_BUDGET"


class ResearchDirectiveCondition(StrEnum):
    MATERIAL_NEW_DIRECTION = "MATERIAL_NEW_DIRECTION"
    WITHIN_SYSTEM_BUDGET = "WITHIN_SYSTEM_BUDGET"


class ResearchDirective(FrozenModel):
    directive_id: str = Field(min_length=1)
    directive_type: ResearchDirectiveType
    parent_obligation_id: str = Field(min_length=1)
    condition: ResearchDirectiveCondition = (
        ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION
    )
    source_refs: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _directive_shape(self):
        expected = {
            ResearchDirectiveType.ADAPT_ON_EVIDENCE:
                ResearchDirectiveCondition.MATERIAL_NEW_DIRECTION,
            ResearchDirectiveType.BROADEN_WITHIN_BUDGET:
                ResearchDirectiveCondition.WITHIN_SYSTEM_BUDGET,
        }[self.directive_type]
        if self.condition != expected:
            raise ValueError(
                f"{self.directive_type.value} requires condition {expected.value}"
            )
        return self


class ResearchDirectiveDispositionStatus(StrEnum):
    OPEN = "OPEN"
    APPLIED = "APPLIED"
    NO_MATERIAL_DIRECTION = "NO_MATERIAL_DIRECTION"
    BLOCKED = "BLOCKED"


class ResearchDirectiveDisposition(FrozenModel):
    """Runtime accounting for accepted research policy, never analytical truth."""

    directive_id: str = Field(min_length=1)
    directive_type: ResearchDirectiveType
    parent_obligation_id: str = Field(min_length=1)
    status: ResearchDirectiveDispositionStatus
    evidence_ref: str | None = None
    branch_task_refs: tuple[str, ...] = ()
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _terminal_shape(self):
        if self.status == ResearchDirectiveDispositionStatus.OPEN:
            if self.evidence_ref is not None or self.branch_task_refs or self.reason is not None:
                raise ValueError("OPEN directive disposition cannot carry accounting proof")
            return self
        if self.evidence_ref is None:
            raise ValueError("terminal directive disposition requires governed Evidence ref")
        if (
            self.status == ResearchDirectiveDispositionStatus.APPLIED
            and not self.branch_task_refs
        ):
            raise ValueError("APPLIED directive disposition requires branch task refs")
        if (
            self.status == ResearchDirectiveDispositionStatus.NO_MATERIAL_DIRECTION
            and self.branch_task_refs
        ):
            raise ValueError("NO_MATERIAL_DIRECTION cannot carry branch task refs")
        return self


class StandardProjection(FrozenModel):
    obligation_ids: tuple[str, ...] = Field(min_length=1)
    metric_handles: tuple[str, ...] = Field(min_length=1)
    dimension_handles: tuple[str, ...] = ()
    filter_handles: tuple[str, ...] = ()
    period_handle: str | None = None
    comparison_handle: str | None = None
    ranking_direction: Literal["asc", "desc"] | None = None
    limit: int | None = Field(default=None, ge=1, le=1000)

    @model_validator(mode="after")
    def _ranking_pair(self):
        if (self.ranking_direction is None) != (self.limit is None):
            raise ValueError("ranking direction ve limit birlikte verilmelidir")
        return self


class SourceSpanRef(FrozenModel):
    source_ref: str = Field(pattern=r"^src_[a-f0-9]{24}$")
    message_id: str = Field(min_length=1)
    message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    start_offset: int = Field(ge=0)
    end_offset: int = Field(gt=0)
    exact_surface: str = Field(min_length=1)

    @model_validator(mode="after")
    def _valid_offsets(self):
        if self.end_offset <= self.start_offset:
            raise ValueError("source span end_offset start_offset'tan büyük olmalı")
        return self


class SemanticHandle(FrozenModel):
    handle_id: str = Field(pattern=r"^sem_[a-f0-9]{24}$")
    tenant_binding: str = Field(min_length=1)
    context_version: str = Field(min_length=1)
    resolver_provenance_id: str = Field(min_length=1)
    target_kind: str = Field(min_length=1)
    provenance_type: Literal["USER_SOURCE", "AGENT_DERIVED"] = "USER_SOURCE"
    parent_obligation_id: str | None = None
    trigger_evidence_ref: str | None = None
    sensitive: bool = False


class SemanticResolutionReceipt(FrozenModel):
    """Anti-laundering proof for one runtime-approved source -> semantic handle edge.

    This receipt proves provenance only. It is not an intent-completeness signal and must
    never be used to infer what other obligations or semantic surfaces the user intended.
    """

    source_ref: str = Field(pattern=r"^src_[a-f0-9]{24}$")
    handle_id: str = Field(pattern=r"^sem_[a-f0-9]{24}$")
    target_kind: str = Field(min_length=1)


class SemanticBindingRef(FrozenModel):
    """Exact runtime-minted provenance edge: source span -> semantic handle."""

    source_ref: str = Field(pattern=r"^src_[a-f0-9]{24}$")
    handle_id: str = Field(pattern=r"^sem_[a-f0-9]{24}$")
    target_kind: str = Field(min_length=1)


class CandidateObligation(FrozenModel):
    obligation_id: str = Field(min_length=1)
    capability_key: ManagerCapabilityKey
    origin: ObligationOrigin
    parent_obligation_id: str | None = None
    priority: ObligationPriority = ObligationPriority.MUST
    polarity: ObligationPolarity = ObligationPolarity.REQUIRED
    source_refs: tuple[str, ...] = Field(min_length=1)
    semantic_handle_refs: tuple[str, ...] = ()
    semantic_bindings: tuple[SemanticBindingRef, ...] = ()
    scope_refs: tuple[str, ...] = ()
    open_questions: tuple[str, ...] = ()
    ranking_direction: Literal["asc", "desc"] | None = None
    ranking_limit: int | None = Field(default=None, ge=1, le=1000)

    @model_validator(mode="after")
    def _origin_contract(self):
        if self.origin == ObligationOrigin.AGENT_DERIVED and not self.parent_obligation_id:
            raise ValueError("AGENT_DERIVED obligation parent_obligation_id gerektirir")
        if self.origin != ObligationOrigin.AGENT_DERIVED and self.parent_obligation_id is not None:
            raise ValueError("yalnız AGENT_DERIVED obligation parent taşıyabilir")
        if (self.ranking_direction is None) != (self.ranking_limit is None):
            raise ValueError("ranking direction + limit birlikte verilmelidir")
        if (
            self.capability_key == ManagerCapabilityKey.RANKING
            and self.polarity == ObligationPolarity.REQUIRED
        ):
            if self.ranking_direction is None or self.ranking_limit is None:
                raise ValueError("required ranking obligation direction + limit gerektirir")
        elif self.capability_key != ManagerCapabilityKey.RANKING and (
            self.ranking_direction is not None or self.ranking_limit is not None
        ):
            raise ValueError("ranking parameters yalnız ranking obligation için geçerlidir")
        declared_handles = tuple(dict.fromkeys(self.semantic_handle_refs))
        scope_refs = tuple(dict.fromkeys(self.scope_refs))
        if any(ref not in declared_handles for ref in scope_refs):
            raise ValueError("scope_refs must be a subset of semantic_handle_refs")
        if self.semantic_bindings:
            bound_handles = tuple(
                dict.fromkeys(binding.handle_id for binding in self.semantic_bindings)
            )
            source_bound = tuple(
                ref for ref in declared_handles if ref not in set(scope_refs)
            )
            if bound_handles != source_bound:
                raise ValueError(
                    "semantic_bindings must exactly match source-bound semantic_handle_refs"
                )
        return self


class UserIntentEnvelope(FrozenModel):
    attempt_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    request_ref: str = Field(min_length=1)
    source_message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    model_role: str = Field(min_length=1)
    obligations: tuple[CandidateObligation, ...] = Field(min_length=1)
    research_directives: tuple[ResearchDirective, ...] = ()
    unresolved_source_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _unique_authority_items(self):
        ids = [item.obligation_id for item in self.obligations]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate obligation IDs unique olmalı")
        directive_ids = [item.directive_id for item in self.research_directives]
        if len(directive_ids) != len(set(directive_ids)):
            raise ValueError("research directive IDs unique olmalı")
        obligation_ids = set(ids)
        for directive in self.research_directives:
            if directive.parent_obligation_id not in obligation_ids:
                raise ValueError(
                    "research directive parent accepted obligation içinde bulunmalı"
                )
        return self


class ObligationLedgerItem(FrozenModel):
    obligation_id: str
    capability_key: ManagerCapabilityKey
    origin: ObligationOrigin
    parent_obligation_id: str | None = None
    priority: ObligationPriority
    polarity: ObligationPolarity
    status: ObligationStatus
    source_refs: tuple[str, ...]
    semantic_handle_refs: tuple[str, ...] = ()
    semantic_bindings: tuple[SemanticBindingRef, ...] = ()
    scope_refs: tuple[str, ...] = ()
    ranking_direction: Literal["asc", "desc"] | None = None
    ranking_limit: int | None = Field(default=None, ge=1, le=1000)
    evidence_refs: tuple[str, ...] = ()
    verdict: str | None = None
    blocker: str | None = None
    introduced_in_version: int = Field(ge=1)
    superseded_by: str | None = None


class UserObligationLedger(FrozenModel):
    lineage_id: str
    version: int = Field(ge=1)
    items: tuple[ObligationLedgerItem, ...]

    @property
    def active_user_must(self) -> tuple[ObligationLedgerItem, ...]:
        return tuple(
            item
            for item in self.items
            if item.origin == ObligationOrigin.USER_MUST
            and item.priority == ObligationPriority.MUST
            and item.polarity == ObligationPolarity.REQUIRED
            and item.status != ObligationStatus.SUPERSEDED
        )


class AcceptedTurnContract(FrozenModel):
    contract_id: str = Field(min_length=1)
    lineage_id: str = Field(min_length=1)
    contract_schema_version: Literal["day6.5-v1"] = "day6.5-v1"
    version: int = Field(ge=1)
    supersedes_contract_id: str | None = None
    turn_id: str
    request_ref: str
    source_message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    accepted_attempt_id: str
    model_role: str
    obligation_ids: tuple[str, ...]
    exclusion_ids: tuple[str, ...] = ()
    research_directives: tuple[ResearchDirective, ...] = ()
    unresolved_ids: tuple[str, ...] = ()
    context_version: str
    accepted_at_iso: str


class AcceptanceResult(FrozenModel):
    status: AcceptanceStatus
    reasons: tuple[str, ...] = ()
    contract: AcceptedTurnContract | None = None
    ledger: UserObligationLedger | None = None

    @model_validator(mode="after")
    def _accepted_has_contract(self):
        if self.status == AcceptanceStatus.ACCEPTED:
            if self.contract is None or self.ledger is None:
                raise ValueError("ACCEPTED result contract ve ledger gerektirir")
        elif self.contract is not None:
            raise ValueError("non-accepted result authoritative contract taşıyamaz")
        return self


class ManagerState(StrEnum):
    INITIAL = "INITIAL"
    UNDERSTANDING = "UNDERSTANDING"
    CONTRACT_ACCEPTED = "CONTRACT_ACCEPTED"
    INVESTIGATING = "INVESTIGATING"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    BLOCKED = "BLOCKED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class ManagerBudget(FrozenModel):
    # One budget authority with independent phase ceilings plus an outer safety bound.
    # A legitimate preacceptance retry must not consume the post-acceptance Research
    # cognition budget. The outer total remains fail-closed and does not imply normal
    # runs should consume all eight turns.
    max_total_manager_turns: int = Field(
        default=8,
        ge=1,
        description="Outer safety ceiling across preacceptance + Research cognition.",
    )
    max_preacceptance_turns: int = Field(
        default=4,
        ge=1,
        description=(
            "Preacceptance hard ceiling; two bounded draft attempts may each "
            "consume one draft and one Coverage cognition call."
        ),
    )
    max_tool_calls: int = Field(default=12, ge=1)
    max_data_queries: int = Field(default=8, ge=0, le=12)
    max_manager_turns: int = Field(
        default=4,
        ge=1,
        description=(
            "Post-acceptance Research cognition hard ceiling, independent of "
            "preacceptance retries; outer total ceiling still applies."
        ),
    )


class ManagerRunSnapshot(FrozenModel):
    run_id: str
    state: ManagerState
    terminal_status: ResearchRunTerminal | None = None
    accepted_contract_id: str | None = None
    lineage_id: str | None = None
    tool_calls: int = 0
    data_queries: int = 0
    manager_turns: int = 0
    preacceptance_turns: int = 0
    research_manager_turns: int = 0
    evidence_refs: tuple[str, ...] = ()
    inspected_evidence_refs: tuple[str, ...] = ()
    latest_evidence_ref: str | None = None
    last_error: str | None = None


class RepresentabilityResult(FrozenModel):
    decision: RepresentabilityDecision
    reasons: tuple[str, ...] = ()
    standard_capability_keys: tuple[ManagerCapabilityKey, ...] = ()
    research_capability_keys: tuple[ManagerCapabilityKey, ...] = ()
    standard_projection: StandardProjection | None = None
