from types import SimpleNamespace

from app.v3.brain_v2.material_groups import project_material_groups
from app.v3.research_contracts import (
    PresentationKind,
    RankingSurface,
    RelationshipIntent,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ScopeVersion,
    SemanticTargetKind,
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


def brief(*questions, report=False):
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
    )


def ranking(*, bounded=False):
    return ResearchQuestion(
        goal_id="g_rank",
        kind=ResearchGoalKind.RANKING,
        source_text="Rank downtime by department.",
        source_fragment_identity="fragment-sha256:" + "1" * 64,
        subject_refs=(DEPT, DOWNTIME),
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
