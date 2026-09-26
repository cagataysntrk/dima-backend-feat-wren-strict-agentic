"""Veto-only user-intent coverage guard for the Standard lane.

This component may block a Standard seal when material user intent was omitted. It is not
semantic authority: it cannot choose capabilities, canonical semantics, handles, query
shape, or clarification truth.
"""

from __future__ import annotations

import copy
import json
from enum import StrEnum
from typing import Any, Callable, Literal

from pydantic import Field, model_validator

from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationPolarity,
)
from app.v2.models import FrozenModel
from app.v2.source_spans import SourceSpanRegistry


class StandardCoverageIssueKind(StrEnum):
    MATERIAL_REQUEST_OMITTED = "MATERIAL_REQUEST_OMITTED"
    EXCLUSION_OMITTED_OR_WRONG_POLARITY = "EXCLUSION_OMITTED_OR_WRONG_POLARITY"
    RESEARCH_NEED_OMITTED = "RESEARCH_NEED_OMITTED"


class StandardCoverageIntentItem(FrozenModel):
    obligation_id: str = Field(min_length=1)
    capability_key: ManagerCapabilityKey
    polarity: ObligationPolarity
    # Provenance anchors for the requested obligation. These are not proof that
    # every material modifier inside the source text has been semantically represented.
    source_surfaces: tuple[str, ...] = Field(min_length=1)
    # Exact user spans that actually reached governed semantic handles.
    semantic_source_surfaces: tuple[str, ...] = ()
    semantic_target_kinds: tuple[str, ...] = ()
    ranking_direction: Literal["asc", "desc"] | None = None
    ranking_limit: int | None = Field(default=None, ge=1, le=1000)

    @model_validator(mode="after")
    def _semantic_alignment(self):
        if len(self.semantic_source_surfaces) != len(self.semantic_target_kinds):
            raise ValueError(
                "semantic source surfaces and target kinds must align"
            )
        if (self.ranking_direction is None) != (self.ranking_limit is None):
            raise ValueError(
                "coverage ranking direction + limit must be supplied together"
            )
        return self


class StandardCoverageIssue(FrozenModel):
    kind: StandardCoverageIssueKind
    source_surfaces: tuple[str, ...] = Field(min_length=1)
    note: str = Field(min_length=1, max_length=300)


class StandardCoverageAudit(FrozenModel):
    status: Literal["PASS", "VETO"]
    issues: tuple[StandardCoverageIssue, ...] = ()

    @model_validator(mode="after")
    def _shape(self):
        if self.status == "PASS" and self.issues:
            raise ValueError("PASS standard coverage audit cannot carry issues")
        if self.status == "VETO" and not self.issues:
            raise ValueError("VETO standard coverage audit requires issues")
        return self


class StandardCoverageError(RuntimeError):
    pass


_STANDARD_COVERAGE_SYSTEM = """You are Dima's final veto-only Standard intent coverage auditor.

Compare USER_MESSAGE against STANDARD_INTENT_VIEW only for material coverage loss.

Interpret the view precisely:
- source_surfaces are provenance anchors for the obligation; they do NOT prove every word
  inside those anchors was represented.
- semantic_source_surfaces are exact user spans that actually reached governed semantic handles.
- capability_key and ranking_direction/ranking_limit are typed operation representation.

You may VETO only when:
1. a materially requested business result is omitted,
2. an explicit user exclusion is omitted or represented with wrong polarity,
3. the user clearly requested an investigation/research task that a Standard analytical
   projection would silently omit,
4. a material qualifier, modifier, negation, threshold or predicate changes the requested
   business meaning but is neither represented inside semantic_source_surfaces nor by a typed
   operation parameter. Such meaning must not silently disappear.

Do NOT veto ordinary grammar/presentation wording, or a qualifier already contained inside a
bound semantic_source_surface when that whole phrase is the governed business concept.
If the requested modifier/predicate cannot be represented safely, VETO with its exact source
substring rather than guessing or repairing it.

You are NOT semantic authority. You MUST NOT:
- choose, add, remove or suggest a capability,
- choose or suggest canonical semantics,
- emit semantic handles, canonical IDs, SQL or database identifiers,
- repair the Standard projection,
- invent obligations,
- decide clarification truth.

Return only PASS or VETO. Every VETO issue must quote exact source substrings from
USER_MESSAGE. The audit may block a seal; it can never create authority.
"""


def _strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
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


class StandardCoverageVeto:
    def __init__(
        self,
        *,
        structured: Callable[..., Any],
        source_spans: SourceSpanRegistry,
    ) -> None:
        if not callable(structured):
            raise ValueError("structured_json callable required")
        self._structured = structured
        self._source_spans = source_spans

    def _intent_view(
        self,
        obligations: tuple[CandidateObligation, ...],
        *,
        source_message_hash: str,
    ) -> tuple[StandardCoverageIntentItem, ...]:
        out: list[StandardCoverageIntentItem] = []
        for item in obligations:
            surfaces = tuple(
                self._source_spans.validate(
                    source_ref,
                    expected_message_hash=source_message_hash,
                ).exact_surface
                for source_ref in item.source_refs
            )
            semantic_surfaces: list[str] = []
            semantic_kinds: list[str] = []
            for binding in item.semantic_bindings:
                semantic_span = self._source_spans.validate(
                    binding.source_ref,
                    expected_message_hash=source_message_hash,
                )
                semantic_surfaces.append(semantic_span.exact_surface)
                semantic_kinds.append(binding.target_kind)

            out.append(
                StandardCoverageIntentItem(
                    obligation_id=item.obligation_id,
                    capability_key=item.capability_key,
                    polarity=item.polarity,
                    source_surfaces=surfaces,
                    semantic_source_surfaces=tuple(semantic_surfaces),
                    semantic_target_kinds=tuple(semantic_kinds),
                    ranking_direction=item.ranking_direction,
                    ranking_limit=item.ranking_limit,
                )
            )
        return tuple(out)

    def audit(
        self,
        *,
        question: str,
        obligations: tuple[CandidateObligation, ...],
        source_message_hash: str,
    ) -> StandardCoverageAudit:
        intent_view = self._intent_view(
            obligations,
            source_message_hash=source_message_hash,
        )
        payload = {
            "USER_MESSAGE": question,
            "STANDARD_INTENT_VIEW": [
                item.model_dump(mode="json")
                for item in intent_view
            ],
        }
        schema = _strict_schema(StandardCoverageAudit.model_json_schema())
        raw = self._structured(
            _STANDARD_COVERAGE_SYSTEM,
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            schema=schema,
            schema_name="dima_standard_coverage_v1",
        )
        data = json.loads(raw) if isinstance(raw, str) else raw
        audit = StandardCoverageAudit.model_validate(data)

        for issue in audit.issues:
            for surface in issue.source_surfaces:
                if not surface or surface not in question:
                    raise StandardCoverageError(
                        "coverage veto source surface is not exact user-message evidence"
                    )
        return audit
