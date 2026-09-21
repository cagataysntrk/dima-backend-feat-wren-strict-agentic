"""Focused P4 tests: ContextProviderV0 + TurnInterpreter only."""

from __future__ import annotations

import hashlib
import inspect
import json

import pytest

from app.v2.context_provider import ContextProviderV0
from app.v2.interpreter import TurnInterpreter, TurnInterpreterError, _normalize_surface_role_overlap
from app.v2.models import (
    AnalyticalRequest,
    ComparisonSurface,
    ConversationStateV2,
    SemanticMention,
    SemanticMentionKind,
    TenantAnalyticsRuntimeV0,
    TurnAct,
    TurnInterpretation,
)



def test_comparison_reference_overlap_is_not_a_second_base_time_requirement():
    turn = TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_NEW,
        analytical_request=AnalyticalRequest(
            time_mentions=(
                SemanticMention(text="current window", kind=SemanticMentionKind.TIME),
                SemanticMention(text="reference window", kind=SemanticMentionKind.TIME),
            ),
            comparisons=(ComparisonSurface(text="reference window comparison"),),
        ),
    )

    normalized = _normalize_surface_role_overlap(turn)
    request = normalized.analytical_request
    assert request is not None
    assert [item.text for item in request.time_mentions] == ["current window"]
    assert [item.text for item in request.comparisons] == ["reference window comparison"]



class FakeService:
    mdl_version = "mdl-test-v1"

    def __init__(self, rules: str = "Ciro yalnız onaylı satışlardan hesaplanır."):
        self._rules = rules

    def schema(self):
        return {
            "catalog": "demo",
            "schema_name": "main",
            "cubes": [
                {
                    "name": "parti",
                    "display": "Parti",
                    "synonyms": ["parti", "üretim partisi"],
                    "measures": ["toplam_ciro", "toplam_fire_kg"],
                    "measure_synonyms": {
                        "toplam_ciro": ["ciro", "satış"],
                        "toplam_fire_kg": ["fire", "zayiat"],
                    },
                    "measure_synonyms_display": {
                        "toplam_ciro": "Ciro",
                        "toplam_fire_kg": "Fire",
                    },
                    "units": {"toplam_ciro": "TRY", "toplam_fire_kg": "kg"},
                    "dimensions": ["makine", "renk"],
                    "dimension_labels": {"makine": "Makine", "renk": "Renk"},
                    "dimension_synonyms": {
                        "makine": ["makine", "tezgah"],
                        "renk": ["renk"],
                    },
                    "time_dimensions": ["tarih"],
                    # Entity values MUST NOT enter V2 prompt context.
                    "dimension_values": {"renk": ["ENTITY_VALUE_MUST_NOT_LEAK"]},
                }
            ],
            "kpis": [
                {
                    "name": "teslimat_performansi",
                    "label": "Teslimat Performansı",
                    "unit": "%",
                    "synonyms": ["zamanında teslimat"],
                }
            ],
            "relationships": [
                {
                    "name": "parti_makine",
                    "models": ["partiler", "makineler"],
                    "join_type": "many_to_one",
                    "condition": "PHYSICAL_JOIN_CONDITION_MUST_NOT_LEAK",
                    "certified": "olculdu:saglikli",
                }
            ],
            "business_rules": self._rules,
            "db_online": True,
        }


def runtime() -> TenantAnalyticsRuntimeV0:
    return TenantAnalyticsRuntimeV0(
        tenant_id="tenant-1",
        tenant_slug="demo-boyahane",
        principal_user_id="user-1",
        roles=("owner",),
        mdl_version="mdl-test-v1",
        catalog="demo",
        schema_name="main",
        db_online=True,
    )


class FakeLLM:
    def __init__(self, *outputs: str):
        self.outputs = list(outputs)
        self.calls = 0

    def structured_text(self, system: str, user: str) -> str:
        self.calls += 1
        assert "SQL" in system
        assert "CURRENT_MESSAGE" in user
        if not self.outputs:
            raise AssertionError("beklenmeyen LLM çağrısı")
        return self.outputs.pop(0)


