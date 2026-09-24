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
        return _draft_response("root_cause")

    coverage_calls = []

    def forbidden_coverage(*args, **kwargs):
        coverage_calls.append((args, kwargs))
        raise AssertionError("correctly typed Research must not spend coverage cognition")

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=forbidden_coverage,
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
    assert coverage_calls == []



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

def test_d10_j_research_omission_veto_routes_research_without_standard_authority(monkeypatch):
    question = "net geliri göster ve kök nedenini araştır"

    def intent(system, user, *, schema, schema_name):
        assert schema_name == "dima_standard_intent_draft_v1"
        return _draft_response("performance")

    coverage_calls = []

    def coverage(system, user, *, schema, schema_name):
        assert schema_name == "dima_standard_coverage_v1"
        coverage_calls.append(user)
        return {
            "status": "VETO",
            "issues": [
                {
                    "kind": "RESEARCH_NEED_OMITTED",
                    "source_surfaces": ["kök nedenini araştır"],
                    "note": "material Research request omitted",
                }
            ],
        }

    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("coverage veto must stop before execution")
        ),
    )
    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=coverage,
        semantic_provider=_SemanticProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-d10-j-current-veto",
        request_ref="request-d10-j-current-veto",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert coverage_calls
    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.coverage_status == "VETO"
    assert outcome.authority is None
    assert outcome.projection is None
    assert outcome.obligations == ()
    assert engine.authority_registry.accepted("turn-d10-j-current-veto") is None


def test_d10_j_presentation_only_standard_draft_stays_unsupported_after_coverage_pass():
    coverage_calls = []

    def intent(system, user, *, schema, schema_name):
        return {
            "obligations": [
                {
                    "obligation_id": "U1",
                    "capability_key": "report",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["rapor"],
                    "semantic_surfaces": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                }
            ],
            "control_requests": [],
        }

    def coverage(*args, **kwargs):
        coverage_calls.append((args, kwargs))
        return {"status": "PASS", "issues": []}

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=coverage,
        semantic_provider=None,
        temporal_provider=None,
    )
    outcome = engine.run(
        question="rapor",
        turn_id="turn-d10-j-unsupported",
        request_ref="request-d10-j-unsupported",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert outcome.status == StandardLaneStatus.UNSUPPORTED
    assert len(coverage_calls) == 1
    assert engine.authority_registry.accepted("turn-d10-j-unsupported") is None


def test_d10_j_two_malformed_drafts_fail_closed_after_one_generic_repair():
    draft_calls = []

    def intent(system, user, *, schema, schema_name):
        import json

        draft_calls.append(json.loads(user))
        raise ValueError("typed draft contract rejected")

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question="net geliri göster",
        turn_id="turn-d10-j-draft-failure",
        request_ref="request-d10-j-draft-failure",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert len(draft_calls) == 2
    assert draft_calls[0]["REVISION_FEEDBACK"] is None
    assert draft_calls[1]["REVISION_FEEDBACK"] == {
        "kind": "DRAFT_CONTRACT_REJECTED",
        "reasons": ["typed response did not satisfy StandardIntentDraft"],
    }
    assert outcome.status == StandardLaneStatus.FAILED
    assert outcome.attempts == 2
    assert engine.authority_registry.accepted("turn-d10-j-draft-failure") is None

def test_d10_j_first_malformed_draft_gets_one_generic_repair_then_standard_can_accept(
    monkeypatch,
):
    import json

    payloads = []

    def intent(system, user, *, schema, schema_name):
        payloads.append(json.loads(user))
        if len(payloads) == 1:
            return {"obligations": []}
        return _draft_response("performance")

    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        lambda *args, **kwargs: _Execution(),
    )
    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question="net geliri",
        turn_id="turn-d10-j-repaired-draft",
        request_ref="request-d10-j-repaired-draft",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert len(payloads) == 2
    assert payloads[1]["REVISION_FEEDBACK"] == {
        "kind": "DRAFT_CONTRACT_REJECTED",
        "reasons": ["typed response did not satisfy StandardIntentDraft"],
    }
    assert outcome.status == StandardLaneStatus.ACCEPTED
    assert outcome.attempts == 2
    assert outcome.authority is not None


