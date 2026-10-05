from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from app.v3.analytical_boundary import (
    AnalyticalBoundaryError,
    AnalyticalOperation,
    V1_ANALYTICAL_GRAMMAR_VERSION,
    V1GrammarControl,
    V1_LEGAL_COMPOSITIONS,
    assert_v1_analytical_composition,
    legal_v1_next_steps,
    project_analytical_intent_v1,
    validate_v1_research_brief,
)
from app.v3.analytical_request_contract import (
    AnalyticalRequestContract,
    AnalyticalScopeIdentity,
)
from app.v3.research_contracts import (
    PresentationKind,
    RankingSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResultSelectionDependency,
    ScopeMutationKind,
    ScopeVersion,
    SemanticTargetKind,
)


def _metric(cid: str = "metric.downtime") -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=cid,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=cid,
        cube_names=("operations",),
    )


def _dimension(cid: str = "dimension.department") -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=cid,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=cid,
        cube_names=("operations",),
    )


def test_v1_analytical_operation_vocabulary_is_closed() -> None:
    assert {item.value for item in AnalyticalOperation} == {
        "OBSERVE",
        "BREAKDOWN",
        "COMPARE",
        "RANK",
        "SELECT",
        "DRILLDOWN",
        "RELATE",
        "RCA",
        "REPORT",
        "SCOPE_PATCH",
    }


def test_scope_patch_vocabulary_is_typed_not_free_form() -> None:
    assert {item.value for item in ScopeMutationKind} == {
        "ADD",
        "REMOVE",
        "REPLACE",
        "NARROW_ENTITY",
        "EXPAND_ENTITY",
        "CHANGE_PERIOD",
        "CHANGE_METRIC",
        "CHANGE_BREAKDOWN",
        "RESET",
    }


