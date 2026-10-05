from __future__ import annotations

import pytest

from app.v3.analytical_boundary import (
    AnalyticalBoundaryError,
    AnalyticalOperation,
    project_analytical_intent_v1,
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
