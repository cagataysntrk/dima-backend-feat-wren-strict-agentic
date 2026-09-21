"""Focused Day 6 / P9 ResearchBrief contracts.

All tests are provider-free and schema/data-independent. Canonical identifiers are
deliberately opaque/permuted so the product cannot pass by learning demo literals.
"""

from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

import pytest

from control_plane.authorize import Principal

import app.v2.orchestrator as orchestrator_module
from app.v2.context_provider import ContextProviderV0
from app.v2.dialogue_policy import DialoguePolicyV0
from app.v2.finalizer import ConversationFinalizerV0
from app.v2.interpreter import TurnInterpreter, TurnInterpreterError
from app.v2.models import (
    AskV2Request,
    BoundedSemanticContextV0,
    ContextVersionV0,
    CandidateSource,
    CompactRelationshipV0,
    ComparisonSurface,
    ClarificationReason,
    ClarificationState,
    ConversationResponseKind,
    ConversationStateV2,
    DialogueAction,
    PresentationKind,
    ResearchBriefStatus,
    ResearchDeliverableSurface,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchMode,
    ResearchModeReason,
    ResearchGoalSurface,
    ResearchRequestSurface,
    ResearchRelationshipSurface,
    RankingSurface,
    ResolutionStatus,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMention,
    SemanticMentionKind,
    SemanticResolutionBundle,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
    TurnAct,
    TurnInterpretation,
)
from app.v2.orchestrator import V2Orchestrator
from app.v2.research import ResearchBriefBuilder, ResearchModePolicy
from app.v2.resolver import SemanticResolver


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
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
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
                    kind=ResearchGoalKind.PERFORMANCE,
                    text="satış performanslarını yorumla",
                    subject_mentions=(sales,),
                ),
            ),
            relationships=(
                ResearchRelationshipSurface(
                    text="makineler ve personellerle ilişkisini analiz et",
                    focus_mentions=(product,),
                    counterpart_mentions=(machine, personnel),
                ),
            ),
            deliverables=(
                ResearchDeliverableSurface(
                    kind=PresentationKind.REPORT,
                    text="raporla",
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

    assert len(brief.questions) == 4
    assert brief.must_requirement_ids == ("g1", "g2", "g3", "g4", "d1")
    assert [q.kind for q in brief.questions] == [
        ResearchGoalKind.COMPARISON,
        ResearchGoalKind.PERFORMANCE,
        ResearchGoalKind.RELATIONSHIP,
        ResearchGoalKind.RELATIONSHIP,
    ]
    assert all(q.priority == "MUST" for q in brief.questions)
    assert all(q.status == ResearchGoalStatus.RESOLVED for q in brief.questions)
    assert len(brief.deliverables) == 1
    assert brief.deliverables[0].requirement_id == "d1"
    assert brief.deliverables[0].kind == PresentationKind.REPORT
    assert brief.deliverables[0].source_text == "raporla"
    assert brief.scope.time_surfaces == ("Son 12 ay",)
    assert brief.required_domains == ("fact_alpha", "fact_beta", "fact_gamma")
    assert brief.blocking_goal_ids == ()
    assert brief.status == ResearchBriefStatus.READY_FOR_RESEARCH


def test_research_brief_never_invents_unrequested_goals_or_domains():
    product = mention("öğeler", SemanticMentionKind.DIMENSION)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        presentation_request=PresentationKind.REPORT,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.COMPARISON,
                    text="öğeleri karşılaştır",
                    subject_mentions=(product,),
                ),
            ),
            deliverables=(
                ResearchDeliverableSurface(
                    kind=PresentationKind.REPORT,
                    text="rapor çıkar",
                ),
            ),
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

    assert [q.kind for q in brief.questions] == [ResearchGoalKind.COMPARISON]
    assert len(brief.questions) == 1
    assert brief.must_requirement_ids == ("g1", "d1")
    assert brief.deliverables[0].kind == PresentationKind.REPORT
    # Single-cube ownership is Resolver provenance, not a ResearchBrief guess.
    assert brief.required_domains == ("fact_delta",)
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

    assert len(brief.questions) == 4
    personnel_goal = next(
        question
        for question in brief.questions
        if any(item.source_mention == "personellerle" for item in question.unresolved)
    )
    assert personnel_goal.status == ResearchGoalStatus.BLOCKED
    assert personnel_goal.related_refs == ()
    assert personnel_goal.unresolved[0].source_mention == "personellerle"
    assert "axis_labor_z" not in {
        ref.canonical_name for ref in brief.scope.semantic_refs
    }
    assert brief.blocking_goal_ids == (personnel_goal.goal_id,)
    assert brief.status == ResearchBriefStatus.BLOCKED


