from __future__ import annotations

from types import SimpleNamespace

from app.v3.hypothesis_root_cause import GroundingRelation
from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductCompositionTerminal,
    ProductRequirementDisposition,
    ProductRequirementFulfillment,
    ProductRequirementKind,
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
from app.v3.research_intake import ResearchIntakeCompiler

from tests.test_v3_research_intake import FakeTransport, catalog, ready_payload


def _phase15_rca_payload() -> dict:
    main = ready_payload(
        kind="root_cause",
        subject=(
            "metric.downtime",
            "metric.fault_count",
            "metric.performance",
        ),
        related=("dimension.department", "dimension.event_date"),
    )
    main["objective"] = "Evaluate two governed mechanisms without repeating analytical work."
    main["goals"][0].update(
        {
            "goal_key": "g-root",
            "source_text": "Evaluate fault count and performance as candidate mechanisms.",
            "source_fragment_text": "Evaluate fault count and performance as candidate mechanisms.",
            "causal_competition": {
                "effect_semantic_id": "metric.downtime",
                "candidate_mechanism_semantic_ids": [
                    "metric.fault_count",
                    "metric.performance",
                ],
                "diagnostic_dimension_ids": [
                    "dimension.department",
                    "dimension.event_date",
                ],
            },
        }
    )
    main["goals"].append(
        {
            "goal_key": "g-evidence-directive",
            "kind": "other",
            "source_text": "Keep supporting and challenging evidence separate.",
            "source_fragment_text": "Keep supporting and challenging evidence separate.",
            "subject_semantic_ids": [
                "metric.downtime",
                "metric.fault_count",
                "metric.performance",
            ],
            "related_semantic_ids": [
                "dimension.department",
                "dimension.event_date",
            ],
            "ranking": None,
            "comparisons": [],
        }
    )
    main["deliverables"] = [
        {
            "key": "d-evidence",
            "kind": "report",
            "source_text": "Keep supporting and challenging evidence separate.",
        },
        {
            "key": "d-terminal",
            "kind": "explain",
            "source_text": "Reach the most defensible terminal conclusion.",
        },
    ]
    return main


def test_xray_h1_h2_canonicalizes_epistemic_directive_without_second_acquisition():
    payload = _phase15_rca_payload()
    question = (
        "Evaluate fault count and performance as candidate mechanisms. "
        "Keep supporting and challenging evidence separate. "
        "Reach the most defensible terminal conclusion."
    )
    transport = FakeTransport(payload)

    result = ResearchIntakeCompiler(
        transport=transport,
        calendar_reference_date="2026-09-30",
    ).compile(question=question, catalog=catalog())

    assert result.brief is not None
    assert transport.call_count == 1
    assert [item.kind for item in result.brief.questions] == [
        ResearchGoalKind.ROOT_CAUSE,
    ]
    assert len(result.brief.questions) == 1
    assert [item.kind for item in result.brief.deliverables] == [
        PresentationKind.REPORT,
        PresentationKind.EXPLAIN,
    ]


def test_xray_h5_pending_explain_is_inconclusive_not_structurally_unsupported():
    goal = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate candidates.",
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id="metric.effect",
            candidate_mechanism_semantic_ids=("metric.a", "metric.b"),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    explain = ResearchDeliverableRequirement(
        requirement_id="d_explain",
        kind=PresentationKind.EXPLAIN,
        source_text="Explain the terminal result.",
    )
    brief = ResearchBrief(
        brief_id="rb-phase15-xray",
        objective="Characterize completion ownership.",
        scope=ResearchScope(),
        questions=(goal,),
        deliverables=(explain,),
        must_requirement_ids=(goal.goal_id, explain.requirement_id),
        context_version="ctx-phase15-xray",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )
    projected = (
        ProductRequirementFulfillment(
            requirement_id=goal.goal_id,
            requirement_kind=ProductRequirementKind.ANALYTICAL,
            state=ProductRequirementState.FULFILLED,
            fulfilled_by_ref="p19a_" + "1" * 24,
        ),
        ProductRequirementFulfillment(
            requirement_id=explain.requirement_id,
            requirement_kind=ProductRequirementKind.DELIVERABLE,
            state=ProductRequirementState.PENDING,
        ),
    )

    ledger = HeadlessProductComposer._completion_ledger(
        brief=brief,
        projected=projected,
        terminal=ProductCompositionTerminal.REPORT,
    )

    by_id = {item.requirement_id: item.disposition for item in ledger.entries}
    assert by_id[explain.requirement_id] == ProductRequirementDisposition.INCONCLUSIVE


class _FakeEpistemics:
    def __init__(self) -> None:
        self.hypotheses: list[tuple[str, str]] = []
        self.groundings: list[dict] = []

    def create_hypothesis(
        self,
        *,
        statement,
        candidate_identity_ref,
        **kwargs,
    ):
        self.hypotheses.append((candidate_identity_ref, statement))
        return SimpleNamespace(
            hypothesis_id="p19h_" + str(len(self.hypotheses)) * 24
        )

    def create_grounding(self, **kwargs):
        self.groundings.append(kwargs)


def test_xray_h8_user_seeded_candidates_bypass_duplicate_p17_synthesis():
    composer = object.__new__(HeadlessProductComposer)
    epistemics = _FakeEpistemics()
    composer._epistemics = epistemics
    goal = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate candidates.",
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id="metric.effect",
            candidate_mechanism_semantic_ids=("metric.a", "metric.b"),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    refs = tuple(
        SimpleNamespace(candidate_id=cid, canonical_name=name)
        for cid, name in (
            ("metric.effect", "Effect"),
            ("metric.a", "Candidate A"),
            ("metric.b", "Candidate B"),
        )
    )
    source_session = SimpleNamespace(
        accepted_brief=SimpleNamespace(
            scope=SimpleNamespace(semantic_refs=refs)
        ),
        evidence_refs=(
            SimpleNamespace(
                evidence_id="evi_" + "1" * 24,
                receipt_id="dqr_" + "1" * 24,
                obligation_id=goal.goal_id,
            ),
        ),
    )

    seeded = composer._seed_user_root_candidates_to_p19(
        session_id="rs_" + "1" * 24,
        goal=goal,
        principal=SimpleNamespace(),
        source_session=source_session,
        mechanism_refs=("metric.a", "metric.b"),
        evidence_refs=("evi_" + "1" * 24,),
    )

    assert seeded == ("metric.a", "metric.b")
    assert [item[0] for item in epistemics.hypotheses] == [
        "metric.a",
        "metric.b",
    ]
    assert len(epistemics.groundings) == 2
    assert all(
        item["relation"] == GroundingRelation.CONTEXT
        for item in epistemics.groundings
    )

def test_xray_h6_typed_relationship_intent_controls_policy_requirement():
    from app.v3.research_contracts import RelationshipIntent

    observational = ResearchQuestion(
        goal_id="g_rel_obs",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text="Observe association.",
        relationship_intent=RelationshipIntent.OBSERVATIONAL,
        status=ResearchGoalStatus.RESOLVED,
    )
    business = observational.model_copy(
        update={
            "goal_id": "g_rel_policy",
            "relationship_intent": RelationshipIntent.BUSINESS_POLICY,
        }
    )
    historical = observational.model_copy(
        update={"goal_id": "g_rel_legacy", "relationship_intent": None}
    )

    assert HeadlessProductComposer._relationship_policy_required(observational) is False
    assert HeadlessProductComposer._relationship_policy_required(business) is True
    assert HeadlessProductComposer._relationship_policy_required(historical) is True
