"""Focused Day 6 / P9 ResearchBrief contracts.

All tests are provider-free and schema/data-independent. Canonical identifiers are
deliberately opaque/permuted so the product cannot pass by learning demo literals.
"""

from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

from control_plane.authorize import Principal

import app.v2.orchestrator as orchestrator_module
from app.v2.dialogue_policy import DialoguePolicyV0
from app.v2.finalizer import ConversationFinalizerV0
from app.v2.interpreter import TurnInterpreter, TurnInterpreterError
from app.v2.models import (
    AskV2Request,
    BoundedSemanticContextV0,
    ContextVersionV0,
    CandidateSource,
    CompactRelationshipV0,
    ClarificationReason,
    ClarificationState,
    ConversationResponseKind,
    ConversationStateV2,
    DialogueAction,
    PresentationKind,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchGoalSurface,
    ResearchRequestSurface,
    ResolutionStatus,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMention,
    SemanticMentionKind,
    SemanticResolutionBundle,
    SemanticTargetKind,
    TurnAct,
    TurnInterpretation,
)
from app.v2.orchestrator import V2Orchestrator
from app.v2.research import ResearchBriefBuilder


def mention(text: str, kind: SemanticMentionKind) -> SemanticMention:
    return SemanticMention(text=text, kind=kind)


def resolved_hypothesis(
    *,
    text: str,
    kind: SemanticMentionKind,
    candidate_id: str,
    canonical_name: str,
    target_kind: SemanticTargetKind,
    cube: str,
) -> SemanticHypothesis:
    candidate = SemanticCandidate(
        candidate_id=candidate_id,
        target_kind=target_kind,
        canonical_name=canonical_name,
        cube_names=(cube,),
        display_label=canonical_name,
        provenance=(CandidateSource.CANONICAL_NAME,),
        score=1.0,
        material=True,
    )
    return SemanticHypothesis(
        source_mention=text,
        mention_kind=kind,
        status=ResolutionStatus.RESOLVED,
        candidates=(candidate,),
        resolved_candidate_id=candidate_id,
    )


def research_context(*, cross_domain_path: bool = True) -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-research-day6",
            mdl_version="mdl-research-day6",
            compact_catalog_builder_version="test",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="test",
        ),
        relationships=(
            (
                CompactRelationshipV0(
                    name="rel-opaque",
                    cube_names=("fact_alpha", "fact_beta"),
                    certified="verified",
                ),
            )
            if cross_domain_path
            else ()
        ),
    )


def canonical_turn() -> TurnInterpretation:
    product = mention("ürünleri", SemanticMentionKind.DIMENSION)
    machine = mention("makineler", SemanticMentionKind.DIMENSION)
    personnel = mention("personellerle", SemanticMentionKind.DIMENSION)
    sales = mention("satış performanslarını", SemanticMentionKind.METRIC)
    return TurnInterpretation(
        dialogue_act=TurnAct.REPORT_REQUEST,
        presentation_request=PresentationKind.REPORT,
        research_request=ResearchRequestSurface(
            time_mentions=(mention("Son 12 ay", SemanticMentionKind.TIME),),
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.COMPARISON,
                    text="ürünleri karşılaştır",
                    subject_mentions=(product,),
                ),
                ResearchGoalSurface(
                    kind=ResearchGoalKind.RELATIONSHIP,
                    text="makineler ve personellerle ilişkisini analiz et",
                    subject_mentions=(product,),
                    related_mentions=(machine,),
                ),
                ResearchGoalSurface(
                    kind=ResearchGoalKind.RELATIONSHIP,
                    text="personellerle ilişkisini analiz et",
                    subject_mentions=(product,),
                    related_mentions=(personnel,),
                ),
                ResearchGoalSurface(
                    kind=ResearchGoalKind.PERFORMANCE,
                    text="satış performanslarını yorumla",
                    subject_mentions=(sales,),
                ),
                ResearchGoalSurface(
                    kind=ResearchGoalKind.DELIVERABLE,
                    text="raporla",
                    deliverable=PresentationKind.REPORT,
                ),
            ),
        ),
    )