def test_cross_domain_relationship_without_semantic_path_is_blocking():
    brief = ResearchBriefBuilder().build(
        turn=canonical_turn(),
        hypotheses=canonical_hypotheses(),
        semantic_context=research_context(cross_domain_path=False),
        context_version="ctx-permuted-no-path",
    )

    relationship_questions = [
        question
        for question in brief.questions
        if question.kind == ResearchGoalKind.RELATIONSHIP
    ]
    assert relationship_questions[0].status == ResearchGoalStatus.RESOLVED
    blocked = relationship_questions[1]
    assert blocked.status == ResearchGoalStatus.BLOCKED
    assert any(
        "no verified semantic relationship path" in item.reason
        for item in blocked.unresolved
    )
    assert brief.blocking_goal_ids == (blocked.goal_id,)
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


class _RelationshipSchemaService:
    def schema(self):
        return {
            "cubes": [
                {
                    "name": "cube_a",
                    "base_object": "model_a",
                    "measures": [],
                    "dimensions": [],
                    "time_dimensions": [],
                },
                {
                    "name": "cube_b",
                    "base_object": "model_b",
                    "measures": [],
                    "dimensions": [],
                    "time_dimensions": [],
                },
            ],
            "relationships": [
                {
                    "name": "rel_ab",
                    "models": ["model_a", "model_b"],
                    "join_type": "many_to_one",
                    "condition": "model_a.secret_id = model_b.secret_id",
                }
            ],
        }


