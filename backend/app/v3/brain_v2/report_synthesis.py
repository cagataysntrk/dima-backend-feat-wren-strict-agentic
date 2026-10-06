"""Bounded governed synthesis cognition for P20.

P20 may use one cognition call to organize already-governed report material into
accepted presentation deliverables.  This module has no native/Metabase handle,
performs no analytics, and cannot mint semantic or causal authority.
"""
from __future__ import annotations

import json
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
        # Numeric truth is never authored in free-form synthesis. Existing
        # governed numeric statements remain separately publishable with exact
        # Evidence lineage.
        if any(char.isdigit() for char in self.text):
            raise ValueError("synthesis text cannot author numeric claims")
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
            schema=strict_json_schema(P20SynthesisEnvelope),
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
        return result
