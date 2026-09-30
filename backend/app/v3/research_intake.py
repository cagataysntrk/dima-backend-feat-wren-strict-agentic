"""Generic raw-language Research intake for the canonical Dima product.

The model may interpret language only into typed ResearchBrief intent over an
explicit grounded semantic catalog. It cannot invent semantic refs, execute
analytics, create Evidence, or promote causal truth.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import date
from enum import StrEnum
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.research_contracts import (
    CausalCompetitionSurface,
    ComparisonRole,
    ComparisonSurface,
    PresentationKind,
    RankingSurface,
    RelationshipIntent,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchNativeVerificationBinding,
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


class ModelCausalCompetitionDraft(Frozen):
    effect_semantic_id: str = Field(min_length=1)
    candidate_mechanism_semantic_ids: tuple[str, ...] = ()
    diagnostic_dimension_ids: tuple[str, ...] = ()


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
    # Compatibility-only for historical deterministic fixtures. This field is
    # deliberately omitted from the provider schema below; live intake cannot
    # mint new untyped comparison authority.
    comparison_texts: tuple[str, ...] = ()


class ModelTimePeriodDraft(Frozen):
    source_text: str = Field(min_length=1)
    time_dimension_semantic_id: str = Field(min_length=1)
    start: str = Field(min_length=1)
    end: str = Field(min_length=1)
    role: TemporalRole = TemporalRole.MATERIAL_WINDOW


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
- If prior_brief is present and the CURRENT request materially changes semantic/time scope,
  emit exactly one typed scope_mutation_kind from the closed enum. If scope is unchanged, emit null.
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
- Emit typed comparisons, never free-text comparison authority. Use TEMPORAL_PERIOD only for an
  actual period-vs-period comparison. Use CAUSAL_CANDIDATE for user-provided candidate mechanisms,
  and ENTITY_OR_MEASURE for governed entity/measure competition. Every non-temporal comparison item
  must carry one semantic_id from the grounded catalog and from that goal's accepted refs.
- Preserve every current MUST analytical/presentation obligation as a separate goal/deliverable.
- For every READY goal emit source_fragment_text as one exact verbatim substring of the CURRENT
  user message that directly supports that goal. Never paraphrase the fragment.
- If multiple goals decompose the same user clause, repeat the same maximal supporting clause
  verbatim for each of those goals. Different clauses must keep different fragment text.
- Adaptive instructions such as "if verified evidence reveals a new material direction, follow it"
  are Core-B product-routing intent, NOT a second analytical goal. Emit the actual analytical goal
  once, then emit FOLLOW_VERIFIED_MATERIAL with source_goal_key pointing to that exact goal.
- An investigation directive never asserts that evidence is material; it only preserves the user's
  conditional instruction for later governed P17 evaluation.
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
  Every ROOT_CAUSE goal MUST emit causal_competition: one governed effect_semantic_id, only the
  candidate_mechanism_semantic_ids explicitly supplied by the user (empty when none were supplied),
  and the governed diagnostic_dimension_ids needed by the request. This typed contract is identity,
  not causal truth. Additional accepted metrics may still be included as analytical material for
  P17 discovery, but must not be mislabeled as user-provided candidates.
  Do NOT manufacture separate RELATIONSHIP goals merely as evidence-gathering subgoals for that
  ROOT_CAUSE investigation. P17/P19 own governed hypothesis competition and discriminating re-entry.
- If the user independently asks both an observational relationship analysis and a causal/root-cause
  investigation, preserve them as distinct goals. Never collapse genuinely distinct user clauses.
- Goal decomposition is semantic obligation decomposition, not a query plan. Do not create multiple
  analytical goals solely because several governed metrics may be useful to one investigation.
- ranking.limit is null unless the user explicitly requested a bounded top-N/result count. Never invent top-N.
- ranking.measure_semantic_id is set only when the user explicitly identifies one governed metric/KPI
  as the ranking basis. With multiple metrics and no explicit single basis, keep it null; do not pick
  the first metric or manufacture a composite score.
- If a native single-metric ranking needs direction and the user's direction is genuinely ambiguous,
  return CLARIFY rather than guessing direction from words, morphology, regex, or a default.
- Do not emit implementation-specific Wren/SQL/lane/token concepts.
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
            comparison_properties["semantic_id"] = {
                "anyOf": [
                    {
                        "type": "string",
                        "enum": list(semantic_ids),
                    },
                    {"type": "null"},
                ],
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
    ) -> ModelResearchBriefDraft:
        """Canonicalize typed analytical authority before execution.

        ROOT_CAUSE causal_competition is itself governed typed semantic intent.
        Its effect/candidate identities therefore belong to the goal's accepted
        measure scope and its diagnostic identities belong to the related scope,
        even when the provider does not redundantly repeat those IDs in the
        generic subject/related arrays. This is deterministic typed assembly,
        not semantic inference.

        A generic OTHER goal can be presentation/epistemic wording rather than a
        distinct analytical obligation. It is safe to remove from P14 only when:
        - the exact source was also emitted as a typed deliverable,
        - it carries no ranking/comparison/relationship/causal analytical surface,
        - every governed semantic ref it carries is already covered by another
          non-OTHER analytical goal in this same provider result.

        The deliverable remains immutable USER_MUST authority. No wording,
        regex, similarity or benchmark identity participates in this decision.
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

        if not draft.deliverables:
            return draft

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
        covered_refs = {
            semantic_id
            for item in analytical
            for semantic_id in (
                *item.subject_semantic_ids,
                *item.related_semantic_ids,
            )
        }

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
            represented_as_non_analytical = (
                goal.source_text in presentation_sources
                and not has_distinct_analytical_surface
                and refs.issubset(covered_refs)
            )
            if represented_as_non_analytical:
                continue
            canonical.append(goal)

        if len(canonical) == len(draft.goals):
            return draft
        return draft.model_copy(update={"goals": tuple(canonical)})

    @staticmethod
    def _ids(prefix: str, seed: dict[str, Any], ordinal: int) -> str:
        raw = _canonical({"seed": seed, "ordinal": ordinal})
        return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]

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

        draft = invoke_provider(
            instruction=(
                "Return the complete CURRENT intent only. Prior brief is context, "
                "not authority to restore obligations the user removed."
            ),
        )

        draft = self._canonicalize_analytical_goals(draft)
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
        if (
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

        draft = self._canonicalize_analytical_goals(draft)
        duplicate_root_keys = self._duplicate_root_cause_goal_keys(draft)
        if duplicate_root_keys:
            raise ResearchIntakeError(
                "INTAKE_DUPLICATE_ANALYTICAL_GOAL",
                ",".join(duplicate_root_keys),
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
                    source_text=goal.source_text,
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

        period_by_source: dict[str, ModelTimePeriodDraft] = {}
        period_identities: set[tuple[str, str, str]] = set()
        periods: list[ResearchTimePeriod] = []
        for item in draft.time_periods:
            if item.source_text in period_by_source:
                raise ResearchIntakeError(
                    "INTAKE_TIME_PERIOD_DUPLICATE",
                    item.source_text,
                )
            identity = (
                item.time_dimension_semantic_id,
                item.start,
                item.end,
            )
            if identity in period_identities:
                raise ResearchIntakeError(
                    "INTAKE_TIME_PERIOD_DUPLICATE",
                    "|".join(identity),
                )
            period_by_source[item.source_text] = item
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
            item.source_text for item in ordered_periods
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
