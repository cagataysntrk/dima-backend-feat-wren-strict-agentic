from app.v3.brain_v2.requirement_dispatch import (
    RequirementOwner,
    dispatch_requirements,
)
from app.v3.research_contracts import (
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
)


def q(goal_id, kind):
    return ResearchQuestion(
        goal_id=goal_id,
        kind=kind,
        source_text=goal_id,
        status=ResearchGoalStatus.RESOLVED,
    )


def test_typed_requirement_kind_selects_owner_without_text_inference():
    questions = (
        q("g_rank", ResearchGoalKind.RANKING),
        q("g_rel", ResearchGoalKind.RELATIONSHIP),
        q("g_rca", ResearchGoalKind.ROOT_CAUSE),
        q("g_trend", ResearchGoalKind.TREND),
    )
    report = ResearchDeliverableRequirement(
        requirement_id="d_report",
        kind=PresentationKind.REPORT,
        source_text="report",
    )
    brief = ResearchBrief(
        brief_id="rb_dispatch",
        objective="typed routing",
        scope=ResearchScope(),
        questions=questions,
        deliverables=(report,),
        must_requirement_ids=tuple(
            [item.goal_id for item in questions] + [report.requirement_id]
        ),
        context_version="ctx_dispatch",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )

    mapping = {
        item.requirement_id: item for item in dispatch_requirements(brief)
    }

    assert mapping["g_rank"].owner == RequirementOwner.DIRECT_EVIDENCE
    assert mapping["g_rel"].owner == RequirementOwner.P18
    assert mapping["g_rca"].owner == RequirementOwner.P19
    assert mapping["g_trend"].owner == RequirementOwner.DIRECT_EVIDENCE
    assert mapping["d_report"].owner == RequirementOwner.P20
    assert mapping["d_report"].analytical is False


def test_requirement_source_wording_cannot_change_owner():
    left = q("g_a", ResearchGoalKind.RELATIONSHIP)
    right = left.model_copy(update={"source_text": "rank report root cause"})
    base = dict(
        brief_id="rb_dispatch_wording",
        objective="typed routing",
        scope=ResearchScope(),
        must_requirement_ids=("g_a",),
        context_version="ctx_dispatch",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    a = ResearchBrief(questions=(left,), **base)
    b = ResearchBrief(questions=(right,), **base)

    assert dispatch_requirements(a) == dispatch_requirements(b)
