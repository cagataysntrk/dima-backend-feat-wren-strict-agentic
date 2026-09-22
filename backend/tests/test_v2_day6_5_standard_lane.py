from __future__ import annotations

import ast
import inspect

from app.v2.manager_models import ManagerCapabilityKey
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
)
from app.v2.semantic_linker import (
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
from app.v2.standard_lane import (
    StandardIntentDraft,
    StandardLaneEngine,
    StandardLaneStatus,
)


class _SemanticProvider:
    def decide(self, requests):
        choices = []
        for request in requests:
            if request.surface == "net geliri":
                target = next(
                    card.candidate_id
                    for card in request.candidates
                    if card.label == "Net Gelir"
                )
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=target,
                    )
                )
            else:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="ABSTAIN",
                        reason="AMBIGUOUS",
                    )
                )
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _Execution:
    pass


def _context():
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-si",
            mdl_version="mdl-si",
            compact_catalog_builder_version="si-test",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="si-test",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="Sales",
                display="Satış",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="Sales.net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir",),
                    ),
                ),
                dimensions=(),
                time_dimensions=("event_date",),
            ),
        ),
    )


def _schema():
    return {"models": [], "cubes": [{"name": "Sales", "dimension_values": {}}]}


def _draft_response(capability="performance"):
    return {
        "obligations": [
            {
                "obligation_id": "U1",
                "capability_key": capability,
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["net geliri"],
                "semantic_surfaces": (
                    [{"surface": "net geliri", "kind_hint": "metric"}]
                    if capability != "relationship"
                    else []
                ),
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [],
    }


def _coverage_pass(system, user, *, schema, schema_name):
    assert schema_name == "dima_standard_coverage_v1"
    return {"status": "PASS", "issues": []}


def test_standard_lane_module_has_no_research_authority_dependencies():
    import app.v2.standard_lane as module

    tree = ast.parse(inspect.getsource(module))
    imported = set()
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)

    assert "AcceptedTurnContract" not in imported
    assert "UserObligationLedger" not in imported
    assert "ResearchManagerLoop" not in imported
    assert "ManagerRuntime" not in imported
    assert "app.v2.manager_runtime" not in modules
    assert "app.v2.manager_loop" not in modules


def test_standard_intent_draft_is_closed_and_typed():
    draft = StandardIntentDraft.model_validate(_draft_response())
    assert draft.obligations[0].capability_key == ManagerCapabilityKey.PERFORMANCE


def test_research_capability_stops_without_standard_authority(monkeypatch):
    def intent(system, user, *, schema, schema_name):
        assert schema_name == "dima_standard_intent_draft_v1"
        return _draft_response("relationship")

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        temporal_provider=None,
    )

    outcome = engine.run(
        question="net geliri",
        turn_id="turn-research",
        request_ref="request-research",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="RESEARCH_MANAGER",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )
    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.authority is None
    assert outcome.projection is None
    assert engine.authority_registry.accepted("turn-research") is None



class _AlwaysAbstainProvider:
    def decide(self, requests):
        return SemanticLinkBatchDecision(
            choices=tuple(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="ABSTAIN",
                    reason="AMBIGUOUS",
                )
                for request in requests
            )
        )


def _rich_context():
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-si-rich",
            mdl_version="mdl-si-rich",
            compact_catalog_builder_version="si-rich-test",
            business_rules_hash="1" * 64,
            prompt_context_policy_version="si-rich-test",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="Sales",
                display="Satış",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="Sales.net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="Sales.gross_margin",
                        display="Brüt Marj",
                        synonyms=("brüt marj",),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="Sales.region",
                        display="Bölge",
                        synonyms=("bölge",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="Sales.channel",
                        display="Kanal",
                        synonyms=("kanal",),
                    ),
                ),
                time_dimensions=("event_date",),
            ),
        ),
    )


