from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

from app.v3.product.composition import (
    HeadlessProductComposer,
    ProductCompositionTerminal,
    ProductRequirementDisposition,
)
from app.v3.research_analytical_scope import coorigin_material_requirements
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
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_intake import (
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
)


def _ref(candidate_id: str, kind: SemanticTargetKind) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=kind,
        canonical_name=candidate_id,
        cube_names=("machine_operations",),
    )


EFFECT = _ref("metric.effect", SemanticTargetKind.METRIC)
H1 = _ref("metric.h1", SemanticTargetKind.METRIC)
H2 = _ref("metric.h2", SemanticTargetKind.METRIC)
DIM = _ref("dimension.segment", SemanticTargetKind.DIMENSION)


class _FakeTransport:
    def __init__(self, payload: dict):
        self.payload = payload
        self.call_count = 0

    def structured_json(self, system, user, *, schema, schema_name):
        self.call_count += 1
        return json.dumps({"result": self.payload})


def _rca_payload() -> tuple[str, dict]:
    clause1 = "Investigate H1 versus H2 for the governed effect."
    clause2 = "Keep supporting and challenging evidence separate."
    current = clause1 + " " + clause2
    payload = {
        "terminal": "READY",
        "objective": current,
        "goals": [
            {
                "goal_key": "root",
                "kind": "root_cause",
                "source_text": clause1,
                "source_fragment_text": clause1,
                "subject_semantic_ids": [
                    EFFECT.candidate_id,
                    H1.candidate_id,
                    H2.candidate_id,
                ],
                "related_semantic_ids": [DIM.candidate_id],
                "ranking": None,
                "comparisons": [
                    {
                        "text": "H1",
                        "role": "causal_candidate",
                        "semantic_id": H1.candidate_id,
                    },
                    {
                        "text": "H2",
                        "role": "causal_candidate",
                        "semantic_id": H2.candidate_id,
                    },
                ],
                "causal_competition": {
                    "effect_semantic_id": EFFECT.candidate_id,
                    "candidate_mechanism_semantic_ids": [
                        H1.candidate_id,
                        H2.candidate_id,
                    ],
                    "diagnostic_dimension_ids": [DIM.candidate_id],
                },
            },
            {
                "goal_key": "evidence-separation",
                "kind": "other",
                "source_text": clause2,
                "source_fragment_text": clause2,
                "subject_semantic_ids": [
                    EFFECT.candidate_id,
                    H1.candidate_id,
                    H2.candidate_id,
                ],
                "related_semantic_ids": [DIM.candidate_id],
                "ranking": None,
                "comparisons": [],
                "causal_competition": None,
            },
        ],
        "deliverables": [
            {
                "key": "report",
                "kind": "report",
                "source_text": clause2,
            }
        ],
        "investigation_directives": [],
        "time_periods": [],
        "required_domains": ["machine_operations"],
        "scope_mutation_kind": None,
    }
    return current, payload


def _catalog() -> ResearchIntakeCatalog:
    return ResearchIntakeCatalog(
        context_version="phase1-5-xray",
        semantic_refs=(EFFECT, H1, H2, DIM),
        supported_domains=("machine_operations",),
    )


def test_xray_h1_current_intake_accepts_epistemic_directive_as_second_analytical_goal():
    current, payload = _rca_payload()
    result = ResearchIntakeCompiler(
        transport=_FakeTransport(payload),
        calendar_reference_date="2026-09-30",
    ).compile(question=current, catalog=_catalog())

    assert result.brief is not None
    assert [item.kind for item in result.brief.questions] == [
        ResearchGoalKind.ROOT_CAUSE,
        ResearchGoalKind.OTHER,
    ]
    assert len(result.brief.questions) == 2
    assert len(result.brief.deliverables) == 1


class _FakeResearch:
    def __init__(self, brief: ResearchBrief):
        self.states = {item.goal_id: "PENDING" for item in brief.questions}
        self.run_calls: list[str] = []

    def resume_state(self, *, session_id, principal):
        return SimpleNamespace(
            obligations=tuple(
                SimpleNamespace(obligation_id=key, state=value)
                for key, value in self.states.items()
            )
        )

    def run_next(
        self,
        *,
        session_id,
        principal,
        obligation_id,
        native_session_token,
    ):
        self.run_calls.append(obligation_id)
        self.states[obligation_id] = "VERIFIED"


def test_xray_h2_same_fact_set_is_executed_once_per_inflated_goal_today():
    current, payload = _rca_payload()
    brief = ResearchIntakeCompiler(
        transport=_FakeTransport(payload),
        calendar_reference_date="2026-09-30",
    ).compile(question=current, catalog=_catalog()).brief
    assert brief is not None
    first, second = brief.questions
    first_facts = {x.candidate_id for x in (*first.subject_refs, *first.related_refs)}
    second_facts = {x.candidate_id for x in (*second.subject_refs, *second.related_refs)}
    assert first_facts == second_facts

    research = _FakeResearch(brief)
    owner_calls: list[str] = []
    HeadlessProductComposer._run_p14(
        research=research,
        session_id="rs_xray",
        brief=brief,
        principal=SimpleNamespace(),
        native_session_token="token",
        owner_calls=owner_calls,
    )
    assert research.run_calls == [first.goal_id, second.goal_id]
    assert owner_calls == ["P14", "P14"]


