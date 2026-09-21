"""Finite pre-acceptance protocol for the Day 6.5 Manager.

The cognition boundary is deliberately not an open tool loop:

    DRAFT -> AUTO_GROUND -> COVERAGE_VETO -> CONTRACT_VALIDITY
          -> ACCEPT / one REVISE / CLARIFY / NOT_ACCEPTED

The draft and coverage auditor are probabilistic. Neither is semantic authority.
Resolver owns canonical grounding, IntentAcceptanceGate owns contract validity, and the
coverage auditor is veto-only: it cannot mint handles, add obligations, or commit truth.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, model_validator

from app.v2.manager_models import (
    AcceptanceStatus,
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ResearchDirective,
    ResearchDirectiveCondition,
    ResearchDirectiveType,
    UserIntentEnvelope,
)
from app.v2.manager_policy import ManagerCapabilityRegistry
from app.v2.manager_runtime import ManagerBudgetError, ManagerRuntime
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.models import ConversationStateV2, FrozenModel
from app.v2.source_spans import SourceSpanRegistry


class DraftSemanticSurface(FrozenModel):
    surface: str = Field(min_length=1)
    kind_hint: Literal[
        "metric", "dimension", "filter", "time", "comparison", "unknown"
    ]


class IntentDraftObligation(FrozenModel):
    obligation_id: str = Field(min_length=1)
    capability_key: ManagerCapabilityKey
    origin: Literal["USER_MUST", "USER_OPTIONAL", "SYSTEM_REQUIRED"]
    priority: ObligationPriority
    polarity: ObligationPolarity
    source_surfaces: tuple[str, ...] = Field(min_length=1)
    semantic_surfaces: tuple[DraftSemanticSurface, ...] = ()
    open_questions: tuple[str, ...] = ()
    ranking_direction: Literal["asc", "desc"] | None = None
    ranking_limit: int | None = Field(default=None, ge=1, le=1000)

    @model_validator(mode="after")
    def _ranking_contract(self):
        if (self.ranking_direction is None) != (self.ranking_limit is None):
            raise ValueError("ranking direction + limit together")
        if (
            self.capability_key == ManagerCapabilityKey.RANKING
            and self.polarity == ObligationPolarity.REQUIRED
        ):
            if self.ranking_direction is None or self.ranking_limit is None:
                raise ValueError("required ranking draft requires direction + limit")
        elif self.capability_key != ManagerCapabilityKey.RANKING and (
            self.ranking_direction is not None or self.ranking_limit is not None
        ):
            raise ValueError("ranking params only valid for ranking draft")
        return self


class DraftResearchDirective(FrozenModel):
    directive_id: str = Field(min_length=1)
    directive_type: Literal["ADAPT_ON_EVIDENCE"]
    parent_obligation_id: str = Field(min_length=1)
    condition: Literal["MATERIAL_NEW_DIRECTION"] = "MATERIAL_NEW_DIRECTION"
    source_surfaces: tuple[str, ...] = Field(min_length=1)


class IntentDraft(FrozenModel):
    obligations: tuple[IntentDraftObligation, ...] = Field(min_length=1)
    research_directives: tuple[DraftResearchDirective, ...] = ()

    @model_validator(mode="after")
    def _unique_ids(self):
        obligation_ids = [item.obligation_id for item in self.obligations]
        if len(obligation_ids) != len(set(obligation_ids)):
            raise ValueError("draft obligation ids unique")
        directive_ids = [item.directive_id for item in self.research_directives]
        if len(directive_ids) != len(set(directive_ids)):
            raise ValueError("draft directive ids unique")
        known = set(obligation_ids)
        for directive in self.research_directives:
            if directive.parent_obligation_id not in known:
                raise ValueError("draft directive parent obligation missing")
        return self


class CoverageIssueKind(StrEnum):
    UNCOVERED_SOURCE = "UNCOVERED_SOURCE"
    POLARITY_CONFLICT = "POLARITY_CONFLICT"
    UNMODELED_DIRECTIVE = "UNMODELED_DIRECTIVE"
    UNRESOLVED_REFERENCE = "UNRESOLVED_REFERENCE"


class CoverageIssue(FrozenModel):
    kind: CoverageIssueKind
    source_surfaces: tuple[str, ...] = Field(min_length=1)
    note: str = Field(min_length=1, max_length=300)


class CoverageAudit(FrozenModel):
    status: Literal["PASS", "VETO"]
    issues: tuple[CoverageIssue, ...] = ()

    @model_validator(mode="after")
    def _status_shape(self):
        if self.status == "PASS" and self.issues:
            raise ValueError("PASS coverage audit cannot carry issues")
        if self.status == "VETO" and not self.issues:
            raise ValueError("VETO coverage audit requires issues")
        return self


@dataclass(frozen=True)
class FiniteAcceptanceOutcome:
    accepted: bool
    clarification_required: bool
    observations: tuple[dict[str, Any], ...]


_DRAFT_SYSTEM = """You are Dima's bounded intent drafter.

