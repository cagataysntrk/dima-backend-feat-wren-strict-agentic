"""Dima V1 P18 relationship-result projection.

This module exposes a typed, non-durable view over governed P16 claim/Evidence
lineage plus the sealed P18 policy-use decision. It performs no analytics, join
discovery, correlation calculation, causal identification or persistence.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.business_relationship_policy import (
    RelationshipPolicyDecision,
    RelationshipPolicyResolutionStatus,
)
from app.v3.claim_lineage import ClaimEpistemicState


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RelationshipAnalyticalKind(StrEnum):
    ASSOCIATION = "ASSOCIATION"
    CO_MOVEMENT = "CO_MOVEMENT"


class RelationshipLayerState(StrEnum):
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    SUPPORTED = "SUPPORTED"
    CHALLENGED = "CHALLENGED"
    CONTESTED = "CONTESTED"
    INSUFFICIENT = "INSUFFICIENT"
    SATISFIED = "SATISFIED"
    BLOCKED = "BLOCKED"


class RelationshipResultProjection(Frozen):
    research_session_id: str = Field(pattern=r"^rs_[a-f0-9]{24}$")
    obligation_id: str = Field(min_length=1)
    claim_id: str = Field(pattern=r"^clm_[a-f0-9]{24}$")
    policy_use_id: str = Field(pattern=r"^bru_[a-f0-9]{24}$")
    policy_id: str | None = Field(default=None, pattern=r"^brp_[a-f0-9]{24}$")
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    applicability_scope: dict[str, Any]
    analytical_kind: RelationshipAnalyticalKind | None = None
    association_state: RelationshipLayerState
    co_movement_state: RelationshipLayerState
    business_relationship_state: RelationshipLayerState
    policy_required: bool = True
    contribution_state: RelationshipLayerState = RelationshipLayerState.NOT_ESTABLISHED
    causality_state: RelationshipLayerState = RelationshipLayerState.NOT_ESTABLISHED
    supporting_evidence_refs: tuple[str, ...] = ()
    challenging_evidence_refs: tuple[str, ...] = ()
    contextual_evidence_refs: tuple[str, ...] = ()
    insufficient_evidence_refs: tuple[str, ...] = ()
    limitation_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def p9_cannot_promote_causality_or_contribution(self):
        if self.contribution_state != RelationshipLayerState.NOT_ESTABLISHED:
            raise ValueError("P9 contribution requires governed P19 authority")
        if self.causality_state != RelationshipLayerState.NOT_ESTABLISHED:
            raise ValueError("P9 causality requires governed P19 authority")
        if not self.applicability_scope:
            raise ValueError("P9 relationship projection requires exact scope")
        return self


def _value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _claim_layer_state(claim) -> RelationshipLayerState:
    state = _value(claim.epistemic_state)
    mapping = {
        ClaimEpistemicState.PROPOSED.value: RelationshipLayerState.NOT_ESTABLISHED,
        ClaimEpistemicState.SUPPORTED.value: RelationshipLayerState.SUPPORTED,
        ClaimEpistemicState.CHALLENGED.value: RelationshipLayerState.CHALLENGED,
        ClaimEpistemicState.CONTESTED.value: RelationshipLayerState.CONTESTED,
        ClaimEpistemicState.INSUFFICIENT_EVIDENCE.value: RelationshipLayerState.INSUFFICIENT,
    }
    try:
        return mapping[state]
    except KeyError as exc:
        raise ValueError(f"P9_UNKNOWN_CLAIM_EPISTEMIC_STATE:{state}") from exc


def _analytical_kind(claim) -> RelationshipAnalyticalKind | None:
    raw = (getattr(claim, "proposition", {}) or {}).get("relationship_kind")
    if raw is None:
        return None
    try:
        return RelationshipAnalyticalKind(str(raw))
    except ValueError as exc:
        raise ValueError(
            "P9_RELATIONSHIP_KIND_REQUIRES_OTHER_GOVERNED_AUTHORITY"
        ) from exc


def project_relationship_result(
    *,
    research_session_id: str,
    claim,
    decision: RelationshipPolicyDecision,
    scope_lineage_id: str,
    scope_version_id: str,
    applicability_scope: dict[str, Any],
) -> RelationshipResultProjection:
    """Project existing authority; never infer a stronger relationship."""

    links = tuple(getattr(claim, "evidence_links", ()) or ())
    by_relation: dict[str, list[str]] = {
        "SUPPORTS": [],
        "CHALLENGES": [],
        "CONTEXTUALIZES": [],
        "INSUFFICIENT": [],
    }
    for link in links:
        relation = _value(link.relation)
        if relation not in by_relation:
            raise ValueError(f"P9_UNKNOWN_EVIDENCE_RELATION:{relation}")
        by_relation[relation].append(link.evidence_id)

    claim_state = _claim_layer_state(claim)
    kind = _analytical_kind(claim)
    co_movement = (
        claim_state
        if kind == RelationshipAnalyticalKind.CO_MOVEMENT
        else RelationshipLayerState.NOT_ESTABLISHED
    )
    if decision.resolution_status == RelationshipPolicyResolutionStatus.SATISFIED:
        business_state = RelationshipLayerState.SATISFIED
    elif (
        not decision.required
        and decision.resolution_status
        == RelationshipPolicyResolutionStatus.NOT_REQUIRED
    ):
        business_state = RelationshipLayerState.NOT_ESTABLISHED
    else:
        business_state = RelationshipLayerState.BLOCKED
    limitations = list(getattr(claim, "limitations", ()) or ())
    if decision.limitation_code:
        limitations.append(decision.limitation_code)

    return RelationshipResultProjection(
        research_session_id=research_session_id,
        obligation_id=claim.obligation_id,
        claim_id=claim.claim_id,
        policy_use_id=decision.policy_use_id,
        policy_id=decision.policy_id,
        scope_lineage_id=scope_lineage_id,
        scope_version_id=scope_version_id,
        applicability_scope=applicability_scope,
        analytical_kind=kind,
        association_state=claim_state,
        co_movement_state=co_movement,
        business_relationship_state=business_state,
        policy_required=bool(getattr(decision, "required", True)),
        supporting_evidence_refs=tuple(dict.fromkeys(by_relation["SUPPORTS"])),
        challenging_evidence_refs=tuple(dict.fromkeys(by_relation["CHALLENGES"])),
        contextual_evidence_refs=tuple(dict.fromkeys(by_relation["CONTEXTUALIZES"])),
        insufficient_evidence_refs=tuple(dict.fromkeys(by_relation["INSUFFICIENT"])),
        limitation_codes=tuple(dict.fromkeys(limitations)),
    )