def test_context_provider_exposes_cube_relation_without_join_condition():
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id="tenant-x",
        tenant_slug="tenant-x",
        principal_user_id="user-x",
        roles=("analyst",),
        mdl_version="mdl-x",
        db_online=True,
    )
    context = ContextProviderV0().build(_RelationshipSchemaService(), runtime)
    assert len(context.relationships) == 1
    relationship = context.relationships[0]
    assert relationship.cube_names == ("cube_a", "cube_b")
    assert relationship.models == ("model_a", "model_b")
    # Compact relationship contract deliberately has no physical join condition field.
    assert "condition" not in relationship.model_dump(mode="json")


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
            dialogue_act=TurnAct.COMPLEX_ANALYSIS,
            presentation_request=PresentationKind.REPORT,
            research_request=ResearchRequestSurface(
                goals=(
                    ResearchGoalSurface(
                        kind=ResearchGoalKind.COMPARISON,
                        text="items compare",
                        subject_mentions=(item,),
                    ),
                ),
                deliverables=(
                    ResearchDeliverableSurface(
                        kind=PresentationKind.REPORT,
                        text="report",
                    ),
                ),
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




def test_interpreter_normalizes_enum_case_without_semantic_schema_migration():
    question = "Ürünlerin makine ilişkisini incele ve raporla."
    llm = _StaticStructuredLlm(
        {
            "dialogue_act": "complex_analysis",
            "references": [],
            "analytical_request": None,
            "research_request": {
                "goals": [
                    {
                        "kind": "RELATIONSHIP",
                        "text": "Ürünlerin makine ilişkisini incele",
                        "subject_mentions": [
                            {"text": "Ürünlerin", "kind": "DIMENSION"}
                        ],
                        "related_mentions": [
                            {"text": "makine", "kind": "DIMENSION"}
                        ],
                        "ranking": None,
                        "comparisons": [],
                    }
                ],
                "time_mentions": [],
                "deliverables": [
                    {"kind": "REPORT", "text": "raporla"}
                ],
            },
            "presentation_request": "REPORT",
            "user_repair": None,
            "unresolved_mentions": [],
        }
    )

    turn = TurnInterpreter().interpret(
        question=question,
        semantic_context=_empty_context(),
        conversation=ConversationStateV2(),
        llm=llm,
    )

    assert llm.calls == 1
    assert turn.dialogue_act == TurnAct.COMPLEX_ANALYSIS
    assert turn.presentation_request == PresentationKind.REPORT
    assert turn.research_request is not None
    assert turn.research_request.goals[0].kind == ResearchGoalKind.RELATIONSHIP
    assert turn.research_request.deliverables[0].kind == PresentationKind.REPORT


def test_legacy_deliverable_pseudo_goal_is_not_silently_migrated():
    question = "Ürünlerin makine ilişkisini incele ve raporla."
    legacy_payload = {
        "dialogue_act": "COMPLEX_ANALYSIS",
        "references": [],
        "analytical_request": None,
        "research_request": {
            "goals": [
                {
                    "kind": "RELATIONSHIP",
                    "text": "Ürünlerin makine ilişkisini incele",
                    "subject_mentions": [
                        {"text": "Ürünlerin", "kind": "dimension"}
                    ],
                    "related_mentions": [
                        {"text": "makine", "kind": "dimension"}
                    ],
                    "ranking": None,
                    "comparisons": [],
                },
                {
                    "kind": "deliverable",
                    "text": "raporla",
                    "subject_mentions": [],
                    "related_mentions": [],
                },
            ],
            "time_mentions": [],
            "deliverables": [],
        },
        "presentation_request": "report",
        "user_repair": None,
        "unresolved_mentions": [],
    }
    llm = _StaticStructuredLlm(legacy_payload)

    with pytest.raises(TurnInterpreterError) as caught:
        TurnInterpreter().interpret(
            question=question,
            semantic_context=_empty_context(),
            conversation=ConversationStateV2(),
            llm=llm,
        )

    assert llm.calls == 2
    assert caught.value.failure.code == "invalid_structured_output"


def test_format_normalization_does_not_relax_surface_grounding():
    question = "Makinelerle ve personelle ilişkilerini ayrı incele."
    llm = _StaticStructuredLlm(
        {
            "dialogue_act": "COMPLEX_ANALYSIS",
            "references": [],
            "analytical_request": None,
            "research_request": {
                "goals": [
                    {
                        "kind": "RELATIONSHIP",
                        "text": "makinelerle ilişkilerini",
                        "subject_mentions": [
                            {"text": "makinelerle", "kind": "DIMENSION"}
                        ],
                        "related_mentions": [],
                        "deliverable": "none",
                    }
                ],
                "time_mentions": [],
            },
            "presentation_request": "NONE",
            "user_repair": None,
            "unresolved_mentions": [],
        }
    )

    with pytest.raises(TurnInterpreterError) as caught:
        TurnInterpreter().interpret(
            question=question,
            semantic_context=_empty_context(),
            conversation=ConversationStateV2(),
            llm=llm,
        )

    assert caught.value.failure.code == "surface_grounding_violation"


@pytest.mark.parametrize(
    "order",
    [
        (0, 1, 2, 3),
        (3, 0, 2, 1),
        (2, 1, 0, 3),
        (1, 3, 0, 2),
    ],
)
def test_goal_order_changes_never_drop_or_duplicate_must_requirements(order):
    base = canonical_turn()
    request = base.research_request
    assert request is not None
    reordered = tuple(request.goals[index] for index in order)
    turn = base.model_copy(
        update={"research_request": request.model_copy(update={"goals": reordered})}
    )

    brief = ResearchBriefBuilder().build(
        turn=turn,
        hypotheses=canonical_hypotheses(),
        semantic_context=research_context(),
        context_version="ctx-order",
    )

    assert len(brief.questions) == len(reordered)
    assert len(set(brief.must_requirement_ids)) == len(reordered) + len(request.deliverables)
    assert brief.must_requirement_ids[-1:] == ("d1",)
    assert [q.source_text for q in brief.questions] == [g.text for g in reordered]
    assert [q.kind for q in brief.questions] == [g.kind for g in reordered]


@pytest.mark.parametrize(
    ("surface", "expected_blocked"),
    [
        ("makineler", {"g2"}),
        ("personellerle", {"g3"}),
        ("satış performanslarını", {"g4"}),
        ("ürünleri", {"g1", "g2", "g3"}),
    ],
)
def test_semantic_gap_blocks_every_dependent_goal_without_silent_loss(
    surface,
    expected_blocked,
):
    hypotheses = []
    for hypothesis in canonical_hypotheses():
        if hypothesis.source_mention == surface:
            hypotheses.append(
                SemanticHypothesis(
                    source_mention=hypothesis.source_mention,
                    mention_kind=hypothesis.mention_kind,
                    status=ResolutionStatus.SEMANTIC_GAP,
                    candidates=(),
                )
            )
        else:
            hypotheses.append(hypothesis)

    brief = ResearchBriefBuilder().build(
        turn=canonical_turn(),
        hypotheses=tuple(hypotheses),
        semantic_context=research_context(),
        context_version="ctx-gap",
    )

    assert len(brief.questions) == 4
    assert set(brief.blocking_goal_ids) == expected_blocked
    assert {
        q.goal_id for q in brief.questions if q.status == ResearchGoalStatus.BLOCKED
    } == expected_blocked
    assert brief.must_requirement_ids == ("g1", "g2", "g3", "g4", "d1")
    assert brief.status == ResearchBriefStatus.BLOCKED


def test_clarify_hypothesis_is_blocking_not_auto_selected():
    hypotheses = list(canonical_hypotheses())
    original = hypotheses[1]
    candidate = original.candidates[0]
    hypotheses[1] = SemanticHypothesis(
        source_mention=original.source_mention,
        mention_kind=original.mention_kind,
        status=ResolutionStatus.CLARIFY,
        candidates=(
            candidate,
            candidate.model_copy(
                update={
                    "candidate_id": "cand-machine-alt",
                    "canonical_name": "axis_asset_alt",
                }
            ),
        ),
        resolved_candidate_id=None,
    )

    brief = ResearchBriefBuilder().build(
        turn=canonical_turn(),
        hypotheses=tuple(hypotheses),
        semantic_context=research_context(),
        context_version="ctx-clarify",
    )

    assert brief.questions[1].status == ResearchGoalStatus.BLOCKED
    assert brief.questions[1].related_refs == ()
    assert brief.blocking_goal_ids == ("g2",)


def test_multi_cube_resolver_provenance_is_not_collapsed_into_required_domain():
    product = mention("kalemleri", SemanticMentionKind.DIMENSION)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.COMPARISON,
                    text="kalemleri karşılaştır",
                    subject_mentions=(product,),
                ),
            )
        ),
    )
    candidate = SemanticCandidate(
        candidate_id="cand-multi",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="axis_shared_product",
        cube_names=("cube-left", "cube-right"),
        display_label="Shared Product",
        provenance=(CandidateSource.CANONICAL_NAME,),
        score=1.0,
        material=True,
    )
    hypotheses = (
        SemanticHypothesis(
            source_mention="kalemleri",
            mention_kind=SemanticMentionKind.DIMENSION,
            status=ResolutionStatus.RESOLVED,
            candidates=(candidate,),
            resolved_candidate_id="cand-multi",
        ),
    )

    brief = ResearchBriefBuilder().build(
        turn=turn,
        hypotheses=hypotheses,
        semantic_context=research_context(),
        context_version="ctx-multi",
    )

    assert brief.status == ResearchBriefStatus.READY_FOR_RESEARCH
    assert brief.required_domains == ()
    assert brief.scope.semantic_refs[0].cube_names == ("cube-left", "cube-right")


