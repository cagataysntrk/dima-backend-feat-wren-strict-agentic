"""Generic raw-language Research intake for the canonical Dima product.

The model may interpret language only into typed ResearchBrief intent over an
explicit grounded semantic catalog. It cannot invent semantic refs, execute
analytics, create Evidence, or promote causal truth.
"""
from __future__ import annotations

import copy
import hashlib
import json
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.research_contracts import (
    ComparisonSurface,
    PresentationKind,
    RankingSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ScopeMutation,
    ScopeMutationKind,
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
    source_text: str = Field(min_length=1)


class ModelGoalDraft(Frozen):
    goal_key: str = Field(min_length=1, max_length=120)
    kind: ResearchGoalKind
    source_text: str = Field(min_length=1)
    allowed_relationship_id: str | None = None
    subject_semantic_ids: tuple[str, ...] = ()
    related_semantic_ids: tuple[str, ...] = ()
    ranking: DraftRanking | None = None
    comparison_texts: tuple[str, ...] = ()


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
- For RELATIONSHIP, select exactly one allowed_relationship_id from the supplied catalog.
  Do not reconstruct its left/right/dimension identities yourself.
- If the request depends on unavailable concepts/data (including psychological/predictive truth
  not represented by the catalog), return UNSUPPORTED.
- If the user's actual intent cannot be determined without one bounded question, return CLARIFY.
- For explicit corrections, the CURRENT message is authoritative: do not silently merge removed
  obligations back from prior context.
- If prior_brief is present and the CURRENT request materially changes semantic/time scope,
  emit exactly one typed scope_mutation_kind from the closed enum. If scope is unchanged, emit null.
- Never emit a scope version or lineage id. Dima deterministically binds those after validation.
- Preserve every current MUST analytical/presentation obligation as a separate goal/deliverable.
- Adaptive instructions such as "if verified evidence reveals a new material direction, follow it"
  are Core-B product-routing intent, NOT a second analytical goal. Emit the actual analytical goal
  once, then emit FOLLOW_VERIFIED_MATERIAL with source_goal_key pointing to that exact goal.
- An investigation directive never asserts that evidence is material; it only preserves the user's
  conditional instruction for later governed P17 evaluation.
- Do not convert association into causality. ROOT_CAUSE means bounded investigation, not a cause.
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
) -> dict[str, Any]:
    """Close every provider-selected authority ID to this exact catalog.

    RELATIONSHIP uses one governed relationship identity. The provider never
    receives left/right/dimension identity fields for that variant; the
    deterministic compiler expands the selected relationship afterwards.
    """

    schema = strict_json_schema(ModelResearchBriefDraft)
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

    semantic_ids = tuple(
        sorted(item.candidate_id for item in catalog.semantic_refs)
    )
    relationship_ids = tuple(
        sorted(
            item.relationship_id
            for item in catalog.allowed_relationships
        )
    )
    common_names = (
        "goal_key",
        "source_text",
        "ranking",
        "comparison_texts",
    )
    variants: list[dict[str, Any]] = []
    for kind in ResearchGoalKind:
        if kind == ResearchGoalKind.RELATIONSHIP:
            if not relationship_ids:
                continue
            properties = {
                name: copy.deepcopy(base_properties[name])
                for name in common_names
            }
            properties["kind"] = {
                "type": "string",
                "enum": [kind.value],
            }
            properties["allowed_relationship_id"] = {
                "type": "string",
                "enum": list(relationship_ids),
            }
        else:
            properties = {
                name: copy.deepcopy(base_properties[name])
                for name in common_names
            }
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
    ) -> None:
        self._transport = transport
        self._schema_name = schema_name

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
                    "cube_names": list(item.cube_names),
                    "sensitive": item.sensitive,
                }
                for item in sorted(
                    catalog.semantic_refs,
                    key=lambda value: value.candidate_id,
                )
            ],
            "allowed_relationships": [
                item.model_dump(mode="json")
                for item in sorted(
                    catalog.allowed_relationships,
                    key=lambda value: value.relationship_id,
                )
            ],
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

        user_payload: dict[str, Any] = {
            "current_user_message": current,
            "grounded_catalog": self._catalog_payload(catalog),
            "prior_brief": (
                prior_brief.model_dump(mode="json")
                if prior_brief is not None
                else None
            ),
            "instruction": (
                "Return the complete CURRENT intent only. Prior brief is context, "
                "not authority to restore obligations the user removed."
            ),
        }
        raw = self._transport.structured_json(
            _SYSTEM,
            _canonical(user_payload),
            schema=_intake_provider_schema(catalog),
            schema_name=self._schema_name,
        )
        try:
            draft = ModelResearchBriefDraft.model_validate_json(raw)
        except Exception as exc:
            raise ResearchIntakeError(
                "INTAKE_MODEL_OUTPUT_INVALID",
                "structured provider output failed the typed intake contract",
            ) from exc

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
            ranking = (
                RankingSurface(
                    text=goal.ranking.source_text,
                    direction=goal.ranking.direction,
                    limit=goal.ranking.limit,
                )
                if goal.ranking is not None
                else None
            )
            comparisons = tuple(
                ComparisonSurface(text=text)
                for text in goal.comparison_texts
            )
            goal_id = self._ids(
                "g_",
                goal.model_dump(mode="json"),
                index,
            )
            goal_id_by_key[goal.goal_key] = goal_id
            questions.append(
                ResearchQuestion(
                    goal_id=goal_id,
                    kind=goal.kind,
                    source_text=goal.source_text,
                    subject_refs=subject,
                    related_refs=related,
                    ranking=ranking,
                    comparisons=comparisons,
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

        draft_scope = ResearchScope(
            semantic_refs=tuple(scope_refs.values()),
            time_surfaces=tuple(dict.fromkeys(draft.time_surfaces)),
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
            prior_times = set(prior_brief.scope.time_surfaces)
            current_times = set(draft_scope.time_surfaces)
            changed = (
                prior_ids != current_ids
                or prior_times != current_times
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