def _rich_schema():
    return {
        "models": [],
        "cubes": [
            {
                "name": "Sales",
                "dimension_values": {
                    "Sales.region": ["Kuzey", "Güney"],
                    "Sales.channel": ["Web", "Mağaza"],
                },
            }
        ],
    }


def _draft(obligations):
    return {"obligations": obligations, "control_requests": []}


def _obligation(
    *,
    obligation_id,
    capability,
    source_surfaces,
    semantic_surfaces,
    origin="USER_MUST",
    priority="MUST",
):
    return {
        "obligation_id": obligation_id,
        "capability_key": capability,
        "origin": origin,
        "priority": priority,
        "polarity": "REQUIRED",
        "source_surfaces": list(source_surfaces),
        "semantic_surfaces": [
            {"surface": surface, "kind_hint": kind}
            for surface, kind in semantic_surfaces
        ],
        "ranking_direction": None,
        "ranking_limit": None,
    }


def _run_surface_case(monkeypatch, *, question, draft_payload):
    def intent(system, user, *, schema, schema_name):
        assert schema_name == "dima_standard_intent_draft_v1"
        return draft_payload

    execution_calls = []

    def no_execution(*args, **kwargs):
        execution_calls.append((args, kwargs))
        raise AssertionError("unresolved semantic surface reached execution")

    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        no_execution,
    )

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=_coverage_pass,
        semantic_provider=_AlwaysAbstainProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-surface-accounting",
        request_ref="request-surface-accounting",
        semantic_context=_rich_context(),
        schema=_rich_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="STANDARD_PROFILE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )
    return engine, outcome, execution_calls


def test_partial_same_kind_metric_binding_fails_closed(monkeypatch):
    question = "net gelir ve belirsiz marj"
    draft_payload = _draft(
        [
            _obligation(
                obligation_id="U1",
                capability="performance",
                source_surfaces=(question,),
                semantic_surfaces=(
                    ("net gelir", "metric"),
                    ("belirsiz marj", "metric"),
                ),
            )
        ]
    )
    engine, outcome, calls = _run_surface_case(
        monkeypatch,
        question=question,
        draft_payload=draft_payload,
    )
    assert outcome.status == StandardLaneStatus.CLARIFICATION_REQUIRED
    assert any("belirsiz marj" in reason for reason in outcome.reasons)
    assert outcome.authority is None
    assert engine.authority_registry.accepted("turn-surface-accounting") is None
    assert calls == []


def test_partial_same_kind_dimension_binding_fails_closed(monkeypatch):
    question = "net geliri bölge ve özel kanal bazında göster"
    draft_payload = _draft(
        [
            _obligation(
                obligation_id="U1",
                capability="breakdown",
                source_surfaces=(question,),
                semantic_surfaces=(
                    ("net gelir", "metric"),
                    ("bölge", "dimension"),
                    ("özel kanal", "dimension"),
                ),
            )
        ]
    )
    engine, outcome, calls = _run_surface_case(
        monkeypatch,
        question=question,
        draft_payload=draft_payload,
    )
    assert outcome.status == StandardLaneStatus.CLARIFICATION_REQUIRED
    assert any("özel kanal" in reason for reason in outcome.reasons)
    assert outcome.authority is None
    assert engine.authority_registry.accepted("turn-surface-accounting") is None
    assert calls == []


def test_partial_filter_binding_fails_closed_even_when_metric_kind_is_complete(monkeypatch):
    question = "net gelir Kuzey ve VIP müşteri"
    draft_payload = _draft(
        [
            _obligation(
                obligation_id="U1",
                capability="performance",
                source_surfaces=(question,),
                semantic_surfaces=(
                    ("net gelir", "metric"),
                    ("Kuzey", "filter"),
                    ("VIP müşteri", "filter"),
                ),
            )
        ]
    )
    engine, outcome, calls = _run_surface_case(
        monkeypatch,
        question=question,
        draft_payload=draft_payload,
    )
    assert outcome.status == StandardLaneStatus.CLARIFICATION_REQUIRED
    assert any("VIP müşteri" in reason for reason in outcome.reasons)
    assert outcome.authority is None
    assert engine.authority_registry.accepted("turn-surface-accounting") is None
    assert calls == []