def test_sensitive_semantic_ref_never_copies_hidden_value():
    member = mention("özel üye", SemanticMentionKind.FILTER)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.BREAKDOWN,
                    text="özel üye için kırılımı incele",
                    subject_mentions=(member,),
                ),
            )
        ),
    )
    candidate = SemanticCandidate(
        candidate_id="cand-sensitive",
        target_kind=SemanticTargetKind.ENTITY_VALUE,
        canonical_name="dim_secret",
        dimension_name="dim_secret",
        value=None,
        cube_names=("cube-secret",),
        display_label="Sensitive member",
        provenance=(CandidateSource.EXACT_ENTITY_VALUE,),
        score=1.0,
        material=True,
        sensitive=True,
    )
    hypothesis = SemanticHypothesis(
        source_mention="özel üye",
        mention_kind=SemanticMentionKind.FILTER,
        status=ResolutionStatus.RESOLVED,
        candidates=(candidate,),
        resolved_candidate_id="cand-sensitive",
        resolved_surface_value="özel üye",
    )

    brief = ResearchBriefBuilder().build(
        turn=turn,
        hypotheses=(hypothesis,),
        semantic_context=research_context(),
        context_version="ctx-sensitive",
    )

    ref = brief.questions[0].subject_refs[0]
    assert ref.sensitive is True
    assert ref.value is None
    assert "özel üye" not in str(ref.model_dump(mode="json").get("value"))