def canonical_hypotheses() -> tuple[SemanticHypothesis, ...]:
    return (
        resolved_hypothesis(
            text="ürünleri",
            kind=SemanticMentionKind.DIMENSION,
            candidate_id="cand-product",
            canonical_name="axis_product_x",
            target_kind=SemanticTargetKind.DIMENSION,
            cube="fact_alpha",
        ),
        resolved_hypothesis(
            text="makineler",
            kind=SemanticMentionKind.DIMENSION,
            candidate_id="cand-machine",
            canonical_name="axis_asset_q",
            target_kind=SemanticTargetKind.DIMENSION,
            cube="fact_alpha",
        ),
        resolved_hypothesis(
            text="personellerle",
            kind=SemanticMentionKind.DIMENSION,
            candidate_id="cand-personnel",
            canonical_name="axis_labor_z",
            target_kind=SemanticTargetKind.DIMENSION,
            cube="fact_beta",
        ),
        resolved_hypothesis(
            text="satış performanslarını",
            kind=SemanticMentionKind.METRIC,
            candidate_id="cand-sales",
            canonical_name="metric_sales_y",
            target_kind=SemanticTargetKind.METRIC,
            cube="fact_gamma",
        ),
    )


def test_canonical_typed_research_brief_preserves_all_five_must_goals():
    brief = ResearchBriefBuilder().build(
        turn=canonical_turn(),
        hypotheses=canonical_hypotheses(),
        semantic_context=research_context(),
        context_version="ctx-permuted-a",
    )

    assert len(brief.questions) == 5
    assert brief.must_requirement_ids == ("g1", "g2", "g3", "g4", "g5")
    assert [q.kind for q in brief.questions] == [
        ResearchGoalKind.COMPARISON,
        ResearchGoalKind.RELATIONSHIP,
        ResearchGoalKind.RELATIONSHIP,
        ResearchGoalKind.PERFORMANCE,
        ResearchGoalKind.DELIVERABLE,
    ]
    assert all(q.priority == "MUST" for q in brief.questions)
    assert all(q.status == ResearchGoalStatus.RESOLVED for q in brief.questions)
    assert brief.deliverables == (PresentationKind.REPORT,)
    assert brief.scope.time_surfaces == ("Son 12 ay",)
    assert brief.blocking_goal_ids == ()
    assert brief.status == ResearchBriefStatus.READY_FOR_RESEARCH


def test_research_brief_never_invents_unrequested_goals_or_domains():
    product = mention("öğeler", SemanticMentionKind.DIMENSION)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.REPORT_REQUEST,
        presentation_request=PresentationKind.REPORT,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.COMPARISON,
                    text="öğeleri karşılaştır",
                    subject_mentions=(product,),
                ),
                ResearchGoalSurface(
                    kind=ResearchGoalKind.DELIVERABLE,
                    text="rapor çıkar",
                    deliverable=PresentationKind.REPORT,
                ),
            )
        ),
    )
    hypotheses = (
        resolved_hypothesis(
            text="öğeler",
            kind=SemanticMentionKind.DIMENSION,
            candidate_id="cand-item",
            canonical_name="axis_item_p9",
            target_kind=SemanticTargetKind.DIMENSION,
            cube="fact_delta",
        ),
    )

    brief = ResearchBriefBuilder().build(
        turn=turn,
        hypotheses=hypotheses,
        semantic_context=research_context(),
        context_version="ctx-permuted-b",
    )

    assert [q.kind for q in brief.questions] == [
        ResearchGoalKind.COMPARISON,
        ResearchGoalKind.DELIVERABLE,
    ]
    assert len(brief.questions) == 2
    # cube_names are provenance, not permission to invent an explicit domain goal.
    assert brief.required_domains == ()
    assert {ref.canonical_name for ref in brief.scope.semantic_refs} == {"axis_item_p9"}