def test_compare_rank_select_drilldown_is_represented_by_existing_typed_contracts() -> None:
    metric = _metric()
    department = _dimension()
    machine = _dimension("dimension.machine")

    comparison = ResearchQuestion(
        goal_id="g_compare",
        kind=ResearchGoalKind.COMPARISON,
        source_text="Compare downtime.",
        subject_refs=(metric,),
        related_refs=(department,),
        status=ResearchGoalStatus.RESOLVED,
    )
    ranking = ResearchQuestion(
        goal_id="g_rank",
        kind=ResearchGoalKind.RANKING,
        source_text="Rank departments.",
        subject_refs=(metric, department),
        ranking=RankingSurface(
            text="rank",
            direction="desc",
            limit=1,
            measure_semantic_id=metric.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    drilldown = ResearchQuestion(
        goal_id="g_drill",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Drill into the selected department by machine.",
        subject_refs=(metric,),
        related_refs=(machine,),
        result_dependency=ResultSelectionDependency(
            source_goal_id=ranking.goal_id,
            dimension_semantic_id=department.candidate_id,
            selection="first_ranked_entity",
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = ResearchBrief(
        brief_id="rb-v1-grammar",
        objective="Typed compare-rank-select-drilldown.",
        scope=ResearchScope(
            semantic_refs=(metric, department, machine),
            scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
        ),
        questions=(comparison, ranking, drilldown),
        deliverables=(),
        must_requirement_ids=(
            comparison.goal_id,
            ranking.goal_id,
            drilldown.goal_id,
        ),
        context_version="ctx-v1-grammar",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )

    assert brief.questions[2].result_dependency is not None
    assert brief.questions[2].result_dependency.source_goal_id == "g_rank"
    assert brief.questions[2].result_dependency.selection == "first_ranked_entity"

    chains = validate_v1_research_brief(brief)
    assert (
        AnalyticalOperation.COMPARE,
        AnalyticalOperation.RANK,
        AnalyticalOperation.SELECT,
        AnalyticalOperation.DRILLDOWN,
    ) in chains


def test_result_dependency_cannot_select_from_non_ranking_parent() -> None:
    metric = _metric()
    department = _dimension()
    parent = ResearchQuestion(
        goal_id="g_compare",
        kind=ResearchGoalKind.COMPARISON,
        source_text="Compare downtime.",
        subject_refs=(metric,),
        related_refs=(department,),
        status=ResearchGoalStatus.RESOLVED,
    )
    child = ResearchQuestion(
        goal_id="g_child",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Use selected department.",
        subject_refs=(metric,),
        result_dependency=ResultSelectionDependency(
            source_goal_id=parent.goal_id,
            dimension_semantic_id=department.candidate_id,
            selection="first_ranked_entity",
        ),
        status=ResearchGoalStatus.RESOLVED,
    )

    with pytest.raises(ValueError, match="source must be a ranking goal"):
        ResearchBrief(
            brief_id="rb-v1-illegal-dependency",
            objective="Reject illegal composition.",
            scope=ResearchScope(
                semantic_refs=(metric, department),
                scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
            ),
            questions=(parent, child),
            deliverables=(),
            must_requirement_ids=(parent.goal_id, child.goal_id),
            context_version="ctx-v1-illegal-dependency",
            status=ResearchBriefStatus.READY_FOR_RESEARCH,
        )


def test_report_is_a_presentation_requirement_not_a_new_analytical_owner() -> None:
    report = ResearchDeliverableRequirement(
        requirement_id="d_report",
        kind=PresentationKind.REPORT,
        source_text="Produce the governed report.",
    )
    brief = ResearchBrief(
        brief_id="rb-v1-report-grammar",
        objective="Report current governed state.",
        scope=ResearchScope(),
        questions=(),
        deliverables=(report,),
        must_requirement_ids=(report.requirement_id,),
        context_version="ctx-v1-report-grammar",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    assert brief.questions == ()
    assert brief.deliverables == (report,)


def test_other_goal_cannot_mint_a_new_analytical_operation() -> None:
    metric = _metric()
    question = ResearchQuestion(
        goal_id="g_other",
        kind=ResearchGoalKind.OTHER,
        source_text="Unsupported analytical primitive.",
        subject_refs=(metric,),
        status=ResearchGoalStatus.RESOLVED,
    )
    scope = ResearchScope(
        semantic_refs=(metric,),
        scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
    )
    contract = AnalyticalRequestContract(
        authority_id="authority-v1-grammar",
        request_ref=question.goal_id,
        semantic_context_version="ctx-v1-grammar-other",
        scope_identity=AnalyticalScopeIdentity(
            lineage_id="lineage-v1-grammar",
            version_id="scope_v1",
        ),
        metric_refs=(metric.candidate_id,),
    )
    brief = ResearchBrief(
        brief_id="rb-v1-grammar-other",
        objective="Unsupported analytical primitive.",
        scope=scope,
        questions=(question,),
        deliverables=(),
        must_requirement_ids=(question.goal_id,),
        context_version="ctx-v1-grammar-other",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    with pytest.raises(AnalyticalBoundaryError) as brief_exc:
        validate_v1_research_brief(brief)
    assert brief_exc.value.code == "ANALYTICAL_V1_OPERATION_UNSUPPORTED"

    with pytest.raises(AnalyticalBoundaryError) as exc:
        project_analytical_intent_v1(
            question=question,
            scope=scope,
            contract=contract,
            tenant_id="tenant-v1",
            principal_id="principal-v1",
            currentness_token="current-v1",
            security_fingerprint="security-v1",
        )
    assert exc.value.code == "ANALYTICAL_V1_OPERATION_UNSUPPORTED"


def test_v1_grammar_version_and_required_compositions_are_explicit() -> None:
    assert V1_ANALYTICAL_GRAMMAR_VERSION == "dima_analytical_grammar_v1"
    required = {
        (AnalyticalOperation.OBSERVE,),
        (AnalyticalOperation.OBSERVE, AnalyticalOperation.BREAKDOWN),
        (AnalyticalOperation.COMPARE,),
        (AnalyticalOperation.COMPARE, AnalyticalOperation.RANK),
        (
            AnalyticalOperation.COMPARE,
            AnalyticalOperation.RANK,
            AnalyticalOperation.SELECT,
            AnalyticalOperation.DRILLDOWN,
        ),
        (AnalyticalOperation.RELATE,),
        (AnalyticalOperation.RCA,),
        (
            AnalyticalOperation.RCA,
            V1GrammarControl.NEXT_TEST,
            AnalyticalOperation.RCA,
        ),
        (AnalyticalOperation.REPORT,),
    }
    assert required.issubset(V1_LEGAL_COMPOSITIONS)


def test_scope_patch_is_only_a_prefix_over_a_supported_composition() -> None:
    assert_v1_analytical_composition(
        (
            AnalyticalOperation.SCOPE_PATCH,
            AnalyticalOperation.COMPARE,
            AnalyticalOperation.RANK,
        )
    )
    with pytest.raises(AnalyticalBoundaryError) as exc:
        assert_v1_analytical_composition(
            (
                AnalyticalOperation.SCOPE_PATCH,
                AnalyticalOperation.SELECT,
            )
        )
    assert exc.value.code == "ANALYTICAL_V1_COMPOSITION_UNSUPPORTED"


def test_rca_next_test_rca_is_legal_but_unbounded_loop_is_not() -> None:
    assert_v1_analytical_composition(
        (
            AnalyticalOperation.RCA,
            V1GrammarControl.NEXT_TEST,
            AnalyticalOperation.RCA,
        )
    )
    with pytest.raises(AnalyticalBoundaryError):
        assert_v1_analytical_composition(
            (
                AnalyticalOperation.RCA,
                V1GrammarControl.NEXT_TEST,
                AnalyticalOperation.RCA,
                V1GrammarControl.NEXT_TEST,
                AnalyticalOperation.RCA,
            )
        )


def test_result_dependent_non_drilldown_operation_is_rejected_by_closed_grammar() -> None:
    metric = _metric()
    department = _dimension()
    ranking = ResearchQuestion(
        goal_id="g_rank_source",
        kind=ResearchGoalKind.RANKING,
        source_text="Rank governed entities.",
        subject_refs=(metric,),
        related_refs=(department,),
        ranking=RankingSurface(
            text="rank",
            direction="desc",
            limit=1,
            measure_semantic_id=metric.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    child = ResearchQuestion(
        goal_id="g_observe_child",
        kind=ResearchGoalKind.PERFORMANCE,
        source_text="Observe the selected entity.",
        subject_refs=(metric,),
        result_dependency=ResultSelectionDependency(
            source_goal_id=ranking.goal_id,
            dimension_semantic_id=department.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = ResearchBrief(
        brief_id="rb-v1-dependent-observe",
        objective="Closed dependency grammar.",
        scope=ResearchScope(
            semantic_refs=(metric, department),
            scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
        ),
        questions=(ranking, child),
        deliverables=(),
        must_requirement_ids=(ranking.goal_id, child.goal_id),
        context_version="ctx-v1-dependent-observe",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )

    with pytest.raises(AnalyticalBoundaryError) as exc:
        validate_v1_research_brief(brief)
    assert exc.value.code == "ANALYTICAL_V1_DEPENDENT_OPERATION_UNSUPPORTED"


_ALL_GRAMMAR_TOKENS = tuple(AnalyticalOperation) + tuple(V1GrammarControl)


@given(
    st.lists(
        st.sampled_from(_ALL_GRAMMAR_TOKENS),
        min_size=1,
        max_size=6,
    ).map(tuple)
)
@settings(max_examples=250, deadline=None)
def test_closed_grammar_property_acceptance_is_exact(steps) -> None:
    if steps in V1_LEGAL_COMPOSITIONS:
        assert assert_v1_analytical_composition(steps) == steps
    else:
        with pytest.raises(AnalyticalBoundaryError):
            assert_v1_analytical_composition(steps)


class V1GrammarStateMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.prefix = ()

    @rule(step=st.sampled_from(_ALL_GRAMMAR_TOKENS))
    def attempt_transition(self, step) -> None:
        next_steps = legal_v1_next_steps(self.prefix)
        if self.prefix and not next_steps:
            self.prefix = ()
            next_steps = legal_v1_next_steps(self.prefix)

        attempted = (*self.prefix, step)
        if step in next_steps:
            self.prefix = assert_v1_analytical_composition(
                attempted,
                complete=False,
            )
        else:
            with pytest.raises(AnalyticalBoundaryError):
                assert_v1_analytical_composition(
                    attempted,
                    complete=False,
                )

    @invariant()
    def prefix_never_leaves_closed_grammar(self) -> None:
        if self.prefix:
            assert_v1_analytical_composition(
                self.prefix,
                complete=False,
            )


TestV1GrammarStateMachine = V1GrammarStateMachine.TestCase
TestV1GrammarStateMachine.settings = settings(
    max_examples=60,
    stateful_step_count=30,
    deadline=None,
)