def test_brief_id_is_deterministic_and_context_bound():
    builder = ResearchBriefBuilder()
    kwargs = dict(
        turn=canonical_turn(),
        hypotheses=canonical_hypotheses(),
        semantic_context=research_context(),
    )
    first = builder.build(context_version="ctx-one", **kwargs)
    same = builder.build(context_version="ctx-one", **kwargs)
    changed = builder.build(context_version="ctx-two", **kwargs)

    assert first.brief_id == same.brief_id
    assert first.brief_id != changed.brief_id


def test_deliverable_requirement_is_separate_from_research_questions_and_domains():
    brief = ResearchBriefBuilder().build(
        turn=canonical_turn(),
        hypotheses=canonical_hypotheses(),
        semantic_context=research_context(),
        context_version="ctx-deliverable",
    )

    assert len(brief.questions) == 4
    assert len(brief.deliverables) == 1
    deliverable = brief.deliverables[0]
    assert deliverable.requirement_id == "d1"
    assert deliverable.kind == PresentationKind.REPORT
    assert deliverable.priority == "MUST"
    assert deliverable.source_text == "raporla"
    assert "d1" in brief.must_requirement_ids
    assert all(question.kind != "deliverable" for question in brief.questions)


def test_transitive_semantic_relationship_path_can_make_brief_ready_without_join_plan():
    left = mention("sol alan", SemanticMentionKind.DIMENSION)
    right = mention("sağ alan", SemanticMentionKind.DIMENSION)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            relationships=(
                ResearchRelationshipSurface(
                    text="sol alan ile sağ alan ilişkisini incele",
                    focus_mentions=(left,),
                    counterpart_mentions=(right,),
                ),
            )
        ),
    )
    hypotheses = (
        resolved_hypothesis(
            text="sol alan",
            kind=SemanticMentionKind.DIMENSION,
            candidate_id="left",
            canonical_name="left_axis",
            target_kind=SemanticTargetKind.DIMENSION,
            cube="cube_a",
        ),
        resolved_hypothesis(
            text="sağ alan",
            kind=SemanticMentionKind.DIMENSION,
            candidate_id="right",
            canonical_name="right_axis",
            target_kind=SemanticTargetKind.DIMENSION,
            cube="cube_c",
        ),
    )
    context = research_context().model_copy(
        update={
            "relationships": (
                CompactRelationshipV0(name="ab", cube_names=("cube_a", "cube_b")),
                CompactRelationshipV0(name="bc", cube_names=("cube_b", "cube_c")),
            )
        }
    )

    brief = ResearchBriefBuilder().build(
        turn=turn,
        hypotheses=hypotheses,
        semantic_context=context,
        context_version="ctx-transitive",
    )

    assert brief.status == ResearchBriefStatus.READY_FOR_RESEARCH
    assert brief.blocking_goal_ids == ()


def test_research_budget_limits_are_not_invented_in_day6():
    brief = ResearchBriefBuilder().build(
        turn=canonical_turn(),
        hypotheses=canonical_hypotheses(),
        semantic_context=research_context(),
        context_version="ctx-budget",
    )
    assert brief.budget.max_data_queries is None
    assert brief.budget.max_branch_depth is None
    assert brief.budget.max_llm_turns is None
    assert brief.budget.max_wall_clock_seconds is None
    assert brief.budget.assignment == "deferred_to_research_execution_policy"


def test_unknown_research_anchor_survives_resolver_as_blocked_must_goal():
    unknown = mention("lojistik performansı", SemanticMentionKind.UNKNOWN)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.PERFORMANCE,
                    text="lojistik performansını değerlendir",
                    subject_mentions=(unknown,),
                ),
            )
        ),
    )
    resolver = SemanticResolver(signing_key=b"day6-unknown-anchor")
    bundle = resolver.resolve_turn(
        turn=turn,
        schema={"models": [], "cubes": [], "company_vocabulary": []},
        semantic_context=research_context(),
        conversation=ConversationStateV2(),
        tenant_binding="id:tenant-x",
        session_id="s-x",
        thread_id="t-x",
    )
    brief = ResearchBriefBuilder().build(
        turn=turn,
        hypotheses=bundle.hypotheses,
        semantic_context=research_context(),
        context_version="ctx-unknown-anchor",
    )

    assert len(brief.questions) == 1
    assert brief.must_requirement_ids == ("g1",)
    assert brief.questions[0].source_text == "lojistik performansını değerlendir"
    assert brief.questions[0].status == ResearchGoalStatus.BLOCKED
    assert brief.questions[0].subject_refs == ()
    assert brief.questions[0].unresolved[0].source_mention == "lojistik performansı"
    assert brief.blocking_goal_ids == ("g1",)
    assert brief.status == ResearchBriefStatus.BLOCKED


