"""Bounded governed synthesis cognition for P20.

P20 may use one cognition call to organize already-governed report material into
accepted presentation deliverables.  This module has no native/Metabase handle,
performs no analytics, and cannot mint semantic or causal authority.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.structured_transport import strict_json_schema


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class P20SynthesisKind(StrEnum):
    OBSERVATION = "observation"
    FINDING = "finding"
    RELATIONSHIP = "relationship"
    EPISTEMIC_STATEMENT = "epistemic_statement"
    LIMITATION = "limitation"
    MANAGEMENT_IMPLICATION = "management_implication"


class P20SynthesisSection(Frozen):
    kind: P20SynthesisKind
    text: str = Field(min_length=1, max_length=1400)
    supporting_statement_ids: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def coherent(self):
        if len(self.supporting_statement_ids) != len(
            set(self.supporting_statement_ids)
        ):
            raise ValueError("synthesis support ids must be unique")
        return self


class P20DeliverableSynthesis(Frozen):
    requirement_id: str = Field(min_length=1)
    status: str = Field(pattern=r"^(FULFILLED|LIMITED)$")
    selected_statement_ids: tuple[str, ...] = ()
    sections: tuple[P20SynthesisSection, ...] = ()
    limitation_detail: str | None = Field(default=None, min_length=1, max_length=1400)

    @model_validator(mode="after")
    def coherent(self):
        if len(self.selected_statement_ids) != len(
            set(self.selected_statement_ids)
        ):
            raise ValueError("deliverable selected statement ids must be unique")
        if self.status == "FULFILLED":
            if not self.selected_statement_ids or not self.sections:
                raise ValueError(
                    "FULFILLED deliverable requires governed support and synthesis"
                )
            if self.limitation_detail is not None:
                raise ValueError("FULFILLED deliverable cannot carry limitation")
        else:
            if (
                self.selected_statement_ids
                or self.sections
                or self.limitation_detail is None
            ):
                raise ValueError(
                    "LIMITED deliverable carries only one explicit limitation"
                )
        return self


class P20SynthesisEnvelope(Frozen):
    deliverables: tuple[P20DeliverableSynthesis, ...]


_SYSTEM = """You are Dima P20's bounded presentation synthesizer.

You receive only accepted presentation deliverables, the current ScopeVersion,
governed EvidenceDigest statements, P18 results, P19 assessment, and explicit
limitations.

Your job is presentation synthesis only:
- organize and restate already-governed material for each accepted deliverable;
- select only supplied statement IDs as support;
- preserve limitations and epistemic strength;
- distinguish observation, finding, relationship/epistemic statement,
  limitation, and management implication when useful.

Hard boundaries:
- perform no analytics or calculations;
- invent no metric, dimension, entity, period, value, ranking, relationship,
  hypothesis, causal strength, or business fact;
- do not produce any number in synthesis text; numeric facts stay in the
  supplied governed statements with their Evidence lineage;
- do not infer causal meaning from correlation or descriptive observations;
- do not claim a deliverable FULFILLED unless the supplied governed statements
  actually support a useful presentation of it;