Produce one complete, non-authoritative intent draft from USER_MESSAGE.
Use only CAPABILITY_BINDING_CONTRACT to choose capability meanings and semantic shapes.
Do not emit canonical IDs, SQL, database names, or semantic handles.

Rules:
- Every materially requested analytical/presentation result must appear as an obligation.
- Explicit exclusions must be represented with EXCLUDED polarity.
- USER_MUST means the user is owed that result. Conditional research behavior is NOT an
  obligation; represent only the declared ADAPT_ON_EVIDENCE research directive.
- source_surfaces and semantic_surfaces must be exact literal substrings of USER_MESSAGE.
- semantic_surfaces identify only material semantic concepts that runtime should ground.
- Do not infer canonical semantics. Runtime/Resolver owns grounding.
- Do not use examples, keyword rules, regex-like logic, or case-specific behavior.
Return only the strict schema.
"""


_COVERAGE_SYSTEM = """You are Dima's veto-only intent coverage auditor.

Compare USER_MESSAGE against INTENT_DRAFT and decide only whether material user intent is
left uncovered, polarity is materially inconsistent, a conditional research directive is
unmodeled, or a reference cannot be safely represented from the current turn/context.

You are NOT semantic authority. You MUST NOT:
- choose or suggest a capability,
- produce an obligation or directive,
- emit canonical IDs or handles,
- rewrite the draft,
- execute tools or SQL.