def test_d10_j_nonresearch_coverage_veto_never_routes_research(monkeypatch):
    question = "net geliri göster ve yönetim özetini de eksiksiz kapsa"

    def intent(system, user, *, schema, schema_name):
        return _draft_response("performance")

    def coverage(system, user, *, schema, schema_name):
        return {
            "status": "VETO",
            "issues": [
                {
                    "kind": "MATERIAL_REQUEST_OMITTED",
                    "source_surfaces": ["yönetim özetini de eksiksiz kapsa"],
                    "note": "material Standard request omitted",
                }
            ],
        }

    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("coverage veto must stop before execution")
        ),
    )
    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=coverage,
        semantic_provider=_SemanticProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-d10-j-nonresearch-veto",
        request_ref="request-d10-j-nonresearch-veto",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert outcome.status == StandardLaneStatus.COGNITION_REJECTED
    assert outcome.coverage_status == "VETO"
    assert outcome.authority is None
    assert engine.authority_registry.accepted("turn-d10-j-nonresearch-veto") is None


def test_d10_j_material_semantic_gap_routes_research_only_when_coverage_proves_omission():
    question = "net gelir ve belirsiz marj için kök neden araştırması yap"

    def intent(system, user, *, schema, schema_name):
        return _draft(
            [
                _obligation(
                    obligation_id="U1",
                    capability="performance",
                    source_surfaces=("net gelir ve belirsiz marj",),
                    semantic_surfaces=(
                        ("net gelir", "metric"),
                        ("belirsiz marj", "metric"),
                    ),
                )
            ]
        )

    def coverage(system, user, *, schema, schema_name):
        return {
            "status": "VETO",
            "issues": [
                {
                    "kind": "RESEARCH_NEED_OMITTED",
                    "source_surfaces": ["kök neden araştırması yap"],
                    "note": "material Research request omitted",
                }
            ],
        }

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=coverage,
        semantic_provider=_AlwaysAbstainProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-d10-j-gap-research",
        request_ref="request-d10-j-gap-research",
        semantic_context=_rich_context(),
        schema=_rich_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.coverage_status == "VETO"
    assert outcome.authority is None
    assert outcome.projection is None


def test_d10_j_unsupported_standard_shape_routes_research_only_on_typed_omission():
    question = "rapor üret ve ilişkiyi araştır"

    def intent(system, user, *, schema, schema_name):
        return {
            "obligations": [
                {
                    "obligation_id": "U1",
                    "capability_key": "report",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["rapor üret"],
                    "semantic_surfaces": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                }
            ],
            "control_requests": [],
        }

    def coverage(system, user, *, schema, schema_name):
        return {
            "status": "VETO",
            "issues": [
                {
                    "kind": "RESEARCH_NEED_OMITTED",
                    "source_surfaces": ["ilişkiyi araştır"],
                    "note": "material Research request omitted",
                }
            ],
        }

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=coverage,
        semantic_provider=None,
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-d10-j-unsupported-research",
        request_ref="request-d10-j-unsupported-research",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.coverage_status == "VETO"
    assert outcome.authority is None
    assert outcome.projection is None
    assert engine.authority_registry.accepted("turn-d10-j-unsupported-research") is None

