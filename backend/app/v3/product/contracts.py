"""Stable headless product contracts for Core Closure B.

These DTOs are deliberate consumer contracts. They are not SQLModel rows and
carry no analytical or business-truth authority of their own.
"""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PRODUCT_CONTRACT_VERSION = "core-b-product-v1"


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProductErrorCode(StrEnum):
    UNAVAILABLE = "UNAVAILABLE"
    FORBIDDEN = "FORBIDDEN"
    STALE = "STALE"
    SUPERSEDED = "SUPERSEDED"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    INCONCLUSIVE = "INCONCLUSIVE"
    DEFERRED_CAPABILITY = "DEFERRED_CAPABILITY"
    UNKNOWN_OUTCOME = "UNKNOWN_OUTCOME"


class ProductCurrentness(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    SUPERSEDED = "SUPERSEDED"
    HISTORICAL = "HISTORICAL"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNKNOWN = "UNKNOWN"


class CapabilityStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    FOUNDATION_ONLY = "FOUNDATION_ONLY"
    DATA_DEPENDENT = "DATA_DEPENDENT"
    SPECIAL_ENGINE_DEFERRED = "SPECIAL_ENGINE_DEFERRED"
    PRODUCTIZATION_DEFERRED = "PRODUCTIZATION_DEFERRED"


class ArtifactKind(StrEnum):
    WATCH = "WATCH"
    SIGNAL = "SIGNAL"
    RESEARCH = "RESEARCH"
    INVESTIGATION = "INVESTIGATION"
    EVIDENCE = "EVIDENCE"
    EPISTEMIC_ASSESSMENT = "EPISTEMIC_ASSESSMENT"
    REPORT = "REPORT"
    DECISION = "DECISION"
    ADOPTION = "ADOPTION"
    ACTION_WORK = "ACTION_WORK"
    OUTCOME = "OUTCOME"
    MEMORY = "MEMORY"


class ArtifactRef(Frozen):
    kind: ArtifactKind
    artifact_id: str = Field(min_length=1)
    scope_id: str | None = None


class CapabilityDescriptor(Frozen):
    capability_id: str = Field(min_length=1)
    status: CapabilityStatus
    reason: str = Field(min_length=1)
    required_data: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()


class CapabilityDiscovery(Frozen):
    product_contract_version: Literal["core-b-product-v1"] = PRODUCT_CONTRACT_VERSION
    context_id: str = Field(pattern=r"^ctx_[a-f0-9]{24}$")
    capabilities: tuple[CapabilityDescriptor, ...]
    catalog_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class CompanyContext(Frozen):
    product_contract_version: Literal["core-b-product-v1"] = PRODUCT_CONTRACT_VERSION
    context_id: str = Field(pattern=r"^ctx_[a-f0-9]{24}$")
    tenant_binding: str = Field(min_length=1)
    company_identity: str = Field(min_length=1)
    analytical_engine: Literal["metabase-metabot"] = "metabase-metabot"
    analytical_context_available: bool
    sector_pack_refs: tuple[str, ...] = ()
    entity_refs: tuple[str, ...] = ()
    capability_discovery: CapabilityDiscovery
    deep_link_id: str = Field(min_length=1)


class ArtifactHeader(Frozen):
    product_contract_version: Literal["core-b-product-v1"] = PRODUCT_CONTRACT_VERSION
    kind: ArtifactKind
    artifact_id: str = Field(min_length=1)
    tenant_binding: str = Field(min_length=1)
    currentness: ProductCurrentness
    deep_link_id: str = Field(min_length=1)
    created_at: datetime | None = None
    revision: int | None = Field(default=None, ge=1)
    lineage_refs: tuple[ArtifactRef, ...] = ()
    terminal_state: str | None = None
    fingerprint: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


class ResearchDTO(Frozen):
    header: ArtifactHeader
    objective: str
    stopping_status: str
    stopping_reason: str | None = None
    obligation_states: tuple[tuple[str, str], ...]
    evidence_ids: tuple[str, ...]
    limitation_codes: tuple[str, ...]


class WatchDTO(Frozen):
    header: ArtifactHeader
    title: str
    kind: str
    source_contract_ref: str
    criterion_ref: str
    entity_refs: tuple[str, ...]
    metric_refs: tuple[str, ...]


class SignalDTO(Frozen):
    header: ArtifactHeader
    watch_id: str
    severity: str
    status: str
    business_significance: str
    source_ref: str
    research_session_id: str | None = None
    action_work_id: str | None = None
    memory_entry_id: str | None = None


class InvestigationDTO(Frozen):
    header: ArtifactHeader
    research_session_id: str
    reasoning_step_ids: tuple[str, ...]
    task_ids: tuple[str, ...]
    active_task_ids: tuple[str, ...]
    stop_reasons: tuple[str, ...]


class EvidenceDTO(Frozen):
    header: ArtifactHeader
    authority_id: str
    obligation_ids: tuple[str, ...]
    evidence_kind: str
    state: str
    receipt_refs: tuple[str, ...]
    limitations: tuple[str, ...]


class EpistemicAssessmentDTO(Frozen):
    header: ArtifactHeader
    research_session_id: str
    obligation_id: str
    aggregate_outcome: str
    root_cause_hypothesis_ids: tuple[str, ...]
    candidate_hypothesis_ids: tuple[str, ...]
    limitations: tuple[str, ...]


class ReportDTO(Frozen):
    header: ArtifactHeader
    research_session_id: str
    report_key: str
    statement_ids: tuple[str, ...]
    limitation_ids: tuple[str, ...]
    coverage: tuple[tuple[str, str], ...]


class DecisionDTO(Frozen):
    header: ArtifactHeader
    report_id: str
    brief_key: str
    objective_text: str
    option_ids: tuple[str, ...]
    recommended_option_ids: tuple[str, ...]
    limitation_ids: tuple[str, ...]


class AdoptionDTO(Frozen):
    header: ArtifactHeader
    decision_brief_id: str
    disposition: str
    selected_option_ids: tuple[str, ...]
    actor_user_id: str
    human_conditions: tuple[str, ...]


class ActionWorkDTO(Frozen):
    header: ArtifactHeader
    decision_adoption_id: str
    title: str
    owner_user_id: str
    due_at: datetime | None
    status: str
    blocker_reason: str | None = None
    completion_reference: str | None = None


class OutcomeDTO(Frozen):
    header: ArtifactHeader
    action_work_id: str
    classification: str
    baseline_definition: str
    baseline_window: str
    observation_window: str
    evidence_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    report_id: str | None = None
    limitations: tuple[str, ...]


class MemoryDTO(Frozen):
    header: ArtifactHeader
    role: str
    problem_type: str
    domain: str
    entity_refs: tuple[str, ...]
    metric_refs: tuple[str, ...]
    summary: str
    limitations: tuple[str, ...]


ProductArtifact = (
    ResearchDTO
    | WatchDTO
    | SignalDTO
    | InvestigationDTO
    | EvidenceDTO
    | EpistemicAssessmentDTO
    | ReportDTO
    | DecisionDTO
    | AdoptionDTO
    | ActionWorkDTO
    | OutcomeDTO
    | MemoryDTO
)


class ArtifactPage(Frozen):
    items: tuple[ProductArtifact, ...]
    next_cursor: str | None = None
    total_visible: int = Field(ge=0)


class TimelineItem(Frozen):
    ordinal: int = Field(ge=1)
    ref: ArtifactRef
    currentness: ProductCurrentness
    occurred_at: datetime | None = None
    terminal_state: str | None = None
    lineage_refs: tuple[ArtifactRef, ...] = ()


class ArtifactTimeline(Frozen):
    context_id: str = Field(pattern=r"^ctx_[a-f0-9]{24}$")
    items: tuple[TimelineItem, ...]
    next_cursor: str | None = None


class OperationTrace(Frozen):
    correlation_id: str = Field(min_length=1)
    tenant_binding: str = Field(min_length=1)
    principal_subject: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    owner_calls: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    terminal_state: str
    failure_class: ProductErrorCode | None = None


class ClosedLoopProjection(Frozen):
    context: CompanyContext
    stages: tuple[ProductArtifact, ...]
    timeline: ArtifactTimeline
    trace: OperationTrace
    complete_stage_kinds: tuple[ArtifactKind, ...]

    @model_validator(mode="after")
    def ordered_unique_stage_kinds(self):
        if len(self.complete_stage_kinds) != len(set(self.complete_stage_kinds)):
            raise ValueError("closed-loop stage kinds must be unique")
        return self