def test_unresolved_must_relationship_is_preserved_and_blocks_brief():
    turn = canonical_turn()
    hypotheses = list(canonical_hypotheses())
    hypotheses[2] = SemanticHypothesis(
        source_mention="personellerle",
        mention_kind=SemanticMentionKind.DIMENSION,
        status=ResolutionStatus.SEMANTIC_GAP,
        candidates=(),
        resolved_candidate_id=None,
    )

    brief = ResearchBriefBuilder().build(
        turn=turn,
        hypotheses=tuple(hypotheses),
        semantic_context=research_context(),
        context_version="ctx-permuted-c",
    )

    assert len(brief.questions) == 5
    personnel_goal = brief.questions[2]
    assert personnel_goal.goal_id == "g3"
    assert personnel_goal.status == ResearchGoalStatus.BLOCKED
    assert personnel_goal.related_refs == ()
    assert personnel_goal.unresolved[0].source_mention == "personellerle"
    assert "axis_labor_z" not in {
        ref.canonical_name for ref in brief.scope.semantic_refs
    }
    assert brief.blocking_goal_ids == ("g3",)
    assert brief.status == ResearchBriefStatus.BLOCKED


def test_cross_domain_relationship_without_semantic_path_is_blocking():
    brief = ResearchBriefBuilder().build(
        turn=canonical_turn(),
        hypotheses=canonical_hypotheses(),
        semantic_context=research_context(cross_domain_path=False),
        context_version="ctx-permuted-no-path",
    )

    # Machine relation shares fact_alpha and remains semantically available.
    assert brief.questions[1].status == ResearchGoalStatus.RESOLVED
    # Personnel ref resolves, but fact_alpha -> fact_beta has no typed semantic path.
    assert brief.questions[2].status == ResearchGoalStatus.BLOCKED
    assert any(
        "no verified semantic relationship path" in item.reason
        for item in brief.questions[2].unresolved
    )
    assert brief.blocking_goal_ids == ("g3",)
    assert brief.status == ResearchBriefStatus.BLOCKED


def test_research_builder_cannot_reparse_raw_user_prompt():
    params = inspect.signature(ResearchBriefBuilder.build).parameters
    assert "question" not in params
    assert "raw_prompt" not in params
    source = inspect.getsource(__import__("app.v2.research", fromlist=["*"]))
    for forbidden in ("WrenService", "dry_plan(", ".query(", "CubePlanner"):
        assert forbidden not in source


def test_dialogue_policy_preserves_complex_brief_before_first_clarification():
    turn = canonical_turn()
    bundle = SemanticResolutionBundle(
        hypotheses=(),
        clarification=ClarificationState(
            pending=True,
            clarification_id="clar-x",
            source_mention="personellerle",
            source_kind=SemanticMentionKind.DIMENSION,
            reason=ClarificationReason.SEMANTIC_GAP,
            question="Bu eksen semantic modelde nasıl bağlanmalı?",
        ),
    )
    action = DialoguePolicyV0().after_grounding(turn=turn, bundle=bundle)
    assert action == DialogueAction.RESEARCH_BRIEF


class _NoQueryService:
    mdl_version = "mdl-day6"

    def __init__(self):
        self.query_calls = 0
        self.dry_plan_calls = 0

    def schema(self):
        return {
            "catalog": "synthetic",
            "schema_name": "synthetic",
            "db_online": True,
            "cubes": [
                {
                    "name": "fact_x",
                    "display": "Fact X",
                    "measures": [],
                    "dimensions": ["axis_item"],
                    "dimension_synonyms": {"axis_item": ["items"]},
                    "dimension_labels": {"axis_item": "Items"},
                    "time_dimensions": [],
                }
            ],
        }

    def dry_plan(self, *args, **kwargs):
        self.dry_plan_calls += 1
        raise AssertionError("Day 6 must not dry-plan")

    def query(self, *args, **kwargs):
        self.query_calls += 1
        raise AssertionError("Day 6 must not execute query")


