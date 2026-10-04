"""Generic raw-language Research intake for the canonical Dima product.

The model may interpret language only into typed ResearchBrief intent over an
explicit grounded semantic catalog. It cannot invent semantic refs, execute
analytics, create Evidence, or promote causal truth.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.research_contracts import (
    CausalCompetitionSurface,
    CausalEffectObservation,
    ComparisonRole,
    ComparisonSurface,
    PresentationKind,
    RankingBasis,
    RankingSurface,
    RelationshipIntent,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchNativeVerificationBinding,
    ResultSelectionDependency,
    ResearchScope,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeMutation,
    ScopeMutationKind,
    SemanticTargetKind,
    TemporalRole,
    TurnScopeContract,
    apply_scope_mutation,
)
from app.v3.research_scope_patch import (
    ScopePatchFacet,
    ScopePatchOperation,
    ScopePatchOperationKind,
    TurnScopePatch,
    resolve_scope_patch,
)
from app.v3.research_temporal_authority import (
    ChangeTemporalAuthorityDisposition,
    resolve_change_temporal_authority,
)
from app.v3.structured_transport import (
    strict_json_schema,
    validate_provider_strict_schema,
)


class StructuredJSONTransport(Protocol):
    call_count: int

    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str: ...


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResearchIntakeError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ResearchIntakeTerminal(StrEnum):
    READY = "READY"
    CLARIFY = "CLARIFY"
    UNSUPPORTED = "UNSUPPORTED"


class AllowedRelationship(Frozen):
    relationship_id: str = Field(min_length=1)
    left_semantic_id: str = Field(min_length=1)
    right_semantic_id: str = Field(min_length=1)
    dimension_semantic_id: str | None = None


class ResearchIntakeCatalog(Frozen):
    context_version: str = Field(min_length=1)
    semantic_refs: tuple[ResearchSemanticRef, ...] = Field(min_length=1)
    allowed_relationships: tuple[AllowedRelationship, ...] = ()
    supported_domains: tuple[str, ...] = ()
    temporal_dimension_ids: tuple[str, ...] = ()
    native_verification_bindings: tuple[
        ResearchNativeVerificationBinding, ...
    ] = ()

    @model_validator(mode="after")
    def unique_and_grounded(self):
        ids = [item.candidate_id for item in self.semantic_refs]
        if len(ids) != len(set(ids)):
            raise ValueError("semantic catalog ids must be unique")
        known = set(ids)
        rel_ids: set[str] = set()
        for rel in self.allowed_relationships:
            if rel.relationship_id in rel_ids:
                raise ValueError("relationship ids must be unique")
            rel_ids.add(rel.relationship_id)
            if rel.left_semantic_id not in known or rel.right_semantic_id not in known:
                raise ValueError("relationship references unknown semantic id")
            if (
                rel.dimension_semantic_id is not None
                and rel.dimension_semantic_id not in known
            ):
                raise ValueError("relationship dimension is unknown")
        by_id = {item.candidate_id: item for item in self.semantic_refs}
        if len(self.temporal_dimension_ids) != len(
            set(self.temporal_dimension_ids)
        ):
            raise ValueError("temporal dimension ids must be unique")
        for candidate_id in self.temporal_dimension_ids:
            ref = by_id.get(candidate_id)
            if ref is None or ref.target_kind.value != "dimension":
                raise ValueError(
                    "temporal dimension id must reference a catalog dimension"
                )
        binding_ids = [
            item.candidate_id for item in self.native_verification_bindings
        ]
        if len(binding_ids) != len(set(binding_ids)):
            raise ValueError("native verification bindings must be unique")
        if not set(binding_ids).issubset(known):
            raise ValueError(
                "native verification binding references unknown semantic id"
            )
        return self

    @property
    def fingerprint(self) -> str:
        # Catalog order is presentation only. Authority identity is the set of
        # legal semantic/relationship choices for this exact context.
        payload = {
            "context_version": self.context_version,
            "semantic_refs": [
                item.model_dump(mode="json")
                for item in sorted(
                    self.semantic_refs,
                    key=lambda value: value.candidate_id,
                )
            ],
            "allowed_relationships": [
                item.model_dump(mode="json")
                for item in sorted(
                    self.allowed_relationships,
                    key=lambda value: value.relationship_id,
                )
            ],
            "supported_domains": sorted(self.supported_domains),
        }
        if self.temporal_dimension_ids:
            payload["temporal_dimension_ids"] = sorted(
                self.temporal_dimension_ids
            )
        if self.native_verification_bindings:
            payload["native_verification_bindings"] = [
                item.model_dump(mode="json")
                for item in sorted(
                    self.native_verification_bindings,
                    key=lambda value: value.candidate_id,
                )
            ]
        return hashlib.sha256(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()


class DraftRanking(Frozen):
    direction: str = Field(pattern=r"^(asc|desc|unspecified)$")
    limit: int | None = Field(default=None, ge=1, le=1000)
    measure_semantic_id: str | None = Field(default=None, min_length=1)
    source_text: str = Field(min_length=1)
    basis: RankingBasis = RankingBasis.LEVEL

    @model_validator(mode="after")
    def coherent_basis(self):
        if self.basis == RankingBasis.CHANGE and self.measure_semantic_id is None:
            raise ValueError("change ranking requires one explicit governed measure")
        return self


class ModelCausalCompetitionDraft(Frozen):
    effect_semantic_id: str = Field(min_length=1)
    effect_observation: CausalEffectObservation = CausalEffectObservation.LEVEL
    candidate_mechanism_semantic_ids: tuple[str, ...] = ()
    diagnostic_dimension_ids: tuple[str, ...] = ()


class ModelTemporalMaterialMode(StrEnum):
    NONE = "none"
    WINDOW = "window"
    COMPARISON = "comparison"


class ModelComparisonDraft(Frozen):
    text: str = Field(min_length=1)
    role: ComparisonRole
    semantic_id: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def coherent(self):
        if self.role == ComparisonRole.TEMPORAL_PERIOD:
            if self.semantic_id is not None:
                raise ValueError(
                    "temporal comparison surface cannot carry a business semantic id"
                )
        elif self.semantic_id is None:
            raise ValueError(
                "business/causal comparison surface requires a governed semantic id"
            )
        return self


class ModelTimePeriodDraft(Frozen):
    source_text: str = Field(min_length=1)
    time_dimension_semantic_id: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str = Field(min_length=1)
    role: TemporalRole = TemporalRole.MATERIAL_WINDOW


class ModelScopePatchOperationDraft(Frozen):
    facet: ScopePatchFacet
    operation: ScopePatchOperationKind
    semantic_ids: tuple[str, ...] = ()
    periods: tuple[ModelTimePeriodDraft, ...] = ()
    source_fragment: str = Field(min_length=1)

    @model_validator(mode="after")
    def coherent(self):
        if self.operation == ScopePatchOperationKind.CLEAR:
            if self.semantic_ids or self.periods:
                raise ValueError("scope patch CLEAR must not carry values")
            return self
        if self.facet == ScopePatchFacet.PERIOD:
            if not self.periods or self.semantic_ids:
                raise ValueError(
                    "PERIOD patch requires periods and no free semantic ids"
                )
        else:
            if not self.semantic_ids or self.periods:
                raise ValueError(
                    "non-PERIOD patch requires semantic ids and no periods"
                )
        return self


class ModelNoTemporalMaterialDraft(Frozen):
    mode: Literal["none"]


class ModelWindowTemporalMaterialDraft(Frozen):
    mode: Literal["window"]
    window: ModelTimePeriodDraft


class ModelComparisonTemporalMaterialDraft(Frozen):
    mode: Literal["comparison"]
    baseline_period: ModelTimePeriodDraft
    comparison_period: ModelTimePeriodDraft

    @model_validator(mode="after")
    def coherent(self):
        if (
            self.baseline_period.time_dimension_semantic_id
            != self.comparison_period.time_dimension_semantic_id
        ):
            raise ValueError(
                "comparison temporal material must use one time dimension"
            )
        return self


ModelTemporalMaterialDraft = (
    ModelNoTemporalMaterialDraft
    | ModelWindowTemporalMaterialDraft
    | ModelComparisonTemporalMaterialDraft
)


class ModelResultSelectionDependencyDraft(Frozen):
    """Typed dependency on one upstream governed ranking result."""

    source_goal_key: str = Field(min_length=1, max_length=120)
    dimension_semantic_id: str = Field(min_length=1)
    selection: Literal["first_ranked_entity"] = "first_ranked_entity"


class ModelGoalDraft(Frozen):
    goal_key: str = Field(min_length=1, max_length=120)
    kind: ResearchGoalKind
    source_text: str = Field(min_length=1)
    source_fragment_text: str | None = Field(default=None, min_length=1)
    allowed_relationship_id: str | None = None
    relationship_intent: RelationshipIntent | None = None
    subject_semantic_ids: tuple[str, ...] = ()
    related_semantic_ids: tuple[str, ...] = ()
    ranking: DraftRanking | None = None
    comparisons: tuple[ModelComparisonDraft, ...] = ()
    causal_competition: ModelCausalCompetitionDraft | None = None
    temporal_material: ModelTemporalMaterialDraft | None = None
    result_dependency: ModelResultSelectionDependencyDraft | None = None
    material_parent_goal_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )
    # Compatibility-only for historical deterministic fixtures. This field is
    # deliberately omitted from the provider schema below; live intake cannot
    # mint new untyped comparison authority.
    comparison_texts: tuple[str, ...] = ()

    @model_validator(mode="after")
    def material_parent_is_comparison_only(self):
        if (
            self.material_parent_goal_key is not None
            and self.kind != ResearchGoalKind.COMPARISON
        ):
            raise ValueError(
                "material_parent_goal_key is legal only on COMPARISON goals"
            )
        return self


class ModelDeliverableDraft(Frozen):
    key: str = Field(min_length=1, max_length=120)
    kind: PresentationKind
    source_text: str = Field(min_length=1)


class ModelInvestigationDirectiveDraft(Frozen):
    key: str = Field(min_length=1, max_length=120)
    kind: ProductInvestigationRequirementKind
    source_goal_key: str = Field(min_length=1, max_length=120)
    source_text: str = Field(min_length=1)


class ModelResearchBriefDraft(Frozen):
    terminal: ResearchIntakeTerminal
    objective: str | None = None
    goals: tuple[ModelGoalDraft, ...] = ()
    deliverables: tuple[ModelDeliverableDraft, ...] = ()
    investigation_directives: tuple[ModelInvestigationDirectiveDraft, ...] = ()
    time_surfaces: tuple[str, ...] = ()
    time_periods: tuple[ModelTimePeriodDraft, ...] = ()
    required_domains: tuple[str, ...] = ()
    scope_mutation_kind: ScopeMutationKind | None = None
    clarification_question: str | None = None
    unsupported_reason: str | None = None

    @model_validator(mode="after")
    def coherent_terminal(self):
        if self.terminal == ResearchIntakeTerminal.READY:
            if not (self.objective or "").strip() or not self.goals:
                raise ValueError("READY requires objective and at least one goal")
            if self.clarification_question is not None or self.unsupported_reason is not None:
                raise ValueError("READY cannot carry clarify/unsupported payload")
        elif self.terminal == ResearchIntakeTerminal.CLARIFY:
            if not (self.clarification_question or "").strip():
                raise ValueError("CLARIFY requires one bounded clarification question")
            if (
                self.goals
                or self.deliverables
                or self.investigation_directives
                or self.unsupported_reason is not None
            ):
                raise ValueError("CLARIFY cannot carry executable goals")
        elif self.terminal == ResearchIntakeTerminal.UNSUPPORTED:
            if not (self.unsupported_reason or "").strip():
                raise ValueError("UNSUPPORTED requires a reason")
            if (
                self.goals
                or self.deliverables
                or self.investigation_directives
                or self.clarification_question is not None
            ):
                raise ValueError("UNSUPPORTED cannot carry executable goals")
        return self


class ModelReadyResearchIntake(Frozen):
    """Provider-facing READY semantics only; Dima binds machine authority."""

    terminal: Literal["READY"]
    objective: str = Field(min_length=1)
    goals: tuple[ModelGoalDraft, ...] = Field(min_length=1)
    deliverables: tuple[ModelDeliverableDraft, ...] = ()
    investigation_directives: tuple[ModelInvestigationDirectiveDraft, ...] = ()
    time_periods: tuple[ModelTimePeriodDraft, ...] = ()
    required_domains: tuple[str, ...] = ()
    scope_mutation_kind: ScopeMutationKind | None = None


class ModelClarifyResearchIntake(Frozen):
    terminal: Literal["CLARIFY"]
    clarification_question: str = Field(min_length=1)


class ModelUnsupportedResearchIntake(Frozen):
    terminal: Literal["UNSUPPORTED"]
    unsupported_reason: str = Field(min_length=1)


class ModelResearchIntakeEnvelope(Frozen):
    """Small closed provider DTO; not a persisted/domain authority contract."""

    result: (
        ModelReadyResearchIntake
        | ModelClarifyResearchIntake
        | ModelUnsupportedResearchIntake
    )


class ModelReadyFollowupScopePatch(Frozen):
    terminal: Literal["READY"]
    operations: tuple[ModelScopePatchOperationDraft, ...] = ()


class ModelFollowupScopeEnvelope(Frozen):
    result: (
        ModelReadyFollowupScopePatch
        | ModelClarifyResearchIntake
        | ModelUnsupportedResearchIntake
    )


class ModelResolvedRankingBasis(Frozen):
    terminal: Literal["RESOLVED"]
    basis: RankingBasis


class ModelRankingBasisReconsiderationEnvelope(Frozen):
    """Narrow provider DTO: only ranking authority may change."""

    result: ModelResolvedRankingBasis | ModelClarifyResearchIntake


class ModelResolvedChangePeriodPair(Frozen):
    """Narrow provider DTO: only accepted temporal pair bounds may change."""

    terminal: Literal["RESOLVED"]
    baseline_period: ModelTimePeriodDraft
    comparison_period: ModelTimePeriodDraft

    @model_validator(mode="after")
    def coherent(self):
        if self.baseline_period.role != TemporalRole.BASELINE_PERIOD:
            raise ValueError("baseline_period must keep BASELINE_PERIOD role")
        if self.comparison_period.role != TemporalRole.COMPARISON_PERIOD:
            raise ValueError("comparison_period must keep COMPARISON_PERIOD role")
        if (
            self.baseline_period.time_dimension_semantic_id
            != self.comparison_period.time_dimension_semantic_id
        ):
            raise ValueError("change period pair must use one governed time dimension")
        for item in (self.baseline_period, self.comparison_period):
            ResearchTimePeriod(
                source_text=item.source_text,
                time_dimension_candidate_id=item.time_dimension_semantic_id,
                start=item.start,
                end=item.end,
                role=item.role,
            )
        return self


class ModelChangePeriodReconsiderationEnvelope(Frozen):
    """Narrow provider DTO: no non-temporal authority is writable."""

    result: ModelResolvedChangePeriodPair | ModelClarifyResearchIntake


class ResearchIntakeResult(Frozen):
    terminal: ResearchIntakeTerminal
    brief: ResearchBrief | None = None
    investigation_requirements: tuple[ProductInvestigationRequirement, ...] = ()
    scope_contract: TurnScopeContract | None = None
    clarification_question: str | None = None
    unsupported_reason: str | None = None
    catalog_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    model_calls: int = Field(ge=0)

    @model_validator(mode="after")
    def coherent(self):
        if self.terminal == ResearchIntakeTerminal.READY:
            if self.brief is None:
                raise ValueError("READY result requires ResearchBrief")
        elif (
            self.brief is not None
            or self.investigation_requirements
            or self.scope_contract is not None
        ):
            raise ValueError(
                "non-READY result cannot carry ResearchBrief, scope contract, or product routing"
            )
        return self


_SYSTEM = """You are Dima's bounded Research-intake interpreter.
Your only job is to translate the CURRENT user message into the strict typed schema.

