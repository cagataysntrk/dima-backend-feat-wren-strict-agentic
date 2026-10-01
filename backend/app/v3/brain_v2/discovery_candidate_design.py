"""Deterministic discovery candidate-vocabulary projection for Brain V2.

This module does not discover mechanisms and does not own hypothesis semantics.
It projects the remaining governed mechanism vocabulary from durable P17 claim
state so repeated discovery turns cannot re-offer an already admitted candidate.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.root_cause_candidate_contract import (
    decode_root_cause_candidate_semantics,
)


class CandidateHypothesisIdentity(BaseModel):
    """Identity/provenance only; this record carries no causal belief."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    semantic_id: str = Field(min_length=1)
    source: Literal["OBSERVED_GOVERNED_MATERIAL"] = "OBSERVED_GOVERNED_MATERIAL"
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    material_requirement_ref: str = Field(min_length=1)

    @model_validator(mode="after")
    def evidence_identity_is_canonical(self):
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("candidate Evidence refs must be unique")
        if any(not item.startswith("evi_") for item in self.evidence_refs):
            raise ValueError("candidate Evidence refs must use canonical identity")
        return self


class CandidateSetProjection(BaseModel):
    """Deterministic legal candidate identities for one current ScopeVersion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    candidates: tuple[CandidateHypothesisIdentity, ...] = ()


def project_candidate_set(
    *,
    allowed_discovery_surface: Iterable[str],
    current_scope_semantic_refs: Iterable[str],
    observed_material_semantic_refs: Iterable[str],
    candidate_eligible_semantic_refs: Iterable[str],
    effect_semantic_id: str,
    scope_version_id: str,
    evidence_refs: Iterable[str],
    material_requirement_ref: str,
) -> CandidateSetProjection:
    """Project candidate identity from typed governed authority only.

    This is deliberately set algebra over canonical semantic ids. It performs
    no text inspection, similarity, ranking, probability, or causal inference.
    Candidate order follows the accepted discovery surface so the projection is
    stable across provider wording and result presentation changes.
    """

    allowed = tuple(dict.fromkeys(str(item) for item in allowed_discovery_surface))
    current = set(str(item) for item in current_scope_semantic_refs)
    observed = set(str(item) for item in observed_material_semantic_refs)
    eligible = set(str(item) for item in candidate_eligible_semantic_refs)
    evidence = tuple(dict.fromkeys(str(item) for item in evidence_refs))

    legal = tuple(
        semantic_id
        for semantic_id in allowed
        if (
            semantic_id != effect_semantic_id
            and semantic_id in current
            and semantic_id in observed
            and semantic_id in eligible
        )
    )
    return CandidateSetProjection(
        candidates=tuple(
            CandidateHypothesisIdentity(
                semantic_id=semantic_id,
                scope_version_id=scope_version_id,
                evidence_refs=evidence,
                material_requirement_ref=material_requirement_ref,
            )
            for semantic_id in legal
        )
    )


def remaining_discovery_mechanism_refs(
    *,
    snapshot: Any,
    obligation_id: str,
    scope_lineage_id: str,
    scope_version_id: str,
    governed_mechanism_refs: Iterable[str],
) -> tuple[str, ...]:
    """Return governed refs not already represented by an admissible claim.

    A candidate is consumed only when durable claim state is eligible for the
    same discovery identity accepted by the canonical hypothesis sync:
    exact obligation, exact scope lineage/version, typed root-cause semantics,
    and at least one Evidence link. Historical/foreign/untyped claims do not
    shrink the current legal vocabulary.
    """

    governed = tuple(dict.fromkeys(str(ref) for ref in governed_mechanism_refs))
    consumed: set[str] = set()
    for claim in getattr(snapshot, "claims", ()):
        if getattr(claim, "obligation_id", None) != obligation_id:
            continue
        if not getattr(claim, "evidence_links", ()):
            continue
        semantics = decode_root_cause_candidate_semantics(
            getattr(claim, "proposition", None) or {}
        )
        if semantics is None:
            continue
        if (
            semantics.explanatory_subject_ref != obligation_id
            or semantics.scope_lineage_id != scope_lineage_id
            or semantics.scope_version_id != scope_version_id
        ):
            continue
        consumed.add(semantics.mechanism_ref)

    return tuple(ref for ref in governed if ref not in consumed)
