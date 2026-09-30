from __future__ import annotations

from types import SimpleNamespace

from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductRequirementState,
)
from app.v3.research_contracts import (
    CausalCompetitionSurface,
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
    ResearchIntakeTerminal,
)

from test_v3_research_intake import FakeTransport, catalog, principal, ready_payload


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


class _EpistemicsRecorder:
    def __init__(self):
        self.hypotheses = []
        self.groundings = []

    def create_hypothesis(
        self,
        *,
        research_session_id,
        obligation_id,
        statement,
        principal,
        candidate_identity_ref=None,
    ):
        hypothesis_id = "p19h_" + str(len(self.hypotheses) + 1) * 24
        self.hypotheses.append(
            {
                "research_session_id": research_session_id,
                "obligation_id": obligation_id,
                "statement": statement,
                "candidate_identity_ref": candidate_identity_ref,
            }
        )
        return SimpleNamespace(hypothesis_id=hypothesis_id)

    def create_grounding(self, **kwargs):
        self.groundings.append(kwargs)
        return SimpleNamespace()


def test_xray_h8_user_seeded_hypotheses_bind_directly_to_evidence_without_p17():
    refs = {item.candidate_id: item for item in catalog().semantic_refs}
    goal = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate governed candidate mechanisms.",
        subject_refs=(
            refs["metric.downtime"],
            refs["metric.fault_count"],
            refs["metric.performance"],
        ),
        related_refs=(refs["dimension.department"],),
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id="metric.downtime",
            candidate_mechanism_semantic_ids=(
                "metric.fault_count",
                "metric.performance",
            ),
            diagnostic_dimension_ids=("dimension.department",),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = ResearchBrief(
        brief_id="rb-phase15-h8",
        objective="Evaluate user-seeded competing explanations.",
        scope=ResearchScope(
            semantic_refs=(
                refs["metric.downtime"],
                refs["metric.fault_count"],
                refs["metric.performance"],
                refs["dimension.department"],
            )
        ),
        questions=(goal,),
        must_requirement_ids=("g_root",),
        context_version="ctx-phase15-h8",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    source_session = SimpleNamespace(
        accepted_brief=brief,
        evidence_refs=(
            SimpleNamespace(
                evidence_id="evi_" + "1" * 24,
                receipt_id="dqr_" + "2" * 24,
                obligation_id="g_root",
            ),
        ),
    )
    recorder = _EpistemicsRecorder()
    composer = object.__new__(HeadlessProductComposer)
    composer._epistemics = recorder

    hypothesis_ids = composer._seed_user_hypotheses(
        session_id="rs_" + "3" * 24,
        goal=goal,
        principal=principal(),
        source_session=source_session,
        mechanism_refs=(
            "metric.fault_count",
            "metric.performance",
        ),
        evidence_refs=("evi_" + "1" * 24,),
    )

    assert len(hypothesis_ids) == 2
    assert [item["candidate_identity_ref"] for item in recorder.hypotheses] == [
        "metric.fault_count",
        "metric.performance",
    ]
    assert len(recorder.groundings) == 2
    assert all(
        item["source_kind"].value == "P14_EVIDENCE"
        for item in recorder.groundings
    )
    assert all(
        item["relation"].value == "CONTEXT"
        for item in recorder.groundings
    )
