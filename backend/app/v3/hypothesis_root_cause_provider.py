"""Typed model adapter for DMP-DEC-0055 P19 epistemic assessment.

The model proposes qualitative P19 judgments over already-governed source
lineage. Deterministic HypothesisRootCauseStore remains final authority for
identity, source legality, P18 eligibility, causal promotion and terminal state.
"""
from __future__ import annotations

import copy
import json
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    CandidateAssessment,
    CausalQualification,
    ContributionClass,
    EvidenceStrength,
    HypothesisDisposition,
    HypothesisEpistemicClass,
    IdentificationLimitation,
    P19CaseSnapshot,
    RootCauseAssessmentDraft,
)


class StructuredJSONTransport(Protocol):
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


class ModelCandidateJudgment(Frozen):
    hypothesis_id: str = Field(pattern=r"^p19h_[a-f0-9]{24}$")
    grounding_link_ids: tuple[str, ...] = Field(min_length=1)
    disposition: HypothesisDisposition
    epistemic_class: HypothesisEpistemicClass
    contribution_class: ContributionClass
    evidence_strength: EvidenceStrength
    causal_qualification: CausalQualification = CausalQualification.NOT_CLAIMED
    relationship_dependent: bool = False
    relationship_policy_use_id: str | None = Field(
        default=None,
        pattern=r"^bru_[a-f0-9]{24}$",
    )
    identification_limitations: tuple[IdentificationLimitation, ...] = ()

    @model_validator(mode="after")
    def coherent(self):
        if len(self.grounding_link_ids) != len(set(self.grounding_link_ids)):
            raise ValueError("grounding_link_ids must be unique")
        if (
            self.relationship_dependent
            and self.relationship_policy_use_id is None
        ):
            raise ValueError(
                "relationship-dependent judgment requires policy-use id"
            )
        return self


class ModelAssessmentDraft(Frozen):
    candidates: tuple[ModelCandidateJudgment, ...] = Field(min_length=1)
    aggregate_outcome: AggregateOutcome
    root_cause_hypothesis_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def coherent(self):
        ids = tuple(item.hypothesis_id for item in self.candidates)
        if len(ids) != len(set(ids)):
            raise ValueError("candidate hypothesis ids must be unique")
        if len(self.root_cause_hypothesis_ids) != len(
            set(self.root_cause_hypothesis_ids)
        ):
            raise ValueError("root-cause ids must be unique")
        return self


_SYSTEM = """You are Dima's bounded P19 epistemic assessor.

Architecture:
- METABASE + METABOT = analytical engine.
- DIMA P19 does not execute analytics; it governs what existing governed sources
  justify epistemically.
- P17 investigation parent/child structure is NOT a causal graph.
- P18 policy direction is NOT causal direction.
- P16 claim state is NOT P19 hypothesis state.
- Preserve viable competing hypotheses. Multiple retained/material contributors
  are legal; there is no winner-takes-all rule.
- Keep contribution class and evidence strength as independent qualitative axes.
- Never invent numeric confidence, contribution %, effect %, probability, score,
  SQL, MBQL, joins, or analytical values.
- Association/correlation must not be promoted directly to cause.
- P18 SATISFIED means interpretation eligibility only, never causal proof.
- A blocked required P18 policy cannot support trusted causal promotion.
- NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED is a successful terminal result.
- Use only hypothesis ids and grounding ids present in the supplied packet.
- Return one qualitative assessment draft. Deterministic Dima validates it.
"""


def _strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(schema)
    unsupported = {
        "default",
        "title",
        "description",
        "minLength",
        "maxLength",
        "pattern",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "format",
    }

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key in unsupported:
                node.pop(key, None)
            props = node.get("properties")
            if isinstance(props, dict):
                node["additionalProperties"] = False
                node["required"] = list(props)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    defs = value.get("$defs")
    if isinstance(defs, dict):
        referenced: set[str] = set()

        def collect(node: Any) -> None:
            if isinstance(node, dict):
                ref = node.get("$ref")
                if isinstance(ref, str) and ref.startswith("#/$defs/"):
                    referenced.add(ref.removeprefix("#/$defs/"))
                for key, child in node.items():
                    if key != "$defs":
                        collect(child)
            elif isinstance(node, list):
                for child in node:
                    collect(child)

        collect(value)
        pending = list(referenced)
        while pending:
            name = pending.pop()
            definition = defs.get(name)
            if definition is None:
                continue
            before = set(referenced)
            collect(definition)
            pending.extend(sorted(referenced - before))
        value["$defs"] = {
            name: definition
            for name, definition in defs.items()
            if name in referenced
        }
        if not value["$defs"]:
            value.pop("$defs", None)
    return value


def provider_schema() -> dict[str, Any]:
    return _strict_json_schema(ModelAssessmentDraft.model_json_schema())


