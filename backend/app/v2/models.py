"""Typed contracts for the greenfield Dima V2 core.

Day 1 owns language understanding only. Canonical semantic binding is deliberately
absent from TurnInterpretation; that becomes the SemanticResolver's job on Day 2.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ---------------------------------------------------------------------------
# Day 0 runtime boundary
# ---------------------------------------------------------------------------


class AskV2BootstrapRequest(FrozenModel):
    """Historical Day 0 envelope kept for boundary-level tests/tools."""

    question: str = Field(min_length=1)
    session_id: str | None = None
    thread_id: str | None = None


class TenantAnalyticsRuntimeV0(FrozenModel):
    """Immutable identity + semantic-engine snapshot for one V2 request."""

    tenant_id: str | None = None
    tenant_slug: str | None = None
    principal_user_id: str
    roles: tuple[str, ...] = ()
    mdl_version: str
    catalog: str | None = None
    schema_name: str | None = None
    db_online: bool


class AskV2BootstrapResponse(FrozenModel):
    status: Literal["bootstrap_ready"] = "bootstrap_ready"
    stage: Literal["day0_runtime_boundary"] = "day0_runtime_boundary"
    runtime: TenantAnalyticsRuntimeV0
    session_id: str | None = None
    thread_id: str | None = None
    query_executed: Literal[False] = False
    llm_called: Literal[False] = False
    legacy_semantic_path_called: Literal[False] = False
    next_stage: Literal["turn_interpreter_day1"] = "turn_interpreter_day1"


# ---------------------------------------------------------------------------
# Day 1 bounded semantic context + provenance
# ---------------------------------------------------------------------------


class ContextVersionV0(FrozenModel):
    version: str
    mdl_version: str
    compact_catalog_builder_version: str
    business_rules_hash: str
    prompt_context_policy_version: str


class CompactSemanticFieldV0(FrozenModel):
    canonical_name: str
    display: str | None = None
    description: str | None = None
    synonyms: tuple[str, ...] = ()
    unit: str | None = None


class CompactCubeContextV0(FrozenModel):
    canonical_name: str
    display: str | None = None
    description: str | None = None
    synonyms: tuple[str, ...] = ()
    measures: tuple[CompactSemanticFieldV0, ...] = ()
    dimensions: tuple[CompactSemanticFieldV0, ...] = ()
    time_dimensions: tuple[str, ...] = ()


class CompactRelationshipV0(FrozenModel):
    name: str
    models: tuple[str, ...] = ()
    join_type: str | None = None
    certified: str | None = None


class BoundedSemanticContextV0(FrozenModel):
    context_version: ContextVersionV0
    cubes: tuple[CompactCubeContextV0, ...] = ()
    relationships: tuple[CompactRelationshipV0, ...] = ()
    approved_business_rules: str = ""
    business_rules_truncated: bool = False


# ---------------------------------------------------------------------------
# Day 1 conversation/language contracts
# ---------------------------------------------------------------------------


class TurnAct(StrEnum):
    ANALYTIC_NEW = "ANALYTIC_NEW"
    ANALYTIC_REFINE = "ANALYTIC_REFINE"
    CLARIFICATION_ANSWER = "CLARIFICATION_ANSWER"
    USER_REPAIR = "USER_REPAIR"
    RESULT_EXPLAIN = "RESULT_EXPLAIN"
    SOCIAL = "SOCIAL"
    UNSUPPORTED = "UNSUPPORTED"


class SemanticMentionKind(StrEnum):
    METRIC = "metric"
    DIMENSION = "dimension"
    FILTER = "filter"
    TIME = "time"
    RANKING = "ranking"
    COMPARISON = "comparison"
    UNKNOWN = "unknown"


class ReferenceKind(StrEnum):
    PRIOR_RESULT = "prior_result"
    PRIOR_REQUEST = "prior_request"
    SELECTED_ANCHOR = "selected_anchor"
    PENDING_CLARIFICATION = "pending_clarification"
    UNKNOWN = "unknown"


class PresentationKind(StrEnum):
    EXPLAIN = "explain"
    TABLE = "table"
    CHART = "chart"
    REPORT = "report"
    NONE = "none"


class SemanticMention(FrozenModel):
    """Exact surface span copied from the current user message.

    No canonical metric/dimension/entity identifier exists in this contract by design.
    """

    text: str = Field(min_length=1)
    kind: SemanticMentionKind


class ReferenceMention(FrozenModel):
    text: str = Field(min_length=1)
    kind: ReferenceKind = ReferenceKind.UNKNOWN


class UnresolvedMention(FrozenModel):
    text: str = Field(min_length=1)
    reason: str = Field(min_length=1, max_length=240)


class RankingSurface(FrozenModel):
    text: str = Field(min_length=1)
    direction: Literal["asc", "desc", "unspecified"] = "unspecified"
    limit: int | None = Field(default=None, ge=1, le=1000)


class ComparisonSurface(FrozenModel):
    text: str = Field(min_length=1)


class AnalyticalRequest(FrozenModel):
    """Language-level request only; canonical semantic resolution is intentionally absent."""

    metric_mentions: tuple[SemanticMention, ...] = ()
    dimension_mentions: tuple[SemanticMention, ...] = ()
    filter_mentions: tuple[SemanticMention, ...] = ()
    time_mentions: tuple[SemanticMention, ...] = ()
    ranking: RankingSurface | None = None
    comparisons: tuple[ComparisonSurface, ...] = ()


class UserRepair(FrozenModel):
    """Surface-level correction signal. Prior semantic slots are not mutated on Day 1."""

    correction_spans: tuple[str, ...] = ()


class ConversationStateV2(FrozenModel):
    """Bounded context supplied to TurnInterpreter; persistence arrives on Day 4."""

    has_prior_analytical_request: bool = False
    has_active_result: bool = False
    pending_clarification: bool = False
    topic_labels: tuple[str, ...] = ()
    focus_labels: tuple[str, ...] = ()
    selected_anchor_label: str | None = None


class TurnInterpretation(FrozenModel):
    dialogue_act: TurnAct
    references: tuple[ReferenceMention, ...] = ()
    analytical_request: AnalyticalRequest | None = None
    presentation_request: PresentationKind = PresentationKind.NONE
    user_repair: UserRepair | None = None
    unresolved_mentions: tuple[UnresolvedMention, ...] = ()


class AskV2Request(FrozenModel):
    question: str = Field(min_length=1)
    session_id: str | None = None
    thread_id: str | None = None
    conversation: ConversationStateV2 = Field(default_factory=ConversationStateV2)


class TurnInterpretationFailure(FrozenModel):
    code: Literal[
        "llm_unavailable",
        "invalid_structured_output",
        "surface_grounding_violation",
    ]
    message: str


class AskV2Day1Response(FrozenModel):
    status: Literal["interpreted"] = "interpreted"
    stage: Literal["day1_turn_interpreter"] = "day1_turn_interpreter"
    runtime: TenantAnalyticsRuntimeV0
    context_version: ContextVersionV0
    turn: TurnInterpretation
    session_id: str | None = None
    thread_id: str | None = None
    query_executed: Literal[False] = False
    sql_generated: Literal[False] = False
    legacy_semantic_path_called: Literal[False] = False
    next_stage: Literal["semantic_resolver_day2"] = "semantic_resolver_day2"