def test_research_mode_policy_ignores_report_presentation_for_standard_shape():
    metric = mention("satış performansını", SemanticMentionKind.METRIC)
    dimension = mention("ürün bazında", SemanticMentionKind.DIMENSION)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.REPORT_REQUEST,
        presentation_request=PresentationKind.REPORT,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.PERFORMANCE,
                    text="satış performansını",
                    subject_mentions=(metric,),
                ),
                ResearchGoalSurface(
                    kind=ResearchGoalKind.BREAKDOWN,
                    text="ürün bazında",
                    subject_mentions=(metric,),
                    related_mentions=(dimension,),
                ),
            ),
            deliverables=(
                ResearchDeliverableSurface(
                    kind=PresentationKind.REPORT,
                    text="raporla",
                ),
            ),
        ),
    )

    decision = ResearchModePolicy().decide(turn)

    assert decision.mode == ResearchMode.STANDARD
    assert decision.reason == ResearchModeReason.STANDARD_PROJECTABLE_OPERATIONS
    assert decision.canonical_turn.dialogue_act == TurnAct.ANALYTIC_NEW
    assert decision.canonical_turn.presentation_request == PresentationKind.REPORT
    assert decision.canonical_turn.research_request is None
    assert decision.canonical_turn.analytical_request is not None
    assert [m.text for m in decision.canonical_turn.analytical_request.metric_mentions] == [
        "satış performansını"
    ]
    assert [m.text for m in decision.canonical_turn.analytical_request.dimension_mentions] == [
        "ürün bazında"
    ]


@pytest.mark.parametrize(
    "presentation",
    [PresentationKind.NONE, PresentationKind.REPORT, PresentationKind.CHART, PresentationKind.TABLE],
)
def test_research_mode_policy_is_presentation_invariant_for_complex_shape(presentation):
    product = mention("ürünleri", SemanticMentionKind.DIMENSION)
    machine = mention("makine", SemanticMentionKind.DIMENSION)
    deliverables = (
        ()
        if presentation == PresentationKind.NONE
        else (
            ResearchDeliverableSurface(
                kind=presentation,
                text="çıktı",
            ),
        )
    )
    turn = TurnInterpretation(
        dialogue_act=(
            TurnAct.REPORT_REQUEST
            if presentation == PresentationKind.REPORT
            else TurnAct.COMPLEX_ANALYSIS
        ),
        presentation_request=presentation,
        research_request=ResearchRequestSurface(
            relationships=(
                ResearchRelationshipSurface(
                    text="ilişki",
                    focus_mentions=(product,),
                    counterpart_mentions=(machine,),
                ),
            ),
            deliverables=deliverables,
        ),
    )

    decision = ResearchModePolicy().decide(turn)

    assert decision.mode == ResearchMode.RESEARCH
    assert decision.reason == ResearchModeReason.COMPLEX_ONLY_OPERATION
    assert decision.canonical_turn.dialogue_act == TurnAct.COMPLEX_ANALYSIS
    assert decision.canonical_turn.presentation_request == presentation


def test_research_mode_policy_never_reads_deliverable_or_goal_text_for_route():
    source = inspect.getsource(ResearchModePolicy)
    assert ".deliverables" not in source
    assert "goal.text" not in source
    assert "re." not in source


