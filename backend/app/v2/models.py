"""Typed contracts for the greenfield Dima V2 core.

Day 1 owns language understanding only. Canonical semantic binding is deliberately
absent from TurnInterpretation; that becomes the SemanticResolver's job on Day 2.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    # Semantic cube-level availability only. No join condition/grain proof lives here;
    # Day 7 CrossDomainJoinGate remains execution authority.
    cube_names: tuple[str, ...] = ()
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
    COMPLEX_ANALYSIS = "COMPLEX_ANALYSIS"
    REPORT_REQUEST = "REPORT_REQUEST"
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
    """Language-level delta/request only; canonical semantic resolution is absent.

    A dimension mention denotes a grouping/breakdown axis. A filter mention denotes a
    concrete member/value used to narrow scope. On REFINE/REPAIR turns only the slots
    explicitly changed or added in the current message belong here.
    """

    metric_mentions: tuple[SemanticMention, ...] = Field(
        default=(),
        description="Metric surface spans explicitly mentioned in the current message.",
    )
    dimension_mentions: tuple[SemanticMention, ...] = Field(
        default=(),
        description=(
            "Grouping/breakdown axis surfaces only; not a concrete selected member/value."
        ),
    )
    filter_mentions: tuple[SemanticMention, ...] = Field(
        default=(),
        description=(
            "Concrete member/value/identifier surfaces that narrow scope; do not duplicate "
            "the same selected member as a dimension unless grouping is also explicitly requested."
        ),
    )
    time_mentions: tuple[SemanticMention, ...] = Field(
        default=(),
        description="Current-message time/period surfaces only; no date arithmetic.",
    )
    ranking: RankingSurface | None = None
    comparisons: tuple[ComparisonSurface, ...] = ()



class ResearchGoalKind(StrEnum):
    COMPARISON = "comparison"
    RELATIONSHIP = "relationship"
    PERFORMANCE = "performance"
    TREND = "trend"
    BREAKDOWN = "breakdown"
    RANKING = "ranking"
    ROOT_CAUSE = "root_cause"
    OTHER = "other"


class ResearchNonRelationshipGoalKind(StrEnum):
    COMPARISON = "comparison"
    PERFORMANCE = "performance"
    TREND = "trend"
    BREAKDOWN = "breakdown"
    RANKING = "ranking"
    ROOT_CAUSE = "root_cause"
    OTHER = "other"


class ResearchGoalSurface(FrozenModel):
    """One explicit non-relationship analytical operation.

    Relationship edges use ResearchRelationshipSurface. Standard-capable ranking and
    comparison carry the exact typed Core payload required for lossless projection;
    routing never reparses `text`.
    """

    kind: ResearchNonRelationshipGoalKind
    text: str = Field(min_length=1)
    subject_mentions: tuple[SemanticMention, ...] = ()
    related_mentions: tuple[SemanticMention, ...] = ()
    ranking: RankingSurface | None = None
    comparisons: tuple[ComparisonSurface, ...] = ()

    @model_validator(mode="after")
    def _operation_shape_invariants(self):
        if self.kind == ResearchNonRelationshipGoalKind.RANKING:
            if self.ranking is None:
                raise ValueError("ranking operation requires typed ranking payload")
        elif self.ranking is not None:
            raise ValueError("ranking payload is valid only for ranking operation")

        if self.kind == ResearchNonRelationshipGoalKind.COMPARISON:
            if len(self.comparisons) > 1:
                raise ValueError(
                    "comparison operation may carry at most one Core comparison surface"
                )
        elif self.comparisons:
            raise ValueError(
                "comparison payload is valid only for comparison operation"
            )
        return self


class ResearchRelationshipSurface(FrozenModel):
    """One relationship request with one focus and one-or-more counterparts.

    The focus may be an exact earlier surface from the same current message (coreference
    resolution is language-owner work). Builder expands each counterpart into one
    atomic ResearchQuestion. Missing focus is preserved and becomes BLOCKED; it is
    never guessed downstream.
    """

    text: str = Field(min_length=1)
    focus_mentions: tuple[SemanticMention, ...] = Field(default=(), max_length=1)
    counterpart_mentions: tuple[SemanticMention, ...] = Field(min_length=1)


class ResearchOperationPolarity(StrEnum):
    REQUESTED = "requested"
    EXCLUDED = "excluded"


class ResearchFocusBinding(StrEnum):
    EXPLICIT = "explicit"
    ANTECEDENT = "antecedent"
    UNRESOLVED = "unresolved"


class ResearchSourceSurface(FrozenModel):
    """One source-grounded semantic surface emitted once for the whole research graph."""

    surface_id: str = Field(
        min_length=1,
        description="Local ID unique only inside this current-message research graph.",
    )
    text: str = Field(
        min_length=1,
        description="Exact CURRENT_MESSAGE surface span; never a canonical semantic ID.",
    )
    semantic_role: SemanticMentionKind = Field(
        description="Language role of this surface, not an analytical operation kind."
    )


class ResearchOperationFrame(FrozenModel):
    """Flat tagged analytical operation for provider-facing structured output.

    One enum field owns analytical capability classification. Operation-specific
    payload rules are validated here so the provider schema does not need a deeply
    nested anyOf/oneOf tree.
    """

    operation: ResearchNonRelationshipGoalKind = Field(
        description="Analytical capability; never a metric/dimension/entity role."
    )
    evidence_text: str = Field(
        min_length=1,
        description="Exact CURRENT_MESSAGE span evidencing this analytical operation.",
    )
    subject_refs: tuple[str, ...] = ()
    related_refs: tuple[str, ...] = ()
    ranking: RankingSurface | None = None
    comparisons: tuple[ComparisonSurface, ...] = Field(default=(), max_length=1)
    outcome_ref: str | None = None
    factor_refs: tuple[str, ...] = ()
    polarity: ResearchOperationPolarity

    @model_validator(mode="after")
    def _operation_contract(self):
        if self.operation == ResearchNonRelationshipGoalKind.ROOT_CAUSE:
            if self.outcome_ref is None:
                raise ValueError("root_cause operation requires outcome_ref")
            if self.subject_refs or self.related_refs:
                raise ValueError(
                    "root_cause uses outcome_ref/factor_refs, not subject/related refs"
                )
        elif self.outcome_ref is not None or self.factor_refs:
            raise ValueError(
                "outcome_ref/factor_refs are valid only for root_cause operation"
            )

        if self.operation == ResearchNonRelationshipGoalKind.RANKING:
            if self.ranking is None:
                raise ValueError("ranking operation requires typed ranking payload")
        elif self.ranking is not None:
            raise ValueError("ranking payload is valid only for ranking operation")

        if self.operation != ResearchNonRelationshipGoalKind.COMPARISON and self.comparisons:
            raise ValueError(
                "comparison payload is valid only for comparison operation"
            )
        return self


class ResearchRelationshipFrame(FrozenModel):
    """Provider-facing relationship frame using local source references only."""

    evidence_text: str = Field(
        min_length=1,
        description="Exact CURRENT_MESSAGE span evidencing the relationship request.",
    )
    focus_ref: str | None = None
    focus_binding: ResearchFocusBinding
    counterpart_refs: tuple[str, ...] = Field(min_length=1)
    polarity: ResearchOperationPolarity

    @model_validator(mode="after")
    def _focus_binding_contract(self):
        if self.focus_binding == ResearchFocusBinding.UNRESOLVED:
            if self.focus_ref is not None:
                raise ValueError("unresolved relationship focus cannot carry focus_ref")
        elif self.focus_ref is None:
            raise ValueError("explicit/antecedent relationship focus requires focus_ref")
        return self


class ResearchDeliverableFrame(FrozenModel):
    format: PresentationKind = Field(
        description="Requested output format; this is not an analytical operation."
    )
    evidence_text: str = Field(
        min_length=1,
        description="Exact CURRENT_MESSAGE span requesting this output format.",
    )
    polarity: ResearchOperationPolarity

    @model_validator(mode="after")
    def _valid_format(self):
        if self.format == PresentationKind.NONE:
            raise ValueError("research deliverable cannot be none")
        return self


class ResearchRequestGraph(FrozenModel):
    """Provider-facing source inventory -> operation graph.

    Local refs are not canonical semantic refs. They only point back to exact surfaces
    from the current user message; semantic binding remains SemanticResolver authority.
    """

    surfaces: tuple[ResearchSourceSurface, ...] = Field(min_length=1)
    operations: tuple[ResearchOperationFrame, ...] = ()
    relationships: tuple[ResearchRelationshipFrame, ...] = ()
    time_refs: tuple[str, ...] = ()
    deliverables: tuple[ResearchDeliverableFrame, ...] = ()

    @model_validator(mode="after")
    def _graph_integrity(self):
        ids = [item.surface_id for item in self.surfaces]
        if len(ids) != len(set(ids)):
            raise ValueError("research source surface IDs must be unique")
        known = set(ids)

        refs: list[str] = list(self.time_refs)
        for operation in self.operations:
            if operation.operation == ResearchNonRelationshipGoalKind.ROOT_CAUSE:
                if operation.outcome_ref is not None:
                    refs.append(operation.outcome_ref)
                refs.extend(operation.factor_refs)
            else:
                refs.extend(operation.subject_refs)
                refs.extend(operation.related_refs)
        for relationship in self.relationships:
            if relationship.focus_ref is not None:
                refs.append(relationship.focus_ref)
            refs.extend(relationship.counterpart_refs)

        unknown = sorted({ref for ref in refs if ref not in known})
        if unknown:
            raise ValueError(f"research graph contains unknown local surface refs: {unknown}")

        surface_index = {item.surface_id: item for item in self.surfaces}
        for ref in self.time_refs:
            if surface_index[ref].semantic_role != SemanticMentionKind.TIME:
                raise ValueError("research time_refs must reference TIME surfaces")
        return self


class ResearchDeliverableSurface(FrozenModel):
    """Source-grounded requested research output, separate from analytical questions."""

    kind: PresentationKind
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def _non_empty_deliverable(self):
        if self.kind == PresentationKind.NONE:
            raise ValueError("research deliverable cannot be none")
        return self


class ResearchRequestSurface(FrozenModel):
    """Stable internal research surface consumed by Resolver/Policy/Builder."""

    goals: tuple[ResearchGoalSurface, ...] = ()
    relationships: tuple[ResearchRelationshipSurface, ...] = ()
    time_mentions: tuple[SemanticMention, ...] = ()
    deliverables: tuple[ResearchDeliverableSurface, ...] = ()
    excluded_mentions: tuple[SemanticMention, ...] = ()

    @model_validator(mode="after")
    def _has_operation(self):
        if not self.goals and not self.relationships:
            raise ValueError("research request requires at least one analytical operation")
        return self


class UserRepair(FrozenModel):
    """Current-message evidence that an existing analytical choice is being corrected/replaced."""

    correction_spans: tuple[str, ...] = Field(
        default=(),
        description=(
            "Surface spans showing retraction/correction/replacement of an existing slot; "
            "must be non-empty for a USER_REPAIR turn."
        ),
    )


class TurnInterpreterTransport(FrozenModel):
    """Provider-facing language contract.

    Research uses a local source inventory and operation graph. The compiler converts
    it into the stable internal TurnInterpretation before Resolver/Policy/Planner see it.
    """

    dialogue_act: TurnAct
    references: tuple[ReferenceMention, ...] = ()
    analytical_request: AnalyticalRequest | None = None
    research_graph: ResearchRequestGraph | None = None
    presentation_request: PresentationKind = PresentationKind.NONE
    user_repair: "UserRepair | None" = None
    unresolved_mentions: tuple[UnresolvedMention, ...] = ()

    @model_validator(mode="after")
    def _validate_transport_shape(self):
        analytic_new_family = {
            TurnAct.ANALYTIC_NEW,
            TurnAct.COMPLEX_ANALYSIS,
            TurnAct.REPORT_REQUEST,
        }
        if self.dialogue_act in analytic_new_family:
            if self.analytical_request is None and self.research_graph is None:
                raise ValueError(
                    "new analytical transport requires analytical_request or research_graph"
                )
        elif self.research_graph is not None:
            raise ValueError(
                "research_graph is valid only on new analytical turn family"
            )

        if self.research_graph is not None:
            requested_deliverables = {
                item.format
                for item in self.research_graph.deliverables
                if item.polarity == ResearchOperationPolarity.REQUESTED
            }
            if (
                self.presentation_request != PresentationKind.NONE
                and self.presentation_request not in requested_deliverables
            ):
                raise ValueError(
                    "research presentation_request must be backed by requested deliverable"
                )
        return self




class CandidateSource(StrEnum):
    EXPLICIT_ANCHOR = "explicit_anchor"
    CURRENT_FOCUS = "current_focus"
    CANONICAL_NAME = "canonical_name"
    VERIFIED_SYNONYM = "verified_synonym"
    MORPHOLOGICAL_MATCH = "morphological_match"
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
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    THIS_QUARTER = "this_quarter"
    THIS_YEAR = "this_year"
    LAST_N_DAYS = "last_n_days"
    LAST_N_WEEKS = "last_n_weeks"
    LAST_N_MONTHS = "last_n_months"
    PREVIOUS_WEEK = "previous_week"
    PREVIOUS_MONTH = "previous_month"
    PREVIOUS_QUARTER = "previous_quarter"
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
    cube: str = ""
    metrics: tuple[ResolvedSemanticRef, ...] = ()
    dimensions: tuple[ResolvedSemanticRef, ...] = ()
    filters: tuple[ResolvedFilterRef, ...] = ()
    period: ResolvedPeriod | None = None
    ranking: ResolvedRanking | None = None
    comparison: ResolvedComparison | None = None
    context_version: str = ""


class DialogueAction(StrEnum):
    TALK = "TALK"
    CLARIFY = "CLARIFY"
    EXPLAIN_EXISTING = "EXPLAIN_EXISTING"
    ANALYTIC_STANDARD = "ANALYTIC_STANDARD"
    RESEARCH_BRIEF = "RESEARCH_BRIEF"
    UNSUPPORTED = "UNSUPPORTED"


class TopicFrameV0(FrozenModel):
    topic_id: str
    cube: str
    context_version: str


class FocusStateV0(FrozenModel):
    metrics: tuple[ResolvedSemanticRef, ...] = ()
    dimensions: tuple[ResolvedSemanticRef, ...] = ()
    filters: tuple[ResolvedFilterRef, ...] = ()
    period: ResolvedPeriod | None = None
    last_contract_refs: tuple[str, ...] = ()


class ResultExecutionAnchorV0(FrozenModel):
    execution_id: str
    role: Literal["primary", "comparison_reference"]
    columns: tuple[str, ...] = ()
    rows: tuple[dict[str, Any], ...] = ()
    row_count: int = 0
    truncated: bool = False


class ResultAnchorV0(FrozenModel):
    contract_refs: tuple[str, ...] = ()
    result_hashes: tuple[str, ...] = ()
    executions: tuple[ResultExecutionAnchorV0, ...] = ()
    verified: bool = False


class PendingAnalyticalStateV0(FrozenModel):
    dialogue_act: TurnAct
    analytical_request: AnalyticalRequest
    user_repair: UserRepair | None = None
    hypotheses: tuple[SemanticHypothesis, ...] = ()
    clarification: ClarificationState
    base_ir: AnalyticsIR | None = None
    context_version: str


class ConversationStateV2(FrozenModel):
    """Bounded typed conversation context. Durable server resume is a later phase."""

    # Compatibility fields retained for the Day1 interpreter contract.
    has_prior_analytical_request: bool = False
    has_active_result: bool = False
    pending_clarification: bool = False
    topic_labels: tuple[str, ...] = ()
    focus_labels: tuple[str, ...] = ()
    selected_anchor_label: str | None = None
    selected_anchor: SemanticAnchor | None = None
    focus_anchors: tuple[SemanticAnchor, ...] = ()
    clarification_state: ClarificationState | None = None

    # Day4 canonical state. Raw SQL/CubeQuery is intentionally absent.
    topic: TopicFrameV0 | None = None
    focus: FocusStateV0 | None = None
    last_ir: AnalyticsIR | None = None
    last_result: ResultAnchorV0 | None = None
    pending_analytical: PendingAnalyticalStateV0 | None = None


class TurnInterpretation(FrozenModel):
    dialogue_act: TurnAct = Field(
        description=(
            "Conversation speech act proposed by the language owner. For new analytical "
            "turns, COMPLEX_ANALYSIS / REPORT_REQUEST are transport hints only; the "
            "deterministic ResearchModePolicy owns final STANDARD vs RESEARCH routing."
        )
    )
    references: tuple[ReferenceMention, ...] = ()
    analytical_request: AnalyticalRequest | None = None
    research_request: ResearchRequestSurface | None = None
    presentation_request: PresentationKind = PresentationKind.NONE
    user_repair: UserRepair | None = Field(
        default=None,
        description=(
            "Required for USER_REPAIR; absent for ordinary ANALYTIC_REFINE. Contains only "
            "current-message correction evidence, never reconstructed prior slots."
        ),
    )
    unresolved_mentions: tuple[UnresolvedMention, ...] = ()

    @model_validator(mode="after")
    def _validate_turn_shape_without_routing_coupling(self):
        analytic_new_family = {
            TurnAct.ANALYTIC_NEW,
            TurnAct.COMPLEX_ANALYSIS,
            TurnAct.REPORT_REQUEST,
        }
        if self.dialogue_act in analytic_new_family:
            if self.analytical_request is None and self.research_request is None:
                raise ValueError(
                    "new analytical turn requires analytical_request or research_request"
                )
        elif self.research_request is not None:
            raise ValueError(
                "research operation surface is valid only on new analytical turn family"
            )
        return self


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
        "no_prior_ir",
        "empty_refinement_delta",
        "followup_cube_incompatible",
        "pending_analytical_state_missing",
        "no_active_result",
        "clarification_state_mismatch",
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
        "conversation",
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



# ---------------------------------------------------------------------------
# Day 6 research-brief contracts (execution lifecycle remains Day 7+)
# ---------------------------------------------------------------------------


class ResearchMode(StrEnum):
    STANDARD = "STANDARD"
    RESEARCH = "RESEARCH"
    BLOCKED = "BLOCKED"


class ResearchModeReason(StrEnum):
    EXISTING_STANDARD_SURFACE = "existing_standard_surface"
    COMPLEX_ONLY_OPERATION = "complex_only_operation"
    MULTI_INDEPENDENT_GOALS = "multi_independent_goals"
    STANDARD_PROJECTABLE_OPERATIONS = "standard_projectable_operations"
    UNPROJECTABLE_RESEARCH_SURFACE = "unprojectable_research_surface"
    UNCLASSIFIED_OPERATION = "unclassified_operation"
    INCOMPLETE_STANDARD_OPERATION = "incomplete_standard_operation"


class ResearchModeDecision(FrozenModel):
    mode: ResearchMode
    reason: ResearchModeReason
    canonical_turn: TurnInterpretation


class ResearchGoalStatus(StrEnum):
    RESOLVED = "RESOLVED"
    BLOCKED = "BLOCKED"


class ResearchBriefStatus(StrEnum):
    READY_FOR_RESEARCH = "READY_FOR_RESEARCH"
    BLOCKED = "BLOCKED"


class ResearchSemanticRef(FrozenModel):
    """Resolver-proven canonical ref with source provenance.

    No ResearchBriefBuilder-created canonical identifier is permitted.
    """

    source_mention: str
    candidate_id: str
    target_kind: SemanticTargetKind
    canonical_name: str
    dimension_name: str | None = None
    value: str | None = None
    cube_names: tuple[str, ...] = ()
    sensitive: bool = False


class ResearchUnresolvedRef(FrozenModel):
    source_mention: str
    role: Literal["subject", "related", "goal"]
    reason: str


class ResearchQuestion(FrozenModel):
    goal_id: str
    kind: ResearchGoalKind
    priority: Literal["MUST"] = "MUST"
    source_text: str
    subject_refs: tuple[ResearchSemanticRef, ...] = ()
    related_refs: tuple[ResearchSemanticRef, ...] = ()
    unresolved: tuple[ResearchUnresolvedRef, ...] = ()
    status: ResearchGoalStatus


class ResearchDeliverableRequirement(FrozenModel):
    requirement_id: str
    kind: PresentationKind
    priority: Literal["MUST"] = "MUST"
    source_text: str


class ResearchScope(FrozenModel):
    semantic_refs: tuple[ResearchSemanticRef, ...] = ()
    time_surfaces: tuple[str, ...] = ()


class ResearchBudget(FrozenModel):
    """Typed budget envelope only; Day 6 does not invent execution limits.

    Concrete limits belong to the Day 7 research execution/model/tool policy owner.
    """

    max_data_queries: int | None = Field(default=None, ge=0)
    max_branch_depth: int | None = Field(default=None, ge=0)
    max_llm_turns: int | None = Field(default=None, ge=0)
    max_wall_clock_seconds: int | None = Field(default=None, ge=1)
    assignment: Literal["deferred_to_research_execution_policy"] = (
        "deferred_to_research_execution_policy"
    )


class ResearchBrief(FrozenModel):
    brief_id: str
    objective: str
    scope: ResearchScope
    required_domains: tuple[str, ...] = ()
    questions: tuple[ResearchQuestion, ...] = ()
    deliverables: tuple[ResearchDeliverableRequirement, ...] = ()
    must_requirement_ids: tuple[str, ...] = ()
    blocking_goal_ids: tuple[str, ...] = ()
    budget: ResearchBudget = Field(default_factory=ResearchBudget)
    context_version: str
    status: ResearchBriefStatus


# Contract shells only in Day 6. Runtime behavior starts in Day 7+.
class ResearchRun(FrozenModel):
    run_id: str
    brief_id: str
    state: Literal["pending", "running", "paused", "complete", "failed", "cancelled"] = "pending"


class ResearchTask(FrozenModel):
    task_id: str
    question_id: str
    task_kind: str
    input_refs: tuple[str, ...] = ()
    origin: Literal["USER_SEED", "AGENT_DERIVED"] = "USER_SEED"
    parent_task_id: str | None = None
    parent_obligation_id: str | None = None
    trigger_evidence_ref: str | None = None
    branch_depth: int = Field(default=0, ge=0)
    state: Literal["pending", "running", "complete", "failed", "blocked"] = "pending"

    @model_validator(mode="after")
    def _day7_provenance(self):
        if self.origin == "USER_SEED":
            if (
                self.parent_task_id is not None
                or self.parent_obligation_id is not None
                or self.trigger_evidence_ref is not None
                or self.branch_depth != 0
            ):
                raise ValueError(
                    "USER_SEED ResearchTask cannot carry derived provenance"
                )
        else:
            if (
                self.parent_task_id is None
                or self.parent_obligation_id is None
                or self.trigger_evidence_ref is None
                or self.branch_depth < 1
            ):
                raise ValueError(
                    "AGENT_DERIVED ResearchTask requires parent task/obligation, "
                    "trigger evidence and branch_depth >= 1"
                )
        return self


class EvidenceArtifact(FrozenModel):
    artifact_id: str
    task_id: str
    obligation_ids: tuple[str, ...] = ()
    query_contract_refs: tuple[str, ...] = ()
    evidence_kind: str
    verified: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)
    limitations: tuple[str, ...] = ()


class Finding(FrozenModel):
    finding_id: str
    question_id: str
    statement: str
    evidence_artifact_refs: tuple[str, ...] = ()


class Hypothesis(FrozenModel):
    hypothesis_id: str
    question_id: str
    statement: str
    evidence_for_refs: tuple[str, ...] = ()
    evidence_against_refs: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Day 4 conversation / dialogue-policy surface
# ---------------------------------------------------------------------------


class AskV2Day4Response(FrozenModel):
    status: Literal["conversation"] = "conversation"
    stage: Literal["day4_conversation"] = "day4_conversation"
    dialogue_action: DialogueAction
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
    existing_result: ResultAnchorV0 | None = None
    research_brief: ResearchBrief | None = None
    conversation: ConversationStateV2
    failure: StandardAnalyticsFailure | None = None
    resumed_by: Literal["signed_chip", "free_text"] | None = None
    session_id: str | None = None
    thread_id: str | None = None
    query_execution_count: int = 0
    used_existing_result: bool = False
    legacy_semantic_path_called: Literal[False] = False
    next_stage: Literal[
        "conversation_day4",
        "clarification_resume_day4",
        "core_mvp_day5",
        "standard_analytics_retry",
        "research_ready_day7",
        "research_brief_blocked",
    ] = "conversation_day4"

# ---------------------------------------------------------------------------
# Day 5 Core MVP product / finalization surface
# ---------------------------------------------------------------------------


class ConversationResponseKind(StrEnum):
    ANSWER = "answer"
    CLARIFY = "clarify"
    TALK = "talk"
    EXPLAIN = "explain"
    RESEARCH_BRIEF = "research_brief"
    SEMANTIC_GAP = "semantic_gap"
    UNSUPPORTED = "unsupported"
    FAILURE = "failure"


class ScopeChipV0(FrozenModel):
    kind: Literal[
        "metric",
        "dimension",
        "filter",
        "time",
        "ranking",
        "comparison",
    ]
    label: str
    canonical_ref: str | None = None


class EvidenceRefV0(FrozenModel):
    contract_id: str
    execution_id: str
    role: Literal["primary", "comparison_reference"]
    sealed: bool = True


class ConversationTableV0(FrozenModel):
    execution_id: str
    role: Literal["primary", "comparison_reference"]
    columns: tuple[str, ...] = ()
    rows: tuple[dict[str, Any], ...] = ()
    row_count: int = 0
    truncated: bool = False


class ConversationResponseV0(FrozenModel):
    """User-facing Core MVP response derived only from typed state/evidence."""

    kind: ConversationResponseKind
    text: str
    scope_chips: tuple[ScopeChipV0, ...] = ()
    clarification_chips: tuple[ClarificationChip, ...] = ()
    evidence_refs: tuple[EvidenceRefV0, ...] = ()
    tables: tuple[ConversationTableV0, ...] = ()
    official_verified: bool = False


class AskV2CoreResponse(AskV2Day4Response):
    status: Literal["core_mvp", "research_brief"] = "core_mvp"
    stage: Literal["day5_core_mvp", "day6_research_brief"] = "day5_core_mvp"
    response: ConversationResponseV0
    next_stage: Literal[
        "core_mvp_gate",
        "research_ready_day7",
        "research_brief_blocked",
    ] = "core_mvp_gate"

