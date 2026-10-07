from types import SimpleNamespace

from app.v3.brain_v2 import material_groups as material_groups_module
from app.v3.brain_v2.material_groups import project_material_groups
from app.v3.research_contracts import (
    ComparisonRole,
    ComparisonSurface,
    PresentationKind,
    RankingBasis,
    RankingSurface,
    RelationshipIntent,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResultSelectionDependency,
    ResearchSemanticRef,
    ResearchTimePeriod,
    ScopeVersion,
    SemanticTargetKind,
    TemporalRole,
)


def metric(cid: str, name: str):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def dim(cid: str, name: str):
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


DOWNTIME = metric("metric.downtime", "Machine Downtime")
FAULTS = metric("metric.faults", "Fault Count")
PERFORMANCE = metric("metric.performance", "Performance")
DEPT = dim("dimension.department", "Department")
DATE = dim("dimension.event_date", "Event Date")
LINE = dim("dimension.line", "Production Line")


def brief(*questions, report=False, temporal=False):
    refs = {}
    for question in questions:
        for ref in (*question.subject_refs, *question.related_refs):
            refs[ref.candidate_id] = ref
    deliverables = (
        (
            ResearchDeliverableRequirement(
                requirement_id="d_report",
                kind=PresentationKind.REPORT,
                source_text="Produce management report.",
            ),
        )
        if report
        else ()
    )
    return ResearchBrief(
        brief_id="rb_material_groups",
        objective="Project minimum typed material.",
        scope=ResearchScope(
            semantic_refs=tuple(refs.values()),
            time_surfaces=(("May-June 2026",) if temporal else ()),
            periods=(
                (
                    ResearchTimePeriod(
                        source_text="May-June 2026",
                        time_dimension_candidate_id=DATE.candidate_id,
                        start="2026-05-01",
                        end="2026-07-01",
                        role=TemporalRole.MATERIAL_WINDOW,
                    ),
                )
                if temporal
                else ()
            ),
            temporal_dimension_ids=((DATE.candidate_id,) if temporal else ()),
            scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
        ),
        questions=tuple(questions),
        deliverables=deliverables,
        must_requirement_ids=tuple(
            [q.goal_id for q in questions]
            + [d.requirement_id for d in deliverables]
        ),
        context_version="ctx_material_groups_v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def session(value):
    return SimpleNamespace(
        accepted_brief=value,
        context_version=value.context_version,
        authority_id="atc_test",
        session_id="rs_" + "a" * 24,
        lineage_id="atl_material_groups",
        tenant_binding="id:tenant-a",
        principal_subject="principal-a",
        authority_revision=1,
    )


def ranking(*, bounded=False, temporal_ref=False, extra_breakdown=False):
    return ResearchQuestion(
        goal_id="g_rank",
        kind=ResearchGoalKind.RANKING,
        source_text="Rank downtime by department.",
        source_fragment_identity="fragment-sha256:" + "1" * 64,
        subject_refs=(DEPT, DOWNTIME),
        related_refs=tuple(
            item
            for item in (
                DATE if temporal_ref else None,
                LINE if extra_breakdown else None,
            )
            if item is not None
        ),
        ranking=RankingSurface(
            text="Rank downtime",
            direction="desc",
            limit=2 if bounded else None,
            measure_semantic_id=DOWNTIME.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )


def relationship():
    return ResearchQuestion(
        goal_id="g_relationship",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text="Assess downtime with faults by department.",
        source_fragment_identity="fragment-sha256:" + "2" * 64,
        subject_refs=(DOWNTIME, FAULTS),
        related_refs=(DEPT,),
        relationship_intent=RelationshipIntent.OBSERVATIONAL,
        status=ResearchGoalStatus.RESOLVED,
    )


def pair_brief(*questions):
    refs = {}
    for question in questions:
        for ref in (*question.subject_refs, *question.related_refs):
            refs[ref.candidate_id] = ref
    return ResearchBrief(
        brief_id="rb_pair_material_groups",
        objective="Compare governed downtime change.",
        scope=ResearchScope(
            semantic_refs=tuple(refs.values()),
            time_surfaces=("May 2026", "June 2026"),
            periods=(
                ResearchTimePeriod(
                    source_text="May 2026",
                    time_dimension_candidate_id=DATE.candidate_id,
                    start="2026-05-01",
                    end="2026-06-01",
                    role=TemporalRole.BASELINE_PERIOD,
                ),
                ResearchTimePeriod(
                    source_text="June 2026",
                    time_dimension_candidate_id=DATE.candidate_id,
                    start="2026-06-01",
                    end="2026-07-01",
                    role=TemporalRole.COMPARISON_PERIOD,
                ),
            ),
            temporal_dimension_ids=(DATE.candidate_id,),
            scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
        ),
        questions=tuple(questions),
        must_requirement_ids=tuple(item.goal_id for item in questions),
        context_version="ctx_material_groups_v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def comparison(goal_id="g_compare", metric_ref=DOWNTIME):
    return ResearchQuestion(
        goal_id=goal_id,
        kind=ResearchGoalKind.COMPARISON,
        source_text="Compare May and June by department.",
        source_fragment_identity="fragment-sha256:" + "3" * 64,
        subject_refs=(metric_ref, DEPT),
        related_refs=(DATE,),
        comparisons=(
            ComparisonSurface(
                text="May versus June",
                role=ComparisonRole.TEMPORAL_PERIOD,
            ),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )


def change_ranking(goal_id, *, limit=None, metric_ref=DOWNTIME):
    return ResearchQuestion(
        goal_id=goal_id,
        kind=ResearchGoalKind.RANKING,
        source_text="Rank department change.",
        source_fragment_identity="fragment-sha256:" + "4" * 64,
        subject_refs=(metric_ref, DEPT),
        related_refs=(DATE,),
        ranking=RankingSurface(
            text="rank governed change",
            direction="desc",
            limit=limit,
            measure_semantic_id=metric_ref.candidate_id,
            basis=RankingBasis.CHANGE,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )


def test_compatible_ranking_relationship_share_one_material_group():
    groups = project_material_groups(session(brief(ranking(), relationship())))

    assert len(groups) == 1
    group = groups[0]
    assert set(group.consumer_requirement_ids) == {"g_rank", "g_relationship"}
    assert group.required_metric_refs == ("metric.downtime", "metric.faults")
    assert group.required_dimension_refs == ("dimension.department",)


def test_incompatible_bounded_ranking_relationship_use_two_groups():
    groups = project_material_groups(
        session(brief(ranking(bounded=True), relationship()))
    )

    assert len(groups) == 2
    assert {
        tuple(group.consumer_requirement_ids) for group in groups
    } == {("g_rank",), ("g_relationship",)}


def test_shared_requirement_resolves_to_exact_material_execution_anchor():
    first = ranking(bounded=True).model_copy(update={"goal_id": "g_anchor"})
    source = ranking(bounded=True).model_copy(update={"goal_id": "g_source"})
    groups = project_material_groups(session(brief(first, source)))

    assert len(groups) == 1
    group = groups[0]
    assert set(group.consumer_requirement_ids) == {"g_anchor", "g_source"}
    assert group.material_group_id.startswith("mg_")
    resolver = getattr(
        material_groups_module,
        "material_execution_anchor_for_requirement",
        None,
    )
    assert callable(resolver), (
        "shared material dependencies need one exact requirement -> execution anchor mapping"
    )
    assert resolver(groups, requirement_id="g_source") == group.anchor_requirement_id
    assert group.anchor_requirement_id == "g_anchor"


def test_result_dependent_material_group_waits_for_verified_parent_group():
    parent = ranking(bounded=True)
    child = ResearchQuestion(
        goal_id="g_child",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect one selected governed slice.",
        source_fragment_identity="fragment-sha256:" + "9" * 64,
        subject_refs=(FAULTS,),
        related_refs=(DEPT, LINE),
        result_dependency=ResultSelectionDependency(
            source_goal_id=parent.goal_id,
            dimension_semantic_id=DEPT.candidate_id,
            selection="first_ranked_entity",
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    groups = project_material_groups(session(brief(parent, child)))
    selector = getattr(
        material_groups_module,
        "select_pending_material_group",
        None,
    )
    assert callable(selector), "result-dependent material needs a typed readiness selector"

    by_consumer = {
        consumer: group
        for group in groups
        for consumer in group.consumer_requirement_ids
    }
    parent_group = by_consumer[parent.goal_id]
    child_group = by_consumer[child.goal_id]
    assert child_group.dependency_requirement_ids == (parent.goal_id,)

    first = selector(groups, completed_material_group_ids=())
    assert first.material_group_id == parent_group.material_group_id
    second = selector(
        groups,
        completed_material_group_ids=(parent_group.material_group_id,),
    )
    assert second.material_group_id == child_group.material_group_id
    assert material_groups_module.result_dependency_execution_anchor(
        session=session(brief(parent, child)),
        groups=groups,
        requirement_id=child.goal_id,
    ) == parent_group.anchor_requirement_id


def test_report_requirement_creates_zero_additional_material_groups():
    no_report = project_material_groups(session(brief(ranking())))
    with_report = project_material_groups(session(brief(ranking(), report=True)))

    assert len(no_report) == len(with_report) == 1
    assert no_report[0].material_fingerprint == with_report[0].material_fingerprint
    assert "d_report" not in with_report[0].consumer_requirement_ids


def test_requirement_order_does_not_change_material_group_authority():
    left = project_material_groups(session(brief(ranking(), relationship())))
    right = project_material_groups(session(brief(relationship(), ranking())))

    assert tuple(item.model_dump(mode="json") for item in left) == tuple(
        item.model_dump(mode="json") for item in right
    )


def test_temporal_scope_dimension_does_not_block_compatible_material_sharing():
    groups = project_material_groups(
        session(
            brief(
                ranking(temporal_ref=True),
                relationship(),
                temporal=True,
            )
        )
    )

    assert len(groups) == 1
    group = groups[0]
    assert set(group.consumer_requirement_ids) == {"g_rank", "g_relationship"}
    assert group.required_metric_refs == ("metric.downtime", "metric.faults")
    assert group.required_dimension_refs == ("dimension.department",)
    assert group.required_periods[0].time_dimension_ref == "dimension.event_date"


def test_real_non_temporal_breakdown_still_blocks_cross_fragment_sharing():
    groups = project_material_groups(
        session(
            brief(
                ranking(temporal_ref=True, extra_breakdown=True),
                relationship(),
                temporal=True,
            )
        )
    )

    assert len(groups) == 2
    assert {
        tuple(group.consumer_requirement_ids) for group in groups
    } == {("g_rank",), ("g_relationship",)}


def test_comparison_change_ranking_and_topk_share_one_acquisition():
    value = pair_brief(
        comparison(),
        change_ranking("g_change"),
        change_ranking("g_top2", limit=2),
    )
    groups = project_material_groups(session(value))

    assert len(groups) == 1
    group = groups[0]
    assert set(group.consumer_requirement_ids) == {
        "g_compare",
        "g_change",
        "g_top2",
    }
    assert group.anchor_requirement_id == "g_change"
    contract = material_groups_module.material_group_acquisition_contract(
        session=session(value),
        group=group,
    )
    assert contract.comparison is not None
    assert contract.ranking is not None
    assert contract.ranking.basis == RankingBasis.CHANGE
    assert contract.ranking.limit is None


def test_comparison_ranking_grouping_is_order_and_wording_invariant():
    left_questions = (
        comparison(),
        change_ranking("g_change"),
        change_ranking("g_top2", limit=2),
    )
    right_questions = tuple(
        item.model_copy(update={"source_text": "Equivalent accepted wording."})
        for item in reversed(left_questions)
    )
    left = project_material_groups(session(pair_brief(*left_questions)))
    right = project_material_groups(session(pair_brief(*right_questions)))

    assert len(left) == len(right) == 1
    assert left[0].material_group_id == right[0].material_group_id
    assert left[0].material_fingerprint == right[0].material_fingerprint
    assert set(left[0].consumer_requirement_ids) == set(
        right[0].consumer_requirement_ids
    )


def test_different_metric_does_not_consolidate():
    groups = project_material_groups(
        session(
            pair_brief(
                comparison(metric_ref=DOWNTIME),
                change_ranking("g_fault_rank", metric_ref=FAULTS),
            )
        )
    )
    assert len(groups) == 2


def test_result_dependent_child_remains_later_occurrence_with_shared_parent():
    parent = change_ranking("g_top2", limit=2)
    child = ResearchQuestion(
        goal_id="g_child_after_selection",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect the selected department.",
        source_fragment_identity="fragment-sha256:" + "8" * 64,
        subject_refs=(FAULTS,),
        related_refs=(DEPT, LINE, DATE),
        result_dependency=ResultSelectionDependency(
            source_goal_id=parent.goal_id,
            dimension_semantic_id=DEPT.candidate_id,
            selection="first_ranked_entity",
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    groups = project_material_groups(
        session(pair_brief(comparison(), parent, child))
    )
    by_consumer = {
        requirement_id: group
        for group in groups
        for requirement_id in group.consumer_requirement_ids
    }
    assert (
        by_consumer["g_compare"].material_group_id
        == by_consumer[parent.goal_id].material_group_id
    )
    assert (
        by_consumer[child.goal_id].material_group_id
        != by_consumer[parent.goal_id].material_group_id
    )
    assert by_consumer[child.goal_id].dependency_requirement_ids == (
        parent.goal_id,
    )
