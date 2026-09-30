from __future__ import annotations

from types import SimpleNamespace

from app.v3.hypothesis_root_cause import (
    AggregateOutcome,
    CausalQualification,
    ContributionClass,
    GroundingRelation,
    GroundingSourceKind,
    HypothesisDisposition,
)
from app.v3.hypothesis_root_cause_v1 import (
    NextTestEvidenceSurface,
    discriminating_test_is_callable,
    next_test_request,
    project_candidate_factors,
)
from app.v3.product.composition import (
    HeadlessProductComposer,
    RootCauseExecutionMode,
    _root_cause_execution_mode,
)
from app.v3.product.process_manager import (
    P19EligibilityDecision,
    ProductProcessObservation,
    RootCauseCandidate,
    p19_eligibility,
)
from app.v3.research_contracts import (
    CausalCompetitionSurface,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_manager import InvestigationIntent
from app.v3.root_cause_candidate_contract import (
    RootCauseCandidateRelation,
    RootCauseCandidateSemantics,
)


def _ref(cid: str, kind: SemanticTargetKind) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=cid,
        candidate_id=cid,
        target_kind=kind,
        canonical_name=cid,
        cube_names=("generic_operations",),
    )


EFFECT = _ref("metric.effect", SemanticTargetKind.METRIC)
H1 = _ref("metric.candidate_a", SemanticTargetKind.METRIC)
H2 = _ref("metric.candidate_b", SemanticTargetKind.METRIC)
H3 = _ref("metric.candidate_c", SemanticTargetKind.METRIC)
DIM = _ref("dimension.segment", SemanticTargetKind.DIMENSION)


def _candidate(index: int, mechanism: str) -> RootCauseCandidate:
    return RootCauseCandidate(
        claim_id="clm_" + f"{index:024x}",
        semantics=RootCauseCandidateSemantics(
            explanatory_subject_ref="g_root",
            relation_kind=RootCauseCandidateRelation.EXPLANATORY_CANDIDATE,
            mechanism_ref=mechanism,
            scope_lineage_id="atl_rca_modes",
            scope_version_id="scope_v1",
        ),
        evidence_refs=("evi_" + f"{index:024x}",),
    )


def _hypothesis_snapshot(
    *,
    challenge_second: bool = False,
):
    h1 = "p19h_" + "1" * 24
    h2 = "p19h_" + "2" * 24

    def links(index: int, challenge: bool):
        items = [
            SimpleNamespace(
                source_kind=GroundingSourceKind.P14_EVIDENCE,
                source_ref="evi_" + str(index) * 24,
                relation=GroundingRelation.SUPPORTS,
            )
        ]
        if challenge:
            items.append(
                SimpleNamespace(
                    source_kind=GroundingSourceKind.P14_EVIDENCE,
                    source_ref="evi_" + "9" * 24,
                    relation=GroundingRelation.CHALLENGES,
                )
            )
        return tuple(items)

    return SimpleNamespace(
        research_session_id="rs_" + "a" * 24,
        obligation_id="g_root",
        hypotheses=(
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h1),
                groundings=links(1, False),
            ),
            SimpleNamespace(
                hypothesis=SimpleNamespace(hypothesis_id=h2),
                groundings=links(2, challenge_second),
            ),
        ),
    )


def _assessment(
    *,
    aggregate=AggregateOutcome.IN_PROGRESS,
    first_materiality=ContributionClass.UNKNOWN,
    second_materiality=ContributionClass.UNKNOWN,
):
    h1 = "p19h_" + "1" * 24
    h2 = "p19h_" + "2" * 24

    def item(hypothesis_id: str, materiality: ContributionClass):
        return SimpleNamespace(
            hypothesis_id=hypothesis_id,
            disposition=HypothesisDisposition.RETAINED,
            identification_limitations=(),
            causal_identification_refs=(),
            contribution_class=materiality,
            causal_qualification=CausalQualification.NOT_CLAIMED,
        )

    return SimpleNamespace(
        aggregate_outcome=aggregate,
        candidates=(
            item(h1, first_materiality),
            item(h2, second_materiality),
        ),
    )


class _Profile:
    max_depth = 3

    @staticmethod
    def rule_for(intent):
        if intent == InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE:
            return object()
        return None


def _callability_snapshot(*, remaining=1, depth=1, consumed_ref=None):
    nodes = ()
    if consumed_ref is not None:
        nodes = (SimpleNamespace(target_ref=consumed_ref),)
    return SimpleNamespace(
        remaining_followup_native_turns=remaining,
        action_profile=_Profile(),
        investigation=SimpleNamespace(
            nodes=nodes,
            max_contract_depth=depth,
        ),
    )


def _root_goal(*, candidates: tuple[str, ...]) -> ResearchQuestion:
    return ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate governed candidate mechanisms.",
        subject_refs=(EFFECT, H1, H2, H3),
        related_refs=(DIM,),
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id=EFFECT.candidate_id,
            candidate_mechanism_semantic_ids=candidates,
            diagnostic_dimension_ids=(DIM.candidate_id,),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )


def test_mode_case_1_decisive_user_seeded_is_one_pass_without_reentry():
    observation = ProductProcessObservation(
        claim_ids=("c1", "c2"),
        root_cause_candidates=(
            _candidate(1, H1.candidate_id),
            _candidate(2, H2.candidate_id),
        ),
    )
    assert p19_eligibility(observation) == P19EligibilityDecision.CALL_P19
    assert _root_cause_execution_mode(
        aggregate_outcome=AggregateOutcome.ROOT_CAUSE_ESTABLISHED,
        analytical_reentry_count=0,
    ) == RootCauseExecutionMode.ONE_PASS


