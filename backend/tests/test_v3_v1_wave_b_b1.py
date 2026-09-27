from __future__ import annotations

from datetime import datetime, timezone

from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    CandidateAssessment,
    CausalQualification,
    ContributionClass,
    EvidenceStrength,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
    HypothesisEpistemicClass,
    HypothesisSnapshot,
    IdentificationLimitation,
    P19CaseSnapshot,
    P19GroundingLink,
    P19Hypothesis,
    RootCauseAssessmentView,
)
from app.v3.hypothesis_root_cause_v1 import (
    AlternativeExplanationState,
    NextTestEvidenceSurface,
    TemporalConsistencyState,
    discriminating_test_is_callable,
    next_test_request,
    project_candidate_factors,
)
from app.v3.research_manager import (
    InvestigationActionProfile,
    InvestigationActionRule,
    InvestigationBranchBehavior,
    InvestigationBranchKeyPolicy,
    InvestigationGainRequirement,
    InvestigationGraph,
    InvestigationIntent,
    InvestigationNodeView,
    InvestigationTargetKind,
    ParentObligationView,
    ReasoningStepStatus,
    ResearchManagerSnapshot,
)


NOW = datetime(2026, 9, 27, 19, 30, tzinfo=timezone.utc)


def hypothesis(index):
    return P19Hypothesis(
        hypothesis_id="p19h_" + f"{index:024x}",
        research_session_id="rs_" + "1" * 24,
        obligation_id="g_root",
        tenant_binding="id:tenant-a",
        semantic_context_version="ctx-wave-b",
        statement=f"candidate {index}",
        identity_fingerprint=f"{index:064x}",
        created_at=NOW,
    )


def grounding(index, hypothesis_id, *, relation):
    return P19GroundingLink(
        grounding_link_id="p19g_" + f"{index:024x}",
        hypothesis_id=hypothesis_id,
        source_kind=GroundingSourceKind.P14_EVIDENCE,
        source_ref="evi_" + f"{index:024x}",
        source_receipt_id="dqr_" + f"{index:024x}",
        relation=relation,
        link_fingerprint=f"{index + 100:064x}",
        created_at=NOW,
    )


def case_and_assessment():
    a = hypothesis(1)
    b = hypothesis(2)
    ga = grounding(1, a.hypothesis_id, relation=GroundingRelation.SUPPORTS)
    gb = grounding(2, b.hypothesis_id, relation=GroundingRelation.SUPPORTS)
    snapshot = P19CaseSnapshot(
        research_session_id=a.research_session_id,
        obligation_id="g_root",
        tenant_binding="id:tenant-a",
        semantic_context_version="ctx-wave-b",
        hypotheses=(
            HypothesisSnapshot(hypothesis=a, groundings=(ga,)),
            HypothesisSnapshot(hypothesis=b, groundings=(gb,)),
        ),
    )
    candidates = (
        CandidateAssessment(
            hypothesis_id=a.hypothesis_id,
            grounding_link_ids=(ga.grounding_link_id,),
            disposition=HypothesisDisposition.RETAINED,
            epistemic_class=HypothesisEpistemicClass.COMPETING_HYPOTHESIS,
            contribution_class=ContributionClass.MATERIAL,
            evidence_strength=EvidenceStrength.MODERATE,
            causal_qualification=CausalQualification.IDENTIFICATION_LIMITED,
            identification_limitations=(
                IdentificationLimitation.TEMPORAL_ORDER_UNESTABLISHED,
            ),
        ),
        CandidateAssessment(
            hypothesis_id=b.hypothesis_id,
            grounding_link_ids=(gb.grounding_link_id,),
            disposition=HypothesisDisposition.RETAINED,
            epistemic_class=HypothesisEpistemicClass.COMPETING_HYPOTHESIS,
            contribution_class=ContributionClass.MATERIAL,
            evidence_strength=EvidenceStrength.MODERATE,
            causal_qualification=CausalQualification.NOT_CLAIMED,
        ),
    )
    assessment = RootCauseAssessmentView(
        assessment_id="p19a_" + "9" * 24,
        research_session_id=a.research_session_id,
        obligation_id="g_root",
        tenant_binding="id:tenant-a",
        semantic_context_version="ctx-wave-b",
        candidates=candidates,
        root_cause_hypothesis_ids=(),
        aggregate_outcome=AggregateOutcome.IN_PROGRESS,
        limitations=("competing explanations remain",),
        mediation_annotations=(),
        assessment_fingerprint="f" * 64,
        created_at=NOW,
    )
    return snapshot, assessment