def _direct_brief(*questions: ResearchQuestion, deliverables=()) -> ResearchBrief:
    return ResearchBrief(
        brief_id="rb-phase1-5-xray",
        objective="Characterize current orchestration.",
        scope=ResearchScope(),
        questions=questions,
        deliverables=tuple(deliverables),
        must_requirement_ids=tuple(
            [item.goal_id for item in questions]
            + [item.requirement_id for item in deliverables]
        ),
        context_version="phase1-5-xray",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def test_xray_h5_non_report_deliverable_becomes_unsupported_even_when_analytics_succeed():
    question = ResearchQuestion(
        goal_id="g_metric",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Inspect the governed metric.",
        subject_refs=(EFFECT,),
        related_refs=(DIM,),
        status=ResearchGoalStatus.RESOLVED,
    )
    report = ResearchDeliverableRequirement(
        requirement_id="d_report",
        kind=PresentationKind.REPORT,
        source_text="Produce a report.",
    )
    explain = ResearchDeliverableRequirement(
        requirement_id="d_explain",
        kind=PresentationKind.EXPLAIN,
        source_text="Explain the governed result.",
    )
    brief = _direct_brief(question, deliverables=(report, explain))
    session = SimpleNamespace(
        obligations=(SimpleNamespace(obligation_id=question.goal_id, state="VERIFIED"),)
    )
    projected, _, _, _ = HeadlessProductComposer._project_user_must(
        brief=brief,
        session=session,
        report=SimpleNamespace(report_id="p20r_" + "1" * 24),
    )
    ledger = HeadlessProductComposer._completion_ledger(
        brief=brief,
        projected=projected,
        terminal=ProductCompositionTerminal.REPORT,
    )
    by_id = {item.requirement_id: item.disposition for item in ledger.entries}
    assert by_id["d_report"] == ProductRequirementDisposition.FULFILLED
    assert by_id["d_explain"] == ProductRequirementDisposition.UNSUPPORTED


def test_xray_h6_relationship_path_forces_business_policy_required():
    source = inspect.getsource(HeadlessProductComposer._resolve_relationship)
    assert "RelationshipPolicyRequirement(" in source
    assert "required=True" in source


def test_xray_h7_cross_fragment_exact_provenance_prevents_material_sharing():
    ranking = ResearchQuestion(
        goal_id="g_rank",
        kind=ResearchGoalKind.RANKING,
        source_text="Rank the effect by segment.",
        source_fragment_identity="fragment-sha256:" + "1" * 64,
        subject_refs=(EFFECT,),
        related_refs=(DIM,),
        status=ResearchGoalStatus.RESOLVED,
    )
    relationship = ResearchQuestion(
        goal_id="g_relationship",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text="Compare H1 for those segments.",
        source_fragment_identity="fragment-sha256:" + "2" * 64,
        subject_refs=(EFFECT, H1),
        related_refs=(DIM,),
        status=ResearchGoalStatus.RESOLVED,
    )
    brief = _direct_brief(ranking, relationship)
    session = SimpleNamespace(accepted_brief=brief, context_version=brief.context_version)
    assert coorigin_material_requirements(session) == ()


class _FakeInvestigation:
    def __init__(self):
        self.run_count = 0

    def run_one(self, **kwargs):
        self.run_count += 1
        return SimpleNamespace(), SimpleNamespace()

    def snapshot(self, **kwargs):
        return SimpleNamespace()


def test_xray_h8_user_seeded_candidate_synthesis_runs_p17_once_per_candidate():
    goal = ResearchQuestion(
        goal_id="g_root",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text="Evaluate H1 versus H2.",
        subject_refs=(EFFECT, H1, H2),
        related_refs=(DIM,),
        causal_competition=CausalCompetitionSurface(
            effect_semantic_id=EFFECT.candidate_id,
            candidate_mechanism_semantic_ids=(H1.candidate_id, H2.candidate_id),
            diagnostic_dimension_ids=(DIM.candidate_id,),
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    composer = object.__new__(HeadlessProductComposer)
    composer._investigation = _FakeInvestigation()
    composer._investigation_manager = SimpleNamespace()
    owner_calls: list[str] = []

    composer._synthesize_root_candidates(
        session_id="rs_xray",
        goal=goal,
        principal=SimpleNamespace(),
        native_session_token="token",
        owner_calls=owner_calls,
        mechanism_refs=(H1.candidate_id, H2.candidate_id),
        evidence_refs=("evi_" + "1" * 24,),
    )

    assert composer._investigation.run_count == 2
    assert owner_calls == ["P17", "P17"]