def test_mode_case_2_ambiguous_user_seeded_requests_one_discriminating_surface():
    snapshot = _hypothesis_snapshot()
    assessment = _assessment()
    request = next_test_request(
        snapshot=snapshot,
        assessment=assessment,
        scope_lineage_id="atl_rca_modes",
        scope_version_id="scope_v1",
    )
    assert request is not None
    assert request.required_evidence_surface == NextTestEvidenceSurface.TEMPORAL_ORDER
    assert discriminating_test_is_callable(
        snapshot=_callability_snapshot(),
        request=request,
        evidence_surface_available=True,
    )
    assert _root_cause_execution_mode(
        aggregate_outcome=AggregateOutcome.IN_PROGRESS,
        analytical_reentry_count=1,
    ) == RootCauseExecutionMode.ADAPTIVE


def test_mode_case_3_evidence_reversal_can_change_candidate_state():
    snapshot = _hypothesis_snapshot(challenge_second=True)
    first = _assessment(
        aggregate=AggregateOutcome.IN_PROGRESS,
        first_materiality=ContributionClass.MATERIAL,
        second_materiality=ContributionClass.LOW,
    )
    second = _assessment(
        aggregate=AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS,
        first_materiality=ContributionClass.LOW,
        second_materiality=ContributionClass.MATERIAL,
    )
    first_view = project_candidate_factors(
        snapshot=snapshot,
        assessment=first,
        scope_lineage_id="atl_rca_modes",
        scope_version_id="scope_v1",
    )
    second_view = project_candidate_factors(
        snapshot=snapshot,
        assessment=second,
        scope_lineage_id="atl_rca_modes",
        scope_version_id="scope_v1",
    )
    assert [item.materiality for item in first_view] == [
        ContributionClass.MATERIAL,
        ContributionClass.LOW,
    ]
    assert [item.materiality for item in second_view] == [
        ContributionClass.LOW,
        ContributionClass.MATERIAL,
    ]
    assert next_test_request(
        snapshot=snapshot,
        assessment=second,
        scope_lineage_id="atl_rca_modes",
        scope_version_id="scope_v1",
    ) is None


def test_mode_case_4_both_weak_is_governed_inconclusive_not_fake_winner():
    snapshot = _hypothesis_snapshot(challenge_second=True)
    assessment = _assessment(
        aggregate=AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED,
        first_materiality=ContributionClass.LOW,
        second_materiality=ContributionClass.LOW,
    )
    assert next_test_request(
        snapshot=snapshot,
        assessment=assessment,
        scope_lineage_id="atl_rca_modes",
        scope_version_id="scope_v1",
    ) is None
    assert _root_cause_execution_mode(
        aggregate_outcome=assessment.aggregate_outcome,
        analytical_reentry_count=0,
    ) == RootCauseExecutionMode.GOVERNED_INCONCLUSIVE


def test_mode_case_5_user_candidates_are_preserved_without_p17_rediscovery():
    refs, user_seeded = HeadlessProductComposer._root_cause_mechanism_refs(
        goal=_root_goal(candidates=(H2.candidate_id, H1.candidate_id)),
        source_session=SimpleNamespace(accepted_brief=None),
    )
    assert user_seeded is True
    assert refs == (H2.candidate_id, H1.candidate_id)


def test_mode_case_6_missing_candidates_keeps_p17_discovery_path_available():
    refs, user_seeded = HeadlessProductComposer._root_cause_mechanism_refs(
        goal=_root_goal(candidates=()),
        source_session=SimpleNamespace(accepted_brief=None),
    )
    assert user_seeded is False
    assert refs == (
        H1.candidate_id,
        H2.candidate_id,
        H3.candidate_id,
    )


def test_mode_case_7_no_useful_discriminating_surface_stops_without_loop_ceremony():
    snapshot = _hypothesis_snapshot()
    assessment = _assessment()
    request = next_test_request(
        snapshot=snapshot,
        assessment=assessment,
        scope_lineage_id="atl_rca_modes",
        scope_version_id="scope_v1",
    )
    assert request is not None
    assert not discriminating_test_is_callable(
        snapshot=_callability_snapshot(),
        request=request,
        evidence_surface_available=False,
    )
    assert _root_cause_execution_mode(
        aggregate_outcome=assessment.aggregate_outcome,
        analytical_reentry_count=0,
    ) == RootCauseExecutionMode.GOVERNED_INCONCLUSIVE


def test_mode_case_8_three_candidates_remain_distinct_without_binary_reduction():
    candidates = (
        _candidate(1, H1.candidate_id),
        _candidate(2, H2.candidate_id),
        _candidate(3, H3.candidate_id),
    )
    observation = ProductProcessObservation(
        claim_ids=("c1", "c2", "c3"),
        root_cause_candidates=candidates,
    )
    assert p19_eligibility(observation) == P19EligibilityDecision.CALL_P19
    assert {
        item.semantics.mechanism_ref
        for item in observation.root_cause_candidates
    } == {
        H1.candidate_id,
        H2.candidate_id,
        H3.candidate_id,
    }
