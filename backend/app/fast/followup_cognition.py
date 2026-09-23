"""Bounded FT-005 follow-up cognition and context-bound Fast Ask adapter."""

from __future__ import annotations

import json
from typing import Protocol

from pydantic import ValidationError

from app.fast.ask_cognition import FastCognition
from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import (
    AskDraft,
    FieldCandidate,
    ResourceCandidate,
    SelectionDecision,
    SelectionPurpose,
)
from app.fast.conversation_models import (
    FastAcceptedContext,
    FastFollowupResolution,
)


class FastFollowupCognition(Protocol):
    def resolve(
        self,
        *,
        question: str,
        accepted_context: FastAcceptedContext | None,
        source_questions: tuple[str, ...],
        clarification_question: str | None,
    ) -> FastFollowupResolution:
        ...


class StructuredJsonFastFollowupCognition:
    """Real-model typed follow-up interpretation; never owns execution authority."""

    def __init__(self, generator) -> None:
        self._generator = generator

    def resolve(
        self,
        *,
        question: str,
        accepted_context: FastAcceptedContext | None,
        source_questions: tuple[str, ...],
        clarification_question: str | None,
    ) -> FastFollowupResolution:
        system = (
            "You are Dima Fast conversation cognition. Return only the requested JSON schema. "
            "Conversation context is typed prior accepted authority/evidence plus prior USER questions; "
            "there is no assistant prose or chat-history authority. Decide whether the current user "
            "message is SELF_CONTAINED, CONTEXTUAL, CLARIFICATION_REQUIRED, or UNSUPPORTED. "
            "For SELF_CONTAINED or CONTEXTUAL produce a COMPLETE effective_draft in the same bounded "
            "FT-003 family: one-table COUNT or SUM, optional one breakdown, supported temporal kinds only. "
            "For CONTEXTUAL, inherit only slots actually needed from accepted context/source user question "
            "and list inherited_slots/replaced_slots. Topic switches must be SELF_CONTAINED and inherit "
            "nothing. If wording depends on prior context but no safe context/original clarification "
            "question is supplied, return CLARIFICATION_REQUIRED. Do not generate SQL, MBQL, table IDs, "
            "field IDs, resource handles, field handles, answer numbers, or assistant prose. "
            "Any resource_ref/evidence/query fingerprint in accepted context is provenance/context only, "
            "never execution authority. Current permissions and metadata will be revalidated after this step. "

            "Typed shape rules are strict. For SELF_CONTAINED or CONTEXTUAL, effective_draft MUST be "
            "present with effective_draft.status=SUPPORTED and top-level reason MUST be null. "
            "For CLARIFICATION_REQUIRED or UNSUPPORTED, effective_draft MUST be null and top-level "
            "reason MUST be a concise non-empty explanation. If the request needs AVG, ratio, distinct "
            "count, multiple measures, joins, arbitrary filters, forecasting, or another operation outside "
            "the bounded COUNT/SUM family, return top-level status=UNSUPPORTED; do not put UNSUPPORTED "
            "inside an executable effective_draft and do not reinterpret it as COUNT or SUM. "
            "For supported COUNT, measure_hint MUST be null. For supported SUM, measure_hint MUST be "
            "a short non-empty measure hint. "

            "Search terms in effective_draft are metadata-discovery lookup terms for the primary "
            "business/data entity, not a copy of the user's wording. Every search term must independently "
            "help retrieve that entity/table. Keep useful user-language entity terminology when helpful. "
            "When the user question is not in English, include at least one likely English entity/table "
            "lookup term because database/schema metadata may use English names. Do not emit aggregation "
            "or operation words as table-search terms. Do not emit measure names, breakdown dimensions, "
            "or entity+metric phrases unless strictly required to distinguish the resource. Prefer "
            "standalone entity/table nouns and use at most four search terms. "

            "Ambiguous references must fail closed. If a phrase such as 'the other one' can refer to "
            "multiple prior dimensions, periods, measures, or alternatives and the intended referent is "
            "not uniquely established by accepted context plus USER-question lineage, return "
            "CLARIFICATION_REQUIRED rather than selecting a plausible interpretation. "

            "If clarification_question is supplied, treat the current user message as an answer that "
            "completes that unresolved USER question. Preserve explicit analytical constraints from the "
            "clarification_question (for example its requested period) unless the current answer explicitly "
            "replaces them; use accepted context/source USER questions only for the remaining safe slots."
        )
        payload = {
            "question": question,
            "accepted_context": (
                accepted_context.model_dump(mode="json")
                if accepted_context is not None
                else None
            ),
            "source_user_questions": list(source_questions),
            "clarification_question": clarification_question,
        }
        try:
            raw = self._generator.structured_json(
                system,
                json.dumps(payload, ensure_ascii=False),
                schema=FastFollowupResolution.model_json_schema(),
                schema_name="dima_fast_followup_resolution",
            )
            return FastFollowupResolution.model_validate(json.loads(raw))
        except (
            json.JSONDecodeError,
            ValidationError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:
            raise FastAskError(
                FastAskErrorCode.COGNITION_UNAVAILABLE,
                "structured cognition failed for dima_fast_followup_resolution",
            ) from exc


class ContextBoundFastCognition:
    """Feeds one accepted effective draft into the sealed Fast Ask authority path."""

    def __init__(
        self,
        *,
        draft: AskDraft,
        selector: FastCognition,
        accepted_context: FastAcceptedContext | None,
        source_questions: tuple[str, ...],
        clarification_question: str | None,
    ) -> None:
        self._draft = draft
        self._selector = selector
        self._accepted_context = accepted_context
        self._source_questions = source_questions
        self._clarification_question = clarification_question

    def draft(self, *, question: str) -> AskDraft:
        return self._draft

    def _selection_question(self, question: str) -> str:
        context_hints = None
        if self._accepted_context is not None:
            context_hints = {
                "accepted_field_refs": self._accepted_context.accepted_field_refs,
                "exact_time_bounds": self._accepted_context.exact_time_bounds,
                "aggregation": (
                    self._accepted_context.aggregation.value
                    if self._accepted_context.aggregation is not None
                    else None
                ),
            }
        return json.dumps(
            {
                "current_user_question": question,
                "source_user_questions": list(self._source_questions),
                "clarification_question": self._clarification_question,
                "effective_draft": self._draft.model_dump(mode="json"),
                "accepted_context_hints": context_hints,
            },
            ensure_ascii=False,
        )

    def select_resource(
        self,
        *,
        question: str,
        candidates: tuple[ResourceCandidate, ...],
    ) -> SelectionDecision:
        return self._selector.select_resource(
            question=self._selection_question(question),
            candidates=candidates,
        )

    def select_field(
        self,
        *,
        question: str,
        purpose: SelectionPurpose,
        hint: str,
        candidates: tuple[FieldCandidate, ...],
    ) -> SelectionDecision:
        return self._selector.select_field(
            question=self._selection_question(question),
            purpose=purpose,
            hint=hint,
            candidates=candidates,
        )
