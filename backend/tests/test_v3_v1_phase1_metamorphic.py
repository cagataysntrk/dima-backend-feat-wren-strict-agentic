from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from app.v3.business_relationship_policy import (
    RelationshipPolicyDecision,
    RelationshipPolicyResolutionStatus,
)
from app.v3.business_relationship_v1 import (
    RelationshipLayerState,
    project_relationship_result,
)
from app.v3.hypothesis_root_cause import (
    CausalQualification,
    ContributionClass,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
)
from app.v3.hypothesis_root_cause_v1 import (
    ExpectedDiscriminatoryValue,
    NextTestEvidenceSurface,
    NextTestRequest,
    discriminating_test_is_callable,
    project_candidate_factors,
)
from app.v3.product.execution_mode import (
    ProductExecutionMode,
    classify_execution_mode,
)
from app.v3.product.process_manager import (
    P19EligibilityDecision,
    ProductProcessObservation,
    RootCauseCandidate,
    p19_eligibility,
)
from app.v3.root_cause_candidate_contract import (
    RootCauseCandidateRelation,
    RootCauseCandidateSemantics,
)
from app.v3.research_contracts import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ScopeMutation,
    ScopeMutationKind,
    SemanticTargetKind,
    apply_scope_mutation,
)
from app.v3.research_manager import InvestigationIntent


MANIFEST = Path("eval/v1/phase1_metamorphic_manifest.json")


def _candidate(claim_id: str, mechanism: str, evidence: str) -> RootCauseCandidate:
    return RootCauseCandidate(
        claim_id=claim_id,
        semantics=RootCauseCandidateSemantics(
            explanatory_subject_ref="g_root",
            relation_kind=RootCauseCandidateRelation.EXPLANATORY_CANDIDATE,
            mechanism_ref=mechanism,
            scope_lineage_id="atl_meta",
            scope_version_id="scope_v2",
        ),
        evidence_refs=(evidence,),
    )


def _p6_observation(candidates, *, claims=("c1", "c2")):
    return ProductProcessObservation(
        claim_ids=tuple(claims),
        remaining_reasoning_steps=3,
        scoped_move_available=True,
        root_cause_candidates=tuple(candidates),
    )


