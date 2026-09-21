"""Typed contracts for the greenfield Dima V2 core.

Day 1 owns language understanding only. Canonical semantic binding is deliberately
absent from TurnInterpretation; that becomes the SemanticResolver's job on Day 2.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

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
    kpis: tuple[CompactSemanticFieldV0, ...] = ()
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


class CandidateSource(StrEnum):
    EXPLICIT_ANCHOR = "explicit_anchor"
    CURRENT_FOCUS = "current_focus"
    CANONICAL_NAME = "canonical_name"
    VERIFIED_SYNONYM = "verified_synonym"
    EXACT_ENTITY_VALUE = "exact_entity_value"
    COMPANY_VOCABULARY = "company_vocabulary"
    FUZZY_SUGGESTION = "fuzzy_suggestion"


class SemanticTargetKind(StrEnum):
    METRIC = "metric"
    DIMENSION = "dimension"
    ENTITY_VALUE = "entity_value"
    KPI = "kpi"
    CUBE = "cube"


class ResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    CLARIFY = "clarify"
    SEMANTIC_GAP = "semantic_gap"


class ClarificationReason(StrEnum):
    MATERIAL_AMBIGUITY = "material_ambiguity"
    FUZZY_ONLY = "fuzzy_only"
    SEMANTIC_GAP = "semantic_gap"


class SemanticAnchor(FrozenModel):
    """Typed conversation anchor. Labels alone never become semantic truth."""

    target_kind: SemanticTargetKind
    canonical_name: str
    dimension_name: str | None = None
    value: str | None = None
    display_label: str | None = None
    aliases: tuple[str, ...] = ()
    sensitive: bool = False


class SemanticCandidate(FrozenModel):
    candidate_id: str
    target_kind: SemanticTargetKind
    canonical_name: str
    dimension_name: str | None = None
    value: str | None = None
    cube_names: tuple[str, ...] = ()
    display_label: str
    provenance: tuple[CandidateSource, ...]
    score: float = Field(ge=0.0, le=1.0)
    material: bool = False
    sensitive: bool = False
    selection_aliases: tuple[str, ...] = ()


class SemanticHypothesis(FrozenModel):
    source_mention: str
    mention_kind: SemanticMentionKind
    status: ResolutionStatus
    candidates: tuple[SemanticCandidate, ...] = ()
    resolved_candidate_id: str | None = None
    resolved_surface_value: str | None = None


class ClarificationChip(FrozenModel):
    candidate_id: str
    label: str
    token: str


class ClarificationState(FrozenModel):
    pending: bool = False
    clarification_id: str | None = None
    source_mention: str | None = None
    source_kind: SemanticMentionKind | None = None
    reason: ClarificationReason | None = None
    question: str | None = None
    candidates: tuple[SemanticCandidate, ...] = ()
    chips: tuple[ClarificationChip, ...] = ()


class Requirement(FrozenModel):
    """Day 1 compatibility marker; Day 3 uses RequirementLedgerItem for lifecycle state."""

    kind: SemanticMentionKind
    must: bool = True


class RequirementKind(StrEnum):
    METRIC = "metric"
    DIMENSION = "dimension"
    FILTER = "filter"
    TIME = "time"
    RANKING_DIRECTION = "ranking_direction"
    LIMIT = "limit"
    COMPARISON = "comparison"


class RequirementState(StrEnum):
    DETECTED = "DETECTED"
    RESOLVED = "RESOLVED"
    REPRESENTED_IN_IR = "REPRESENTED_IN_IR"
    REPRESENTED_IN_PLAN = "REPRESENTED_IN_PLAN"
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"


class PeriodKind(StrEnum):
    THIS_MONTH = "this_month"
    THIS_YEAR = "this_year"
    LAST_N_DAYS = "last_n_days"
    LAST_N_MONTHS = "last_n_months"
    PREVIOUS_MONTH = "previous_month"
    PREVIOUS_YEAR = "previous_year"


class ResolvedSemanticRef(FrozenModel):
    candidate_id: str
    target_kind: SemanticTargetKind
    canonical_name: str
    cube_names: tuple[str, ...] = ()


class ResolvedFilterRef(FrozenModel):
    candidate_id: str
    dimension_name: str
    value: str
    cube_names: tuple[str, ...] = ()
    sensitive: bool = False


class ResolvedPeriod(FrozenModel):
    kind: PeriodKind
    source_text: str
    time_dimension: str
    start: str
    end: str | None = None
    n: int | None = None


class ResolvedRanking(FrozenModel):
    measure: str
    direction: Literal["asc", "desc"]
    limit: int = Field(ge=1, le=1000)


class ResolvedComparison(FrozenModel):
    mode: Literal["previous_period"]
    source_text: str
    base_period: ResolvedPeriod
    reference_period: ResolvedPeriod


class RequirementLedgerItem(FrozenModel):
    requirement_id: str
    kind: RequirementKind
    source_text: str
    must: bool = True
    state: RequirementState = RequirementState.DETECTED
    history: tuple[RequirementState, ...] = (RequirementState.DETECTED,)
    detail: str | None = None


class RequirementLedger(FrozenModel):
    items: tuple[RequirementLedgerItem, ...] = ()

    @property
    def all_must_verified(self) -> bool:
        return all(
            (not item.must) or item.state == RequirementState.VERIFIED
            for item in self.items
        )


class AnalyticsIR(FrozenModel):
    """Canonical standard-analytics request. No raw-question semantic selection lives here."""

    # Compatibility surface retained for Day 1 imports/tests.
    requirements: tuple[Requirement, ...] = ()
    cube: str
    metrics: tuple[ResolvedSemanticRef, ...]
    dimensions: tuple[ResolvedSemanticRef, ...] = ()
    filters: tuple[ResolvedFilterRef, ...] = ()
    period: ResolvedPeriod | None = None
    ranking: ResolvedRanking | None = None
    comparison: ResolvedComparison | None = None
    context_version: str


class ConversationStateV2(FrozenModel):
    """Bounded context supplied to TurnInterpreter; persistence arrives on Day 4."""

    has_prior_analytical_request: bool = False
    has_active_result: bool = False
    pending_clarification: bool = False
    topic_labels: tuple[str, ...] = ()
    focus_labels: tuple[str, ...] = ()
    selected_anchor_label: str | None = None
    selected_anchor: SemanticAnchor | None = None
    focus_anchors: tuple[SemanticAnchor, ...] = ()
    clarification_state: ClarificationState | None = None


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
    clarification_token: str | None = None


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



# ---------------------------------------------------------------------------
# Day 2 semantic grounding / clarification
# ---------------------------------------------------------------------------


class SemanticResolutionBundle(FrozenModel):
    hypotheses: tuple[SemanticHypothesis, ...] = ()
    clarification: ClarificationState | None = None

    @property
    def semantic_status(self) -> str:
        if self.clarification is not None:
            return (
                "semantic_gap"
                if self.clarification.reason == ClarificationReason.SEMANTIC_GAP
                else "clarification_required"
            )
        return "resolved"


class AskV2Day2Response(FrozenModel):
    status: Literal["interpreted"] = "interpreted"
    stage: Literal["day2_semantic_grounding"] = "day2_semantic_grounding"
    semantic_status: Literal[
        "resolved",
        "clarification_required",
        "semantic_gap",
        "not_applicable",
    ]
    runtime: TenantAnalyticsRuntimeV0
    context_version: ContextVersionV0
    turn: TurnInterpretation | None = None
    hypotheses: tuple[SemanticHypothesis, ...] = ()
    clarification: ClarificationState | None = None
    resumed_by: Literal["signed_chip", "free_text"] | None = None
    session_id: str | None = None
    thread_id: str | None = None
    query_executed: Literal[False] = False
    sql_generated: Literal[False] = False
    legacy_semantic_path_called: Literal[False] = False
    next_stage: Literal[
        "analytics_ir_day3",
        "clarification_resume_day2",
        "conversation_policy_future",
    ]



# ---------------------------------------------------------------------------
# Day 3 standard analytics / execution evidence
# ---------------------------------------------------------------------------


class StandardAnalyticsFailure(FrozenModel):
    code: Literal[
        "not_analytic_turn",
        "semantic_not_resolved",
        "missing_metric",
        "unsupported_kpi",
        "no_viable_cube",
        "ambiguous_cube",
        "missing_time_axis",
        "ambiguous_time_axis",
        "unsupported_time",
        "unsupported_comparison",
        "ranking_incomplete",
        "plan_validation_failed",
        "dry_plan_failed",
        "query_failed",
        "result_validation_failed",
        "contract_seal_failed",
        "context_version_mismatch",
    ]
    stage: Literal[
        "policy",
        "ir",
        "temporal",
        "planner",
        "dry_plan",
        "execution",
        "result_validation",
        "contract",
    ]
    message: str


class PlannedExecution(FrozenModel):
    execution_id: str
    role: Literal["primary", "comparison_reference"] = "primary"
    cube_query: dict[str, Any]
    sql: str


class ExecutionResultV0(FrozenModel):
    execution_id: str
    role: Literal["primary", "comparison_reference"]
    columns: tuple[str, ...] = ()
    rows: tuple[dict[str, Any], ...] = ()
    row_count: int = 0
    column_types: tuple[str, ...] = ()
    verified: bool = False
    verification_errors: tuple[str, ...] = ()


class MinimumQueryContract(FrozenModel):
    contract_id: str
    execution_id: str
    request_ref: str
    planner_id: str
    planner_version: str
    mdl_version: str
    context_version: str
    executed_sql: str
    result_hash: str | None = None
    tenant_id: str | None = None
    principal_user_id: str
    principal_roles: tuple[str, ...] = ()
    cube_query: dict[str, Any]
    analytics_ir: dict[str, Any]
    durability: Literal["db", "spool_pending", "none"]
    sealed: bool


class AskV2Day3Response(FrozenModel):
    status: Literal["standard_analytics"] = "standard_analytics"
    stage: Literal["day3_standard_analytics"] = "day3_standard_analytics"
    semantic_status: Literal[
        "resolved",
        "clarification_required",
        "semantic_gap",
        "not_applicable",
    ]
    analytics_status: Literal[
        "verified",
        "not_executable",
        "not_applicable",
        "failed",
    ]
    official_verified: bool = False
    runtime: TenantAnalyticsRuntimeV0
    context_version: ContextVersionV0
    turn: TurnInterpretation | None = None
    hypotheses: tuple[SemanticHypothesis, ...] = ()
    clarification: ClarificationState | None = None
    analytics_ir: AnalyticsIR | None = None
    ledger: RequirementLedger | None = None
    executions: tuple[ExecutionResultV0, ...] = ()
    query_contracts: tuple[MinimumQueryContract, ...] = ()
    failure: StandardAnalyticsFailure | None = None
    resumed_by: Literal["signed_chip", "free_text"] | None = None
    session_id: str | None = None
    thread_id: str | None = None
    legacy_semantic_path_called: Literal[False] = False
    next_stage: Literal[
        "conversation_day4",
        "clarification_resume_day2",
        "standard_analytics_retry",
    ]