def semantic_context():
    return ContextProviderV0().build(FakeService(), runtime())


def test_context_version_is_deterministic_and_rule_bound():
    p = ContextProviderV0()
    a = p.build(FakeService("kural-a"), runtime())
    b = p.build(FakeService("kural-a"), runtime())
    c = p.build(FakeService("kural-b"), runtime())

    assert a.context_version.version == b.context_version.version
    assert a.context_version.version != c.context_version.version
    assert a.context_version.business_rules_hash == hashlib.sha256(b"kural-a").hexdigest()
    assert a.context_version.mdl_version == runtime().mdl_version


def test_compact_context_keeps_canonical_catalog_but_excludes_entity_values_and_join_sql():
    ctx = semantic_context()
    raw = ctx.model_dump_json()

    assert "toplam_ciro" in raw
    assert "toplam_fire_kg" in raw
    assert "makine" in raw
    assert "ciro" in raw
    assert "teslimat_performansi" in raw
    assert "zamanında teslimat" in raw
    assert "ENTITY_VALUE_MUST_NOT_LEAK" not in raw
    assert "PHYSICAL_JOIN_CONDITION_MUST_NOT_LEAK" not in raw


def test_valid_structured_output_uses_exactly_one_call():
    llm = FakeLLM(json.dumps({
        "dialogue_act": "ANALYTIC_NEW",
        "analytical_request": {
            "metric_mentions": [{"text": "ciro", "kind": "metric"}],
            "time_mentions": [{"text": "bu ay", "kind": "time"}],
        },
    }))
    turn = TurnInterpreter().interpret(
        question="bu ay ciro",
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        llm=llm,
    )
    assert turn.dialogue_act == TurnAct.ANALYTIC_NEW
    assert llm.calls == 1


def test_one_format_retry_only():
    valid = json.dumps({
        "dialogue_act": "SOCIAL",
        "analytical_request": None,
    })
    llm = FakeLLM("{bozuk-json", valid)
    turn = TurnInterpreter().interpret(
        question="teşekkürler",
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        llm=llm,
    )
    assert turn.dialogue_act == TurnAct.SOCIAL
    assert llm.calls == 2


def test_second_invalid_format_fails_without_third_call():
    llm = FakeLLM("{bozuk", "{hala-bozuk")
    with pytest.raises(TurnInterpreterError) as exc:
        TurnInterpreter().interpret(
            question="teşekkürler",
            semantic_context=semantic_context(),
            conversation=ConversationStateV2(),
            llm=llm,
        )
    assert exc.value.failure.code == "invalid_structured_output"
    assert llm.calls == 2


def test_model_corrected_typos_are_realigned_to_exact_user_surface_without_retry():
    llm = FakeLLM(json.dumps({
        "dialogue_act": "ANALYTIC_NEW",
        "analytical_request": {
            "metric_mentions": [{"text": "net gelir", "kind": "metric"}],
            "dimension_mentions": [{"text": "bölge", "kind": "dimension"}],
            "time_mentions": [{"text": "bu ay", "kind": "time"}],
        },
    }, ensure_ascii=False))

    turn = TurnInterpreter().interpret(
        question="bu ay bolge bazında net gelr ne durumda?",
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        llm=llm,
    )

    request = turn.analytical_request
    assert request is not None
    assert [m.text for m in request.metric_mentions] == ["net gelr"]
    assert [m.text for m in request.dimension_mentions] == ["bolge"]
    assert llm.calls == 1