Authority rules:
- Use ONLY semantic IDs present in the supplied grounded catalog.
- Never invent a metric, dimension, entity value, relationship, number, SQL, or factual result.
- This step performs NO analytics and creates NO Evidence.
- For RELATIONSHIP, select exactly one allowed_relationship_id from the supplied catalog
  and exactly one relationship_intent.
  Use OBSERVATIONAL for association/co-movement/relationship-strength interpretation.
  Use BUSINESS_POLICY only when the user explicitly requests governed business-policy,
  directional business-rule, or policy applicability meaning. Do not infer BUSINESS_POLICY
  merely because two governed measures have an allowed relationship identity.
  Do not reconstruct relationship left/right/dimension identities yourself.
- If the request depends on unavailable concepts/data (including psychological/predictive truth
  not represented by the catalog), return UNSUPPORTED.
- If the user's actual intent cannot be determined without one bounded question, return CLARIFY.
- For explicit corrections, the CURRENT message is authoritative: do not silently merge removed
  obligations back from prior context.
- Never emit a scope version or lineage id. Dima deterministically binds those after validation.
- For every explicit calendar/time surface in READY, emit exactly one time_periods entry.
  Select time_dimension_semantic_id only from the grounded catalog, and resolve exact ISO-8601
  half-open [start,end) bounds. The payload includes calendar_reference_date. For a bare named
  month/month-range with no year, resolve only the most recent non-future occurrence anchored by
  calendar_reference_date when that interpretation is unique; otherwise return CLARIFY.
- calendar_reference_date is calendar context only. It never proves that data exists for a period.
- A bounded management report/overview does not require the user to enumerate every metric. When
  exactly one supported domain exists, you MAY form a grounded domain overview from materially
  relevant catalog refs and explicit deliverables. Never use this rule to satisfy concepts absent
  from the catalog, invent KPI priorities, invent causes, or silently broaden a specific request.
- Do not use implementation-specific SQL/MBQL temporal syntax; time_periods are semantic scope only.
- Every time_period must carry its semantic role. Use MATERIAL_WINDOW for one ordinary bounded
  analysis window; BASELINE_PERIOD + COMPARISON_PERIOD for a true temporal comparison;
  EFFECT_PERIOD + EVIDENCE_WINDOW for causal investigation when those distinct roles are requested.
  Never infer roles from tuple position.
- Every ROOT_CAUSE goal must emit one closed typed temporal_material shape.
  {mode:none} means no temporal material.
  {mode:window, window:{...}} means one pooled bounded interval is sufficient.
  {mode:comparison, baseline_period:{...}, comparison_period:{...}} means the answer requires two
  accepted periods to remain distinguishable. Both comparison periods must use one time dimension.
  The nested periods are ROOT_CAUSE temporal authority; do not duplicate them into top-level
  time_periods. This object interprets user intent only; it never asserts data truth.
- Emit typed non-temporal comparisons only: use CAUSAL_CANDIDATE for user-provided candidate
  mechanisms and ENTITY_OR_MEASURE for governed entity/measure competition. Every provider-emitted
  comparison item must carry one semantic_id from the grounded catalog and from that goal's accepted
  refs. Temporal comparison authority is NOT emitted through this generic list: for a standalone
  period-vs-period comparison emit one COMPARISON goal plus exactly two role-bound top-level periods
  (BASELINE_PERIOD and COMPARISON_PERIOD). ROOT_CAUSE uses its closed temporal_material contract.
  Dima deterministically projects the corresponding TEMPORAL_PERIOD surface after validation.
- Preserve every current MUST analytical/presentation obligation as a separate goal/deliverable.
- For every READY goal emit source_fragment_text as one exact verbatim substring of the CURRENT
  user message that directly supports that goal. Never paraphrase the fragment.
- If multiple goals decompose the same user clause, repeat the same maximal supporting clause
  verbatim for each of those goals. Different clauses must keep different fragment text.
- Adaptive instructions such as "if verified evidence reveals a new material direction, follow it"
  or "if current governed Evidence cannot discriminate the accepted alternatives, run one bounded
  discriminating test" are Core-B product-routing intent, NOT a second analytical goal. Emit the
  actual analytical goal once, then emit FOLLOW_VERIFIED_MATERIAL with source_goal_key pointing to
  that exact goal.
- FOLLOW_VERIFIED_MATERIAL is AFFIRMATIVE conditional routing authority. Emit it only when the user
  explicitly asks for additional analytical/investigative work to occur if a governed condition is
  met (for example insufficient discrimination or a newly verified material direction).
- A negative stopping/depth instruction such as "do not open another query when current Evidence is
  sufficient", "do not deepen just to look thorough", or merely "stop when enough" does NOT authorize
  future analytical work and MUST NOT emit FOLLOW_VERIFIED_MATERIAL. Causal-boundary language alone
  also does not authorize a follow-up.
- An investigation directive never asserts that evidence is material; it only preserves the user's
  affirmative conditional instruction for later governed P17 evaluation.
- Do not convert association into causality. ROOT_CAUSE means bounded investigation, not a cause.
- Use RELATIONSHIP when the user's requested analytical object is observational association,
  co-movement, relative relationship strength, or similar non-causal relationship interpretation.
- Use ROOT_CAUSE when one user clause asks which cause/explanation/mechanism better explains an
  outcome, asks competing explanations to be tested, or asks supporting/challenging evidence to
  discriminate causal hypotheses. One such clause should normally be ONE ROOT_CAUSE goal carrying
  the governed outcome/candidate material refs needed for its initial analytical acquisition.
  Do not split the same causal competition into another ROOT_CAUSE goal merely to preserve
  support/challenge, reporting, causal-boundary, or stopping instructions; those remain
  deliverable/investigation semantics unless the user actually supplied a distinct governed
  outcome, candidate set, diagnostic scope, or analytical material need.
  Every ROOT_CAUSE goal MUST emit causal_competition: one governed effect_semantic_id, one
  effect_observation, only the candidate_mechanism_semantic_ids explicitly supplied by the user
  (empty when none were supplied), and the governed diagnostic_dimension_ids needed by the request.
  Use effect_observation=LEVEL when the explanatory target is a bounded state/level; use CHANGE when
  the explanatory target is variation/change over accepted time. This typed field records user
  intent only; it never asserts that a change or causal effect actually exists. Additional accepted
  metrics may still be included as analytical material for P17 discovery, but must not be mislabeled
  as user-provided candidates.
  Do NOT manufacture separate RELATIONSHIP goals merely as evidence-gathering subgoals for that
  ROOT_CAUSE investigation. P17/P19 own governed hypothesis competition and discriminating re-entry.
- If the user independently asks both an observational relationship analysis and a causal/root-cause
  investigation, preserve them as distinct goals. Never collapse genuinely distinct user clauses.
- Goal decomposition is semantic obligation decomposition, not a query plan. Do not create multiple
  analytical goals solely because several governed metrics may be useful to one investigation.
- If a COMPARISON goal exists only to preserve temporal material for one ROOT_CAUSE goal in the
  same response, set material_parent_goal_key to that ROOT_CAUSE goal_key. If the comparison is an
  independently requested analytical obligation, set material_parent_goal_key to null. This typed
  parentage records semantic obligation ownership only; it never specifies SQL, MBQL or query shape.
- ranking.limit is null unless the user explicitly requested a bounded top-N/result count. Never invent top-N.
- ranking.basis=LEVEL means rank the accepted metric level or magnitude.
- ranking.basis=CHANGE means rank baseline-to-comparison change of one accepted metric. CHANGE
  requires one explicit ranking.measure_semantic_id plus exactly one BASELINE_PERIOD and one
  COMPARISON_PERIOD over the same governed time dimension. Never encode CHANGE as one pooled
  MATERIAL_WINDOW; intake records semantic authority only and performs no calculation.
- ranking.measure_semantic_id is set only when the user explicitly identifies one governed metric/KPI
  as the ranking basis. With multiple metrics and no explicit single basis, keep it null; do not pick
  the first metric or manufacture a composite score.
- result_dependency is used only when one analytical goal explicitly depends on an upstream ranked
  entity selection. source_goal_key must name that ranking goal; dimension_semantic_id must be the
  governed non-temporal dimension whose FIRST ranked row becomes an execution-local constraint.
  This does not mutate user scope and does not authorize inventing a value.
- If a native single-metric ranking needs direction and the user's direction is genuinely ambiguous,
  return CLARIFY rather than guessing direction from words, morphology, regex, or a default.
- Do not emit implementation-specific Wren/SQL/lane/token concepts.
"""


_RANKING_BASIS_RECONSIDERATION_SYSTEM = """You are Dima's bounded ranking-authority resolver.
You receive only already-grounded typed Research Intake material and exact verbatim user fragments.

Return exactly one of:
- RESOLVED with basis=LEVEL or basis=CHANGE, or
- CLARIFY with one bounded clarification question.

Authority rules:
- Decide only whether the requested ranking orders the governed measure by LEVEL/magnitude or by
  baseline-to-comparison CHANGE.
- Do not change metric identity, ranking direction, result count, goals, scope, periods, dependencies,
  deliverables, or any other semantic state.
- Do not plan a query, calculate a delta, write SQL/MBQL, choose an entity, or inspect results.
- The supplied baseline/comparison periods are typed accepted context, not evidence of a CHANGE request.
- If the exact user fragments do not deliberately distinguish LEVEL from CHANGE, return CLARIFY.
- Never use keyword lists, regex, morphology rules, benchmark identity, or hidden defaults.
"""


_CHANGE_PERIOD_RECONSIDERATION_SYSTEM = """You are Dima's bounded temporal-authority resolver.
You receive only an already-grounded CHANGE ranking, its exact verbatim user fragments, one governed
time dimension, calendar context, and the current typed baseline/comparison pair.

Return exactly one of:
- RESOLVED with one BASELINE_PERIOD and one COMPARISON_PERIOD, or
- CLARIFY with one bounded clarification question.

Authority rules:
- Decide only the two accepted period authorities: each period's exact verbatim source_text plus its
  half-open [start,end) normalized bounds.
- Keep the supplied governed time dimension and period roles exactly.
- Goal source fragments are immutable. A returned period.source_text must remain an exact verbatim
  source surface from the supplied user fragments. It may be a more atomic substring, but it may also
  remain one shared exact span when that single span jointly denotes the two-period comparison.
- BASELINE_PERIOD and COMPARISON_PERIOD are distinct semantic authorities because of their typed role
  and normalized half-open bounds, not because they must have different source_text strings. When one
  shared source span genuinely establishes both periods, preserve that provenance and deliberately
  resolve the two role-bound spans. If the shared surface does not establish an unambiguous pair,
  return CLARIFY rather than inventing distinct wording.
- Do not change goals, metrics, ranking basis/direction/limit, dependencies, deliverables, scope refs,
  or any other semantic state.
- Overlap is not globally illegal: preserve overlapping windows only when the exact user fragments
  deliberately establish an overlapping/rolling comparison. Otherwise resolve the exact period pair
  established by the user and calendar context, or return CLARIFY.
- Calendar context resolves calendar references only; it never proves data availability.
- Do not plan a query, calculate a delta, write SQL/MBQL, choose an entity, or inspect results.
- Never use keyword lists, regex, morphology rules, benchmark identity, or hidden defaults.
"""


_FOLLOWUP_SCOPE_SYSTEM = """You are Dima's bounded follow-up scope interpreter.
The current user message is a DELTA over one already accepted Research scope.

Authority rules:
- Return ONLY typed scope patch operations. Do not reconstruct a new ResearchBrief.
- A facet absent from operations means INHERIT EXACTLY from the prior accepted scope.
- Clearing a facet requires operation=CLEAR. Never encode clear as omission.
- Use only semantic IDs present in the supplied grounded catalog.
- ENTITY values must be governed entity-value IDs.
- METRIC values must be governed metric/KPI IDs.
- BREAKDOWN values must be governed non-temporal dimension IDs.
- PERIOD values must use governed temporal dimensions and exact ISO-8601 half-open bounds.
- Every operation must carry source_fragment as an exact verbatim substring of the CURRENT
  user message that directly supports that operation.
- Do not emit a mutation kind, scope version, lineage id, fingerprint, SQL, MBQL, JOIN,
  GROUP BY, query plan, factual result, Evidence, or causal truth.
- If the current turn makes no material scope change (for example report-only/presentation-only),
  return READY with operations=[].