def _packet(
    snapshot: P19CaseSnapshot,
    *,
    policy_statuses: dict[str, str] | None,
    deterministic_feedback_code: str | None,
) -> str:
    hypotheses = []
    for item in snapshot.hypotheses:
        hypotheses.append(
            {
                "hypothesis_id": item.hypothesis.hypothesis_id,
                "statement": item.hypothesis.statement,
                "groundings": [
                    {
                        "grounding_link_id": link.grounding_link_id,
                        "source_kind": link.source_kind.value,
                        "source_ref": link.source_ref,
                        "source_receipt_id": link.source_receipt_id,
                        "relation": link.relation.value,
                    }
                    for link in item.groundings
                ],
            }
        )
    packet = {
        "research_session_id": snapshot.research_session_id,
        "obligation_id": snapshot.obligation_id,
        "semantic_context_version": snapshot.semantic_context_version,
        "hypotheses": hypotheses,
        "p18_policy_use_statuses": policy_statuses or {},
        "causal_identification_source_refs_exposed": [],
        "numeric_values_exposed_to_model": False,
        "deterministic_feedback_code": deterministic_feedback_code,
    }
    return json.dumps(packet, ensure_ascii=False, sort_keys=True)


class StructuredP19AssessmentManager:
    """One bounded qualitative proposal call; never final epistemic authority."""

    def __init__(
        self,
        *,
        transport: StructuredJSONTransport,
        schema_name: str = "dima_p19_epistemic_assessment",
    ) -> None:
        self._transport = transport
        self._schema_name = schema_name
        self.call_count = 0

    def propose(
        self,
        snapshot: P19CaseSnapshot,
        *,
        policy_statuses: dict[str, str] | None = None,
        deterministic_feedback_code: str | None = None,
    ) -> RootCauseAssessmentDraft:
        known_hypotheses = {
            item.hypothesis.hypothesis_id
            for item in snapshot.hypotheses
        }
        known_groundings = {
            link.grounding_link_id: item.hypothesis.hypothesis_id
            for item in snapshot.hypotheses
            for link in item.groundings
        }
        if len(known_hypotheses) < 2:
            raise ValueError(
                "P19 model assessment requires competing hypotheses"
            )

        user = (
            "Assess the bounded P19 case using only this governed packet. "
            "Preserve every current hypothesis in candidates. Do not invent "
            "sources or numeric values. If causal identification is not "
            "explicitly exposed, do not claim a defensible root cause.\n\n"
            + _packet(
                snapshot,
                policy_statuses=policy_statuses,
                deterministic_feedback_code=deterministic_feedback_code,
            )
        )
        raw = self._transport.structured_json(
            _SYSTEM,
            user,
            schema=provider_schema(),
            schema_name=self._schema_name,
        )
        self.call_count += 1
        draft = ModelAssessmentDraft.model_validate_json(raw)

        ids = {item.hypothesis_id for item in draft.candidates}
        if ids != known_hypotheses:
            raise ValueError(
                "model assessment must preserve the complete hypothesis set"
            )
        challenge_ids = {
            item.hypothesis.hypothesis_id: {
                link.grounding_link_id
                for link in item.groundings
                if link.relation.value == "CHALLENGES"
            }
            for item in snapshot.hypotheses
        }
        for candidate in draft.candidates:
            selected = set(candidate.grounding_link_ids)
            for grounding_id in selected:
                owner = known_groundings.get(grounding_id)
                if owner != candidate.hypothesis_id:
                    raise ValueError(
                        "model assessment used unknown/foreign grounding"
                    )
            if not challenge_ids[candidate.hypothesis_id].issubset(selected):
                raise ValueError(
                    "model assessment cannot hide governed challenge grounding"
                )

        return RootCauseAssessmentDraft(
            research_session_id=snapshot.research_session_id,
            obligation_id=snapshot.obligation_id,
            candidates=tuple(
                CandidateAssessment(
                    hypothesis_id=item.hypothesis_id,
                    grounding_link_ids=item.grounding_link_ids,
                    disposition=item.disposition,
                    epistemic_class=item.epistemic_class,
                    contribution_class=item.contribution_class,
                    evidence_strength=item.evidence_strength,
                    causal_qualification=item.causal_qualification,
                    relationship_dependent=item.relationship_dependent,
                    relationship_policy_use_id=(
                        item.relationship_policy_use_id
                    ),
                    identification_limitations=(
                        item.identification_limitations
                    ),
                    numeric_provenance=(),
                    causal_identification_refs=(),
                )
                for item in draft.candidates
            ),
            aggregate_outcome=draft.aggregate_outcome,
            root_cause_hypothesis_ids=draft.root_cause_hypothesis_ids,
            limitations=draft.limitations,
            mediation_annotations=(),
        )