def test_d10_j_control_request_uses_only_typed_research_omission_as_bridge():
    question = "net geliri göster, konuşmayı da düzelt ve kök nedeni araştır"

    def intent(system, user, *, schema, schema_name):
        return {
            "obligations": [
                {
                    "obligation_id": "U1",
                    "capability_key": "performance",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["net geliri"],
                    "semantic_surfaces": [
                        {"surface": "net geliri", "kind_hint": "metric"}
                    ],
                    "ranking_direction": None,
                    "ranking_limit": None,
                }
            ],
            "control_requests": [
                {
                    "request_id": "C1",
                    "category": "CONVERSATION_REPAIR",
                    "source_surfaces": ["konuşmayı da düzelt"],
                }
            ],
        }

    coverage_modes = iter(
        (
            {
                "status": "PASS",
                "issues": [],
            },
            {
                "status": "VETO",
                "issues": [
                    {
                        "kind": "RESEARCH_NEED_OMITTED",
                        "source_surfaces": ["kök nedeni araştır"],
                        "note": "material Research request omitted",
                    }
                ],
            },
        )
    )

    def run_once(turn_id):
        def coverage(system, user, *, schema, schema_name):
            return next(coverage_modes)

        engine = StandardLaneEngine(
            intent_structured=intent,
            coverage_structured=coverage,
            semantic_provider=_SemanticProvider(),
            temporal_provider=None,
        )
        outcome = engine.run(
            question=question,
            turn_id=turn_id,
            request_ref=f"request-{turn_id}",
            semantic_context=_context(),
            schema=_schema(),
            conversation=ConversationStateV2(),
            tenant_binding="tenant-a",
            cognition_model_role="FAST_LANGUAGE",
            principal=object(),
            service=object(),
            tenant_runtime=object(),
            contract_store=object(),
            session_id=None,
        )
        return engine, outcome

    first_engine, first = run_once("turn-d10-j-control-pass")
    assert first.status == StandardLaneStatus.CLARIFICATION_REQUIRED
    assert first_engine.authority_registry.accepted("turn-d10-j-control-pass") is None

    second_engine, second = run_once("turn-d10-j-control-research")
    assert second.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert second.coverage_status == "VETO"
    assert second.authority is None
    assert second.projection is None
    assert second_engine.authority_registry.accepted("turn-d10-j-control-research") is None


def test_d10_j_research_omission_has_priority_over_other_coverage_vetoes(monkeypatch):
    question = "net geliri göster, yönetim özetini kapsa ve kök nedeni araştır"

    def intent(system, user, *, schema, schema_name):
        return _draft_response("performance")

    def coverage(system, user, *, schema, schema_name):
        return {
            "status": "VETO",
            "issues": [
                {
                    "kind": "MATERIAL_REQUEST_OMITTED",
                    "source_surfaces": ["yönetim özetini kapsa"],
                    "note": "material Standard request omitted",
                },
                {
                    "kind": "RESEARCH_NEED_OMITTED",
                    "source_surfaces": ["kök nedeni araştır"],
                    "note": "material Research request omitted",
                },
            ],
        }

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=coverage,
        semantic_provider=_SemanticProvider(),
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-d10-j-mixed-veto",
        request_ref="request-d10-j-mixed-veto",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.coverage_status == "VETO"
    assert outcome.authority is None
    assert outcome.projection is None



# D10-L: deterministic typed lane ownership must precede Standard-local work.

class _D10LForbiddenSemanticProvider:
    def __init__(self):
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        raise AssertionError("typed-direct Research must not spend Standard semantic cognition")


def _run_d10_l_engine(
    *,
    question,
    draft_payload,
    coverage,
    semantic_provider,
    turn_id,
):
    def intent(system, user, *, schema, schema_name):
        assert schema_name == "dima_standard_intent_draft_v1"
        return draft_payload

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=coverage,
        semantic_provider=semantic_provider,
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id=turn_id,
        request_ref=f"request-{turn_id}",
        semantic_context=_rich_context(),
        schema=_rich_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )
    return engine, outcome