def research_snapshot(*, consumed_target=None, max_depth=2, followups=1):
    root = InvestigationNodeView(
        step_id="rrs_" + "1" * 24,
        parent_step_id=None,
        root_obligation_id="g_root",
        depth=0,
        branch_id="ibr_root",
        intent=InvestigationIntent.INVESTIGATE_GAP,
        target_kind=InvestigationTargetKind.GAP,
        target_ref=None,
        objective_key="root",
        bounded_objective="root",
        status=ReasoningStepStatus.COMPLETED,
    )
    alt = InvestigationNodeView(
        step_id="rrs_" + "2" * 24,
        parent_step_id=root.step_id,
        root_obligation_id="g_root",
        depth=1,
        branch_id="ibr_alt",
        intent=InvestigationIntent.EXPLORE_ALTERNATIVES,
        target_kind=InvestigationTargetKind.ALTERNATIVE,
        target_ref="candidate",
        objective_key="alt",
        bounded_objective="alt",
        status=ReasoningStepStatus.COMPLETED,
    )
    nodes = [root, alt]
    if consumed_target is not None:
        nodes.append(
            InvestigationNodeView(
                step_id="rrs_" + "3" * 24,
                parent_step_id=alt.step_id,
                root_obligation_id="g_root",
                depth=2,
                branch_id="ibr_alt",
                intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
                target_kind=InvestigationTargetKind.EXPLANATION,
                target_ref=consumed_target,
                objective_key="test",
                bounded_objective="test",
                status=ReasoningStepStatus.COMPLETED,
            )
        )
    profile = InvestigationActionProfile(
        rules=(
            InvestigationActionRule(
                intent=InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
                legal_parent_step_ids=(alt.step_id,),
                allow_parentless=False,
                branch_behavior=InvestigationBranchBehavior.INHERIT_BRANCH,
                branch_key_policy=InvestigationBranchKeyPolicy.FORBIDDEN,
                depth_delta=1,
                gain_requirement=InvestigationGainRequirement.POSITIVE_EXPECTED_GAIN,
            ),
        ),
        max_depth=3,
    )
    return ResearchManagerSnapshot(
        research_session_id="rs_" + "1" * 24,
        research_authority_id="atc_wave_b",
        source_revision=3,
        objective="root cause",
        parent_obligations=(
            ParentObligationView(
                obligation_id="g_root",
                objective="root cause",
                state="VERIFIED",
            ),
        ),
        evidence_refs=("evi_" + "1" * 24, "evi_" + "2" * 24),
        material_refs=(),
        materials=(),
        action_profile=profile,
        claims=(),
        investigation=InvestigationGraph(
            nodes=tuple(nodes),
            root_step_ids=(root.step_id,),
            open_branch_ids=("ibr_root", "ibr_alt"),
            stopped_branch_ids=(),
            max_observed_depth=max_depth - 1,
        ),
        limitation_refs=(),
        completed_reasoning_steps=tuple(node.step_id for node in nodes),
        pending_reasoning_steps=(),
        remaining_reasoning_steps=4,
        remaining_followup_native_turns=followups,
        remaining_counter_evidence_attempts=1,
    )


def test_p7_multifactor_projection_exposes_evidence_temporal_alternative_materiality():
    snapshot, assessment = case_and_assessment()
    factors = project_candidate_factors(
        snapshot=snapshot,
        assessment=assessment,
        scope_lineage_id="atl_wave_b",
        scope_version_id="scope_v2",
    )
    assert len(factors) == 2
    assert factors[0].scope_lineage_id == "atl_wave_b"
    assert factors[0].scope_version_id == "scope_v2"
    assert factors[0].supporting_evidence_refs == ("evi_" + "1" * 24,)
    assert factors[0].challenging_evidence_refs == ()
    assert factors[0].missing_evidence is False
    assert factors[0].temporal_consistency == TemporalConsistencyState.UNESTABLISHED
    assert (
        factors[0].alternative_explanation_state
        == AlternativeExplanationState.COMPETING_PRESENT
    )
    assert factors[0].materiality == ContributionClass.MATERIAL


def test_p8_next_test_request_is_typed_and_contains_no_query_plan():
    snapshot, assessment = case_and_assessment()
    request = next_test_request(
        snapshot=snapshot,
        assessment=assessment,
        scope_lineage_id="atl_wave_b",
        scope_version_id="scope_v2",
    )
    assert request is not None
    assert request.required_evidence_surface == NextTestEvidenceSurface.TEMPORAL_ORDER
    assert len(request.hypothesis_ids) == 2
    payload = request.model_dump()
    assert "sql" not in str(payload).lower()
    assert "mbql" not in str(payload).lower()
    assert "query" not in payload


def test_p8_deepen_requires_available_surface_and_unconsumed_test_and_depth_room():
    p19, assessment = case_and_assessment()
    request = next_test_request(
        snapshot=p19,
        assessment=assessment,
        scope_lineage_id="atl_wave_b",
        scope_version_id="scope_v2",
    )
    assert request is not None
    assert discriminating_test_is_callable(
        snapshot=research_snapshot(),
        request=request,
        evidence_surface_available=True,
    )
    assert not discriminating_test_is_callable(
        snapshot=research_snapshot(),
        request=request,
        evidence_surface_available=False,
    )
    assert not discriminating_test_is_callable(
        snapshot=research_snapshot(consumed_target=request.request_id, max_depth=3),
        request=request,
        evidence_surface_available=True,
    )
    assert not discriminating_test_is_callable(
        snapshot=research_snapshot(followups=0),
        request=request,
        evidence_surface_available=True,
    )


def test_p8_terminal_p19_outcome_emits_no_next_test():
    snapshot, assessment = case_and_assessment()
    terminal = assessment.model_copy(
        update={
            "aggregate_outcome": AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
        }
    )
    assert next_test_request(
        snapshot=snapshot,
        assessment=terminal,
        scope_lineage_id="atl_wave_b",
        scope_version_id="scope_v2",
    ) is None



def test_b1_projection_has_no_lexical_or_analytical_shadow_authority():
    import inspect
    import app.v3.hypothesis_root_cause_v1 as p19v1
    import app.v3.product.process_manager as process_manager

    source = (
        inspect.getsource(p19v1)
        + "\n"
        + inspect.getsource(process_manager)
    ).lower()
    forbidden = (
        "levenshtein(",
        "fuzz.ratio(",
        "embedding_threshold",
        "sqlparse",
        "parse_mbql",
        "query_optimizer",
        "causal_score =",
        "causal_probability =",
    )
    assert not any(token in source for token in forbidden)