- if support is insufficient, return LIMITED with one explicit limitation;
- every synthesis section must cite one or more supplied statement IDs.
"""


def _canonical_numeric_token(value: str) -> str | None:
    """Canonicalize one already-scanned numeric token without semantic inference."""

    token = value.strip()
    if not token:
        return None
    if "," in token and "." not in token:
        token = token.replace(",", ".")
    try:
        number = Decimal(token)
    except InvalidOperation:
        return None
    if not number.is_finite():
        return None
    if number == 0:
        number = Decimal(0)
    normalized = format(number.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def _numeric_tokens(text: str) -> frozenset[str]:
    """Extract decimal tokens with a tiny deterministic scanner, never regex."""

    output: set[str] = set()
    current: list[str] = []
    value = str(text)

    def flush() -> None:
        if not current:
            return
        token = _canonical_numeric_token("".join(current))
        if token is not None:
            output.add(token)
        current.clear()

    for index, char in enumerate(value):
        next_char = value[index + 1] if index + 1 < len(value) else ""
        if char.isdigit():
            current.append(char)
            continue
        if (
            char in {"+", "-"}
            and not current
            and next_char.isdigit()
        ):
            current.append(char)
            continue
        if (
            char in {".", ","}
            and current
            and any(item.isdigit() for item in current)
            and next_char.isdigit()
        ):
            current.append(char)
            continue
        flush()
    flush()
    return frozenset(output)


def _numeric_tokens_from_value(value: Any) -> frozenset[str]:
    """Collect numeric literals already present in one governed statement."""

    output: set[str] = set()
    if isinstance(value, bool) or value is None:
        return frozenset()
    if isinstance(value, (int, float, Decimal)):
        token = _canonical_numeric_token(str(value))
        return frozenset((token,)) if token is not None else frozenset()
    if isinstance(value, str):
        return _numeric_tokens(value)
    if isinstance(value, dict):
        for item in value.values():
            output.update(_numeric_tokens_from_value(item))
        return frozenset(output)
    if isinstance(value, (list, tuple)):
        for item in value:
            output.update(_numeric_tokens_from_value(item))
        return frozenset(output)
    return frozenset()


def _p20_synthesis_schema(
    *,
    deliverable_ids: tuple[str, ...],
    statement_ids: tuple[str, ...],
) -> dict[str, Any]:
    """Close provider-selected identities to the exact governed input set."""

    schema = strict_json_schema(P20SynthesisEnvelope)
    definitions = schema.get("$defs")
    if not isinstance(definitions, dict):
        raise ValueError("P20 synthesis schema definitions are absent")
    deliverable = definitions.get("P20DeliverableSynthesis")
    section = definitions.get("P20SynthesisSection")
    if not isinstance(deliverable, dict) or not isinstance(section, dict):
        raise ValueError("P20 synthesis schema definitions are incomplete")
    deliverable_props = deliverable.get("properties")
    section_props = section.get("properties")
    if not isinstance(deliverable_props, dict) or not isinstance(section_props, dict):
        raise ValueError("P20 synthesis schema properties are incomplete")

    requirement = deliverable_props.get("requirement_id")
    selected = deliverable_props.get("selected_statement_ids")
    supporting = section_props.get("supporting_statement_ids")
    if not isinstance(requirement, dict):
        raise ValueError("P20 requirement id schema is absent")
    if not isinstance(selected, dict) or not isinstance(supporting, dict):
        raise ValueError("P20 statement id schemas are absent")

    requirement["enum"] = list(deliverable_ids)
    for field in (selected, supporting):
        items = field.get("items")
        if not isinstance(items, dict):
            raise ValueError("P20 statement id item schema is absent")
        items["enum"] = list(statement_ids)

    root_props = schema.get("properties")
    if not isinstance(root_props, dict):
        raise ValueError("P20 envelope schema properties are absent")
    deliverables = root_props.get("deliverables")
    if not isinstance(deliverables, dict):
        raise ValueError("P20 deliverables schema is absent")
    deliverables["minItems"] = len(deliverable_ids)
    deliverables["maxItems"] = len(deliverable_ids)
    return schema


class StructuredP20SynthesisManager:
    """One-call typed P20 cognition adapter with deterministic ID closure."""

    def __init__(self, *, transport) -> None:
        self._transport = transport

    def synthesize(
        self,
        *,
        accepted_deliverables: tuple[dict[str, Any], ...],
        scope_version_id: str,
        evidence_digests: tuple[dict[str, Any], ...],
        p18_results: tuple[dict[str, Any], ...],
        p19_assessment: dict[str, Any] | None,
        limitations: tuple[dict[str, Any], ...],
    ) -> P20SynthesisEnvelope:
        deliverable_ids = tuple(
            str(item["requirement_id"])
            for item in accepted_deliverables
        )
        if not deliverable_ids:
            return P20SynthesisEnvelope(deliverables=())
        if len(deliverable_ids) != len(set(deliverable_ids)):
            raise ValueError("accepted P20 deliverable ids must be unique")

        statement_ids = tuple(
            str(item["statement_id"])
            for item in evidence_digests
        )
        if not statement_ids:
            return P20SynthesisEnvelope(
                deliverables=tuple(
                    P20DeliverableSynthesis(
                        requirement_id=requirement_id,
                        status="LIMITED",
                        limitation_detail=(
                            "No governed publishable statement is available "
                            "for this accepted presentation requirement."
                        ),
                    )
                    for requirement_id in deliverable_ids
                )
            )
        if len(statement_ids) != len(set(statement_ids)):
            raise ValueError("P20 EvidenceDigest statement ids must be unique")

        payload = {
            "accepted_deliverables": list(accepted_deliverables),
            "current_scope_version": scope_version_id,
            "evidence_digests": list(evidence_digests),
            "p18_results": list(p18_results),
            "p19_assessment": p19_assessment,
            "limitations": list(limitations),
        }
        raw = self._transport.structured_json(
            _SYSTEM,
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
                default=str,
            ),
            schema=_p20_synthesis_schema(
                deliverable_ids=deliverable_ids,
                statement_ids=statement_ids,
            ),
            schema_name="dima_p20_governed_synthesis_v1",
        )
        result = P20SynthesisEnvelope.model_validate_json(raw)
        by_requirement = {
            item.requirement_id: item
            for item in result.deliverables
        }
        if (
            len(by_requirement) != len(result.deliverables)
            or set(by_requirement) != set(deliverable_ids)
        ):
            raise ValueError(
                "P20 synthesis must exactly cover accepted deliverable ids"
            )
        legal_statement_ids = set(statement_ids)
        statements_by_id = {
            str(item["statement_id"]): item
            for item in evidence_digests
        }
        for item in result.deliverables:
            if not set(item.selected_statement_ids).issubset(
                legal_statement_ids
            ):
                raise ValueError(
                    "P20 synthesis selected an unknown governed statement"
                )
            for section in item.sections:
                if not set(section.supporting_statement_ids).issubset(
                    legal_statement_ids
                ):
                    raise ValueError(
                        "P20 synthesis section selected unknown support"
                    )
                if not set(section.supporting_statement_ids).issubset(
                    set(item.selected_statement_ids)
                ):
                    raise ValueError(
                        "P20 synthesis section escaped deliverable support set"
                    )

                # Numeric synthesis is legal only when every literal already
                # exists in the governed supporting statements. This enforces
                # Evidence-backed numeric provenance without turning P20 into
                # an analytics/calculation owner and without blanket-rejecting
                # safe restatement of an existing governed value.
                authored_numbers = _numeric_tokens(section.text)
                if authored_numbers:
                    supported_numbers: set[str] = set()
                    for statement_id in section.supporting_statement_ids:
                        source = statements_by_id[statement_id]
                        supported_numbers.update(
                            _numeric_tokens_from_value(source.get("text"))
                        )
                        supported_numbers.update(
                            _numeric_tokens_from_value(source.get("payload"))
                        )
                    invented = authored_numbers - supported_numbers
                    if invented:
                        raise ValueError(
                            "P20 synthesis authored numeric truth absent from "
                            "its governed support"
                        )
        return result
