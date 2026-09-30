"""Deterministic owner-specific Brain V2 projections.

These are prompt/input views over canonical Dima artifacts. They own no business,
analytical, Evidence or epistemic truth.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.evidence import DimaQueryReceipt, EvidenceArtifact
from app.v3.research_contracts import (
    ResearchSemanticRef,
    SemanticTargetKind,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


class EvidenceDigest(Frozen):
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    state: str = Field(min_length=1)

    metric_ids: tuple[str, ...] = ()
    dimension_ids: tuple[str, ...] = ()
    entity_ids: tuple[str, ...] = ()

    # Exact deterministic payload summary only when bounded enough for working
    # context. Full payload remains in the canonical Evidence store.
    exact_material_json: str | None = Field(default=None, max_length=4096)
    payload_hash: str = Field(pattern=r"^[a-f0-9]{64}$")

    hypothesis_relations: tuple[str, ...] = ()
    receipt_ref: str | None = None
    result_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def unique_refs(self):
        for name in (
            "metric_ids",
            "dimension_ids",
            "entity_ids",
            "hypothesis_relations",
        ):
            values = getattr(self, name)
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        return self


def evidence_digest(
    *,
    evidence: EvidenceArtifact,
    scope_version_id: str,
    semantic_refs: tuple[ResearchSemanticRef, ...],
    receipt: DimaQueryReceipt | None = None,
    hypothesis_relations: tuple[str, ...] = (),
    max_exact_json_chars: int = 4096,
) -> EvidenceDigest:
    """Project canonical Evidence into a deterministic bounded working-set index."""

    if max_exact_json_chars < 0:
        raise ValueError("max_exact_json_chars must be non-negative")

    payload_json = _canonical_json(evidence.payload)
    payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    exact = payload_json if len(payload_json) <= max_exact_json_chars else None

    metrics = tuple(
        dict.fromkeys(
            item.candidate_id
            for item in semantic_refs
            if item.target_kind in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        )
    )
    dimensions = tuple(
        dict.fromkeys(
            item.candidate_id
            for item in semantic_refs
            if item.target_kind == SemanticTargetKind.DIMENSION
        )
    )
    entities = tuple(
        dict.fromkeys(
            item.candidate_id
            for item in semantic_refs
            if item.target_kind == SemanticTargetKind.ENTITY_VALUE
        )
    )

    receipt_ref: str | None = None
    result_hash: str | None = None
    if receipt is not None:
        if receipt.receipt_id not in set(evidence.query_receipt_refs):
            raise ValueError("receipt is not referenced by canonical Evidence")
        receipt_ref = receipt.receipt_id
        result_hash = receipt.result_hash

    return EvidenceDigest(
        evidence_id=evidence.artifact_id,
        scope_version_id=scope_version_id,
        state=evidence.state.value,
        metric_ids=metrics,
        dimension_ids=dimensions,
        entity_ids=entities,
        exact_material_json=exact,
        payload_hash=payload_hash,
        hypothesis_relations=tuple(dict.fromkeys(hypothesis_relations)),
        receipt_ref=receipt_ref,
        result_hash=result_hash,
    )


class IntakeView(Frozen):
    new_user_message: str = Field(min_length=1, max_length=16000)
    current_scope_version_id: str | None = Field(
        default=None, pattern=r"^scope_v[1-9][0-9]*$"
    )
    relevant_semantic_ids: tuple[str, ...] = ()
    prior_intent_delta_ref: str | None = None


class HypothesisView(Frozen):
    hypothesis_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    supporting_evidence_refs: tuple[str, ...] = ()
    challenging_evidence_refs: tuple[str, ...] = ()
    contextual_evidence_refs: tuple[str, ...] = ()


class P19View(Frozen):
    objective: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    candidate_hypotheses: tuple[HypothesisView, ...] = ()
    evidence: tuple[EvidenceDigest, ...] = ()
    unresolved_discrimination: tuple[str, ...] = ()
    legal_actions: tuple[str, ...] = ()


class P17NextTestView(Frozen):
    objective: str = Field(min_length=1)
    unresolved_gap: str = Field(min_length=1)
    candidate_hypotheses: tuple[HypothesisView, ...] = ()
    evidence: tuple[EvidenceDigest, ...] = ()
    legal_analytical_actions: tuple[str, ...] = ()
    remaining_depth: int = Field(ge=0)
    remaining_provider_budget: int = Field(ge=0)


class ReportView(Frozen):
    accepted_observations: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    epistemic_state_ref: str = Field(min_length=1)
    evidence: tuple[EvidenceDigest, ...] = ()
    limitations: tuple[str, ...] = ()
    decision_implications: tuple[str, ...] = ()