- If an explicit requested mutation cannot be grounded to the catalog, return UNSUPPORTED.
- If the requested patch is genuinely ambiguous, return one bounded CLARIFY question.
"""


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def _intake_provider_schema(
    catalog: ResearchIntakeCatalog,
    *,
    has_prior_brief: bool = False,
) -> dict[str, Any]:
    """Close every provider-selected authority ID to this exact catalog.

    RELATIONSHIP uses one governed relationship identity. The provider never
    receives left/right/dimension identity fields for that variant; the
    deterministic compiler expands the selected relationship afterwards.
    """

    schema = strict_json_schema(ModelResearchIntakeEnvelope)
    definitions = schema.get("$defs") or {}
    goal_definition = definitions.get("ModelGoalDraft")
    if not isinstance(goal_definition, dict):
        raise ResearchIntakeError(
            "INTAKE_SCHEMA_INVALID",
            "ModelGoalDraft definition is absent",
        )
    base_properties = goal_definition.get("properties")
    if not isinstance(base_properties, dict):
        raise ResearchIntakeError(
            "INTAKE_SCHEMA_INVALID",
            "ModelGoalDraft properties are absent",
        )

    ready_definition = definitions.get("ModelReadyResearchIntake")
    if not isinstance(ready_definition, dict):
        raise ResearchIntakeError(
            "INTAKE_SCHEMA_INVALID",
            "provider READY definition is absent",
        )
    ready_properties = ready_definition.get("properties")
    if not isinstance(ready_properties, dict):
        raise ResearchIntakeError(
            "INTAKE_SCHEMA_INVALID",
            "provider READY properties are absent",
        )

    # Provider emits semantic intent only. Fields that are impossible for the
    # current governed catalog/turn are absent from the provider contract,
    # rather than being required null/empty boilerplate.
    if not catalog.temporal_dimension_ids:
        ready_properties.pop("time_periods", None)
        definitions.pop("ModelTimePeriodDraft", None)
    if not has_prior_brief:
        ready_properties.pop("scope_mutation_kind", None)
        definitions.pop("ScopeMutationKind", None)
    if catalog.supported_domains:
        ready_properties["required_domains"] = {
            "type": "array",
            "items": {
                "type": "string",
                "enum": list(sorted(catalog.supported_domains)),
            },
        }
    else:
        ready_properties.pop("required_domains", None)
    ready_definition["required"] = list(ready_properties)

    semantic_ids = tuple(
        sorted(item.candidate_id for item in catalog.semantic_refs)
    )
    ranking_metric_ids = tuple(
        sorted(
            item.candidate_id
            for item in catalog.semantic_refs
            if item.target_kind
            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
    )
    ranking_definition = definitions.get("DraftRanking")
    if isinstance(ranking_definition, dict):
        ranking_properties = ranking_definition.get("properties")
        if isinstance(ranking_properties, dict):
            ranking_properties["measure_semantic_id"] = {
                "anyOf": [
                    {
                        "type": "string",
                        "enum": list(ranking_metric_ids),
                    },
                    {"type": "null"},
                ],
            }
    result_dependency_definition = definitions.get(
        "ModelResultSelectionDependencyDraft"
    )
    if isinstance(result_dependency_definition, dict):
        dependency_properties = result_dependency_definition.get("properties")
        if isinstance(dependency_properties, dict):
            dependency_dimension_ids = tuple(
                sorted(
                    item.candidate_id
                    for item in catalog.semantic_refs
                    if (
                        item.target_kind == SemanticTargetKind.DIMENSION
                        and item.candidate_id
                        not in set(catalog.temporal_dimension_ids)
                    )
                )
            )
            dependency_properties["dimension_semantic_id"] = {
                "type": "string",
                "enum": list(dependency_dimension_ids),
            }

    relationship_ids = tuple(
        sorted(
            item.relationship_id
            for item in catalog.allowed_relationships
        )
    )
    time_dimension_ids = tuple(sorted(catalog.temporal_dimension_ids))
    period_definition = definitions.get("ModelTimePeriodDraft")
    if isinstance(period_definition, dict):
        period_properties = period_definition.get("properties")
        if isinstance(period_properties, dict):
            period_properties["time_dimension_semantic_id"] = {
                "type": "string",
                "enum": list(time_dimension_ids),
            }
    comparison_definition = definitions.get("ModelComparisonDraft")
    if isinstance(comparison_definition, dict):
        comparison_properties = comparison_definition.get("properties")
        if isinstance(comparison_properties, dict):
            # Temporal comparison authority is carried atomically by typed
            # period roles (or ROOT_CAUSE temporal_material), then projected by
            # Dima. The provider may use this generic comparison DTO only for
            # governed non-temporal identities, so one truth is never split
            # across an LLM-selected role and separately selected periods.
            comparison_properties["role"] = {
                "type": "string",
                "enum": [
                    ComparisonRole.ENTITY_OR_MEASURE.value,
                    ComparisonRole.CAUSAL_CANDIDATE.value,
                ],
            }
            comparison_properties["semantic_id"] = {
                "type": "string",
                "enum": list(semantic_ids),
            }
    causal_definition = definitions.get("ModelCausalCompetitionDraft")
    if isinstance(causal_definition, dict):
        causal_properties = causal_definition.get("properties")
        if isinstance(causal_properties, dict):
            metric_ids = tuple(
                sorted(
                    item.candidate_id
                    for item in catalog.semantic_refs
                    if item.target_kind
                    in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                )
            )
            dimension_ids = tuple(
                sorted(
                    item.candidate_id
                    for item in catalog.semantic_refs
                    if item.target_kind == SemanticTargetKind.DIMENSION
                )
            )
            causal_properties["effect_semantic_id"] = {
                "type": "string",
                "enum": list(metric_ids),
            }
            causal_properties["effect_observation"] = {
                "type": "string",
                "enum": [item.value for item in CausalEffectObservation],
            }
            causal_properties["candidate_mechanism_semantic_ids"] = {
                "type": "array",
                "items": {"type": "string", "enum": list(metric_ids)},
            }
            causal_properties["diagnostic_dimension_ids"] = {
                "type": "array",
                "items": {"type": "string", "enum": list(dimension_ids)},
            }
    common_names = (
        "goal_key",
        "source_text",
        "source_fragment_text",
        "ranking",
        "comparisons",
        "result_dependency",
    )
    source_fragment_schema = {
        "type": "string",
        "minLength": 1,
    }
    variants: list[dict[str, Any]] = []
    for kind in ResearchGoalKind:
        if kind == ResearchGoalKind.RELATIONSHIP:
            if not relationship_ids:
                continue
            properties = {
                name: copy.deepcopy(base_properties[name])
                for name in common_names
            }
            properties["source_fragment_text"] = copy.deepcopy(
                source_fragment_schema
            )
            properties["kind"] = {
                "type": "string",
                "enum": [kind.value],
            }
            properties["allowed_relationship_id"] = {
                "type": "string",
                "enum": list(relationship_ids),
            }
            properties["relationship_intent"] = {
                "type": "string",
                "enum": [item.value for item in RelationshipIntent],
            }
        else:
            properties = {
                name: copy.deepcopy(base_properties[name])
                for name in common_names
            }
            properties["source_fragment_text"] = copy.deepcopy(
                source_fragment_schema
            )
            properties["kind"] = {
                "type": "string",
                "enum": [kind.value],
            }
            closed_refs = {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(semantic_ids),
                },
            }
            properties["subject_semantic_ids"] = copy.deepcopy(closed_refs)
            properties["related_semantic_ids"] = copy.deepcopy(closed_refs)
            if kind == ResearchGoalKind.COMPARISON:
                properties["material_parent_goal_key"] = copy.deepcopy(
                    base_properties["material_parent_goal_key"]
                )
            if kind == ResearchGoalKind.ROOT_CAUSE:
                raw_causal = copy.deepcopy(base_properties["causal_competition"])
                choices = raw_causal.get("anyOf") or []
                non_null = [
                    item for item in choices
                    if not (isinstance(item, dict) and item.get("type") == "null")
                ]
                if len(non_null) != 1:
                    raise ResearchIntakeError(
                        "INTAKE_SCHEMA_INVALID",
                        "ROOT_CAUSE causal competition schema is invalid",
                    )
                properties["causal_competition"] = non_null[0]
                raw_temporal = copy.deepcopy(
                    base_properties["temporal_material"]
                )
                temporal_choices = raw_temporal.get("anyOf") or []
                temporal_non_null = [
                    item
                    for item in temporal_choices
                    if not (
                        isinstance(item, dict)
                        and item.get("type") == "null"
                    )
                ]
                if not temporal_non_null:
                    raise ResearchIntakeError(
                        "INTAKE_SCHEMA_INVALID",
                        "ROOT_CAUSE temporal material schema is invalid",
                    )
                properties["temporal_material"] = (
                    temporal_non_null[0]
                    if len(temporal_non_null) == 1
                    else {"anyOf": temporal_non_null}
                )
        variants.append(
            {
                "type": "object",
                "properties": properties,
                "required": list(properties),
                "additionalProperties": False,
            }
        )

    goal_definition.clear()
    goal_definition["anyOf"] = variants
    validate_provider_strict_schema(schema)
    return schema


def _ranking_basis_reconsideration_schema() -> dict[str, Any]:
    """Provider contract exposing only the one authority field being reconsidered."""

    schema = strict_json_schema(ModelRankingBasisReconsiderationEnvelope)
    validate_provider_strict_schema(schema)
    return schema


def _change_period_reconsideration_schema(
    time_dimension_semantic_id: str,
) -> dict[str, Any]:
    """Provider contract exposing only the temporal pair being reconsidered."""

    schema = strict_json_schema(ModelChangePeriodReconsiderationEnvelope)
    definitions = schema.get("$defs") or {}
    period_definition = definitions.get("ModelTimePeriodDraft")
    if not isinstance(period_definition, dict):
        raise ResearchIntakeError(
            "INTAKE_CHANGE_PERIOD_SCHEMA_INVALID",
            "ModelTimePeriodDraft definition is absent",
        )
    period_properties = period_definition.get("properties")
    if not isinstance(period_properties, dict):
        raise ResearchIntakeError(
            "INTAKE_CHANGE_PERIOD_SCHEMA_INVALID",
            "ModelTimePeriodDraft properties are absent",
        )
    period_properties["time_dimension_semantic_id"] = {
        "type": "string",
        "enum": [time_dimension_semantic_id],
    }
    validate_provider_strict_schema(schema)
    return schema


def _followup_scope_provider_schema(
    catalog: ResearchIntakeCatalog,
) -> dict[str, Any]:
    schema = strict_json_schema(ModelFollowupScopeEnvelope)
    definitions = schema.get("$defs") or {}
    operation = definitions.get("ModelScopePatchOperationDraft")
    if not isinstance(operation, dict):
        raise ResearchIntakeError(
            "INTAKE_SCOPE_PATCH_SCHEMA_INVALID",
            "scope patch operation definition is absent",
        )
    base = operation.get("properties")
    if not isinstance(base, dict):
        raise ResearchIntakeError(
            "INTAKE_SCOPE_PATCH_SCHEMA_INVALID",
            "scope patch operation properties are absent",
        )

    by_facet = {
        ScopePatchFacet.ENTITY: tuple(
            sorted(
                item.candidate_id
                for item in catalog.semantic_refs
                if item.target_kind == SemanticTargetKind.ENTITY_VALUE
            )
        ),
        ScopePatchFacet.METRIC: tuple(
            sorted(
                item.candidate_id
                for item in catalog.semantic_refs
                if item.target_kind
                in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
            )
        ),
        ScopePatchFacet.BREAKDOWN: tuple(
            sorted(
                item.candidate_id
                for item in catalog.semantic_refs
                if (
                    item.target_kind == SemanticTargetKind.DIMENSION
                    and item.candidate_id
                    not in set(catalog.temporal_dimension_ids)
                )
            )
        ),
    }
    period_definition = definitions.get("ModelTimePeriodDraft")
    if isinstance(period_definition, dict):
        period_properties = period_definition.get("properties")
        if isinstance(period_properties, dict):
            period_properties["time_dimension_semantic_id"] = {
                "type": "string",
                "enum": list(sorted(catalog.temporal_dimension_ids)),
            }

    variants: list[dict[str, Any]] = []
    for facet in ScopePatchFacet:
        properties = {
            "facet": {"type": "string", "enum": [facet.value]},
            "operation": copy.deepcopy(base["operation"]),
            "source_fragment": copy.deepcopy(base["source_fragment"]),
        }
        if facet == ScopePatchFacet.PERIOD:
            properties["periods"] = copy.deepcopy(base["periods"])
        else:
            properties["semantic_ids"] = {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(by_facet[facet]),
                },
            }
        variants.append(
            {
                "type": "object",
                "properties": properties,
                "required": list(properties),
                "additionalProperties": False,
            }
        )
    operation.clear()
    operation["anyOf"] = variants
    validate_provider_strict_schema(schema)
    return schema


class ResearchIntakeCompiler:
    def __init__(
        self,
        *,
        transport: StructuredJSONTransport,
        schema_name: str = "dima_research_intake_v1",
        calendar_reference_date: str | None = None,
    ) -> None:
        self._transport = transport
        self._schema_name = schema_name
        reference = calendar_reference_date or date.today().isoformat()
        try:
            date.fromisoformat(reference)
        except ValueError as exc:
            raise ResearchIntakeError(
                "INTAKE_CALENDAR_REFERENCE_INVALID",
                reference,
            ) from exc
        self._calendar_reference_date = reference

    @property
    def call_count(self) -> int:
        return int(getattr(self._transport, "call_count", 0))

    @staticmethod
    def _catalog_payload(catalog: ResearchIntakeCatalog) -> dict[str, Any]:
        return {
            "context_version": catalog.context_version,
            "supported_domains": sorted(catalog.supported_domains),
            "semantic_refs": [
                {
                    "candidate_id": item.candidate_id,
                    "target_kind": item.target_kind.value,
                    "canonical_name": item.canonical_name,
                    "source_mention": item.source_mention,
                    "dimension_name": item.dimension_name,
                    "value": item.value,
                    "temporal": (
                        item.candidate_id
                        in set(catalog.temporal_dimension_ids)
                    ),
                }
                for item in sorted(
                    catalog.semantic_refs,
                    key=lambda value: value.candidate_id,
                )
            ],
            "temporal_dimension_ids": sorted(
                catalog.temporal_dimension_ids
            ),
            "allowed_relationships": [
                item.model_dump(mode="json")
                for item in sorted(
                    catalog.allowed_relationships,
                    key=lambda value: value.relationship_id,
                )
            ],
        }

    @staticmethod
    def _provider_prior_brief_payload(
        brief: ResearchBrief | None,
    ) -> dict[str, Any] | None:
        """Project prior semantic intent without exposing machine authority.

        The provider may interpret the user's follow-up against prior meaning.
        Durable IDs, scope/version lineage, verification bindings, budgets and
        owner state remain Dima-owned and are never provider-selected.
        """
        if brief is None:
            return None
        return {
            "context_version": brief.context_version,
            "objective": brief.objective,
            "scope": {
                "semantic_ids": sorted(
                    item.candidate_id
                    for item in brief.scope.semantic_refs
                ),
                "time_periods": [
                    item.model_dump(mode="json")
                    for item in brief.scope.periods
                ],
            },
            "questions": [
                {
                    "kind": question.kind.value,
                    "relationship_intent": (
                        question.relationship_intent.value
                        if question.relationship_intent is not None
                        else None
                    ),
                    "source_text": question.source_text,
                    "subject_semantic_ids": [
                        item.candidate_id
                        for item in question.subject_refs
                    ],
                    "related_semantic_ids": [
                        item.candidate_id
                        for item in question.related_refs
                    ],
                    "ranking": (
                        question.ranking.model_dump(mode="json")
                        if question.ranking is not None
                        else None
                    ),
                    "comparisons": [
                        item.model_dump(mode="json")
                        for item in question.comparisons
                    ],
                    "causal_competition": (
                        question.causal_competition.model_dump(mode="json")
                        if question.causal_competition is not None
                        else None
                    ),
                }
                for question in brief.questions
            ],
            "deliverables": [
                {
                    "kind": item.kind.value,
                    "source_text": item.source_text,
                }
                for item in brief.deliverables
            ],
            "required_domains": list(brief.required_domains),
        }

    @staticmethod
    def _relationship_for_goal(
        goal: ModelGoalDraft,
        *,
        catalog: ResearchIntakeCatalog,
    ) -> AllowedRelationship | None:
        if goal.kind != ResearchGoalKind.RELATIONSHIP:
            if goal.allowed_relationship_id is not None:
                raise ResearchIntakeError(
                    "INTAKE_RELATIONSHIP_ID_ON_NON_RELATIONSHIP",
                    goal.goal_key,
                )
            if goal.relationship_intent is not None:
                raise ResearchIntakeError(
                    "INTAKE_RELATIONSHIP_INTENT_ON_NON_RELATIONSHIP",
                    goal.goal_key,
                )
            return None
        if goal.subject_semantic_ids or goal.related_semantic_ids:
            raise ResearchIntakeError(
                "INTAKE_RELATIONSHIP_RECONSTRUCTION_FORBIDDEN",
                goal.goal_key,
            )
        relationship_id = str(goal.allowed_relationship_id or "").strip()
        if not relationship_id:
            raise ResearchIntakeError(
                "INTAKE_RELATIONSHIP_INCOMPLETE",
                goal.goal_key,
            )
        relationship = next(
            (
                item
                for item in catalog.allowed_relationships
                if item.relationship_id == relationship_id
            ),
            None,
        )
        if relationship is None:
            raise ResearchIntakeError(
                "INTAKE_RELATIONSHIP_UNAUTHORIZED",
                goal.goal_key,
            )
        return relationship

    @staticmethod
    def _duplicate_root_cause_goal_keys(
        draft: ModelResearchBriefDraft,
    ) -> tuple[str, ...]:
        """Return exact typed duplicate RCA identities, never text similarity."""
        seen: dict[
            tuple[
                str,
                tuple[str, ...],
                tuple[str, ...],
                tuple[str, ...],
                tuple[str, ...],
            ],
            str,
        ] = {}
        duplicates: list[str] = []
        for goal in draft.goals:
            causal = goal.causal_competition
            if goal.kind != ResearchGoalKind.ROOT_CAUSE or causal is None:
                continue
            identity = (
                causal.effect_semantic_id,
                causal.effect_observation.value,
                tuple(sorted(causal.candidate_mechanism_semantic_ids)),
                tuple(sorted(causal.diagnostic_dimension_ids)),
                tuple(sorted(goal.subject_semantic_ids)),
                tuple(sorted(goal.related_semantic_ids)),
            )
            first = seen.get(identity)
            if first is None:
                seen[identity] = goal.goal_key
                continue
            if first not in duplicates:
                duplicates.append(first)
            duplicates.append(goal.goal_key)
        return tuple(dict.fromkeys(duplicates))

    @staticmethod
    def _canonicalize_analytical_goals(
        draft: ModelResearchBriefDraft,
        *,
        catalog: ResearchIntakeCatalog,
    ) -> ModelResearchBriefDraft:
        """Canonicalize typed analytical authority before execution.

        ROOT_CAUSE causal_competition is itself governed typed semantic intent.
        Its effect/candidate identities therefore belong to the goal's accepted
        measure scope and its diagnostic identities belong to the related scope,
        even when the provider does not redundantly repeat those IDs in the
        generic subject/related arrays. This is deterministic typed assembly,
        not semantic inference.

        A generic OTHER goal can be presentation/epistemic wording rather than a
        distinct analytical obligation. It is safe to remove from P14 when it
        carries no ranking/comparison/relationship/causal analytical surface and
        either:
        - its exact source was also emitted as a typed deliverable and all refs
          are already covered by another typed analytical goal, or
        - all of its governed refs are already covered by exactly one ROOT_CAUSE
          goal. In that second case OTHER adds no independently executable
          analytical authority; P17/P19 already own the evidence/hypothesis
          treatment inside that governed causal investigation.

        Typed RELATIONSHIP/RANKING/TREND/etc., distinct refs/scope, and real
        multi-intent are never collapsed by this rule. No wording, regex,
        similarity or benchmark identity participates in the decision.
        """
        if (
            draft.terminal != ResearchIntakeTerminal.READY
            or not draft.goals
        ):
            return draft

        normalized_goals: list[ModelGoalDraft] = []
        scope_changed = False
        for goal in draft.goals:
            causal = goal.causal_competition
            if goal.kind == ResearchGoalKind.ROOT_CAUSE and causal is not None:
                subject_ids = tuple(
                    dict.fromkeys(
                        (
                            *goal.subject_semantic_ids,
                            causal.effect_semantic_id,
                            *causal.candidate_mechanism_semantic_ids,
                        )
                    )
                )
                related_ids = tuple(
                    dict.fromkeys(
                        (
                            *goal.related_semantic_ids,
                            *causal.diagnostic_dimension_ids,
                        )
                    )
                )
                if (
                    subject_ids != goal.subject_semantic_ids
                    or related_ids != goal.related_semantic_ids
                ):
                    scope_changed = True
                    goal = goal.model_copy(
                        update={
                            "subject_semantic_ids": subject_ids,
                            "related_semantic_ids": related_ids,
                        }
                    )
            normalized_goals.append(goal)

        if scope_changed:
            draft = draft.model_copy(update={"goals": tuple(normalized_goals)})

        presentation_sources = {
            item.source_text
            for item in draft.deliverables
            if item.kind != PresentationKind.NONE
        }
        analytical = tuple(
            item for item in draft.goals
            if item.kind != ResearchGoalKind.OTHER
        )
        if not analytical:
            return draft
        covered_refs: set[str] = set()
        for item in analytical:
            if item.kind == ResearchGoalKind.RELATIONSHIP:
                relationship = ResearchIntakeCompiler._relationship_for_goal(
                    item,
                    catalog=catalog,
                )
                if relationship is None:
                    raise ResearchIntakeError(
                        "INTAKE_RELATIONSHIP_INCOMPLETE",
                        item.goal_key,
                    )
                covered_refs.update(
                    (
                        relationship.left_semantic_id,
                        relationship.right_semantic_id,
                    )
                )
                if relationship.dimension_semantic_id is not None:
                    covered_refs.add(relationship.dimension_semantic_id)
                continue
            covered_refs.update(item.subject_semantic_ids)
            covered_refs.update(item.related_semantic_ids)
        root_ref_sets = tuple(
            frozenset(
                (*item.subject_semantic_ids, *item.related_semantic_ids)
            )
            for item in analytical
            if item.kind == ResearchGoalKind.ROOT_CAUSE
        )

        canonical: list[ModelGoalDraft] = []
        for goal in draft.goals:
            if goal.kind != ResearchGoalKind.OTHER:
                canonical.append(goal)
                continue
            has_distinct_analytical_surface = bool(
                goal.allowed_relationship_id
                or goal.ranking is not None
                or goal.comparisons
                or goal.comparison_texts
                or goal.causal_competition is not None
            )
            refs = set((*goal.subject_semantic_ids, *goal.related_semantic_ids))
            represented_by_deliverable = (
                goal.source_text in presentation_sources
                and not has_distinct_analytical_surface
                and refs.issubset(covered_refs)
            )
            subsumed_by_one_root = (
                not has_distinct_analytical_surface
                and (
                    (
                        not refs
                        and len(root_ref_sets) == 1
                    )
                    or (
                        bool(refs)
                        and sum(
                            refs.issubset(root_refs)
                            for root_refs in root_ref_sets
                        )
                        == 1
                    )
                )
            )
            if represented_by_deliverable or subsumed_by_one_root:
                continue
            canonical.append(goal)

        if len(canonical) == len(draft.goals):
            return draft
        return draft.model_copy(update={"goals": tuple(canonical)})

    @staticmethod
    def _canonicalize_root_temporal_material(
        draft: ModelResearchBriefDraft,
    ) -> ModelResearchBriefDraft:
        """Lift closed ROOT_CAUSE temporal material into durable typed scope."""

        if draft.terminal != ResearchIntakeTerminal.READY:
            return draft
        roots = tuple(
            goal
            for goal in draft.goals
            if goal.kind == ResearchGoalKind.ROOT_CAUSE
        )
        changed = False
        goals: list[ModelGoalDraft] = []
        lifted_periods: list[ModelTimePeriodDraft] = []
        for goal in draft.goals:
            if goal.kind != ResearchGoalKind.ROOT_CAUSE:
                goals.append(goal)
                continue
            temporal = goal.temporal_material
            # Historical deterministic fixtures predate this provider-facing
            # DTO. Existing typed comparisons/time_periods remain authoritative.
            if temporal is None:
                goals.append(goal)
                continue

            temporal_comparisons = tuple(
                item
                for item in goal.comparisons
                if item.role == ComparisonRole.TEMPORAL_PERIOD
            )
            if temporal.mode == "none":
                if temporal_comparisons:
                    raise ResearchIntakeError(
                        "INTAKE_TEMPORAL_MATERIAL_MODE_CONFLICT",
                        goal.goal_key,
                    )
            elif temporal.mode == "window":
                if temporal_comparisons:
                    raise ResearchIntakeError(
                        "INTAKE_TEMPORAL_MATERIAL_MODE_CONFLICT",
                        goal.goal_key,
                    )
                assert temporal.window is not None
                lifted_periods.append(
                    temporal.window.model_copy(
                        update={"role": TemporalRole.MATERIAL_WINDOW}
                    )
                )
            else:
                assert temporal.baseline_period is not None
                assert temporal.comparison_period is not None
                baseline = temporal.baseline_period.model_copy(
                    update={"role": TemporalRole.BASELINE_PERIOD}
                )
                comparison = temporal.comparison_period.model_copy(
                    update={"role": TemporalRole.COMPARISON_PERIOD}
                )
                lifted_periods.extend((baseline, comparison))
                if len(temporal_comparisons) > 1:
                    raise ResearchIntakeError(
                        "INTAKE_TEMPORAL_COMPARISON_AMBIGUOUS",
                        goal.goal_key,
                    )
                if not temporal_comparisons:
                    label = goal.source_fragment_text or goal.source_text
                    goal = goal.model_copy(
                        update={
                            "comparisons": (
                                *goal.comparisons,
                                ModelComparisonDraft(
                                    text=label,
                                    role=ComparisonRole.TEMPORAL_PERIOD,
                                    semantic_id=None,
                                ),
                            )
                        }
                    )
                    changed = True
            goals.append(goal)

        if lifted_periods:
            # With one analytical goal the nested ROOT_CAUSE object is the
            # stronger typed authority. Discard provider-level duplicate/pooled
            # top-level period rendering rather than asking language output to
            # encode the same authority twice.
            source_periods = (
                ()
                if len(draft.goals) == 1 and len(roots) == 1
                else draft.time_periods
            )
            existing = {
                (
                    item.time_dimension_semantic_id,
                    item.start,
                    item.end,
                ): item
                for item in source_periods
            }
            for item in lifted_periods:
                existing[
                    (
                        item.time_dimension_semantic_id,
                        item.start,
                        item.end,
                    )
                ] = item
            draft = draft.model_copy(
                update={"time_periods": tuple(existing.values())}
            )
            changed = True

        if changed:
            draft = draft.model_copy(update={"goals": tuple(goals)})
        return draft

    @staticmethod
    def _canonicalize_temporal_comparison_subgoals(
        draft: ModelResearchBriefDraft,
    ) -> ModelResearchBriefDraft:
        """Absorb typed temporal material subgoals into their canonical RCA owner.

        Live provider output carries explicit material_parent_goal_key on a
        COMPARISON goal. That typed relation is the authority for deciding
        whether the comparison is material for one ROOT_CAUSE or an independent
        analytical obligation. Wording and fragment identity do not participate.

        Historical deterministic fixtures predate the field. For those fixtures
        only, exact source-fragment identity remains a compatibility bridge.
        """

        if draft.terminal != ResearchIntakeTerminal.READY:
            return draft
        roots = tuple(
            goal
            for goal in draft.goals
            if (
                goal.kind == ResearchGoalKind.ROOT_CAUSE
                and goal.causal_competition is not None
            )
        )
        if not roots:
            return draft

        roots_by_key = {goal.goal_key: goal for goal in roots}
        if len(roots_by_key) != len(roots):
            raise ResearchIntakeError(
                "INTAKE_DUPLICATE_GOAL_KEY",
                "ROOT_CAUSE goal keys must be unique",
            )

        merged = dict(roots_by_key)
        removed: set[str] = set()
        for goal in draft.goals:
            if goal.kind != ResearchGoalKind.COMPARISON:
                continue

            temporal_only = (
                goal.ranking is None
                and goal.allowed_relationship_id is None
                and goal.relationship_intent is None
                and goal.causal_competition is None
                and bool(goal.comparisons)
                and all(
                    item.role == ComparisonRole.TEMPORAL_PERIOD
                    and item.semantic_id is None
                    for item in goal.comparisons
                )
            )
            if not temporal_only:
                if goal.material_parent_goal_key is not None:
                    raise ResearchIntakeError(
                        "INTAKE_TEMPORAL_MATERIAL_PARENT_CONFLICT",
                        goal.goal_key,
                    )
                continue

            parent_was_explicit = (
                "material_parent_goal_key" in goal.model_fields_set
            )
            parent_key = goal.material_parent_goal_key

            if parent_key is not None:
                root = merged.get(parent_key)
                if root is None:
                    raise ResearchIntakeError(
                        "INTAKE_TEMPORAL_MATERIAL_PARENT_INVALID",
                        parent_key,
                    )
                temporal = root.temporal_material
                if temporal is None or temporal.mode != "comparison":
                    raise ResearchIntakeError(
                        "INTAKE_TEMPORAL_MATERIAL_PARENT_CONFLICT",
                        parent_key,
                    )
                root_refs = set(
                    (*root.subject_semantic_ids, *root.related_semantic_ids)
                )
                refs = set(
                    (*goal.subject_semantic_ids, *goal.related_semantic_ids)
                )
                if not refs.issubset(root_refs):
                    raise ResearchIntakeError(
                        "INTAKE_TEMPORAL_MATERIAL_PARENT_SCOPE_ESCAPE",
                        goal.goal_key,
                    )
            elif parent_was_explicit:
                # Current strict provider schema requires this nullable field.
                # Explicit null therefore means independently requested intent.
                continue
            else:
                # Compatibility only: historical deterministic fixtures had no
                # typed parent field. Current provider output never uses this.
                if goal.source_fragment_text is None:
                    continue
                refs = set(
                    (*goal.subject_semantic_ids, *goal.related_semantic_ids)
                )
                matches = []
                for candidate in roots:
                    root_refs = set(
                        (
                            *candidate.subject_semantic_ids,
                            *candidate.related_semantic_ids,
                        )
                    )
                    if (
                        candidate.source_fragment_text
                        == goal.source_fragment_text
                        and refs.issubset(root_refs)
                    ):
                        matches.append(candidate)
                if len(matches) != 1:
                    continue
                root = merged[matches[0].goal_key]

            seen = {
                _canonical(item.model_dump(mode="json"))
                for item in root.comparisons
            }
            comparisons = list(root.comparisons)
            for item in goal.comparisons:
                identity = _canonical(item.model_dump(mode="json"))
                if identity not in seen:
                    comparisons.append(item)
                    seen.add(identity)
            merged[root.goal_key] = root.model_copy(
                update={"comparisons": tuple(comparisons)}
            )
            removed.add(goal.goal_key)

        if not removed:
            return draft
        canonical = tuple(
            merged.get(goal.goal_key, goal)
            for goal in draft.goals
            if goal.goal_key not in removed
        )
        return draft.model_copy(update={"goals": canonical})

    @staticmethod
    def _derive_standalone_temporal_comparison(
        draft: ModelResearchBriefDraft,
    ) -> ModelResearchBriefDraft:
        """Project atomic period authority into a durable comparison surface.

        Provider-facing generic comparisons cannot carry TEMPORAL_PERIOD. A
        standalone temporal comparison is therefore recognized only from the
        typed combination of one COMPARISON goal and exactly two role-bound
        same-dimension periods. No wording, month name, metric identity or
        benchmark fixture participates in this projection.
        """

        if draft.terminal != ResearchIntakeTerminal.READY:
            return draft
        if any(
            item.role == ComparisonRole.TEMPORAL_PERIOD
            for goal in draft.goals
            for item in goal.comparisons
        ):
            # Backward-compatible deterministic fixtures may already carry the
            # canonical surface. Existing validation remains authoritative.
            return draft
        if len(draft.time_periods) != 2:
            return draft
        left, right = draft.time_periods
        if {left.role, right.role} != {
            TemporalRole.BASELINE_PERIOD,
            TemporalRole.COMPARISON_PERIOD,
        }:
            return draft
        if (
            left.time_dimension_semantic_id
            != right.time_dimension_semantic_id
        ):
            raise ResearchIntakeError(
                "INTAKE_TEMPORAL_COMPARISON_DIMENSION_DRIFT",
                "typed temporal comparison periods must use one time dimension",
            )

        comparison_goals = tuple(
            goal
            for goal in draft.goals
            if goal.kind == ResearchGoalKind.COMPARISON
        )
        if not comparison_goals:
            return draft
        if len(comparison_goals) != 1:
            raise ResearchIntakeError(
                "INTAKE_TEMPORAL_COMPARISON_AMBIGUOUS",
                "role-bound temporal periods require exactly one comparison owner",
            )

        owner = comparison_goals[0]
        label = owner.source_fragment_text or owner.source_text
        projected = owner.model_copy(
            update={
                "comparisons": (
                    *owner.comparisons,
                    ModelComparisonDraft(
                        text=label,
                        role=ComparisonRole.TEMPORAL_PERIOD,
                        semantic_id=None,
                    ),
                )
            }
        )
        return draft.model_copy(
            update={
                "goals": tuple(
                    projected if goal.goal_key == owner.goal_key else goal
                    for goal in draft.goals
                )
            }
        )

    @staticmethod
    def _ranking_basis_reconsideration_issue(
        draft: ModelResearchBriefDraft,
        *,
        current: str,
        catalog: ResearchIntakeCatalog,
    ) -> dict[str, Any] | None:
        """Detect structurally coupled temporal-comparison ranking authority.

        This function infers nothing from wording. Exact user fragments are
        forwarded to one bounded typed reconsideration call.
        """

        if draft.terminal != ResearchIntakeTerminal.READY:
            return None
        baselines = tuple(
            item
            for item in draft.time_periods
            if item.role == TemporalRole.BASELINE_PERIOD
        )
        comparisons = tuple(
            item
            for item in draft.time_periods
            if item.role == TemporalRole.COMPARISON_PERIOD
        )
        if len(baselines) != 1 or len(comparisons) != 1:
            return None
        baseline, comparison = baselines[0], comparisons[0]
        if (
            baseline.time_dimension_semantic_id
            != comparison.time_dimension_semantic_id
        ):
            return None

        temporal_goals = tuple(
            goal
            for goal in draft.goals
            if (
                goal.kind == ResearchGoalKind.COMPARISON
                and any(
                    item.role == ComparisonRole.TEMPORAL_PERIOD
                    for item in goal.comparisons
                )
            )
        )
        candidates: list[
            tuple[ModelGoalDraft, tuple[ModelGoalDraft, ...]]
        ] = []
        for goal in draft.goals:
            ranking = goal.ranking
            if (
                ranking is None
                or ranking.basis != RankingBasis.LEVEL
                or ranking.measure_semantic_id is None
            ):
                continue
            measure = ranking.measure_semantic_id
            owners = tuple(
                owner
                for owner in temporal_goals
                if measure
                in {
                    *owner.subject_semantic_ids,
                    *owner.related_semantic_ids,
                }
            )
            if owners:
                candidates.append((goal, owners))
        if not candidates:
            return None
        if len(candidates) != 1:
            raise ResearchIntakeError(
                "INTAKE_RANKING_BASIS_RECONSIDERATION_AMBIGUOUS",
                "multiple LEVEL rankings share typed temporal comparison material",
            )

        ranking_goal, owners = candidates[0]
        ranking_fragment = ranking_goal.source_fragment_text
        comparison_fragments = tuple(
            owner.source_fragment_text for owner in owners
        )
        if (
            ranking_fragment is None
            or ranking_fragment != ranking_fragment.strip()
            or ranking_fragment not in current
            or any(
                fragment is None
                or fragment != fragment.strip()
                or fragment not in current
                for fragment in comparison_fragments
            )
        ):
            raise ResearchIntakeError(
                "INTAKE_RANKING_BASIS_SOURCE_FRAGMENT_REQUIRED",
                "ranking-basis deliberation requires exact verbatim user fragments",
            )

        measure = ranking_goal.ranking.measure_semantic_id
        assert measure is not None
        accepted_metric_refs = [
            {
                "candidate_id": item.candidate_id,
                "canonical_name": item.canonical_name,
            }
            for item in catalog.semantic_refs
            if (
                item.candidate_id == measure
                and item.target_kind
                in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
            )
        ]
        if len(accepted_metric_refs) != 1:
            raise ResearchIntakeError(
                "INTAKE_RANKING_MEASURE_UNAUTHORIZED",
                measure,
            )
        return {
            "kind": "RANKING_BASIS_DELIBERATION",
            "ranking_goal_key": ranking_goal.goal_key,
            "current_basis": RankingBasis.LEVEL.value,
            "ranking_source_fragment": ranking_fragment,
            "comparison_source_fragments": list(comparison_fragments),
            "accepted_metric_refs": accepted_metric_refs,
            "typed_periods": [
                baseline.model_dump(mode="json"),
                comparison.model_dump(mode="json"),
            ],
            "candidate_ranking_measure": measure,
        }

    @staticmethod
    def _change_ranking_period_reconsideration_issue(
        draft: ModelResearchBriefDraft,
        *,
        current: str,
        calendar_reference_date: str,
    ) -> dict[str, Any] | None:
        """Detect a structurally suspicious CHANGE pair without calendar guessing.

        Exact collapse is always invalid. Partial overlap is not automatically
        invalid because rolling comparisons are legitimate; one narrow model
        adjudication decides only period bounds from exact user fragments.
        """

        if draft.terminal != ResearchIntakeTerminal.READY:
            return None
        change_goals = tuple(
            goal
            for goal in draft.goals
            if (
                goal.ranking is not None
                and goal.ranking.basis == RankingBasis.CHANGE
            )
        )
        if len(change_goals) != 1:
            return None
        baselines = tuple(
            item
            for item in draft.time_periods
            if item.role == TemporalRole.BASELINE_PERIOD
        )
        comparisons = tuple(
            item
            for item in draft.time_periods
            if item.role == TemporalRole.COMPARISON_PERIOD
        )
        if len(baselines) != 1 or len(comparisons) != 1:
            return None
        baseline, comparison = baselines[0], comparisons[0]
        if (
            baseline.time_dimension_semantic_id
            != comparison.time_dimension_semantic_id
        ):
            return None

        collapsed = (
            baseline.start,
            baseline.end,
        ) == (
            comparison.start,
            comparison.end,
        )

        def parse_bound(value: str):
            if "T" not in value:
                return ("date", date.fromisoformat(value))
            normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return ("datetime", parsed)

        overlap = False
        if not collapsed:
            try:
                b_start_kind, b_start = parse_bound(baseline.start)
                b_end_kind, b_end = parse_bound(baseline.end)
                c_start_kind, c_start = parse_bound(comparison.start)
                c_end_kind, c_end = parse_bound(comparison.end)
            except (TypeError, ValueError):
                return None
            kinds = {
                b_start_kind,
                b_end_kind,
                c_start_kind,
                c_end_kind,
            }
            if len(kinds) == 1:
                overlap = max(b_start, c_start) < min(b_end, c_end)
        period_source_ungrounded = any(
            item.source_text != item.source_text.strip()
            or item.source_text not in current
            for item in (baseline, comparison)
        )
        shared_source_surface = baseline.source_text == comparison.source_text
        if (
            not collapsed
            and not overlap
            and not period_source_ungrounded
            and not shared_source_surface
        ):
            return None

        ranking_goal = change_goals[0]
        ranking_fragment = ranking_goal.source_fragment_text
        if (
            ranking_fragment is None
            or ranking_fragment != ranking_fragment.strip()
            or ranking_fragment not in current
        ):
            raise ResearchIntakeError(
                "INTAKE_CHANGE_PERIOD_SOURCE_FRAGMENT_REQUIRED",
                "temporal deliberation requires an exact ranking source fragment",
            )

        measure = ranking_goal.ranking.measure_semantic_id
        comparison_fragments = tuple(
            goal.source_fragment_text
            for goal in draft.goals
            if (
                goal.kind == ResearchGoalKind.COMPARISON
                and measure is not None
                and measure
                in {
                    *goal.subject_semantic_ids,
                    *goal.related_semantic_ids,
                }
            )
        )
        if any(
            fragment is None
            or fragment != fragment.strip()
            or fragment not in current
            for fragment in comparison_fragments
        ):
            raise ResearchIntakeError(
                "INTAKE_CHANGE_PERIOD_SOURCE_FRAGMENT_REQUIRED",
                "temporal deliberation requires exact comparison source fragments",
            )

        return {
            "kind": "CHANGE_PERIOD_PAIR_DELIBERATION",
            "reason": (
                "COLLAPSED"
                if collapsed
                else "OVERLAPPING"
                if overlap
                else "UNGROUNDED_PERIOD_SOURCE"
                if period_source_ungrounded
                else "SHARED_SOURCE_SURFACE"
            ),
            "time_dimension_semantic_id": baseline.time_dimension_semantic_id,
            "calendar_reference_date": calendar_reference_date,
            "ranking_source_fragment": ranking_fragment,
            "comparison_source_fragments": list(comparison_fragments),
            "baseline_period": baseline.model_dump(mode="json"),
            "comparison_period": comparison.model_dump(mode="json"),
        }

    @staticmethod
    def _assert_change_ranking_temporal_contract(
        draft: ModelResearchBriefDraft,
    ) -> None:
        if draft.terminal != ResearchIntakeTerminal.READY:
            return
        if not any(
            goal.ranking is not None
            and goal.ranking.basis == RankingBasis.CHANGE
            for goal in draft.goals
        ):
            return
        baselines = tuple(
            item
            for item in draft.time_periods
            if item.role == TemporalRole.BASELINE_PERIOD
        )
        comparisons = tuple(
            item
            for item in draft.time_periods
            if item.role == TemporalRole.COMPARISON_PERIOD
        )
        if len(baselines) != 1 or len(comparisons) != 1:
            raise ResearchIntakeError(
                "INTAKE_CHANGE_RANKING_COMPARISON_REQUIRED",
                "CHANGE ranking requires exactly one baseline and one comparison period",
            )
        baseline, comparison = baselines[0], comparisons[0]
        if (
            baseline.time_dimension_semantic_id
            != comparison.time_dimension_semantic_id
        ):
            raise ResearchIntakeError(
                "INTAKE_CHANGE_RANKING_TIME_DIMENSION_DRIFT",
                "CHANGE ranking periods must use one governed time dimension",
            )
        if (
            baseline.start,
            baseline.end,
        ) == (
            comparison.start,
            comparison.end,
        ):
            raise ResearchIntakeError(
                "INTAKE_CHANGE_RANKING_PERIOD_PAIR_COLLAPSED",
                "CHANGE ranking baseline and comparison periods must be distinct bounded spans",
            )

    @staticmethod
    def _change_ranking_collapsed_period_issue(
        draft: ModelResearchBriefDraft,
    ) -> dict[str, Any] | None:
        """Detect only the proven invalid CHANGE pair collapse.

        A role-bound baseline/comparison pair cannot denote CHANGE when both
        periods have the exact same governed time dimension and half-open span.
        This check does not parse wording or manufacture calendar authority.
        """

        if draft.terminal != ResearchIntakeTerminal.READY:
            return None
        if not any(
            goal.ranking is not None
            and goal.ranking.basis == RankingBasis.CHANGE
            for goal in draft.goals
        ):
            return None
        if len(draft.time_periods) != 2:
            return None

        left, right = draft.time_periods
        if {left.role, right.role} != {
            TemporalRole.BASELINE_PERIOD,
            TemporalRole.COMPARISON_PERIOD,
        }:
            return None
        if (
            left.time_dimension_semantic_id
            != right.time_dimension_semantic_id
        ):
            return None
        if (left.start, left.end) != (right.start, right.end):
            return None

        return {
            "kind": "CHANGE_PERIOD_PAIR_COLLAPSED",
            "time_dimension_semantic_id": left.time_dimension_semantic_id,
            "baseline": {
                "start": left.start,
                "end": left.end,
            },
            "comparison": {
                "start": right.start,
                "end": right.end,
            },
        }

    @staticmethod
    def _canonicalize_change_ranking_period_roles(
        draft: ModelResearchBriefDraft,
    ) -> ModelResearchBriefDraft:
        """Bind CHANGE ranking authority to exactly two typed period roles.

        RankingBasis.CHANGE is itself typed temporal-comparison authority. When
        the provider has already resolved exactly two same-dimension bounded
        periods but left both with the neutral MATERIAL_WINDOW role, Dima may
        deterministically assign earlier/later baseline/comparison roles. No
        wording, benchmark identity, metric name, tuple order, or prompt
        heuristic participates.
        """

        if draft.terminal != ResearchIntakeTerminal.READY:
            return draft
        change_goals = tuple(
            goal
            for goal in draft.goals
            if (
                goal.ranking is not None
                and goal.ranking.basis == RankingBasis.CHANGE
            )
        )
        if not change_goals:
            return draft
        if len(draft.time_periods) != 2:
            return draft

        left, right = draft.time_periods
        if (
            left.time_dimension_semantic_id
            != right.time_dimension_semantic_id
        ):
            raise ResearchIntakeError(
                "INTAKE_CHANGE_RANKING_TIME_DIMENSION_DRIFT",
                "CHANGE ranking periods must use one governed time dimension",
            )
        existing = {left.role, right.role}
        if existing == {
            TemporalRole.BASELINE_PERIOD,
            TemporalRole.COMPARISON_PERIOD,
        }:
            return draft
        if existing != {TemporalRole.MATERIAL_WINDOW}:
            raise ResearchIntakeError(
                "INTAKE_CHANGE_RANKING_PERIOD_ROLE_CONFLICT",
                "CHANGE ranking conflicts with non-comparison period roles",
            )

        ordered = sorted(
            (left, right),
            key=lambda item: (item.start, item.end, item.source_text),
        )
        baseline = ordered[0].model_copy(
            update={"role": TemporalRole.BASELINE_PERIOD}
        )
        comparison = ordered[1].model_copy(
            update={"role": TemporalRole.COMPARISON_PERIOD}
        )
        by_identity = {
            (
                baseline.time_dimension_semantic_id,
                baseline.start,
                baseline.end,
                baseline.source_text,
            ): baseline,
            (
                comparison.time_dimension_semantic_id,
                comparison.start,
                comparison.end,
                comparison.source_text,
            ): comparison,
        }
        canonical = tuple(
            by_identity[
                (
                    item.time_dimension_semantic_id,
                    item.start,
                    item.end,
                    item.source_text,
                )
            ]
            for item in draft.time_periods
        )
        return draft.model_copy(update={"time_periods": canonical})

    @staticmethod
    def _canonicalize_typed_temporal_comparison(
        draft: ModelResearchBriefDraft,
    ) -> ModelResearchBriefDraft:
        """Bind typed temporal-comparison authority to exact period roles.

        The provider decides only whether the user asked for a temporal
        comparison and resolves exact periods. Dima deterministically assigns
        the operational earlier/later role when exactly one temporal-comparison
        goal and exactly two same-dimension periods exist. No wording, tuple
        position, metric identity, month name, or benchmark case participates.
        """

        if draft.terminal != ResearchIntakeTerminal.READY:
            return draft
        comparison_goals = tuple(
            goal
            for goal in draft.goals
            if any(
                item.role == ComparisonRole.TEMPORAL_PERIOD
                for item in goal.comparisons
            )
        )
        if not comparison_goals:
            return draft
        if len(comparison_goals) != 1:
            raise ResearchIntakeError(
                "INTAKE_TEMPORAL_COMPARISON_AMBIGUOUS",
                "multiple analytical goals carry temporal-comparison authority",
            )
        if len(draft.time_periods) != 2:
            raise ResearchIntakeError(
                "INTAKE_TEMPORAL_COMPARISON_PERIODS_REQUIRED",
                "one typed temporal comparison requires exactly two accepted periods",
            )
        left, right = draft.time_periods
        if (
            left.time_dimension_semantic_id
            != right.time_dimension_semantic_id
        ):
            raise ResearchIntakeError(
                "INTAKE_TEMPORAL_COMPARISON_DIMENSION_DRIFT",
                "typed temporal comparison periods must use one time dimension",
            )
        existing = {left.role, right.role}
        if existing == {
            TemporalRole.BASELINE_PERIOD,
            TemporalRole.COMPARISON_PERIOD,
        }:
            return draft
        if existing != {TemporalRole.MATERIAL_WINDOW}:
            raise ResearchIntakeError(
                "INTAKE_TEMPORAL_COMPARISON_ROLE_CONFLICT",
                "typed temporal comparison conflicts with non-comparison period roles",
            )
        ordered = sorted(
            (left, right),
            key=lambda item: (item.start, item.end, item.source_text),
        )
        baseline = ordered[0].model_copy(
            update={"role": TemporalRole.BASELINE_PERIOD}
        )
        comparison = ordered[1].model_copy(
            update={"role": TemporalRole.COMPARISON_PERIOD}
        )
        by_identity = {
            (
                baseline.time_dimension_semantic_id,
                baseline.start,
                baseline.end,
                baseline.source_text,
            ): baseline,
            (
                comparison.time_dimension_semantic_id,
                comparison.start,
                comparison.end,
                comparison.source_text,
            ): comparison,
        }
        canonical = tuple(
            by_identity[
                (
                    item.time_dimension_semantic_id,
                    item.start,
                    item.end,
                    item.source_text,
                )
            ]
            for item in draft.time_periods
        )
        return draft.model_copy(update={"time_periods": canonical})

    @staticmethod
    def _canonicalize_exact_period_repeats(
        draft: ModelResearchBriefDraft,
    ) -> ModelResearchBriefDraft:
        """Collapse only byte-equivalent typed period DTO repetition.

        A provider may mechanically repeat the exact same structured period
        object. That carries zero additional authority and is safe to make
        idempotent before durable binding. Any difference in wording, role,
        dimension or bounds remains visible to the existing duplicate/conflict
        checks and therefore still fails closed.
        """
        if (
            draft.terminal != ResearchIntakeTerminal.READY
            or len(draft.time_periods) < 2
        ):
            return draft
        seen: set[str] = set()
        periods: list[ModelTimePeriodDraft] = []
        for item in draft.time_periods:
            identity = _canonical(item.model_dump(mode="json"))
            if identity in seen:
                continue
            seen.add(identity)
            periods.append(item)
        if len(periods) == len(draft.time_periods):
            return draft
        return draft.model_copy(update={"time_periods": tuple(periods)})

    @staticmethod
    def _ids(prefix: str, seed: dict[str, Any], ordinal: int) -> str:
        raw = _canonical({"seed": seed, "ordinal": ordinal})
        return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]

    @staticmethod
    def _followup_questions(
        *,
        prior_brief: ResearchBrief,
        accepted_scope: ResearchScope,
        changed_facets: tuple[ScopePatchFacet, ...],
    ) -> tuple[ResearchQuestion, ...]:
        if not changed_facets:
            return prior_brief.questions

        accepted = {
            item.candidate_id: item
            for item in accepted_scope.semantic_refs
        }
        accepted_metrics = tuple(
            item
            for item in accepted_scope.semantic_refs
            if item.target_kind
            in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
        accepted_entities = tuple(
            item
            for item in accepted_scope.semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        )
        accepted_breakdowns = tuple(
            item
            for item in accepted_scope.semantic_refs
            if (
                item.target_kind == SemanticTargetKind.DIMENSION
                and item.candidate_id
                not in set(accepted_scope.temporal_dimension_ids)
            )
        )
        changed = set(changed_facets)
        metric_question_count = sum(
            1
            for question in prior_brief.questions
            if any(
                item.target_kind
                in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                for item in (*question.subject_refs, *question.related_refs)
            )
        )
        output: list[ResearchQuestion] = []
        for question in prior_brief.questions:
            original = tuple((*question.subject_refs, *question.related_refs))
            original_metric_ids = {
                item.candidate_id
                for item in original
                if item.target_kind
                in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
            }
            had_metrics = bool(original_metric_ids)
            had_entities = any(
                item.target_kind == SemanticTargetKind.ENTITY_VALUE
                for item in original
            )
            had_breakdowns = any(
                item.target_kind == SemanticTargetKind.DIMENSION
                and item.candidate_id
                not in set(prior_brief.scope.temporal_dimension_ids)
                for item in original
            )

            subject = [
                item
                for item in question.subject_refs
                if item.candidate_id in accepted
            ]
            related = [
                item
                for item in question.related_refs
                if item.candidate_id in accepted
            ]

            def append_unique(target, values):
                seen = {item.candidate_id for item in (*subject, *related)}
                for value in values:
                    if value.candidate_id not in seen:
                        target.append(value)
                        seen.add(value.candidate_id)

            if ScopePatchFacet.METRIC in changed and had_metrics:
                subject = [
                    item
                    for item in subject
                    if item.target_kind
                    not in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                ]
                related = [
                    item
                    for item in related
                    if item.target_kind
                    not in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                ]
                if metric_question_count == 1:
                    append_unique(subject, accepted_metrics)
                else:
                    retained = tuple(
                        accepted[candidate_id]
                        for candidate_id in sorted(
                            original_metric_ids & set(accepted)
                        )
                    )
                    if not retained:
                        # Explicit scope removal retires the obligation whose
                        # only governed measure left the accepted scope.  Do not
                        # silently rewrite it into another metric goal.
                        continue
                    append_unique(subject, retained)

            if ScopePatchFacet.ENTITY in changed and had_entities:
                subject = [
                    item
                    for item in subject
                    if item.target_kind != SemanticTargetKind.ENTITY_VALUE
                ]
                related = [
                    item
                    for item in related
                    if item.target_kind != SemanticTargetKind.ENTITY_VALUE
                ]
                append_unique(subject, accepted_entities)

            if ScopePatchFacet.BREAKDOWN in changed and had_breakdowns:
                subject = [
                    item
                    for item in subject
                    if not (
                        item.target_kind == SemanticTargetKind.DIMENSION
                        and item.candidate_id
                        not in set(accepted_scope.temporal_dimension_ids)
                    )
                ]
                related = [
                    item
                    for item in related
                    if not (
                        item.target_kind == SemanticTargetKind.DIMENSION
                        and item.candidate_id
                        not in set(accepted_scope.temporal_dimension_ids)
                    )
                ]
                append_unique(related, accepted_breakdowns)

            causal = question.causal_competition
            if causal is not None:
                refs = {
                    item.candidate_id for item in (*subject, *related)
                }
                required = {
                    causal.effect_semantic_id,
                    *causal.candidate_mechanism_semantic_ids,
                    *causal.diagnostic_dimension_ids,
                }
                if not required.issubset(refs):
                    raise ResearchIntakeError(
                        "INTAKE_SCOPE_PATCH_CAUSAL_IDENTITY_CONFLICT",
                        question.goal_id,
                    )

            output.append(
                question.model_copy(
                    update={
                        "subject_refs": tuple(subject),
                        "related_refs": tuple(related),
                    }
                )
            )

        if not output:
            raise ResearchIntakeError(
                "INTAKE_SCOPE_PATCH_REMOVED_ALL_GOALS",
                "scope patch removed every accepted analytical obligation",
            )
        return tuple(output)

    def _compile_followup_scope_patch(
        self,
        *,
        current: str,
        catalog: ResearchIntakeCatalog,
        prior_brief: ResearchBrief,
    ) -> ResearchIntakeResult:
        if prior_brief.context_version != catalog.context_version:
            raise ResearchIntakeError(
                "INTAKE_SCOPE_CONTEXT_MISMATCH",
                "follow-up scope must remain inside the accepted semantic context",
            )
        raw = self._transport.structured_json(
            _FOLLOWUP_SCOPE_SYSTEM,
            _canonical(
                {
                    "current_user_message": current,
                    "grounded_catalog": self._catalog_payload(catalog),
                    "prior_brief": self._provider_prior_brief_payload(
                        prior_brief
                    ),
                    "calendar_reference_date": self._calendar_reference_date,
                    "instruction": (
                        "Return only the grounded CURRENT-turn scope delta. "
                        "Absent facets inherit from prior scope."
                    ),
                }
            ),
            schema=_followup_scope_provider_schema(catalog),
            schema_name=self._schema_name + "_scope_patch",
        )
        try:
            envelope = ModelFollowupScopeEnvelope.model_validate_json(raw)
        except Exception as exc:
            raise ResearchIntakeError(
                "INTAKE_SCOPE_PATCH_MODEL_OUTPUT_INVALID",
                "structured follow-up output failed the typed patch contract",
            ) from exc
        provider_result = envelope.result
        if isinstance(provider_result, ModelClarifyResearchIntake):
            return ResearchIntakeResult(
                terminal=ResearchIntakeTerminal.CLARIFY,
                clarification_question=provider_result.clarification_question,
                catalog_fingerprint=catalog.fingerprint,
                model_calls=self.call_count,
            )
        if isinstance(provider_result, ModelUnsupportedResearchIntake):
            return ResearchIntakeResult(
                terminal=ResearchIntakeTerminal.UNSUPPORTED,
                unsupported_reason=provider_result.unsupported_reason,
                catalog_fingerprint=catalog.fingerprint,
                model_calls=self.call_count,
            )

        by_id = {item.candidate_id: item for item in catalog.semantic_refs}
        binding_by_id = {
            item.candidate_id: item
            for item in catalog.native_verification_bindings
        }
        operations: list[ScopePatchOperation] = []
        for item in provider_result.operations:
            fragment = item.source_fragment
            if fragment != fragment.strip() or fragment not in current:
                raise ResearchIntakeError(
                    "INTAKE_SCOPE_PATCH_SOURCE_UNGROUNDED",
                    fragment,
                )

            if item.facet == ScopePatchFacet.PERIOD:
                periods: list[ResearchTimePeriod] = []
                temporal_refs: dict[str, ResearchSemanticRef] = {}
                for period in item.periods:
                    if (
                        period.time_dimension_semantic_id
                        not in set(catalog.temporal_dimension_ids)
                    ):
                        raise ResearchIntakeError(
                            "INTAKE_TIME_DIMENSION_UNAUTHORIZED",
                            period.time_dimension_semantic_id,
                        )
                    ref = by_id.get(period.time_dimension_semantic_id)
                    if (
                        ref is None
                        or ref.target_kind != SemanticTargetKind.DIMENSION
                    ):
                        raise ResearchIntakeError(
                            "INTAKE_TIME_DIMENSION_UNAUTHORIZED",
                            period.time_dimension_semantic_id,
                        )
                    temporal_refs[ref.candidate_id] = ref
                    try:
                        periods.append(
                            ResearchTimePeriod(
                                source_text=period.source_text,
                                time_dimension_candidate_id=(
                                    period.time_dimension_semantic_id
                                ),
                                start=period.start,
                                end=period.end,
                                role=period.role,
                            )
                        )
                    except ValueError as exc:
                        raise ResearchIntakeError(
                            "INTAKE_TIME_PERIOD_INVALID",
                            str(exc),
                        ) from exc
                refs = tuple(temporal_refs.values())
            else:
                refs_list: list[ResearchSemanticRef] = []
                for candidate_id in item.semantic_ids:
                    ref = by_id.get(candidate_id)
                    if ref is None:
                        raise ResearchIntakeError(
                            "INTAKE_SCOPE_PATCH_REF_UNAUTHORIZED",
                            candidate_id,
                        )
                    if (
                        item.facet == ScopePatchFacet.ENTITY
                        and ref.target_kind
                        != SemanticTargetKind.ENTITY_VALUE
                    ):
                        raise ResearchIntakeError(
                            "INTAKE_SCOPE_PATCH_REF_KIND_INVALID",
                            candidate_id,
                        )
                    if (
                        item.facet == ScopePatchFacet.METRIC
                        and ref.target_kind
                        not in {
                            SemanticTargetKind.METRIC,
                            SemanticTargetKind.KPI,
                        }
                    ):
                        raise ResearchIntakeError(
                            "INTAKE_SCOPE_PATCH_REF_KIND_INVALID",
                            candidate_id,
                        )
                    if (
                        item.facet == ScopePatchFacet.BREAKDOWN
                        and (
                            ref.target_kind != SemanticTargetKind.DIMENSION
                            or ref.candidate_id
                            in set(catalog.temporal_dimension_ids)
                        )
                    ):
                        raise ResearchIntakeError(
                            "INTAKE_SCOPE_PATCH_REF_KIND_INVALID",
                            candidate_id,
                        )
                    refs_list.append(ref)
                refs = tuple(refs_list)
                periods = []

            operations.append(
                ScopePatchOperation(
                    facet=item.facet,
                    operation=item.operation,
                    semantic_refs=refs,
                    periods=tuple(periods),
                    native_verification_bindings=tuple(
                        binding_by_id[ref.candidate_id]
                        for ref in refs
                        if ref.candidate_id in binding_by_id
                    ),
                    source_fragment=fragment,
                )
            )

        try:
            patch = TurnScopePatch(
                source_scope_version_id=(
                    prior_brief.scope.scope_version.version_id
                ),
                operations=tuple(operations),
            )
            resolved = resolve_scope_patch(
                prior_brief.scope,
                patch,
                context_version=catalog.context_version,
            )
        except ValueError as exc:
            raise ResearchIntakeError(
                "INTAKE_SCOPE_PATCH_INVALID",
                str(exc),
            ) from exc

        questions = self._followup_questions(
            prior_brief=prior_brief,
            accepted_scope=resolved.current_scope,
            changed_facets=resolved.changed_facets,
        )
        identity = {
            "prior_brief_id": prior_brief.brief_id,
            "current_user_message": current,
            "patch": patch.model_dump(mode="json"),
            "scope_fingerprint": resolved.scope_fingerprint,
        }
        active_goal_ids = {item.goal_id for item in questions}
        deliverable_ids = {
            item.requirement_id for item in prior_brief.deliverables
        }
        brief = prior_brief.model_copy(
            update={
                "brief_id": "rb_" + hashlib.sha256(
                    _canonical(identity).encode("utf-8")
                ).hexdigest()[:24],
                "scope": resolved.current_scope,
                "questions": questions,
                "must_requirement_ids": tuple(
                    item
                    for item in prior_brief.must_requirement_ids
                    if item in active_goal_ids or item in deliverable_ids
                ),
                "blocking_goal_ids": tuple(
                    item
                    for item in prior_brief.blocking_goal_ids
                    if item in active_goal_ids
                ),
            }
        )
        return ResearchIntakeResult(
            terminal=ResearchIntakeTerminal.READY,
            brief=brief,
            investigation_requirements=(),
            scope_contract=resolved.scope_contract,
            catalog_fingerprint=catalog.fingerprint,
            model_calls=self.call_count,
        )

    def compile(
        self,
        *,
        question: str,
        catalog: ResearchIntakeCatalog,
        prior_brief: ResearchBrief | None = None,
    ) -> ResearchIntakeResult:
        current = str(question or "").strip()
        if not current:
            raise ResearchIntakeError(
                "INTAKE_QUESTION_REQUIRED",
                "current user question is required",
            )
        if prior_brief is not None:
            return self._compile_followup_scope_patch(
                current=current,
                catalog=catalog,
                prior_brief=prior_brief,
            )

        def invoke_provider(
            *,
            instruction: str,
            reconsideration: dict[str, Any] | None = None,
        ) -> ModelResearchBriefDraft:
            user_payload: dict[str, Any] = {
                "current_user_message": current,
                "grounded_catalog": self._catalog_payload(catalog),
                "prior_brief": self._provider_prior_brief_payload(prior_brief),
                "calendar_reference_date": self._calendar_reference_date,
                "instruction": instruction,
            }
            if reconsideration is not None:
                user_payload["reconsideration"] = reconsideration
            raw = self._transport.structured_json(
                _SYSTEM,
                _canonical(user_payload),
                schema=_intake_provider_schema(
                    catalog,
                    has_prior_brief=prior_brief is not None,
                ),
                schema_name=self._schema_name,
            )
            try:
                envelope = ModelResearchIntakeEnvelope.model_validate_json(raw)
                provider_result = envelope.result
                if isinstance(provider_result, ModelReadyResearchIntake):
                    return ModelResearchBriefDraft(
                        terminal=ResearchIntakeTerminal.READY,
                        objective=provider_result.objective,
                        goals=provider_result.goals,
                        deliverables=provider_result.deliverables,
                        investigation_directives=(
                            provider_result.investigation_directives
                        ),
                        time_surfaces=tuple(
                            item.source_text
                            for item in provider_result.time_periods
                        ),
                        time_periods=provider_result.time_periods,
                        required_domains=provider_result.required_domains,
                        scope_mutation_kind=(
                            provider_result.scope_mutation_kind
                        ),
                    )
                if isinstance(provider_result, ModelClarifyResearchIntake):
                    return ModelResearchBriefDraft(
                        terminal=ResearchIntakeTerminal.CLARIFY,
                        clarification_question=(
                            provider_result.clarification_question
                        ),
                    )
                return ModelResearchBriefDraft(
                    terminal=ResearchIntakeTerminal.UNSUPPORTED,
                    unsupported_reason=provider_result.unsupported_reason,
                )
            except Exception as exc:
                raise ResearchIntakeError(
                    "INTAKE_MODEL_OUTPUT_INVALID",
                    "structured provider output failed the typed intake contract",
                ) from exc

        def reconsider_ranking_basis(
            draft: ModelResearchBriefDraft,
            issue: dict[str, Any],
        ) -> ModelResearchBriefDraft:
            raw = self._transport.structured_json(
                _RANKING_BASIS_RECONSIDERATION_SYSTEM,
                _canonical(
                    {
                        "reconsideration": issue,
                        "instruction": (
                            "Return only typed ranking basis authority or CLARIFY. "
                            "All omitted semantic state is immutable."
                        ),
                    }
                ),
                schema=_ranking_basis_reconsideration_schema(),
                schema_name=self._schema_name + "_ranking_basis",
            )
            try:
                envelope = (
                    ModelRankingBasisReconsiderationEnvelope.model_validate_json(
                        raw
                    )
                )
            except Exception as exc:
                raise ResearchIntakeError(
                    "INTAKE_RANKING_BASIS_MODEL_OUTPUT_INVALID",
                    "ranking-basis output failed the narrow typed contract",
                ) from exc
            provider_result = envelope.result
            if isinstance(provider_result, ModelClarifyResearchIntake):
                return ModelResearchBriefDraft(
                    terminal=ResearchIntakeTerminal.CLARIFY,
                    clarification_question=(
                        provider_result.clarification_question
                    ),
                )

            goal_key = str(issue["ranking_goal_key"])
            measure = str(issue["candidate_ranking_measure"])
            changed = False
            goals: list[ModelGoalDraft] = []
            for goal in draft.goals:
                if goal.goal_key != goal_key:
                    goals.append(goal)
                    continue
                if (
                    goal.ranking is None
                    or goal.ranking.measure_semantic_id != measure
                ):
                    raise ResearchIntakeError(
                        "INTAKE_RANKING_BASIS_TARGET_DRIFT",
                        goal_key,
                    )
                goals.append(
                    goal.model_copy(
                        update={
                            "ranking": goal.ranking.model_copy(
                                update={"basis": provider_result.basis}
                            )
                        }
                    )
                )
                changed = True
            if not changed:
                raise ResearchIntakeError(
                    "INTAKE_RANKING_BASIS_TARGET_MISSING",
                    goal_key,
                )
            return draft.model_copy(update={"goals": tuple(goals)})

        def reconsider_change_period_pair(
            draft: ModelResearchBriefDraft,
            issue: dict[str, Any],
        ) -> ModelResearchBriefDraft:
            time_dimension = str(issue["time_dimension_semantic_id"])
            raw = self._transport.structured_json(
                _CHANGE_PERIOD_RECONSIDERATION_SYSTEM,
                _canonical(
                    {
                        "reconsideration": issue,
                        "instruction": (
                            "Return only typed baseline/comparison period authority "
                            "or CLARIFY. All omitted semantic state is immutable."
                        ),
                    }
                ),
                schema=_change_period_reconsideration_schema(time_dimension),
                schema_name=self._schema_name + "_change_period_pair",
            )
            try:
                envelope = (
                    ModelChangePeriodReconsiderationEnvelope.model_validate_json(
                        raw
                    )
                )
            except Exception as exc:
                raise ResearchIntakeError(
                    "INTAKE_CHANGE_PERIOD_MODEL_OUTPUT_INVALID",
                    "change-period output failed the narrow typed contract",
                ) from exc
            provider_result = envelope.result
            if isinstance(provider_result, ModelClarifyResearchIntake):
                return ModelResearchBriefDraft(
                    terminal=ResearchIntakeTerminal.CLARIFY,
                    clarification_question=(
                        provider_result.clarification_question
                    ),
                )

            if (
                provider_result.baseline_period.time_dimension_semantic_id
                != time_dimension
                or provider_result.comparison_period.time_dimension_semantic_id
                != time_dimension
            ):
                raise ResearchIntakeError(
                    "INTAKE_CHANGE_PERIOD_TIME_DIMENSION_DRIFT",
                    time_dimension,
                )

            resolved_sources = (
                provider_result.baseline_period.source_text,
                provider_result.comparison_period.source_text,
            )
            if any(
                source != source.strip() or source not in current
                for source in resolved_sources
            ):
                raise ResearchIntakeError(
                    "INTAKE_CHANGE_PERIOD_SOURCE_FRAGMENT_NOT_VERBATIM",
                    "resolved temporal authority must retain exact user source provenance",
                )
            original_baselines = tuple(
                item
                for item in draft.time_periods
                if item.role == TemporalRole.BASELINE_PERIOD
            )
            original_comparisons = tuple(
                item
                for item in draft.time_periods
                if item.role == TemporalRole.COMPARISON_PERIOD
            )
            if len(original_baselines) != 1 or len(original_comparisons) != 1:
                raise ResearchIntakeError(
                    "INTAKE_CHANGE_RANKING_COMPARISON_REQUIRED",
                    "narrow temporal reconsideration lost the accepted pair",
                )
            original_baseline = original_baselines[0]
            original_comparison = original_comparisons[0]
            replacement_by_role = {
                TemporalRole.BASELINE_PERIOD: original_baseline.model_copy(
                    update={
                        "source_text": provider_result.baseline_period.source_text,
                        "start": provider_result.baseline_period.start,
                        "end": provider_result.baseline_period.end,
                    }
                ),
                TemporalRole.COMPARISON_PERIOD: original_comparison.model_copy(
                    update={
                        "source_text": provider_result.comparison_period.source_text,
                        "start": provider_result.comparison_period.start,
                        "end": provider_result.comparison_period.end,
                    }
                ),
            }
            return draft.model_copy(
                update={
                    "time_periods": tuple(
                        replacement_by_role.get(item.role, item)
                        for item in draft.time_periods
                    )
                }
            )

        draft = invoke_provider(
            instruction=(
                "Return the complete CURRENT intent only. Prior brief is context, "
                "not authority to restore obligations the user removed."
            ),
        )

        draft = self._canonicalize_analytical_goals(
            draft,
            catalog=catalog,
        )
        draft = self._canonicalize_temporal_comparison_subgoals(draft)
        draft = self._canonicalize_root_temporal_material(draft)
        draft = self._canonicalize_exact_period_repeats(draft)
        draft = self._derive_standalone_temporal_comparison(draft)
        draft = self._canonicalize_change_ranking_period_roles(draft)
        draft = self._canonicalize_typed_temporal_comparison(draft)
        duplicate_root_keys = self._duplicate_root_cause_goal_keys(draft)
        if duplicate_root_keys:
            # Duplicate typed analytical authority is deterministic invalid input
            # from the provider. Do not spend a second stochastic call rewriting
            # the workflow graph; fail closed instead.
            raise ResearchIntakeError(
                "INTAKE_DUPLICATE_ANALYTICAL_GOAL",
                ",".join(duplicate_root_keys),
            )

        # At most one bounded reconsideration is allowed inside the same intake owner.
        # It is not a retry loop: the provider ceiling remains two calls. The
        # second pass receives no new authority, only deterministic calendar /
        # single-domain context already present in this request.
        ranking_basis_issue = self._ranking_basis_reconsideration_issue(
            draft,
            current=current,
            catalog=catalog,
        )
        change_period_issue = self._change_ranking_period_reconsideration_issue(
            draft,
            current=current,
            calendar_reference_date=self._calendar_reference_date,
        )
        if (
            prior_brief is None
            and self.call_count < 2
            and ranking_basis_issue is not None
        ):
            draft = reconsider_ranking_basis(draft, ranking_basis_issue)
        elif (
            prior_brief is None
            and self.call_count < 2
            and change_period_issue is not None
        ):
            draft = reconsider_change_period_pair(
                draft,
                change_period_issue,
            )
        elif (
            prior_brief is None
            and self.call_count < 2
            and draft.terminal == ResearchIntakeTerminal.CLARIFY
            and len(catalog.temporal_dimension_ids) == 1
        ):
            draft = invoke_provider(
                instruction=(
                    "Reconsider once. Preserve CLARIFY unless the sole blocker is "
                    "calendar anchoring that calendar_reference_date resolves under "
                    "the system rule. Do not guess metrics, entities, or unavailable data."
                ),
                reconsideration={
                    "kind": "TEMPORAL_CLARIFICATION_ONLY",
                    "prior_clarification_question": draft.clarification_question,
                },
            )
        elif (
            prior_brief is None
            and self.call_count < 2
            and draft.terminal == ResearchIntakeTerminal.UNSUPPORTED
            and len(catalog.supported_domains) == 1
        ):
            draft = invoke_provider(
                instruction=(
                    "Reconsider once against the single grounded domain. A broad "
                    "management report/overview may become READY only if it can be "
                    "bounded entirely to materially relevant governed catalog refs. "
                    "Requests that depend on absent concepts/data MUST remain UNSUPPORTED."
                ),
                reconsideration={
                    "kind": "SINGLE_DOMAIN_GROUNDED_OVERVIEW",
                    "supported_domain": catalog.supported_domains[0],
                    "prior_unsupported_reason": draft.unsupported_reason,
                },
            )

        draft = self._canonicalize_analytical_goals(
            draft,
            catalog=catalog,
        )
        draft = self._canonicalize_temporal_comparison_subgoals(draft)
        draft = self._canonicalize_root_temporal_material(draft)
        draft = self._canonicalize_exact_period_repeats(draft)
        draft = self._derive_standalone_temporal_comparison(draft)
        draft = self._canonicalize_change_ranking_period_roles(draft)
        draft = self._canonicalize_typed_temporal_comparison(draft)
        duplicate_root_keys = self._duplicate_root_cause_goal_keys(draft)
        if duplicate_root_keys:
            raise ResearchIntakeError(
                "INTAKE_DUPLICATE_ANALYTICAL_GOAL",
                ",".join(duplicate_root_keys),
            )

        self._assert_change_ranking_temporal_contract(draft)
        final_change_period_issue = (
            self._change_ranking_collapsed_period_issue(draft)
        )
        if final_change_period_issue is not None:
            raise ResearchIntakeError(
                "INTAKE_CHANGE_RANKING_PERIOD_PAIR_COLLAPSED",
                (
                    "CHANGE ranking baseline and comparison periods must be "
                    "distinct bounded spans"
                ),
            )

        change_observation_temporal_ids: list[str] = []
        if draft.terminal == ResearchIntakeTerminal.READY:
            for goal in draft.goals:
                if (
                    goal.kind != ResearchGoalKind.ROOT_CAUSE
                    or goal.causal_competition is None
                    or goal.temporal_material is None
                ):
                    continue
                decision = resolve_change_temporal_authority(
                    effect_observation=(
                        goal.causal_competition.effect_observation
                    ),
                    explicit_temporal_material=(
                        goal.temporal_material.mode != "none"
                    ),
                    governed_temporal_dimension_ids=(
                        catalog.temporal_dimension_ids
                    ),
                )
                if (
                    decision.disposition
                    == ChangeTemporalAuthorityDisposition.CLARIFY_TIME_AXIS
                ):
                    return ResearchIntakeResult(
                        terminal=ResearchIntakeTerminal.CLARIFY,
                        clarification_question=(
                            "Which governed time dimension should define the "
                            "requested change observation?"
                        ),
                        catalog_fingerprint=catalog.fingerprint,
                        model_calls=self.call_count,
                    )
                if (
                    decision.disposition
                    == ChangeTemporalAuthorityDisposition.BLOCKED_NO_TIME_AXIS
                ):
                    return ResearchIntakeResult(
                        terminal=ResearchIntakeTerminal.UNSUPPORTED,
                        unsupported_reason=(
                            "The requested change observation has no governed "
                            "temporal dimension in the current semantic context."
                        ),
                        catalog_fingerprint=catalog.fingerprint,
                        model_calls=self.call_count,
                    )
                if (
                    decision.disposition
                    == ChangeTemporalAuthorityDisposition.OBSERVE_GOVERNED_TIME
                ):
                    assert decision.time_dimension_id is not None
                    change_observation_temporal_ids.append(
                        decision.time_dimension_id
                    )

        calls = self.call_count
        if draft.terminal == ResearchIntakeTerminal.CLARIFY:
            return ResearchIntakeResult(
                terminal=draft.terminal,
                clarification_question=draft.clarification_question,
                catalog_fingerprint=catalog.fingerprint,
                model_calls=calls,
            )
        if draft.terminal == ResearchIntakeTerminal.UNSUPPORTED:
            return ResearchIntakeResult(
                terminal=draft.terminal,
                unsupported_reason=draft.unsupported_reason,
                catalog_fingerprint=catalog.fingerprint,
                model_calls=calls,
            )

        by_id = {item.candidate_id: item for item in catalog.semantic_refs}
        questions: list[ResearchQuestion] = []
        scope_refs: dict[str, ResearchSemanticRef] = {}
        for candidate_id in tuple(
            dict.fromkeys(change_observation_temporal_ids)
        ):
            ref = by_id.get(candidate_id)
            if (
                ref is None
                or ref.target_kind != SemanticTargetKind.DIMENSION
                or candidate_id not in set(catalog.temporal_dimension_ids)
            ):
                raise ResearchIntakeError(
                    "INTAKE_CHANGE_TEMPORAL_DIMENSION_INVALID",
                    candidate_id,
                )
            scope_refs[candidate_id] = ref
        seen_goal_keys: set[str] = set()
        goal_id_by_key: dict[str, str] = {}
        for index, goal in enumerate(draft.goals, start=1):
            if goal.goal_key in seen_goal_keys:
                raise ResearchIntakeError(
                    "INTAKE_GOAL_KEY_DUPLICATE",
                    goal.goal_key,
                )
            seen_goal_keys.add(goal.goal_key)
            source_fragment_identity = None
            if goal.source_fragment_text is not None:
                fragment = goal.source_fragment_text
                if fragment != fragment.strip() or fragment not in current:
                    raise ResearchIntakeError(
                        "INTAKE_SOURCE_FRAGMENT_NOT_VERBATIM",
                        goal.goal_key,
                    )
                source_fragment_identity = (
                    "fragment-sha256:"
                    + hashlib.sha256(fragment.encode("utf-8")).hexdigest()
                )
            relationship = self._relationship_for_goal(
                goal,
                catalog=catalog,
            )
            if relationship is not None:
                subject_ids = (
                    relationship.left_semantic_id,
                    relationship.right_semantic_id,
                )
                related_ids = (
                    (relationship.dimension_semantic_id,)
                    if relationship.dimension_semantic_id is not None
                    else ()
                )
            else:
                subject_ids = goal.subject_semantic_ids
                related_ids = goal.related_semantic_ids
            ids = (*subject_ids, *related_ids)
            unknown = [item for item in ids if item not in by_id]
            if unknown:
                raise ResearchIntakeError(
                    "INTAKE_UNKNOWN_SEMANTIC_REF",
                    ",".join(sorted(set(unknown))),
                )
            subject = tuple(by_id[item] for item in subject_ids)
            related = tuple(by_id[item] for item in related_ids)
            for item in (*subject, *related):
                scope_refs.setdefault(item.candidate_id, item)
            ranking = None
            if goal.ranking is not None:
                goal_metric_ids = {
                    item.candidate_id
                    for item in (*subject, *related)
                    if item.target_kind
                    in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
                }
                ranking_measure = goal.ranking.measure_semantic_id
                if (
                    ranking_measure is not None
                    and ranking_measure not in goal_metric_ids
                ):
                    raise ResearchIntakeError(
                        "INTAKE_RANKING_MEASURE_OUTSIDE_GOAL_SCOPE",
                        ranking_measure,
                    )
                ranking = RankingSurface(
                    text=goal.ranking.source_text,
                    direction=goal.ranking.direction,
                    limit=goal.ranking.limit,
                    measure_semantic_id=ranking_measure,
                    basis=goal.ranking.basis,
                )
            if goal.comparisons and goal.comparison_texts:
                raise ResearchIntakeError(
                    "INTAKE_COMPARISON_AUTHORITY_AMBIGUOUS",
                    goal.goal_key,
                )
            typed_comparisons: list[ComparisonSurface] = []
            if goal.comparisons:
                goal_ref_ids = set(ids)
                for item in goal.comparisons:
                    if (
                        item.semantic_id is not None
                        and item.semantic_id not in goal_ref_ids
                    ):
                        raise ResearchIntakeError(
                            "INTAKE_COMPARISON_SEMANTIC_OUTSIDE_GOAL_SCOPE",
                            item.semantic_id,
                        )
                    typed_comparisons.append(
                        ComparisonSurface(
                            text=item.text,
                            role=item.role,
                            semantic_id=item.semantic_id,
                        )
                    )
            else:
                # Historical deterministic fixtures may still deserialize this
                # compatibility field. Live provider schema cannot emit it.
                typed_comparisons.extend(
                    ComparisonSurface(text=text)
                    for text in goal.comparison_texts
                )
            comparisons = tuple(typed_comparisons)
            causal_competition = None
            if goal.kind == ResearchGoalKind.ROOT_CAUSE:
                if goal.causal_competition is None:
                    raise ResearchIntakeError(
                        "INTAKE_ROOT_CAUSE_SURFACE_REQUIRED",
                        goal.goal_key,
                    )
                causal = goal.causal_competition
                goal_ref_ids = set(ids)
                required_ids = {
                    causal.effect_semantic_id,
                    *causal.candidate_mechanism_semantic_ids,
                    *causal.diagnostic_dimension_ids,
                }
                outside = sorted(required_ids - goal_ref_ids)
                if outside:
                    raise ResearchIntakeError(
                        "INTAKE_CAUSAL_SURFACE_OUTSIDE_GOAL_SCOPE",
                        ",".join(outside),
                    )
                try:
                    causal_competition = CausalCompetitionSurface(
                        effect_semantic_id=causal.effect_semantic_id,
                        effect_observation=causal.effect_observation,
                        candidate_mechanism_semantic_ids=causal.candidate_mechanism_semantic_ids,
                        diagnostic_dimension_ids=causal.diagnostic_dimension_ids,
                    )
                except ValueError as exc:
                    raise ResearchIntakeError(
                        "INTAKE_CAUSAL_SURFACE_INVALID",
                        str(exc),
                    ) from exc
            elif goal.causal_competition is not None:
                raise ResearchIntakeError(
                    "INTAKE_CAUSAL_SURFACE_ON_NON_ROOT_CAUSE",
                    goal.goal_key,
                )
            goal_seed = goal.model_dump(mode="json")
            if (
                goal.causal_competition is not None
                and "effect_observation"
                not in goal.causal_competition.model_fields_set
            ):
                goal_seed["causal_competition"].pop("effect_observation", None)
            if goal_seed.get("relationship_intent") is None:
                # Preserve historical/non-relationship stable identity. The new
                # optional field becomes authority only when it is explicitly set.
                goal_seed.pop("relationship_intent", None)
            goal_id = self._ids(
                "g_",
                goal_seed,
                index,
            )
            goal_id_by_key[goal.goal_key] = goal_id
            questions.append(
                ResearchQuestion(
                    goal_id=goal_id,
                    kind=goal.kind,
                    # The exact grounded fragment is the canonical local
                    # obligation wording.  Broad provider source_text remains
                    # compatibility-only when no verbatim fragment exists.
                    source_text=(
                        goal.source_fragment_text
                        if goal.source_fragment_text is not None
                        else goal.source_text
                    ),
                    source_fragment_identity=source_fragment_identity,
                    subject_refs=subject,
                    related_refs=related,
                    ranking=ranking,
                    comparisons=comparisons,
                    causal_competition=causal_competition,
                    relationship_intent=(
                        (
                            goal.relationship_intent
                            or RelationshipIntent.BUSINESS_POLICY
                        )
                        if goal.kind == ResearchGoalKind.RELATIONSHIP
                        else None
                    ),
                    status=ResearchGoalStatus.RESOLVED,
                )
            )

        question_by_key = {
            goal.goal_key: question
            for goal, question in zip(draft.goals, questions, strict=True)
        }

        def dependency_parent_dimensions(question: ResearchQuestion) -> set[str]:
            return {
                item.candidate_id
                for item in (*question.subject_refs, *question.related_refs)
                if item.target_kind == SemanticTargetKind.DIMENSION
            }

        resolved_dependency_source_keys: dict[str, str] = {}
        for goal in draft.goals:
            dependency = goal.result_dependency
            if dependency is None:
                continue
            declared_source_key = dependency.source_goal_key
            if declared_source_key not in goal_id_by_key:
                raise ResearchIntakeError(
                    "INTAKE_RESULT_DEPENDENCY_SOURCE_UNKNOWN",
                    declared_source_key,
                )
            if declared_source_key == goal.goal_key:
                raise ResearchIntakeError(
                    "INTAKE_RESULT_DEPENDENCY_SELF_REFERENCE",
                    goal.goal_key,
                )

            declared_parent = question_by_key[declared_source_key]
            if declared_parent.ranking is not None:
                # A structurally valid typed reference is authoritative. Do not
                # redirect it merely because another ranking goal also exists.
                resolved_source_key = declared_source_key
            else:
                compatible_ranking_keys = tuple(
                    candidate_goal.goal_key
                    for candidate_goal, candidate_question in zip(
                        draft.goals,
                        questions,
                        strict=True,
                    )
                    if (
                        candidate_goal.goal_key != goal.goal_key
                        and candidate_question.ranking is not None
                        and dependency.dimension_semantic_id
                        in dependency_parent_dimensions(candidate_question)
                    )
                )
                if len(compatible_ranking_keys) == 0:
                    raise ResearchIntakeError(
                        "INTAKE_RESULT_DEPENDENCY_SOURCE_NOT_RANKING",
                        declared_source_key,
                    )
                if len(compatible_ranking_keys) > 1:
                    raise ResearchIntakeError(
                        "INTAKE_RESULT_DEPENDENCY_SOURCE_AMBIGUOUS",
                        ",".join(sorted(compatible_ranking_keys)),
                    )
                resolved_source_key = compatible_ranking_keys[0]

            resolved_dependency_source_keys[goal.goal_key] = resolved_source_key

        dependency_edges = dict(resolved_dependency_source_keys)
        for child_key, source_key in dependency_edges.items():
            seen: set[str] = set()
            current_key = child_key
            while current_key in dependency_edges:
                if current_key in seen:
                    raise ResearchIntakeError(
                        "INTAKE_RESULT_DEPENDENCY_CYCLE",
                        child_key,
                    )
                seen.add(current_key)
                current_key = dependency_edges[current_key]

        question_by_id = {item.goal_id: item for item in questions}
        resolved_questions: list[ResearchQuestion] = []
        for goal, question in zip(draft.goals, questions, strict=True):
            dependency = goal.result_dependency
            if dependency is None:
                resolved_questions.append(question)
                continue
            source_key = resolved_dependency_source_keys[goal.goal_key]
            source_goal_id = goal_id_by_key[source_key]
            parent = question_by_id.get(source_goal_id)
            if parent is None or parent.ranking is None:
                raise ResearchIntakeError(
                    "INTAKE_RESULT_DEPENDENCY_SOURCE_NOT_RANKING",
                    source_key,
                )
            if parent.ranking.direction == "unspecified":
                raise ResearchIntakeError(
                    "INTAKE_RESULT_DEPENDENCY_RANKING_DIRECTION_REQUIRED",
                    source_key,
                )
            dimension = by_id.get(dependency.dimension_semantic_id)
            if (
                dimension is None
                or dimension.target_kind != SemanticTargetKind.DIMENSION
                or dependency.dimension_semantic_id
                in set(catalog.temporal_dimension_ids)
            ):
                raise ResearchIntakeError(
                    "INTAKE_RESULT_DEPENDENCY_DIMENSION_INVALID",
                    dependency.dimension_semantic_id,
                )
            parent_dimensions = dependency_parent_dimensions(parent)
            if dependency.dimension_semantic_id not in parent_dimensions:
                raise ResearchIntakeError(
                    "INTAKE_RESULT_DEPENDENCY_PARENT_DIMENSION_MISSING",
                    dependency.dimension_semantic_id,
                )
            # A result-selected dimension constrains the child execution as a
            # filter. It need not also be projected/grouped in the child output.
            # The governed parent dimension plus accepted scope remain authority.
            payload = question.model_dump(mode="python")
            payload["result_dependency"] = ResultSelectionDependency(
                source_goal_id=source_goal_id,
                dimension_semantic_id=dependency.dimension_semantic_id,
                selection=dependency.selection,
            )
            resolved_questions.append(ResearchQuestion(**payload))
        questions = resolved_questions

        deliverables: list[ResearchDeliverableRequirement] = []
        seen_deliverables: set[str] = set()
        for index, item in enumerate(draft.deliverables, start=1):
            if item.key in seen_deliverables:
                raise ResearchIntakeError(
                    "INTAKE_DELIVERABLE_KEY_DUPLICATE",
                    item.key,
                )
            seen_deliverables.add(item.key)
            requirement_id = self._ids(
                "d_",
                item.model_dump(mode="json"),
                index,
            )
            deliverables.append(
                ResearchDeliverableRequirement(
                    requirement_id=requirement_id,
                    kind=item.kind,
                    source_text=item.source_text,
                )
            )

        investigation_requirements: list[ProductInvestigationRequirement] = []
        seen_directive_keys: set[str] = set()
        seen_directive_identity: set[tuple[str, str]] = set()
        for index, item in enumerate(draft.investigation_directives, start=1):
            if item.key in seen_directive_keys:
                raise ResearchIntakeError(
                    "INTAKE_INVESTIGATION_KEY_DUPLICATE",
                    item.key,
                )
            seen_directive_keys.add(item.key)
            source_goal_id = goal_id_by_key.get(item.source_goal_key)
            if source_goal_id is None:
                raise ResearchIntakeError(
                    "INTAKE_INVESTIGATION_SOURCE_UNKNOWN",
                    item.source_goal_key,
                )
            identity = (item.kind.value, source_goal_id)
            if identity in seen_directive_identity:
                raise ResearchIntakeError(
                    "INTAKE_INVESTIGATION_DUPLICATE",
                    item.key,
                )
            seen_directive_identity.add(identity)
            investigation_requirements.append(
                ProductInvestigationRequirement(
                    requirement_id=self._ids(
                        "pir_",
                        {
                            "directive": item.model_dump(mode="json"),
                            "source_goal_id": source_goal_id,
                        },
                        index,
                    ),
                    kind=item.kind,
                    source_goal_id=source_goal_id,
                    source_text=item.source_text,
                )
            )

        if not questions:
            raise ResearchIntakeError(
                "INTAKE_READY_WITHOUT_ANALYTICAL_GOALS",
                "READY intake must contain at least one analytical goal",
            )

        period_identities: set[tuple[str, str, str, str]] = set()
        periods: list[ResearchTimePeriod] = []
        for item in draft.time_periods:
            identity = (
                item.time_dimension_semantic_id,
                item.start,
                item.end,
                item.role.value,
            )
            if identity in period_identities:
                raise ResearchIntakeError(
                    "INTAKE_TIME_PERIOD_DUPLICATE",
                    "|".join(identity),
                )
            period_identities.add(identity)
            dimension_ref = by_id.get(item.time_dimension_semantic_id)
            if (
                dimension_ref is None
                or dimension_ref.target_kind.value != "dimension"
                or item.time_dimension_semantic_id
                not in set(catalog.temporal_dimension_ids)
            ):
                raise ResearchIntakeError(
                    "INTAKE_TIME_DIMENSION_UNAUTHORIZED",
                    item.time_dimension_semantic_id,
                )
            scope_refs.setdefault(dimension_ref.candidate_id, dimension_ref)
            try:
                periods.append(
                    ResearchTimePeriod(
                        source_text=item.source_text,
                        time_dimension_candidate_id=(
                            item.time_dimension_semantic_id
                        ),
                        start=item.start,
                        end=item.end,
                        role=item.role,
                    )
                )
            except ValueError as exc:
                raise ResearchIntakeError(
                    "INTAKE_TIME_PERIOD_INVALID",
                    str(exc),
                ) from exc
        ordered_periods = tuple(periods)
        time_surfaces = tuple(
            dict.fromkeys(item.source_text for item in ordered_periods)
        )

        accepted_ids = set(scope_refs)
        scope_bindings = tuple(
            item
            for item in catalog.native_verification_bindings
            if item.candidate_id in accepted_ids
        )
        scope_temporal_ids = tuple(
            item
            for item in catalog.temporal_dimension_ids
            if item in accepted_ids
        )
        draft_scope = ResearchScope(
            semantic_refs=tuple(scope_refs.values()),
            time_surfaces=time_surfaces,
            periods=ordered_periods,
            temporal_dimension_ids=scope_temporal_ids,
            native_verification_bindings=scope_bindings,
        )
        scope_contract = None
        accepted_scope = draft_scope
        if prior_brief is None:
            if draft.scope_mutation_kind is not None:
                raise ResearchIntakeError(
                    "INTAKE_SCOPE_MUTATION_WITHOUT_PRIOR",
                    draft.scope_mutation_kind.value,
                )
        else:
            if prior_brief.context_version != catalog.context_version:
                raise ResearchIntakeError(
                    "INTAKE_SCOPE_CONTEXT_MISMATCH",
                    "follow-up scope must remain inside the accepted semantic context",
                )
            prior_ids = {
                item.candidate_id for item in prior_brief.scope.semantic_refs
            }
            current_ids = {
                item.candidate_id for item in draft_scope.semantic_refs
            }
            prior_period_identity = tuple(
                (
                    item.time_dimension_candidate_id,
                    item.start,
                    item.end,
                )
                for item in prior_brief.scope.periods
            )
            current_period_identity = tuple(
                (
                    item.time_dimension_candidate_id,
                    item.start,
                    item.end,
                )
                for item in draft_scope.periods
            )
            changed = (
                prior_ids != current_ids
                or prior_period_identity != current_period_identity
            )
            if not changed and (
                tuple(prior_brief.scope.temporal_dimension_ids)
                != tuple(draft_scope.temporal_dimension_ids)
                or tuple(prior_brief.scope.native_verification_bindings)
                != tuple(draft_scope.native_verification_bindings)
            ):
                raise ResearchIntakeError(
                    "INTAKE_SCOPE_CONTEXT_MISMATCH",
                    "execution verification metadata changed inside one semantic context",
                )
            if changed:
                if draft.scope_mutation_kind is None:
                    raise ResearchIntakeError(
                        "INTAKE_SCOPE_MUTATION_KIND_REQUIRED",
                        "material follow-up scope change requires typed mutation kind",
                    )
                try:
                    scope_contract = apply_scope_mutation(
                        prior_brief.scope,
                        ScopeMutation(
                            kind=draft.scope_mutation_kind,
                            source_version_id=(
                                prior_brief.scope.scope_version.version_id
                            ),
                            target_semantic_refs=draft_scope.semantic_refs,
                            target_time_surfaces=draft_scope.time_surfaces,
                            target_periods=draft_scope.periods,
                            target_temporal_dimension_ids=(
                                draft_scope.temporal_dimension_ids
                            ),
                            target_native_verification_bindings=(
                                draft_scope.native_verification_bindings
                            ),
                            reason=current,
                        ),
                    )
                except ValueError as exc:
                    raise ResearchIntakeError(
                        "INTAKE_SCOPE_MUTATION_INVALID",
                        str(exc),
                    ) from exc
                accepted_scope = scope_contract.current_scope
            else:
                if draft.scope_mutation_kind is not None:
                    raise ResearchIntakeError(
                        "INTAKE_SCOPE_MUTATION_KIND_UNEXPECTED",
                        draft.scope_mutation_kind.value,
                    )
                accepted_scope = ResearchScope(
                    semantic_refs=draft_scope.semantic_refs,
                    time_surfaces=draft_scope.time_surfaces,
                    periods=draft_scope.periods,
                    temporal_dimension_ids=draft_scope.temporal_dimension_ids,
                    native_verification_bindings=(
                        draft_scope.native_verification_bindings
                    ),
                    scope_version=prior_brief.scope.scope_version,
                )

        identity = {
            "question": current,
            "prior_brief_fingerprint": (
                hashlib.sha256(
                    _canonical(prior_brief.model_dump(mode="json")).encode("utf-8")
                ).hexdigest()
                if prior_brief is not None
                else None
            ),
            "catalog_fingerprint": catalog.fingerprint,
            "draft": draft.model_dump(mode="json"),
        }
        brief_id = "rb_" + hashlib.sha256(
            _canonical(identity).encode("utf-8")
        ).hexdigest()[:24]
        must_ids = tuple(
            [item.goal_id for item in questions]
            + [item.requirement_id for item in deliverables]
        )
        brief = ResearchBrief(
            brief_id=brief_id,
            objective=(draft.objective or "").strip(),
            scope=accepted_scope,
            required_domains=tuple(dict.fromkeys(draft.required_domains)),
            questions=tuple(questions),
            deliverables=tuple(deliverables),
            must_requirement_ids=must_ids,
            blocking_goal_ids=(),
            context_version=catalog.context_version,
            status=ResearchBriefStatus.READY_FOR_RESEARCH,
        )
        return ResearchIntakeResult(
            terminal=ResearchIntakeTerminal.READY,
            brief=brief,
            investigation_requirements=tuple(investigation_requirements),
            scope_contract=scope_contract,
            catalog_fingerprint=catalog.fingerprint,
            model_calls=calls,
        )