def test_other_operation_is_fail_closed_not_research_escalation():
    unknown = mention("belirsiz eksen", SemanticMentionKind.UNKNOWN)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.OTHER,
                    text="belirsiz işlemi incele",
                    subject_mentions=(unknown,),
                ),
            )
        ),
    )

    decision = ResearchModePolicy().decide(turn)

    assert decision.mode == ResearchMode.BLOCKED
    assert decision.reason == ResearchModeReason.UNCLASSIFIED_OPERATION
    assert decision.canonical_turn.dialogue_act == TurnAct.UNSUPPORTED
    assert decision.canonical_turn.research_request is None
    assert decision.canonical_turn.analytical_request is None
    assert decision.canonical_turn.unresolved_mentions
    assert decision.canonical_turn.unresolved_mentions[-1].text == "belirsiz işlemi incele"


def test_standard_ranking_operation_projects_without_raw_text_reparse():
    metric = mention("metrik-z", SemanticMentionKind.METRIC)
    dimension = mention("eksen-q", SemanticMentionKind.DIMENSION)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.RANKING,
                    text="opaque ranking surface",
                    subject_mentions=(dimension,),
                    related_mentions=(metric,),
                    ranking=RankingSurface(
                        text="opaque ranking surface",
                        direction="desc",
                        limit=7,
                    ),
                ),
            ),
            time_mentions=(mention("opaque period", SemanticMentionKind.TIME),),
        ),
    )

    decision = ResearchModePolicy().decide(turn)

    assert decision.mode == ResearchMode.STANDARD
    assert decision.reason == ResearchModeReason.STANDARD_PROJECTABLE_OPERATIONS
    projected = decision.canonical_turn.analytical_request
    assert projected is not None
    assert [x.text for x in projected.metric_mentions] == ["metrik-z"]
    assert [x.text for x in projected.dimension_mentions] == ["eksen-q"]
    assert projected.ranking is not None
    assert projected.ranking.direction == "desc"
    assert projected.ranking.limit == 7
    assert [x.text for x in projected.time_mentions] == ["opaque period"]


def test_standard_period_comparison_projects_only_from_typed_comparison_payload():
    metric = mention("metrik-p", SemanticMentionKind.METRIC)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.COMPARISON,
                    text="opaque comparison operation",
                    subject_mentions=(metric,),
                    comparisons=(
                        ComparisonSurface(text="opaque reference period"),
                    ),
                ),
            ),
            time_mentions=(mention("opaque base period", SemanticMentionKind.TIME),),
        ),
    )

    decision = ResearchModePolicy().decide(turn)

    assert decision.mode == ResearchMode.STANDARD
    projected = decision.canonical_turn.analytical_request
    assert projected is not None
    assert [x.text for x in projected.metric_mentions] == ["metrik-p"]
    assert [x.text for x in projected.comparisons] == ["opaque reference period"]
    assert [x.text for x in projected.time_mentions] == ["opaque base period"]


def test_generic_comparison_without_core_payload_is_blocked_not_research():
    dimension = mention("eksen-k", SemanticMentionKind.DIMENSION)
    turn = TurnInterpretation(
        dialogue_act=TurnAct.COMPLEX_ANALYSIS,
        research_request=ResearchRequestSurface(
            goals=(
                ResearchGoalSurface(
                    kind=ResearchGoalKind.COMPARISON,
                    text="opaque generic comparison",
                    subject_mentions=(dimension,),
                ),
            )
        ),
    )

    decision = ResearchModePolicy().decide(turn)

    assert decision.mode == ResearchMode.BLOCKED
    assert decision.reason == ResearchModeReason.INCOMPLETE_STANDARD_OPERATION
    assert decision.canonical_turn.dialogue_act == TurnAct.UNSUPPORTED


def test_research_mode_policy_declares_core_capabilities_instead_of_fixture_cases():
    source = inspect.getsource(ResearchModePolicy)
    assert "_STANDARD_CAPABLE" in source
    assert "ResearchGoalKind.RANKING" in source
    assert "ResearchGoalKind.COMPARISON" in source
    assert "ResearchGoalKind.OTHER" in source
    assert "goal.text" not in source
    for forbidden in ("ürün", "makine", "personel", "satış", "Gemini"):
        assert forbidden not in source


def test_relationship_surface_schema_rejects_multiple_focus_endpoints():
    a = mention("a", SemanticMentionKind.DIMENSION)
    b = mention("b", SemanticMentionKind.DIMENSION)
    c = mention("c", SemanticMentionKind.DIMENSION)
    with pytest.raises(ValueError):
        ResearchRelationshipSurface(
            text="a b c",
            focus_mentions=(a, b),
            counterpart_mentions=(c,),
        )
