"""Deterministic discovery candidate-vocabulary projection for Brain V2.

This module does not discover mechanisms and does not own hypothesis semantics.
It projects the remaining governed mechanism vocabulary from durable P17 claim
state so repeated discovery turns cannot re-offer an already admitted candidate.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.v3.root_cause_candidate_contract import (
    decode_root_cause_candidate_semantics,
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