def test_optional_declared_semantic_surface_is_never_implicitly_discarded(monkeypatch):
    question = "net gelir, mümkünse belirsiz marj da"
    draft_payload = _draft(
        [
            _obligation(
                obligation_id="U1",
                capability="performance",
                source_surfaces=("net gelir",),
                semantic_surfaces=(("net gelir", "metric"),),
            ),
            _obligation(
                obligation_id="U2",
                capability="performance",
                source_surfaces=("belirsiz marj",),
                semantic_surfaces=(("belirsiz marj", "metric"),),
                origin="USER_OPTIONAL",
                priority="SHOULD",
            ),
        ]
    )
    engine, outcome, calls = _run_surface_case(
        monkeypatch,
        question=question,
        draft_payload=draft_payload,
    )
    assert outcome.status == StandardLaneStatus.CLARIFICATION_REQUIRED
    assert any("U2" in reason and "belirsiz marj" in reason for reason in outcome.reasons)
    assert outcome.authority is None
    assert engine.authority_registry.accepted("turn-surface-accounting") is None
    assert calls == []


def test_all_declared_semantic_surfaces_are_accounted_when_bound(monkeypatch):
    question = "net gelir ve brüt marj"
    draft_payload = _draft(
        [
            _obligation(
                obligation_id="U1",
                capability="performance",
                source_surfaces=(question,),
                semantic_surfaces=(
                    ("net gelir", "metric"),
                    ("brüt marj", "metric"),
                ),
            )
        ]
    )

    def intent(system, user, *, schema, schema_name):
        return draft_payload

    class _ExecutionResult:
        pass

    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        lambda *args, **kwargs: _ExecutionResult(),
    )
    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=_coverage_pass,
        semantic_provider=_AlwaysAbstainProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-all-bound",
        request_ref="request-all-bound",
        semantic_context=_rich_context(),
        schema=_rich_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="STANDARD_PROFILE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert outcome.status == StandardLaneStatus.ACCEPTED
    assert outcome.authority is not None
    assert outcome.projection is not None
    declared_refs = {
        binding.source_ref
        for obligation in outcome.obligations
        for binding in obligation.semantic_bindings
    }
    assert len(declared_refs) == 2
    assert len(outcome.authority.semantic_handle_refs) == 2
    assert engine.authority_registry.accepted("turn-all-bound") is not None



def test_standard_filter_contract_is_concrete_value_only_and_case_agnostic():
    import app.v2.standard_lane as module

    prompt = module._STANDARD_DRAFT_SYSTEM
    schema = module.StandardDraftSemanticSurface.model_json_schema()
    hint = schema["properties"]["kind_hint"]["description"]

    assert "explicit concrete" in prompt
    assert "governed value catalog" in prompt
    assert "descriptive qualifiers" in prompt
    assert "explicit concrete governed category/entity value" in hint

    forbidden_literals = (
        "cari",
        "bakiye",
        "mizan",
        "tahsil edilmemiş",
        "fatura",
    )
    lowered = prompt.casefold()
    assert not any(value in lowered for value in forbidden_literals)


def test_unresolved_declared_filter_still_fails_closed_after_contract_clarification(
    monkeypatch,
):
    question = "net gelir özel durum"
    draft_payload = _draft(
        [
            _obligation(
                obligation_id="U1",
                capability="performance",
                source_surfaces=(question,),
                semantic_surfaces=(
                    ("net gelir", "metric"),
                    ("özel durum", "filter"),
                ),
            )
        ]
    )
    engine, outcome, calls = _run_surface_case(
        monkeypatch,
        question=question,
        draft_payload=draft_payload,
    )
    assert outcome.status == StandardLaneStatus.CLARIFICATION_REQUIRED
    assert any("özel durum" in reason for reason in outcome.reasons)
    assert outcome.authority is None
    assert calls == []