Return PASS or VETO with exact source substrings that justify the veto. The audit may
block commit; it can never create authority.
"""


def _strict_native_schema(schema: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties") or {}
                node["required"] = list(properties.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


def _conversation_surface_view(
    conversation: ConversationStateV2 | None,
) -> dict[str, Any]:
    if conversation is None:
        return {
            "has_prior_analytical_request": False,
            "has_active_result": False,
            "pending_clarification": False,
            "topic_labels": [],
            "focus_labels": [],
            "selected_anchor_label": None,
            "pending_source_mention": None,
        }
    clarification = conversation.clarification_state
    return {
        "has_prior_analytical_request": conversation.has_prior_analytical_request,
        "has_active_result": conversation.has_active_result,
        "pending_clarification": conversation.pending_clarification,
        "topic_labels": list(conversation.topic_labels[:8]),
        "focus_labels": list(conversation.focus_labels[:8]),
        "selected_anchor_label": conversation.selected_anchor_label,
        "pending_source_mention": (
            clarification.source_mention if clarification is not None else None
        ),
    }


class PreAcceptanceController:
    """Run the bounded finite workflow; no free-form pre-acceptance tool choice."""

    def __init__(
        self,
        *,
        structured,
        source_spans: SourceSpanRegistry,
        capabilities: ManagerCapabilityRegistry | None = None,
        max_draft_attempts: int = 2,
    ) -> None:
        if not callable(structured):
            raise ValueError("structured_json callable required")
        self._structured = structured
        self._source_spans = source_spans
        self._capabilities = capabilities or ManagerCapabilityRegistry()
        self._max_draft_attempts = max(1, int(max_draft_attempts))

    def _structured_call(self, *, system: str, payload: dict, model, schema_name: str):
        schema = _strict_native_schema(model.model_json_schema())
        raw = self._structured(
            system,
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            schema=schema,
            schema_name=schema_name,
        )
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            return model.model_validate(data)
        except Exception as first_error:
            repair_system = (
                system
                + "\n\nFORMAT_REPAIR_ONLY: Keep the same semantic decision. "
                "Only repair strict-schema formatting; do not add/remove material intent."
            )
            repaired = self._structured(
                repair_system,
                json.dumps(
                    {
                        **payload,
                        "PREVIOUS_INVALID_OUTPUT": raw,
                        "FORMAT_ERROR": str(first_error)[:1200],
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                schema=schema,
                schema_name=schema_name,
            )
            data = json.loads(repaired) if isinstance(repaired, str) else repaired
            return model.model_validate(data)

    def _draft(
        self,
        *,
        question: str,
        conversation: ConversationStateV2 | None,
        revision_feedback: dict[str, Any] | None,
    ) -> IntentDraft:
        payload = {
            "USER_MESSAGE": question,
            "CONVERSATION_SURFACE": _conversation_surface_view(conversation),
            "CAPABILITY_BINDING_CONTRACT": self._capabilities.manager_contract(),
            "REVISION_FEEDBACK": revision_feedback,
        }
        return self._structured_call(
            system=_DRAFT_SYSTEM,
            payload=payload,
            model=IntentDraft,
            schema_name="dima_intent_draft_v1",
        )

    def _coverage(
        self,
        *,
        question: str,
        draft: IntentDraft,
        conversation: ConversationStateV2 | None,
    ) -> CoverageAudit:
        payload = {
            "USER_MESSAGE": question,
            "CONVERSATION_SURFACE": _conversation_surface_view(conversation),
            "INTENT_DRAFT": draft.model_dump(mode="json"),
        }
        return self._structured_call(
            system=_COVERAGE_SYSTEM,
            payload=payload,
            model=CoverageAudit,
            schema_name="dima_intent_coverage_v1",
        )

    def _source_refs(
        self,
        *,
        message_id: str,
        surfaces: tuple[str, ...],
    ) -> tuple[str, ...]:
        return tuple(
            self._source_spans.mint_exact(
                message_id=message_id,
                surface=surface,
            ).source_ref
            for surface in surfaces
        )

    def _ground(
        self,
        *,
        draft: IntentDraft,
        message_id: str,
        runtime: ManagerRuntime,
        executor,
    ) -> tuple[dict[tuple[str, str], str], Any | None]:
        requests: list[tuple[str, str]] = []
        for obligation in draft.obligations:
            for item in obligation.semantic_surfaces:
                pair = (item.surface, item.kind_hint)
                if pair not in requests:
                    requests.append(pair)

        if not requests:
            return {}, None

        refs = tuple(
            self._source_spans.mint_exact(
                message_id=message_id,
                surface=surface,
            ).source_ref
            for surface, _ in requests
        )
        hints = tuple(kind for _, kind in requests)
        step = runtime.call_tool(
            ManagerToolCall(
                name=ManagerToolName.RESOLVE_SEMANTICS,
                args={
                    "provenance": "USER_SOURCE",
                    "source_refs": refs,
                    "target_kind_hints": hints,
                    "temporal_anchor_handle": None,
                    "base_period_handle": None,
                },
            ),
            executor=executor,
        )
        result = step.tool_result
        by_source_ref = {
            item.source_ref: item.handle.handle_id
            for item in tuple(getattr(result, "resolved", ()) or ())
            if item.source_ref is not None
        }
        grounded: dict[tuple[str, str], str] = {}
        for (surface, kind), source_ref in zip(requests, refs, strict=True):
            handle_id = by_source_ref.get(source_ref)
            if handle_id:
                grounded[(surface, kind)] = handle_id
        return grounded, result

    def _envelope(
        self,
        *,
        draft: IntentDraft,
        grounded: dict[tuple[str, str], str],
        message_id: str,
        source_hash: str,
        request_ref: str,
        runtime: ManagerRuntime,
    ) -> UserIntentEnvelope:
        obligations: list[CandidateObligation] = []
        for item in draft.obligations:
            source_refs = self._source_refs(
                message_id=message_id,
                surfaces=item.source_surfaces,
            )
            semantic_handle_refs = tuple(
                dict.fromkeys(
                    grounded[(surface.surface, surface.kind_hint)]
                    for surface in item.semantic_surfaces
                    if (surface.surface, surface.kind_hint) in grounded
                )
            )
            obligations.append(
                CandidateObligation(
                    obligation_id=item.obligation_id,
                    capability_key=item.capability_key,
                    origin=ObligationOrigin(item.origin),
                    priority=item.priority,
                    polarity=item.polarity,
                    source_refs=source_refs,
                    semantic_handle_refs=semantic_handle_refs,
                    open_questions=item.open_questions,
                    ranking_direction=item.ranking_direction,
                    ranking_limit=item.ranking_limit,
                )
            )

        directives = tuple(
            ResearchDirective(
                directive_id=item.directive_id,
                directive_type=ResearchDirectiveType(item.directive_type),
                parent_obligation_id=item.parent_obligation_id,
                condition=ResearchDirectiveCondition(item.condition),
                source_refs=self._source_refs(
                    message_id=message_id,
                    surfaces=item.source_surfaces,
                ),
            )
            for item in draft.research_directives
        )

        return UserIntentEnvelope(
            attempt_id=(
                f"{runtime.snapshot.run_id}:draft:{runtime.snapshot.manager_turns}"
            ),
            turn_id=message_id,
            request_ref=request_ref,
            source_message_hash=source_hash,
            model_role="RESEARCH_MANAGER",
            obligations=tuple(obligations),
            research_directives=directives,
        )

    @staticmethod
    def _coverage_feedback(audit: CoverageAudit) -> dict[str, Any]:
        return {
            "kind": "COVERAGE_VETO",
            "issues": [
                {
                    "kind": issue.kind.value,
                    "source_surfaces": list(issue.source_surfaces),
                    "note": issue.note,
                }
                for issue in audit.issues
            ],
        }

    @staticmethod
    def _validity_feedback(result) -> dict[str, Any]:
        return {
            "kind": "CONTRACT_VALIDITY_REJECTED",
            "reasons": list(result.reasons),
        }

    def run(
        self,
        *,
        question: str,
        message_id: str,
        request_ref: str,
        source_hash: str,
        runtime: ManagerRuntime,
        executor,
        conversation: ConversationStateV2 | None,
    ) -> FiniteAcceptanceOutcome:
        observations: list[dict[str, Any]] = [
            {
                "kind": "phase",
                "name": "FINITE_PRE_ACCEPTANCE",
                "protocol": [
                    "DRAFT",
                    "AUTO_GROUND",
                    "COVERAGE_VETO",
                    "CONTRACT_VALIDITY",
                    "ACCEPT_OR_REVISE_OR_CLARIFY",
                ],
            }
        ]
        revision_feedback: dict[str, Any] | None = None

        for attempt in range(1, self._max_draft_attempts + 1):
            runtime.reset_semantic_resolution_receipts()
            try:
                runtime.note_manager_turn()
                draft = self._draft(
                    question=question,
                    conversation=conversation,
                    revision_feedback=revision_feedback,
                )
            except ManagerBudgetError:
                raise
            except Exception as exc:
                observations.append(
                    {
                        "kind": "draft_error",
                        "attempt": attempt,
                        "message": str(exc),
                    }
                )
                return FiniteAcceptanceOutcome(
                    accepted=False,
                    clarification_required=False,
                    observations=tuple(observations),
                )

            observations.append(
                {
                    "kind": "intent_draft",
                    "attempt": attempt,
                    "draft": draft.model_dump(mode="json"),
                }
            )

            try:
                grounded, resolution = self._ground(
                    draft=draft,
                    message_id=message_id,
                    runtime=runtime,
                    executor=executor,
                )
            except Exception as exc:
                observations.append(
                    {
                        "kind": "grounding_error",
                        "attempt": attempt,
                        "message": str(exc),
                    }
                )
                return FiniteAcceptanceOutcome(
                    accepted=False,
                    clarification_required=False,
                    observations=tuple(observations),
                )

            if resolution is not None and bool(
                getattr(resolution, "clarification_required", False)
            ):
                runtime.require_clarification(
                    "SemanticResolver requires clarification for draft grounding"
                )
                observations.append(
                    {
                        "kind": "grounding",
                        "attempt": attempt,
                        "status": "NEEDS_CLARIFICATION",
                    }
                )
                return FiniteAcceptanceOutcome(
                    accepted=False,
                    clarification_required=True,
                    observations=tuple(observations),
                )

            observations.append(
                {
                    "kind": "grounding",
                    "attempt": attempt,
                    "status": "GROUNDED",
                    "receipt_count": len(runtime.semantic_resolution_receipts),
                }
            )

            try:
                runtime.note_manager_turn()
                coverage = self._coverage(
                    question=question,
                    draft=draft,
                    conversation=conversation,
                )
            except Exception as exc:
                observations.append(
                    {
                        "kind": "coverage_error",
                        "attempt": attempt,
                        "message": str(exc),
                    }
                )
                return FiniteAcceptanceOutcome(
                    accepted=False,
                    clarification_required=False,
                    observations=tuple(observations),
                )

            observations.append(
                {
                    "kind": "coverage_audit",
                    "attempt": attempt,
                    "status": coverage.status,
                    "issues": [
                        {
                            "kind": issue.kind.value,
                            "source_surfaces": list(issue.source_surfaces),
                            "note": issue.note,
                        }
                        for issue in coverage.issues
                    ],
                }
            )

            if coverage.status == "VETO":
                if attempt < self._max_draft_attempts:
                    revision_feedback = self._coverage_feedback(coverage)
                    continue
                return FiniteAcceptanceOutcome(
                    accepted=False,
                    clarification_required=False,
                    observations=tuple(observations),
                )

            envelope = self._envelope(
                draft=draft,
                grounded=grounded,
                message_id=message_id,
                source_hash=source_hash,
                request_ref=request_ref,
                runtime=runtime,
            )
            step = runtime.call_tool(
                ManagerToolCall(
                    name=ManagerToolName.PROPOSE_ACCEPTANCE,
                    args={"envelope": envelope.model_dump(mode="json")},
                ),
                executor=executor,
            )
            result = step.tool_result
            observations.append(
                {
                    "kind": "contract_validity",
                    "attempt": attempt,
                    "status": result.status.value,
                    "reasons": list(result.reasons),
                }
            )

            if result.status == AcceptanceStatus.ACCEPTED:
                return FiniteAcceptanceOutcome(
                    accepted=True,
                    clarification_required=False,
                    observations=tuple(observations),
                )

            if result.status == AcceptanceStatus.NEEDS_CLARIFICATION:
                return FiniteAcceptanceOutcome(
                    accepted=False,
                    clarification_required=True,
                    observations=tuple(observations),
                )

            if attempt < self._max_draft_attempts:
                revision_feedback = self._validity_feedback(result)
                continue

            missing_binding_only = bool(result.reasons) and all(
                "missing required semantic kinds:" in str(reason)
                for reason in result.reasons
            )
            if missing_binding_only:
                runtime.require_clarification(
                    "accepted intent needs a trusted semantic binding unavailable "
                    "from the current turn"
                )
                return FiniteAcceptanceOutcome(
                    accepted=False,
                    clarification_required=True,
                    observations=tuple(observations),
                )

            return FiniteAcceptanceOutcome(
                accepted=False,
                clarification_required=False,
                observations=tuple(observations),
            )

        return FiniteAcceptanceOutcome(
            accepted=False,
            clarification_required=False,
            observations=tuple(observations),
        )