class _TypedResearchInterpreter:
    def interpret(self, **kwargs):
        item = mention("items", SemanticMentionKind.DIMENSION)
        return TurnInterpretation(
            dialogue_act=TurnAct.REPORT_REQUEST,
            presentation_request=PresentationKind.REPORT,
            research_request=ResearchRequestSurface(
                goals=(
                    ResearchGoalSurface(
                        kind=ResearchGoalKind.COMPARISON,
                        text="items compare",
                        subject_mentions=(item,),
                    ),
                    ResearchGoalSurface(
                        kind=ResearchGoalKind.DELIVERABLE,
                        text="report",
                        deliverable=PresentationKind.REPORT,
                    ),
                )
            ),
        )


def test_day6_orchestrator_stops_before_wren_execution(monkeypatch):
    service = _NoQueryService()
    monkeypatch.setattr(orchestrator_module, "wren_for_request", lambda request: service)

    orchestrator = V2Orchestrator()
    orchestrator._interpreter = _TypedResearchInterpreter()

    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(llm=object()))
    )
    body = AskV2Request(
        question="synthetic complex request",
        session_id="s-day6",
        thread_id="t-day6",
        conversation=ConversationStateV2(),
    )
    principal = Principal(
        user_id="user-day6",
        tenant_id="tenant-day6",
        tenant_slug="tenant-day6",
        roles=["analyst"],
    )

    core = orchestrator.handle(request, body, principal)
    out = ConversationFinalizerV0().finalize(core)

    assert core.dialogue_action == DialogueAction.RESEARCH_BRIEF
    assert core.query_execution_count == 0
    assert service.dry_plan_calls == 0
    assert service.query_calls == 0
    assert core.research_brief is not None
    assert core.research_brief.status == ResearchBriefStatus.READY_FOR_RESEARCH
    assert out.status == "research_brief"
    assert out.stage == "day6_research_brief"
    assert out.response.kind == ConversationResponseKind.RESEARCH_BRIEF
    assert out.next_stage == "research_ready_day7"


class _StaticStructuredLlm:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls = 0

    def structured_text(self, system: str, user: str) -> str:
        self.calls += 1
        return json.dumps(self.payload, ensure_ascii=False)


def _empty_context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-surface-day6",
            mdl_version="mdl-surface-day6",
            compact_catalog_builder_version="test",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="test",
        )
    )


def test_interpreter_rejects_invented_research_goal_surface_before_resolver():
    question = "Son 12 ay ürünleri karşılaştır ve raporla."
    llm = _StaticStructuredLlm(
        {
            "dialogue_act": "REPORT_REQUEST",
            "references": [],
            "analytical_request": None,
            "research_request": {
                "goals": [
                    {
                        "kind": "comparison",
                        "text": "ürünleri karşılaştır",
                        "subject_mentions": [
                            {"text": "ürünleri", "kind": "dimension"}
                        ],
                        "related_mentions": [],
                        "deliverable": None,
                    },
                    {
                        "kind": "relationship",
                        "text": "uydurulmuş personel ilişkisi",
                        "subject_mentions": [
                            {"text": "ürünleri", "kind": "dimension"}
                        ],
                        "related_mentions": [],
                        "deliverable": None,
                    },
                    {
                        "kind": "deliverable",
                        "text": "raporla",
                        "subject_mentions": [],
                        "related_mentions": [],
                        "deliverable": "report",
                    },
                ],
                "time_mentions": [
                    {"text": "Son 12 ay", "kind": "time"}
                ],
            },
            "presentation_request": "report",
            "user_repair": None,
            "unresolved_mentions": [],
        }
    )

    try:
        TurnInterpreter().interpret(
            question=question,
            semantic_context=_empty_context(),
            conversation=ConversationStateV2(),
            llm=llm,
        )
    except TurnInterpreterError as exc:
        assert exc.failure.code == "surface_grounding_violation"
        assert "uydurulmuş personel ilişkisi" in exc.failure.message
    else:
        raise AssertionError("invented research goal surface must fail closed")
