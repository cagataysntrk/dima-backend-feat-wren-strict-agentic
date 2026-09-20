"""Typed contracts for the greenfield Dima V2 core.

Day 1 deliberately models language-level intent only. Canonical metric/dimension
binding belongs to SemanticResolver; SQL belongs to later execution stages.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class TurnAct(StrEnum):
    ANALYTIC_NEW = "ANALYTIC_NEW"
    ANALYTIC_REFINE = "ANALYTIC_REFINE"
    CLARIFICATION_ANSWER = "CLARIFICATION_ANSWER"
    USER_REPAIR = "USER_REPAIR"
    RESULT_EXPLAIN = "RESULT_EXPLAIN"
    SOCIAL = "SOCIAL"
    UNSUPPORTED = "UNSUPPORTED"
    COMPLEX_ANALYSIS = "COMPLEX_ANALYSIS"
    REPORT_REQUEST = "REPORT_REQUEST"


class SemanticMention(BaseModel):
    """A phrase copied from the user turn, before canonical grounding."""

    surface: str = Field(min_length=1)
    kind_hint: Literal[
        "metric", "dimension", "filter", "entity", "time", "comparison", "ranking", "unknown"
    ] = "unknown"


class ReferenceMention(BaseModel):
    """Conversation reference such as "bunu", "o makine", or "ilk kart"."""

    surface: str = Field(min_length=1)
    target_hint: Literal[
        "result", "artifact", "entity", "time", "topic", "unknown"
    ] = "unknown"


class UnresolvedMention(BaseModel):
    surface: str = Field(min_length=1)
    reason: Literal["ambiguous", "unknown", "reference", "other"] = "unknown"


class RankingIntent(BaseModel):
    direction: Literal["asc", "desc"] | None = None
    limit: int | None = Field(default=None, ge=1)
    surface: str | None = None


class AnalyticalRequest(BaseModel):
    """Surface-language analytical request; contains no canonical IDs."""

    metrics: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)
    time_expressions: list[str] = Field(default_factory=list)
    comparisons: list[str] = Field(default_factory=list)
    ranking: RankingIntent | None = None
    deliverables: list[Literal["answer", "table", "chart", "report"]] = Field(
        default_factory=list
    )


class UserRepair(BaseModel):
    rejected_surface: str | None = None
    replacement_surface: str | None = None


class TurnInterpretation(BaseModel):
    dialogue_act: TurnAct
    mentions: list[SemanticMention] = Field(default_factory=list)
    references: list[ReferenceMention] = Field(default_factory=list)
    analytical_request: AnalyticalRequest | None = None
    presentation_request: list[Literal["table", "chart", "report"]] = Field(
        default_factory=list
    )
    user_repair: UserRepair | None = None
    unresolved: list[UnresolvedMention] = Field(default_factory=list)


class SemanticCandidate(BaseModel):
    canonical_ref: str
    label: str
    provenance: Literal[
        "explicit_anchor",
        "current_focus",
        "canonical_name",
        "verified_synonym",
        "exact_entity_value",
        "company_vocabulary",
        "fuzzy_suggestion",
    ]
    confidence_class: Literal["strong", "suggestion"]


class ClarificationState(BaseModel):
    mention_surface: str
    question: str
    candidates: list[SemanticCandidate]
    blocking: bool = True


class RequirementState(StrEnum):
    DETECTED = "DETECTED"
    RESOLVED = "RESOLVED"
    REPRESENTED_IN_IR = "REPRESENTED_IN_IR"
    REPRESENTED_IN_PLAN = "REPRESENTED_IN_PLAN"
    VERIFIED = "VERIFIED"


class Requirement(BaseModel):
    kind: Literal[
        "metric", "dimension", "filter", "time", "ranking", "limit", "comparison", "deliverable"
    ]
    source_text: str
    must: bool = True
    state: RequirementState = RequirementState.DETECTED


class AnalyticsIR(BaseModel):
    """Canonical analytical request produced only after semantic grounding."""

    metrics: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: list[dict[str, Any]] = Field(default_factory=list)
    time: dict[str, Any] | None = None
    ranking: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None


class ConversationStateV2(BaseModel):
    topic_frame: dict[str, Any] | None = None
    focus_state: dict[str, Any] | None = None
    clarification: ClarificationState | None = None
    last_contract_id: str | None = None
    last_ir: AnalyticsIR | None = None
    active_research_run_id: str | None = None


class ContextVersionV0(BaseModel):
    mdl_version: str
    compact_catalog_builder_version: str
    business_rules_hash: str
    prompt_context_policy_version: str
    value: str


class TenantAnalyticsRuntime(BaseModel):
    tenant_id: str | None = None
    tenant_slug: str | None = None
    principal_user_id: str
    roles: tuple[str, ...] = ()
    connection_id: str | None = None
    mdl_version: str
    context_version: str
    fiscal_year_start_month: int | None = None
    timezone: str | None = None


class CompactSemanticContext(BaseModel):
    runtime: TenantAnalyticsRuntime
    context_version: ContextVersionV0
    catalog: dict[str, Any]
    db_online: bool = True


class AskV2Request(BaseModel):
    question: str = Field(min_length=1)
    history: list[str] = Field(default_factory=list)
    session_id: str | None = None
    thread_id: str | None = None


class AskV2Response(BaseModel):
    status: Literal["interpreted"] = "interpreted"
    stage: Literal["turn_interpretation"] = "turn_interpretation"
    turn: TurnInterpretation
    mdl_version: str
    context_version: str
    query_executed: bool = False
