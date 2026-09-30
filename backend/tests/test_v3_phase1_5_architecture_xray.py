from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v3.product.composition import (
    HeadlessProductComposer,
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
from app.v3.research_intake import (
    ResearchIntakeCompiler,
    ResearchIntakeCatalog,
    ResearchIntakeTerminal,
)

from test_v3_research_intake import FakeTransport, catalog, ready_payload


@pytest.mark.xfail(
    strict=True,
    reason="PHASE1.5 H1: provider workflow graph still lacks typed epistemic/stop atoms",
)
def test_xray_h1_rca_directives_do_not_become_second_analytical_goal():
    payload = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department",),
    )
    clause = "Determine which governed explanation better accounts for downtime."
    payload["goals"][0].update(
        {
            "source_text": clause,
            "source_fragment_text": clause,
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": ["dimension.department"],
            },
        }
    )
    payload["directives"] = [
        {
            "key": "support-challenge",
            "kind": "SUPPORT_CHALLENGE",
            "source_goal_key": "g-current",
            "source_text": "Keep supporting and challenging evidence separate.",
        },
        {
            "key": "causal-restraint",
            "kind": "CAUSAL_RESTRAINT",
            "source_goal_key": "g-current",
            "source_text": "Do not overclaim causality.",
        },
        {
            "key": "stop-when-sufficient",
            "kind": "STOP_WHEN_SUFFICIENT",
            "source_goal_key": "g-current",
            "source_text": "If the governed evidence is sufficient, stop.",
        },
    ]
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload),
        calendar_reference_date="2026-09-30",
    ).compile(
        question=(
            clause
            + " Keep supporting and challenging evidence separate. "
            + "Do not overclaim causality. "
            + "If the governed evidence is sufficient, stop."
        ),
        catalog=catalog(),
    )

    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.brief is not None
    assert len(result.brief.questions) == 1
    assert result.brief.questions[0].kind == ResearchGoalKind.ROOT_CAUSE
    assert [item.kind.value for item in result.brief.directives] == [
        "SUPPORT_CHALLENGE",
        "CAUSAL_RESTRAINT",
        "STOP_WHEN_SUFFICIENT",
    ]
    assert len(result.brief.must_requirement_ids) == 4


@pytest.mark.xfail(
    strict=True,
    reason="PHASE1.5 H5: EXPLAIN deliverable is currently projected PENDING/UNSUPPORTED",
)
def test_xray_h5_explain_is_fulfilled_by_governed_p20_report():
    question = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate governed competing explanations.",
        status=ResearchGoalStatus.RESOLVED,
    )
    explain = ResearchDeliverableRequirement(
        requirement_id="d_explain",
        kind=PresentationKind.EXPLAIN,
        source_text="Explain the governed terminal conclusion.",
    )
    brief = ResearchBrief(
        brief_id="rb-phase15-h5",
        objective="Close typed completion ownership.",
        scope=ResearchScope(),
        questions=(question,),
        deliverables=(explain,),
        must_requirement_ids=("g_root", "d_explain"),
        context_version="ctx-phase15-h5",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    assessment = SimpleNamespace(
        assessment_id="p19a_" + "1" * 24,
        aggregate_outcome=SimpleNamespace(value="NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED"),
    )
    session = SimpleNamespace(
        obligations=(SimpleNamespace(obligation_id="g_root", state=SimpleNamespace(value="VERIFIED")),)
    )
    report = SimpleNamespace(report_id="p20r_" + "2" * 24)

    projected, total, accounted, fulfilled = HeadlessProductComposer._project_user_must(
        brief=brief,
        session=session,
        report=report,
        root_cause_assessments={"g_root": assessment},
    )

    assert total == 2
    assert accounted == 2
    assert fulfilled == 2
    by_id = {item.requirement_id: item for item in projected}
    assert by_id["d_explain"].state == ProductRequirementState.FULFILLED
    assert by_id["d_explain"].fulfilled_by_ref == report.report_id


def test_xray_h3_h4_remain_conditional_until_current_material_admission_proves_loss():
    # Phase 1.5 does not authorize speculative EvidenceBundle or R1 rewrites.
    # This sentinel is intentionally architectural: the current contracts keep
    # native material ownership outside Product and no new evidence family exists.
    assert not hasattr(HeadlessProductComposer, "EvidenceBundle")
