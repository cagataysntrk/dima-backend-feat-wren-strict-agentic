"""Dima V1 P19 factor visibility and discriminating-test contract.

This module is a typed projection over the sealed P19 durable owner. It creates
no hypothesis, Evidence, causal truth, SQL/MBQL, score or durable graph.
"""
from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    CausalQualification,
    ContributionClass,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
    IdentificationLimitation,
    P19CaseSnapshot,
    RootCauseAssessmentView,
)
from app.v3.research_manager import (
    InvestigationIntent,
    ResearchManagerSnapshot,
    project_discriminating_test_reentry_rule,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class TemporalConsistencyState(StrEnum):
    ESTABLISHED = "ESTABLISHED"
    UNESTABLISHED = "UNESTABLISHED"
    UNKNOWN = "UNKNOWN"


class AlternativeExplanationState(StrEnum):
    COMPETING_PRESENT = "COMPETING_PRESENT"
    NO_COMPETING_RETAINED = "NO_COMPETING_RETAINED"


class NextTestEvidenceSurface(StrEnum):
    GOVERNED_EVIDENCE = "GOVERNED_EVIDENCE"
    TEMPORAL_ORDER = "TEMPORAL_ORDER"
    COUNTER_EVIDENCE = "COUNTER_EVIDENCE"
    MECHANISM_DISCRIMINATION = "MECHANISM_DISCRIMINATION"


class ExpectedDiscriminatoryValue(StrEnum):
    POSITIVE_MATERIAL = "POSITIVE_MATERIAL"


class P19CandidateFactorView(Frozen):
    hypothesis_id: str
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    supporting_evidence_refs: tuple[str, ...] = ()
    challenging_evidence_refs: tuple[str, ...] = ()
    contextual_evidence_refs: tuple[str, ...] = ()
    missing_evidence: bool
    temporal_consistency: TemporalConsistencyState
    alternative_explanation_state: AlternativeExplanationState
    materiality: ContributionClass
    disposition: HypothesisDisposition
    causal_qualification: CausalQualification


class NextTestRequest(Frozen):
    request_id: str = Field(pattern=r"^ntr_[a-f0-9]{24}$")
    ambiguity_code: str = Field(min_length=1)
    hypothesis_ids: tuple[str, ...] = Field(min_length=2)
    required_evidence_surface: NextTestEvidenceSurface
    expected_discriminatory_value: ExpectedDiscriminatoryValue
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")

    def bounded_objective(self) -> str:
        return (
            "Discriminate the governed competing hypotheses using the required "
            f"{self.required_evidence_surface.value} Evidence surface."
        )


def _stable_id(value: dict) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return "ntr_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def project_candidate_factors(
    *,
    snapshot: P19CaseSnapshot,
    assessment: RootCauseAssessmentView,
    scope_lineage_id: str,
    scope_version_id: str,
) -> tuple[P19CandidateFactorView, ...]:
    by_hypothesis = {item.hypothesis.hypothesis_id: item for item in snapshot.hypotheses}
    viable = {
        item.hypothesis_id
        for item in assessment.candidates
        if item.disposition != HypothesisDisposition.REJECTED
    }
    alternative_state = (
        AlternativeExplanationState.COMPETING_PRESENT
        if len(viable) >= 2
        else AlternativeExplanationState.NO_COMPETING_RETAINED
    )
    out = []
    for candidate in assessment.candidates:
        item = by_hypothesis[candidate.hypothesis_id]
        evidence_links = tuple(
            link for link in item.groundings
            if link.source_kind == GroundingSourceKind.P14_EVIDENCE
        )
        support = tuple(
            link.source_ref for link in evidence_links
            if link.relation == GroundingRelation.SUPPORTS
        )
        challenge = tuple(
            link.source_ref for link in evidence_links
            if link.relation == GroundingRelation.CHALLENGES
        )
        context = tuple(
            link.source_ref for link in evidence_links
            if link.relation == GroundingRelation.CONTEXT
        )
        if (
            IdentificationLimitation.TEMPORAL_ORDER_UNESTABLISHED
            in candidate.identification_limitations
        ):
            temporal = TemporalConsistencyState.UNESTABLISHED
        elif candidate.causal_identification_refs:
            temporal = TemporalConsistencyState.ESTABLISHED
        else:
            temporal = TemporalConsistencyState.UNKNOWN
        out.append(
            P19CandidateFactorView(
                hypothesis_id=candidate.hypothesis_id,
                scope_lineage_id=scope_lineage_id,
                scope_version_id=scope_version_id,
                supporting_evidence_refs=tuple(dict.fromkeys(support)),
                challenging_evidence_refs=tuple(dict.fromkeys(challenge)),
                contextual_evidence_refs=tuple(dict.fromkeys(context)),
                missing_evidence=not bool(evidence_links),
                temporal_consistency=temporal,
                alternative_explanation_state=alternative_state,
                materiality=candidate.contribution_class,
                disposition=candidate.disposition,
                causal_qualification=candidate.causal_qualification,
            )
        )
    return tuple(out)