def _semantic(cid: str, kind: SemanticTargetKind, name: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=kind,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


M1 = _semantic("metric.downtime", SemanticTargetKind.METRIC, "Downtime")
M2 = _semantic("metric.faults", SemanticTargetKind.METRIC, "Faults")
D1 = _semantic("dimension.department", SemanticTargetKind.DIMENSION, "Department")
E1 = ResearchSemanticRef(
    source_mention="Assembly",
    candidate_id="entity.department.assembly",
    target_kind=SemanticTargetKind.ENTITY_VALUE,
    canonical_name="Assembly",
    dimension_name="department",
    value="Assembly",
    cube_names=("machine_operations",),
)
E2 = ResearchSemanticRef(
    source_mention="Packaging",
    candidate_id="entity.department.packaging",
    target_kind=SemanticTargetKind.ENTITY_VALUE,
    canonical_name="Packaging",
    dimension_name="department",
    value="Packaging",
    cube_names=("machine_operations",),
)


def _brief(*, source_text="Show downtime", metrics=(M1,), kind=ResearchGoalKind.BREAKDOWN):
    refs = (*metrics, D1)
    question = ResearchQuestion(
        goal_id="g1",
        kind=kind,
        source_text=source_text,
        subject_refs=tuple(metrics),
        related_refs=(D1,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-meta",
        objective="metamorphic routing",
        scope=ResearchScope(semantic_refs=refs),
        questions=(question,),
        must_requirement_ids=("g1",),
        context_version="ctx-meta",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _next_test_request() -> NextTestRequest:
    return NextTestRequest(
        request_id="ntr_" + "a" * 24,
        ambiguity_code="COUNTER_EVIDENCE_REQUIRED",
        hypothesis_ids=("p19h_" + "1" * 24, "p19h_" + "2" * 24),
        required_evidence_surface=NextTestEvidenceSurface.COUNTER_EVIDENCE,
        expected_discriminatory_value=ExpectedDiscriminatoryValue.POSITIVE_MATERIAL,
        scope_lineage_id="atl_meta",
        scope_version_id="scope_v2",
    )


class _Profile:
    max_depth = 3

    @staticmethod
    def rule_for(intent):
        if intent == InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE:
            return object()
        return None


def _p8_snapshot(*, consumed=False, max_contract_depth=2):
    request = _next_test_request()
    nodes = (
        (SimpleNamespace(target_ref=request.request_id),)
        if consumed
        else (SimpleNamespace(target_ref="other"),)
    )
    return SimpleNamespace(
        remaining_followup_native_turns=1,
        action_profile=_Profile(),
        investigation=SimpleNamespace(
            nodes=nodes,
            max_contract_depth=max_contract_depth,
        ),
    )


def _p19_projection(*, challenge: bool):
    h1 = "p19h_" + "1" * 24
    h2 = "p19h_" + "2" * 24
    links1 = [
        SimpleNamespace(
            source_kind=GroundingSourceKind.P14_EVIDENCE,
            source_ref="evi_" + "1" * 24,
            relation=GroundingRelation.SUPPORTS,
        )
    ]
    if challenge:
        links1.append(
            SimpleNamespace(
                source_kind=GroundingSourceKind.P14_EVIDENCE,
                source_ref="evi_" + "3" * 24,
                relation=GroundingRelation.CHALLENGES,
            )
        )
    snapshot = SimpleNamespace(
        hypotheses=(
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h1),
                groundings=tuple(links1),
            ),
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h2),
                groundings=(
                    SimpleNamespace(
                        source_kind=GroundingSourceKind.P14_EVIDENCE,
                        source_ref="evi_" + "2" * 24,
                        relation=GroundingRelation.SUPPORTS,
                    ),
                ),
            ),
        )
    )
    candidates = tuple(
        SimpleNamespace(
            hypothesis_id=hypothesis_id,
            disposition=HypothesisDisposition.RETAINED,
            contribution_class=ContributionClass.MATERIAL,
            causal_qualification=CausalQualification.NOT_CLAIMED,
            identification_limitations=(),
            causal_identification_refs=(),
        )
        for hypothesis_id in (h1, h2)
    )
    return project_candidate_factors(
        snapshot=snapshot,
        assessment=SimpleNamespace(candidates=candidates),
        scope_lineage_id="atl_meta",
        scope_version_id="scope_v2",
    )


def _relationship_projection(*, challenge: bool):
    links = [
        SimpleNamespace(
            evidence_id="evi_" + "1" * 24,
            relation="SUPPORTS",
        )
    ]
    if challenge:
        links.append(
            SimpleNamespace(
                evidence_id="evi_" + "2" * 24,
                relation="CHALLENGES",
            )
        )
    claim = SimpleNamespace(
        claim_id="clm_" + "1" * 24,
        obligation_id="g1",
        proposition={"relationship_kind": "ASSOCIATION"},
        epistemic_state=SimpleNamespace(value="SUPPORTED"),
        limitations=("ASSOCIATION_ONLY",),
        evidence_links=tuple(links),
    )
    decision = RelationshipPolicyDecision(
        required=True,
        eligible=True,
        resolution_status=RelationshipPolicyResolutionStatus.SATISFIED,
        policy_use_id="bru_" + "1" * 24,
        policy_id="brp_" + "1" * 24,
        limitation_code=None,
    )
    return project_relationship_result(
        research_session_id="rs_" + "1" * 24,
        claim=claim,
        decision=decision,
        scope_lineage_id="atl_meta",
        scope_version_id="scope_v2",
        applicability_scope={"department": ["Assembly"]},
    )


def test_manifest_is_eval_only_and_covers_all_declared_mutations():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "dima-v1-phase1-metamorphic-v1"
    assert manifest["authority"] == "EVAL_ONLY"
    assert len(manifest["cases"]) == 12
    assert len({item["id"] for item in manifest["cases"]}) == 12
    assert {item["family"] for item in manifest["cases"]} >= {
        "P6", "P7_P9", "P8", "P11", "P2", "P10", "P0"
    }