def test_explicit_adjacent_ranking_limit_is_restored_without_second_llm_call():
    llm = FakeLLM(json.dumps({
        "dialogue_act": "ANALYTIC_NEW",
        "analytical_request": {
            "metric_mentions": [{"text": "ciro", "kind": "metric"}],
            "dimension_mentions": [{"text": "makine", "kind": "dimension"}],
            "ranking": {"text": "en yüksek", "direction": "desc", "limit": None},
        },
    }, ensure_ascii=False))

    turn = TurnInterpreter().interpret(
        question="makine bazında en yüksek 2 ciro",
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        llm=llm,
    )

    request = turn.analytical_request
    assert request is not None
    assert request.ranking is not None
    assert request.ranking.text == "en yüksek 2"
    assert request.ranking.limit == 2
    assert llm.calls == 1


def test_canonical_id_or_invented_span_is_rejected_without_semantic_retry():
    llm = FakeLLM(json.dumps({
        "dialogue_act": "ANALYTIC_NEW",
        "analytical_request": {
            "metric_mentions": [{"text": "toplam_ciro", "kind": "metric"}],
        },
    }))
    with pytest.raises(TurnInterpreterError) as exc:
        TurnInterpreter().interpret(
            question="ciro",
            semantic_context=semantic_context(),
            conversation=ConversationStateV2(),
            llm=llm,
        )
    assert exc.value.failure.code == "surface_grounding_violation"
    assert llm.calls == 1


@pytest.mark.parametrize(
    ("question", "conversation", "payload", "expected"),
    [
        (
            "bu ay ciro",
            ConversationStateV2(),
            {
                "dialogue_act": "ANALYTIC_NEW",
                "analytical_request": {
                    "metric_mentions": [{"text": "ciro", "kind": "metric"}],
                    "time_mentions": [{"text": "bu ay", "kind": "time"}],
                },
            },
            TurnAct.ANALYTIC_NEW,
        ),
        (
            "makine bazında OEE",
            ConversationStateV2(),
            {
                "dialogue_act": "ANALYTIC_NEW",
                "analytical_request": {
                    "metric_mentions": [{"text": "OEE", "kind": "metric"}],
                    "dimension_mentions": [{"text": "makine", "kind": "dimension"}],
                },
            },
            TurnAct.ANALYTIC_NEW,
        ),
        (
            "teşekkürler",
            ConversationStateV2(),
            {"dialogue_act": "SOCIAL"},
            TurnAct.SOCIAL,
        ),
        (
            "bunu yorumla",
            ConversationStateV2(has_active_result=True, has_prior_analytical_request=True),
            {
                "dialogue_act": "RESULT_EXPLAIN",
                "references": [{"text": "bunu", "kind": "prior_result"}],
                "presentation_request": "explain",
            },
            TurnAct.RESULT_EXPLAIN,
        ),
        (
            "hayır son üç ay",
            ConversationStateV2(has_prior_analytical_request=True),
            {
                "dialogue_act": "USER_REPAIR",
                "analytical_request": {
                    "time_mentions": [{"text": "son üç ay", "kind": "time"}],
                },
                "user_repair": {"correction_spans": ["hayır", "son üç ay"]},
            },
            TurnAct.USER_REPAIR,
        ),
        (
            "siyah fire",
            ConversationStateV2(),
            {
                "dialogue_act": "ANALYTIC_NEW",
                "analytical_request": {
                    "metric_mentions": [{"text": "fire", "kind": "metric"}],
                    "filter_mentions": [{"text": "siyah", "kind": "filter"}],
                },
                "unresolved_mentions": [
                    {"text": "siyah", "reason": "Birden fazla gerçek kavrama bağlanabilir."}
                ],
            },
            TurnAct.ANALYTIC_NEW,
        ),
        (
            "renk olan siyah",
            ConversationStateV2(pending_clarification=True),
            {
                "dialogue_act": "CLARIFICATION_ANSWER",
                "analytical_request": {
                    "filter_mentions": [{"text": "renk", "kind": "filter"}, {"text": "siyah", "kind": "filter"}],
                },
            },
            TurnAct.CLARIFICATION_ANSWER,
        ),
        (
            "sadece RAM-3",
            ConversationStateV2(has_prior_analytical_request=True),
            {
                "dialogue_act": "ANALYTIC_REFINE",
                "analytical_request": {
                    "filter_mentions": [{"text": "RAM-3", "kind": "filter"}],
                },
            },
            TurnAct.ANALYTIC_REFINE,
        ),
        (
            "yarın hava nasıl",
            ConversationStateV2(),
            {"dialogue_act": "UNSUPPORTED"},
            TurnAct.UNSUPPORTED,
        ),
    ],
)
def test_day1_act_contract_family(question, conversation, payload, expected):
    llm = FakeLLM(json.dumps(payload, ensure_ascii=False))
    turn = TurnInterpreter().interpret(
        question=question,
        semantic_context=semantic_context(),
        conversation=conversation,
        llm=llm,
    )
    assert turn.dialogue_act == expected
    assert llm.calls == 1