def next_test_request(
    *,
    snapshot: P19CaseSnapshot,
    assessment: RootCauseAssessmentView,
    scope_lineage_id: str,
    scope_version_id: str,
) -> NextTestRequest | None:
    if assessment.aggregate_outcome != AggregateOutcome.IN_PROGRESS:
        return None
    viable = tuple(
        item for item in assessment.candidates
        if item.disposition != HypothesisDisposition.REJECTED
    )
    if len(viable) < 2:
        return None
    factors = project_candidate_factors(
        snapshot=snapshot,
        assessment=assessment,
        scope_lineage_id=scope_lineage_id,
        scope_version_id=scope_version_id,
    )
    selected = tuple(
        item.hypothesis_id for item in factors
        if item.hypothesis_id in {x.hypothesis_id for x in viable}
    )
    if any(item.missing_evidence for item in factors):
        surface = NextTestEvidenceSurface.GOVERNED_EVIDENCE
        ambiguity = "MISSING_GOVERNED_EVIDENCE"
    elif any(
        item.temporal_consistency != TemporalConsistencyState.ESTABLISHED
        for item in factors
    ):
        surface = NextTestEvidenceSurface.TEMPORAL_ORDER
        ambiguity = "TEMPORAL_DISCRIMINATION_REQUIRED"
    elif not any(item.challenging_evidence_refs for item in factors):
        surface = NextTestEvidenceSurface.COUNTER_EVIDENCE
        ambiguity = "COUNTER_EVIDENCE_REQUIRED"
    else:
        surface = NextTestEvidenceSurface.MECHANISM_DISCRIMINATION
        ambiguity = "MECHANISM_AMBIGUITY_REMAINS"
    identity = {
        "session": snapshot.research_session_id,
        "obligation": snapshot.obligation_id,
        "scope_lineage": scope_lineage_id,
        "scope_version": scope_version_id,
        "hypotheses": sorted(selected),
        "surface": surface.value,
        "ambiguity": ambiguity,
    }
    return NextTestRequest(
        request_id=_stable_id(identity),
        ambiguity_code=ambiguity,
        hypothesis_ids=selected,
        required_evidence_surface=surface,
        expected_discriminatory_value=ExpectedDiscriminatoryValue.POSITIVE_MATERIAL,
        scope_lineage_id=scope_lineage_id,
        scope_version_id=scope_version_id,
    )


def discriminating_test_capacity_available(
    *,
    snapshot: ResearchManagerSnapshot,
    evidence_surface_available: bool,
    target_obligation_id: str | None = None,
) -> bool:
    """Whether one legal/material discriminating P17 move can still be opened.

    This is a deterministic capability check, not an epistemic decision. P19
    still decides whether the current ambiguity warrants using that capacity.
    """

    if not evidence_surface_available:
        return False
    if target_obligation_id is None:
        return False
    return (
        project_discriminating_test_reentry_rule(
            snapshot=snapshot,
            obligation_id=target_obligation_id,
        )
        is not None
    )


def discriminating_test_is_callable(
    *,
    snapshot: ResearchManagerSnapshot,
    request: NextTestRequest,
    evidence_surface_available: bool,
    target_obligation_id: str | None = None,
) -> bool:
    if not discriminating_test_capacity_available(
        snapshot=snapshot,
        evidence_surface_available=evidence_surface_available,
        target_obligation_id=target_obligation_id,
    ):
        return False
    if any(
        node.target_ref == request.request_id
        for node in snapshot.investigation.nodes
    ):
        return False
    return True
