from __future__ import annotations

import pytest

from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductCompositionTerminal,
    ProductRequirementDisposition,
    ProductRequirementFulfillment,
    ProductRequirementKind,
    ProductRequirementState,
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


def brief():
    questions = tuple(
        ResearchQuestion(
            goal_id=f"g_{index}",
            kind=ResearchGoalKind.BREAKDOWN,
            source_text=f"analytical must {index}",
            status=ResearchGoalStatus.RESOLVED,
        )
        for index in range(1, 4)
    )
    deliverables = (
        ResearchDeliverableRequirement(
            requirement_id="d_report",
            kind=PresentationKind.REPORT,
            source_text="Produce report.",
        ),
        ResearchDeliverableRequirement(
            requirement_id="d_chart",
            kind=PresentationKind.CHART,
            source_text="Produce chart.",
        ),
    )
    return ResearchBrief(
        brief_id="rb-v1-completion",
        objective="Prove exact completion accounting.",
        scope=ResearchScope(),
        questions=questions,
        deliverables=deliverables,
        must_requirement_ids=(
            "g_1", "g_2", "g_3", "d_report", "d_chart"
        ),
        context_version="ctx-v1-completion",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def test_five_part_user_must_contract_has_one_terminal_disposition_each():
    item = brief()
    projected = (
        ProductRequirementFulfillment(
            requirement_id="g_1",
            requirement_kind=ProductRequirementKind.ANALYTICAL,
            state=ProductRequirementState.VERIFIED,
        ),
        ProductRequirementFulfillment(
            requirement_id="g_2",
            requirement_kind=ProductRequirementKind.ANALYTICAL,
            state=ProductRequirementState.LIMITED,
        ),
        ProductRequirementFulfillment(
            requirement_id="g_3",
            requirement_kind=ProductRequirementKind.ANALYTICAL,
            state=ProductRequirementState.PENDING,
        ),
        ProductRequirementFulfillment(
            requirement_id="d_report",
            requirement_kind=ProductRequirementKind.DELIVERABLE,
            state=ProductRequirementState.PENDING,
        ),
        ProductRequirementFulfillment(
            requirement_id="d_chart",
            requirement_kind=ProductRequirementKind.DELIVERABLE,
            state=ProductRequirementState.PENDING,
        ),
    )
    ledger = HeadlessProductComposer._completion_ledger(
        brief=item,
        projected=projected,
        terminal=ProductCompositionTerminal.INCONCLUSIVE,
    )
    assert tuple(x.requirement_id for x in ledger.entries) == item.must_requirement_ids
    assert [x.disposition for x in ledger.entries] == [
        ProductRequirementDisposition.FULFILLED,
        ProductRequirementDisposition.LIMITED,
        ProductRequirementDisposition.INCONCLUSIVE,
        ProductRequirementDisposition.INCONCLUSIVE,
        ProductRequirementDisposition.UNSUPPORTED,
    ]
    assert ledger.process_complete is True
    assert ledger.requirement_complete is False
    assert ledger.trusted_complete is True


def test_trusted_answer_cannot_hide_pending_supported_requirement():
    item = brief()
    projected = tuple(
        ProductRequirementFulfillment(
            requirement_id=requirement_id,
            requirement_kind=(
                ProductRequirementKind.DELIVERABLE
                if requirement_id.startswith("d_")
                else ProductRequirementKind.ANALYTICAL
            ),
            state=(
                ProductRequirementState.PENDING
                if requirement_id == "g_3"
                else ProductRequirementState.FULFILLED
            ),
        )
        for requirement_id in item.must_requirement_ids
    )
    with pytest.raises(ValueError, match="cannot hide"):
        HeadlessProductComposer._completion_ledger(
            brief=item,
            projected=projected,
            terminal=ProductCompositionTerminal.ANSWER,
        )


def test_unsupported_is_structural_not_text_inference():
    item = brief()
    projected = tuple(
        ProductRequirementFulfillment(
            requirement_id=requirement_id,
            requirement_kind=(
                ProductRequirementKind.DELIVERABLE
                if requirement_id.startswith("d_")
                else ProductRequirementKind.ANALYTICAL
            ),
            state=(
                ProductRequirementState.PENDING
                if requirement_id == "d_chart"
                else ProductRequirementState.FULFILLED
            ),
        )
        for requirement_id in item.must_requirement_ids
    )
    ledger = HeadlessProductComposer._completion_ledger(
        brief=item,
        projected=projected,
        terminal=ProductCompositionTerminal.REPORT,
    )
    by_id = {x.requirement_id: x.disposition for x in ledger.entries}
    assert by_id["d_chart"] == ProductRequirementDisposition.UNSUPPORTED

def test_all_fulfilled_user_must_is_both_process_and_requirement_complete():
    item = brief()
    projected = tuple(
        ProductRequirementFulfillment(
            requirement_id=requirement_id,
            requirement_kind=(
                ProductRequirementKind.DELIVERABLE
                if requirement_id.startswith("d_")
                else ProductRequirementKind.ANALYTICAL
            ),
            state=ProductRequirementState.FULFILLED,
            fulfilled_by_ref="artifact:" + requirement_id,
        )
        for requirement_id in item.must_requirement_ids
    )
    ledger = HeadlessProductComposer._completion_ledger(
        brief=item,
        projected=projected,
        terminal=ProductCompositionTerminal.REPORT,
    )
    assert ledger.process_complete is True
    assert ledger.requirement_complete is True
    assert ledger.trusted_complete is True

def test_root_cause_terminal_assessment_fulfills_single_explain_requirement():
    goal = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate competing mechanisms.",
        status=ResearchGoalStatus.RESOLVED,
    )
    explain = ResearchDeliverableRequirement(
        requirement_id="d_explain",
        kind=PresentationKind.EXPLAIN,
        source_text="Explain the terminal epistemic conclusion.",
    )
    item = ResearchBrief(
        brief_id="rb-v1-explain-owner",
        objective="Map typed completion to the actual owner.",
        scope=ResearchScope(),
        questions=(goal,),
        deliverables=(explain,),
        must_requirement_ids=(goal.goal_id, explain.requirement_id),
        context_version="ctx-v1-explain-owner",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    session = type(
        "Session",
        (),
        {
            "obligations": (
                type(
                    "Obligation",
                    (),
                    {"obligation_id": goal.goal_id, "state": "VERIFIED"},
                )(),
            )
        },
    )()
    assessment = type(
        "Assessment",
        (),
        {
            "assessment_id": "p19a_" + "1" * 24,
            "aggregate_outcome": "NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED",
        },
    )()

    projected, total, accounted, fulfilled = HeadlessProductComposer._project_user_must(
        brief=item,
        session=session,
        report=None,
        root_cause_assessments={goal.goal_id: assessment},
    )
    by_id = {entry.requirement_id: entry for entry in projected}

    assert by_id[goal.goal_id].state == ProductRequirementState.FULFILLED
    assert by_id[explain.requirement_id].state == ProductRequirementState.FULFILLED
    assert by_id[explain.requirement_id].fulfilled_by_ref == assessment.assessment_id
    assert (total, accounted, fulfilled) == (2, 2, 2)


def test_pending_explain_is_inconclusive_not_structurally_unsupported():
    goal = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate candidates.",
        status=ResearchGoalStatus.RESOLVED,
    )
    explain = ResearchDeliverableRequirement(
        requirement_id="d_explain",
        kind=PresentationKind.EXPLAIN,
        source_text="Explain the result.",
    )
    item = ResearchBrief(
        brief_id="rb-v1-explain-inconclusive",
        objective="Keep incomplete explanation honest.",
        scope=ResearchScope(),
        questions=(goal,),
        deliverables=(explain,),
        must_requirement_ids=(goal.goal_id, explain.requirement_id),
        context_version="ctx-v1-explain-inconclusive",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    projected = (
        ProductRequirementFulfillment(
            requirement_id=goal.goal_id,
            requirement_kind=ProductRequirementKind.ANALYTICAL,
            state=ProductRequirementState.FULFILLED,
        ),
        ProductRequirementFulfillment(
            requirement_id=explain.requirement_id,
            requirement_kind=ProductRequirementKind.DELIVERABLE,
            state=ProductRequirementState.PENDING,
        ),
    )
    ledger = HeadlessProductComposer._completion_ledger(
        brief=item,
        projected=projected,
        terminal=ProductCompositionTerminal.REPORT,
    )
    by_id = {entry.requirement_id: entry.disposition for entry in ledger.entries}
    assert by_id[explain.requirement_id] == ProductRequirementDisposition.INCONCLUSIVE

