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
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"


class ResearchRunTerminal(StrEnum):
    VERIFIED_COMPLETE = "VERIFIED_COMPLETE"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


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
    sensitive: bool = False


class CandidateObligation(FrozenModel):
    obligation_id: str = Field(min_length=1)
    capability_key: ManagerCapabilityKey
    origin: ObligationOrigin
    parent_obligation_id: str | None = None
    priority: ObligationPriority = ObligationPriority.MUST
    polarity: ObligationPolarity = ObligationPolarity.REQUIRED
    source_refs: tuple[str, ...] = Field(min_length=1)
    semantic_handle_refs: tuple[str, ...] = ()
    scope_refs: tuple[str, ...] = ()
    open_questions: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _origin_contract(self):
        if self.origin == ObligationOrigin.AGENT_DERIVED and not self.parent_obligation_id:
            raise ValueError("AGENT_DERIVED obligation parent_obligation_id gerektirir")
        if self.origin != ObligationOrigin.AGENT_DERIVED and self.parent_obligation_id is not None:
            raise ValueError("yalnız AGENT_DERIVED obligation parent taşıyabilir")
        return self


class UserIntentEnvelope(FrozenModel):
    attempt_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    request_ref: str = Field(min_length=1)
    source_message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    model_role: str = Field(min_length=1)
    obligations: tuple[CandidateObligation, ...] = Field(min_length=1)
    unresolved_source_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _unique_obligations(self):
        ids = [item.obligation_id for item in self.obligations]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate obligation IDs unique olmalı")
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
    max_tool_calls: int = Field(default=12, ge=1)
    max_data_queries: int = Field(default=8, ge=0)
    max_manager_turns: int = Field(default=8, ge=1)


class ManagerRunSnapshot(FrozenModel):
    run_id: str
    state: ManagerState
    accepted_contract_id: str | None = None
    lineage_id: str | None = None
    tool_calls: int = 0
    data_queries: int = 0
    manager_turns: int = 0
    evidence_refs: tuple[str, ...] = ()
    last_error: str | None = None


class RepresentabilityResult(FrozenModel):
    decision: RepresentabilityDecision
    reasons: tuple[str, ...] = ()
    standard_capability_keys: tuple[ManagerCapabilityKey, ...] = ()
    research_capability_keys: tuple[ManagerCapabilityKey, ...] = ()