def test_d10_l_typed_root_cause_preempts_non_authoritative_control_before_all_standard_work(
    monkeypatch,
):
    question = "net geliri için kök nedenini araştır. Nedensel kesinlik iddia etme"
    draft_payload = {
        "obligations": [
            {
                "obligation_id": "U_ROOT",
                "capability_key": "root_cause",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["kök nedenini araştır"],
                "semantic_surfaces": [
                    {"surface": "net geliri", "kind_hint": "metric"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [
            {
                "request_id": "C1",
                "category": "NON_AUTHORITATIVE_CONTROL_REQUEST",
                "source_surfaces": ["Nedensel kesinlik iddia etme"],
            }
        ],
    }
    coverage_calls = []

    def forbidden_coverage(*args, **kwargs):
        coverage_calls.append((args, kwargs))
        raise AssertionError("typed-direct Research must not spend Standard coverage")

    semantic = _D10LForbiddenSemanticProvider()
    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("typed-direct Research must not touch Standard Wren")
        ),
    )

    engine, outcome = _run_d10_l_engine(
        question=question,
        draft_payload=draft_payload,
        coverage=forbidden_coverage,
        semantic_provider=semantic,
        turn_id="turn-d10-l-root-control",
    )

    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.obligations == ()
    assert outcome.projection is None
    assert outcome.authority is None
    assert semantic.calls == 0
    assert coverage_calls == []
    assert engine.authority_registry.accepted("turn-d10-l-root-control") is None


def test_d10_l_typed_relationship_preempts_conversation_repair():
    question = "net geliri bölge ile ilişkilendir ve konuşmayı düzelt"
    draft_payload = {
        "obligations": [
            {
                "obligation_id": "U_REL",
                "capability_key": "relationship",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["net geliri bölge ile ilişkilendir"],
                "semantic_surfaces": [
                    {"surface": "net geliri", "kind_hint": "metric"},
                    {"surface": "bölge", "kind_hint": "dimension"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [
            {
                "request_id": "C1",
                "category": "CONVERSATION_REPAIR",
                "source_surfaces": ["konuşmayı düzelt"],
            }
        ],
    }

    semantic = _D10LForbiddenSemanticProvider()
    engine, outcome = _run_d10_l_engine(
        question=question,
        draft_payload=draft_payload,
        coverage=lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("typed-direct Research must not call coverage")
        ),
        semantic_provider=semantic,
        turn_id="turn-d10-l-rel-repair",
    )

    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert semantic.calls == 0
    assert engine.authority_registry.accepted("turn-d10-l-rel-repair") is None


def test_d10_l_typed_research_does_not_depend_on_standard_semantic_resolution():
    question = "belirsiz metrik için kök nedeni araştır"
    draft_payload = {
        "obligations": [
            {
                "obligation_id": "U_ROOT",
                "capability_key": "root_cause",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["kök nedeni araştır"],
                "semantic_surfaces": [
                    {"surface": "belirsiz metrik", "kind_hint": "metric"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [],
    }

    semantic = _D10LForbiddenSemanticProvider()
    _, outcome = _run_d10_l_engine(
        question=question,
        draft_payload=draft_payload,
        coverage=lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("typed-direct Research must not call coverage")
        ),
        semantic_provider=semantic,
        turn_id="turn-d10-l-unresolved-semantic",
    )

    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert semantic.calls == 0


def test_d10_l_excluded_root_cause_does_not_force_research(monkeypatch):
    question = "net geliri göster, kök neden analizi yapma"
    draft_payload = {
        "obligations": [
            {
                "obligation_id": "U_PERF",
                "capability_key": "performance",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["net geliri"],
                "semantic_surfaces": [
                    {"surface": "net geliri", "kind_hint": "metric"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            },
            {
                "obligation_id": "X_ROOT",
                "capability_key": "root_cause",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "EXCLUDED",
                "source_surfaces": ["kök neden analizi yapma"],
                "semantic_surfaces": [
                    {"surface": "net geliri", "kind_hint": "metric"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            },
        ],
        "control_requests": [],
    }
    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        lambda *args, **kwargs: _Execution(),
    )

    engine, outcome = _run_d10_l_engine(
        question=question,
        draft_payload=draft_payload,
        coverage=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        turn_id="turn-d10-l-excluded-root",
    )

    assert outcome.status != StandardLaneStatus.RESEARCH_REQUIRED
    if outcome.status == StandardLaneStatus.ACCEPTED:
        assert outcome.authority is not None
    assert engine.authority_registry.accepted("turn-d10-l-excluded-root") is not None or (
        outcome.status != StandardLaneStatus.ACCEPTED
    )


def test_d10_l_deferred_capability_preserves_nonresearch_policy():
    question = "net geliri trend olarak izle"
    draft_payload = {
        "obligations": [
            {
                "obligation_id": "U_TREND",
                "capability_key": "trend",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["trend olarak izle"],
                "semantic_surfaces": [
                    {"surface": "net geliri", "kind_hint": "metric"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [],
    }

    engine, outcome = _run_d10_l_engine(
        question=question,
        draft_payload=draft_payload,
        coverage=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        turn_id="turn-d10-l-deferred",
    )

    assert outcome.status == StandardLaneStatus.UNSUPPORTED
    assert engine.authority_registry.accepted("turn-d10-l-deferred") is None


def test_d10_l_standard_business_ignores_non_authoritative_control(monkeypatch):
    question = "net geliri göster, iç araçları değiştirme"
    draft_payload = {
        "obligations": [
            {
                "obligation_id": "U_PERF",
                "capability_key": "performance",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["net geliri"],
                "semantic_surfaces": [
                    {"surface": "net geliri", "kind_hint": "metric"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [
            {
                "request_id": "C1",
                "category": "NON_AUTHORITATIVE_CONTROL_REQUEST",
                "source_surfaces": ["iç araçları değiştirme"],
            }
        ],
    }
    monkeypatch.setattr(
        "app.v2.standard_lane.WrenStandardExecutionAdapter.execute",
        lambda *args, **kwargs: _Execution(),
    )

    engine, outcome = _run_d10_l_engine(
        question=question,
        draft_payload=draft_payload,
        coverage=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        turn_id="turn-d10-l-standard-control",
    )

    assert outcome.status == StandardLaneStatus.ACCEPTED
    assert outcome.authority is not None
    assert engine.authority_registry.accepted("turn-d10-l-standard-control") is not None


def test_d10_l_standard_business_with_conversation_repair_remains_conservative():
    question = "net geliri göster ve konuşmayı düzelt"
    draft_payload = {
        "obligations": [
            {
                "obligation_id": "U_PERF",
                "capability_key": "performance",
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["net geliri"],
                "semantic_surfaces": [
                    {"surface": "net geliri", "kind_hint": "metric"},
                ],
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [
            {
                "request_id": "C1",
                "category": "CONVERSATION_REPAIR",
                "source_surfaces": ["konuşmayı düzelt"],
            }
        ],
    }

    engine, outcome = _run_d10_l_engine(
        question=question,
        draft_payload=draft_payload,
        coverage=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        turn_id="turn-d10-l-conversation-repair",
    )

    assert outcome.status == StandardLaneStatus.CLARIFICATION_REQUIRED
    assert engine.authority_registry.accepted("turn-d10-l-conversation-repair") is None


def test_d10_l_source_invalid_research_draft_repairs_before_typed_lane_route():
    import json

    question = "net geliri için kök nedenini araştır"
    calls = []

    def intent(system, user, *, schema, schema_name):
        assert schema_name == "dima_standard_intent_draft_v1"
        payload = json.loads(user)
        calls.append(payload)
        source_surface = "uydurulmuş araştırma" if len(calls) == 1 else "kök nedenini araştır"
        return {
            "obligations": [
                {
                    "obligation_id": "U_ROOT",
                    "capability_key": "root_cause",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": [source_surface],
                    "semantic_surfaces": [
                        {"surface": "net geliri", "kind_hint": "metric"},
                    ],
                    "ranking_direction": None,
                    "ranking_limit": None,
                }
            ],
            "control_requests": [],
        }

    semantic = _D10LForbiddenSemanticProvider()
    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("source-valid typed Research must not call coverage")
        ),
        semantic_provider=semantic,
        temporal_provider=None,
    )
    outcome = engine.run(
        question=question,
        turn_id="turn-d10-l-source-repair",
        request_ref="request-d10-l-source-repair",
        semantic_context=_rich_context(),
        schema=_rich_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="FAST_LANGUAGE",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )

    assert len(calls) == 2
    assert calls[1]["REVISION_FEEDBACK"]["kind"] == "SOURCE_CONTRACT_REJECTED"
    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.attempts == 2
    assert semantic.calls == 0
    assert engine.authority_registry.accepted("turn-d10-l-source-repair") is None