def test_interpreter_source_has_no_execution_or_legacy_semantic_owner():
    import app.v2.interpreter as module

    source = inspect.getsource(module)
    forbidden = (
        "cube_router",
        "routers.ask",
        "uyum",
        "plan_tuketici",
        "plan_semasi",
        "followup",
        "intent_semasi",
        ".query(",
        ".dry_plan(",
        ".cube_sql(",
        "generate_sql(",
        "select_cube(",
        "refine_cube(",
    )
    for token in forbidden:
        assert token not in source, token


def test_ask_v2_day1_http_path_never_executes_query(client, monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "ask_v2_enabled", True)

    fake = FakeLLM(json.dumps({
        "dialogue_act": "ANALYTIC_NEW",
        "analytical_request": {
            "metric_mentions": [{"text": "ciro", "kind": "metric"}],
            "time_mentions": [{"text": "bu ay", "kind": "time"}],
        },
    }))
    monkeypatch.setattr(client.app.state, "llm", fake)

    response = client.post("/ask-v2", json={"question": "bu ay ciro"})
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "interpreted"
    assert data["turn"]["dialogue_act"] == "ANALYTIC_NEW"
    assert data["query_executed"] is False
    assert data["sql_generated"] is False
    assert data["legacy_semantic_path_called"] is False
    assert data["context_version"]["version"]
    assert data["next_stage"] == "semantic_resolver_day2"
    assert fake.calls == 1


def test_p4_minimum_domain_represents_required_surface_families():
    from app.v2.models import (
        AnalyticsIR,
        AnalyticalRequest,
        ClarificationState,
        ComparisonSurface,
        RankingSurface,
        ReferenceMention,
        Requirement,
        SemanticMention,
        SemanticMentionKind,
        UserRepair,
    )

    request = AnalyticalRequest(
        metric_mentions=(SemanticMention(text="ciro", kind="metric"),),
        dimension_mentions=(SemanticMention(text="makine", kind="dimension"),),
        filter_mentions=(SemanticMention(text="siyah", kind="filter"),),
        time_mentions=(SemanticMention(text="son üç ay", kind="time"),),
        ranking=RankingSurface(text="en çok 5", direction="desc", limit=5),
        comparisons=(ComparisonSurface(text="geçen ayla"),),
    )
    assert request.ranking and request.ranking.limit == 5
    assert request.comparisons[0].text == "geçen ayla"
    assert ReferenceMention(text="bunu", kind="prior_result").text == "bunu"
    assert UserRepair(correction_spans=("hayır",)).correction_spans == ("hayır",)
    assert ClarificationState(pending=True, source_mention="siyah").pending is True

    # P4 requires the domain names to exist, but Day 1 must not prematurely implement
    # Day 3's resolved IR/ledger semantics.
    marker = Requirement(kind=SemanticMentionKind.METRIC)
    assert AnalyticsIR(requirements=(marker,)).requirements == (marker,)