def test_p6_paraphrase_and_candidate_permutation_do_not_change_typed_eligibility():
    candidates = (
        _candidate("c1", "fault-pressure", "e1"),
        _candidate("c2", "maintenance-delay", "e2"),
    )
    a = _p6_observation(candidates)
    b = _p6_observation(tuple(reversed(candidates)))
    # Claim prose is deliberately absent from ProductProcessObservation.
    assert p19_eligibility(a) == P19EligibilityDecision.CALL_P19
    assert p19_eligibility(b) == P19EligibilityDecision.CALL_P19


def test_p6_missing_evidence_or_duplicate_mechanism_cannot_fake_distinct_candidates():
    missing = _p6_observation(
        (_candidate("c1", "fault-pressure", "e1"),),
        claims=("c1", "c2"),
    )
    duplicate = _p6_observation(
        (
            _candidate("c1", "same-mechanism", "e1"),
            _candidate("c2", "same-mechanism", "e2"),
        )
    )
    assert p19_eligibility(missing) == P19EligibilityDecision.NEED_MORE_EVIDENCE
    assert p19_eligibility(duplicate) == P19EligibilityDecision.NEED_MORE_EVIDENCE


def test_p7_challenge_mutation_is_visible_without_causal_promotion():
    before = _p19_projection(challenge=False)[0]
    after = _p19_projection(challenge=True)[0]
    assert before.challenging_evidence_refs == ()
    assert after.challenging_evidence_refs == ("evi_" + "3" * 24,)
    assert before.causal_qualification == after.causal_qualification == CausalQualification.NOT_CLAIMED


def test_p9_challenge_mutation_is_visible_without_contribution_or_causality():
    before = _relationship_projection(challenge=False)
    after = _relationship_projection(challenge=True)
    assert before.challenging_evidence_refs == ()
    assert after.challenging_evidence_refs == ("evi_" + "2" * 24,)
    assert after.causality_state == RelationshipLayerState.NOT_ESTABLISHED
    assert after.contribution_state == RelationshipLayerState.NOT_ESTABLISHED


def test_p8_same_next_test_request_is_one_shot_and_depth_three_is_hard_stop():
    request = _next_test_request()
    assert discriminating_test_is_callable(
        snapshot=_p8_snapshot(),
        request=request,
        evidence_surface_available=True,
    )
    assert not discriminating_test_is_callable(
        snapshot=_p8_snapshot(consumed=True),
        request=request,
        evidence_surface_available=True,
    )
    assert not discriminating_test_is_callable(
        snapshot=_p8_snapshot(max_contract_depth=3),
        request=request,
        evidence_surface_available=True,
    )


def test_p11_paraphrase_does_not_change_mode_but_second_typed_metric_does():
    original = _brief(source_text="Show downtime")
    paraphrase = _brief(source_text="Duruş süresini bölüm bazında getir.")
    multi = _brief(
        source_text="Show downtime and faults",
        metrics=(M1, M2),
        kind=ResearchGoalKind.COMPARISON,
    )
    assert classify_execution_mode(original).mode == ProductExecutionMode.FAST
    assert classify_execution_mode(paraphrase).mode == ProductExecutionMode.FAST
    assert classify_execution_mode(multi).mode == ProductExecutionMode.GUIDED


def test_p2_entity_narrowing_advances_exact_scope_version_and_parent():
    current = ResearchScope(
        semantic_refs=(M1, D1, E1, E2),
        time_surfaces=("2026-05", "2026-06"),
    )
    mutation = ScopeMutation(
        kind=ScopeMutationKind.NARROW_ENTITY,
        source_version_id="scope_v1",
        target_semantic_refs=(M1, D1, E1),
        target_time_surfaces=("2026-05", "2026-06"),
        reason="Narrow to Assembly.",
    )
    contract = apply_scope_mutation(current, mutation)
    assert contract.previous_scope.scope_version.version_id == "scope_v1"
    assert contract.current_scope.scope_version.version_id == "scope_v2"
    assert contract.current_scope.scope_version.parent_version_id == "scope_v1"
    assert {x.candidate_id for x in contract.current_scope.semantic_refs} == {
        M1.candidate_id, D1.candidate_id, E1.candidate_id
    }
