"""Bounded cognition interface for Fast Ask.

The model is permitted to draft intent and choose from opaque candidate handles only.
Semantic/resource authority remains deterministic in app.fast.
"""

from __future__ import annotations

import json
from typing import Protocol

from pydantic import ValidationError

from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import (
    AskDraft,
    FieldCandidate,
    ResourceCandidate,
    SelectionDecision,
    SelectionPurpose,
)


class FastCognition(Protocol):
    def draft(self, *, question: str) -> AskDraft:
        ...

    def select_resource(
        self,
        *,
        question: str,
        candidates: tuple[ResourceCandidate, ...],
    ) -> SelectionDecision:
        ...

    def select_field(
        self,
        *,
        question: str,
        purpose: SelectionPurpose,
        hint: str,
        candidates: tuple[FieldCandidate, ...],
    ) -> SelectionDecision:
        ...


class StructuredJsonFastCognition:
    """Adapter over the existing structured-json transport, with Fast-owned schemas."""

    def __init__(self, generator) -> None:
        self._generator = generator

    def _call(self, *, system: str, user: str, model_cls, schema_name: str):
        try:
            raw = self._generator.structured_json(
                system,
                user,
                schema=model_cls.model_json_schema(),
                schema_name=schema_name,
            )
            payload = json.loads(raw)
            return model_cls.model_validate(payload)
        except (json.JSONDecodeError, ValidationError, RuntimeError, TypeError, ValueError) as exc:
            raise FastAskError(
                FastAskErrorCode.COGNITION_UNAVAILABLE,
                f"structured cognition failed for {schema_name}",
            ) from exc

    def draft(self, *, question: str) -> AskDraft:
        system = (
            "You are Dima Fast Ask cognition. Return only the requested JSON schema. "
            "Do not generate SQL, MBQL, database IDs, table IDs, field IDs, or answer numbers. "
            "FT-003 supports only row COUNT or SUM of one measure, with optional one breakdown "
            "and optional supported time period. Set status=SUPPORTED only when the request is "
            "fully representable by that family. If the request needs AVG, ratio, distinct count, "
            "multiple measures, joins, arbitrary filters, forecasting, or another unsupported "
            "operation, set status=UNSUPPORTED with a concise unsupported_reason; do not reinterpret "
            "it as COUNT or SUM. For an UNSUPPORTED draft use a structurally valid neutral COUNT "
            "placeholder because execution will stop before metadata/query work. Supported time "
            "kinds are NONE, LAST_N_DAYS, CURRENT_MONTH, PREVIOUS_MONTH, ABSOLUTE_DATE_RANGE. "
            "Search terms should describe the relevant business entity for metadata retrieval. "
            "For supported SUM provide a short measure hint; for supported COUNT measure_hint must "
            "be null. breakdown_hint is null unless the user explicitly asks for grouping."
        )
        return self._call(
            system=system,
            user=question,
            model_cls=AskDraft,
            schema_name="dima_fast_ask_draft",
        )

    def select_resource(
        self,
        *,
        question: str,
        candidates: tuple[ResourceCandidate, ...],
    ) -> SelectionDecision:
        public = [candidate.model_dump(mode="json") for candidate in candidates]
        system = (
            "Choose exactly one opaque resource handle only when the user's wording contains "
            "enough explicit distinguishing information to identify one candidate over every "
            "other candidate. Candidate order, rank, generic familiarity, or a merely plausible "
            "match is not sufficient evidence. If two or more candidates remain materially "
            "plausible, return selected_handle null. Never invent a handle and never infer raw IDs."
        )
        return self._call(
            system=system,
            user=json.dumps(
                {"question": question, "candidates": public},
                ensure_ascii=False,
            ),
            model_cls=SelectionDecision,
            schema_name="dima_fast_resource_selection",
        )

    def select_field(
        self,
        *,
        question: str,
        purpose: SelectionPurpose,
        hint: str,
        candidates: tuple[FieldCandidate, ...],
    ) -> SelectionDecision:
        public = [candidate.model_dump(mode="json") for candidate in candidates]
        system = (
            "Choose one opaque field handle from the provided candidates for the stated purpose. "
            "Use only supplied handles. If the intent is ambiguous or no candidate matches, "
            "return selected_handle null. Do not invent field names or IDs."
        )
        return self._call(
            system=system,
            user=json.dumps(
                {
                    "question": question,
                    "purpose": purpose.value,
                    "hint": hint,
                    "candidates": public,
                },
                ensure_ascii=False,
            ),
            model_cls=SelectionDecision,
            schema_name=f"dima_fast_field_selection_{purpose.value.lower()}",
        )
