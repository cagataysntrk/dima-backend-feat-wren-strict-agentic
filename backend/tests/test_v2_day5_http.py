"""Day 5 HTTP attack gate over the real /ask-v2 product boundary.

The semantic/data fixtures are deliberately synthetic and use opaque canonical names.
Assertions are on product invariants (state, evidence, query count, principal propagation),
never on implementation-generated SQL text.
"""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_principal
from app.contracts import result_hash
from app.config import get_settings
from app.routers.ask_v2 import router as ask_v2_router
from control_plane.authorize import Principal


SPEC = {
    "cube": "ops_delta",
    "metric": "yield_score_n",
    "metric_surface": "çıktı verimi",
    "metric_display": "Çıktı Verimi",
    "dimension": "line_axis_p",
    "dimension_surface": "üretim hattı",
    "dimension_display": "Üretim Hattı",
    "entity": "CELL-Q9",
    "time": "event_date_k",
}


def schema(*, ambiguous: bool = False) -> dict:
    dimensions = [SPEC["dimension"]]
    labels = {SPEC["dimension"]: SPEC["dimension_display"]}
    synonyms = {SPEC["dimension"]: [SPEC["dimension_surface"]]}
    values = {SPEC["dimension"]: [SPEC["entity"], "CELL-R8"]}
    columns = [
        {"name": SPEC["dimension"], "type": "VARCHAR"},
        {"name": SPEC["time"], "type": "DATE"},
    ]
    if ambiguous:
        dimensions.append("account_axis_r")
        labels["account_axis_r"] = "Hesap"
        synonyms["account_axis_r"] = ["hesap"]
        values[SPEC["dimension"]] = ["Prime"]
        values["account_axis_r"] = ["Prime"]
        columns.append({"name": "account_axis_r", "type": "VARCHAR"})

    return {
        "catalog": "day5-synthetic",
        "schema_name": "main",
        "models": [{"name": "source_delta", "columns": columns}],
        "cubes": [{
            "name": SPEC["cube"],
            "display": "Synthetic Operations",
            "measures": [SPEC["metric"]],
            "measure_synonyms": {SPEC["metric"]: [SPEC["metric_surface"]]},
            "measure_synonyms_display": {SPEC["metric"]: SPEC["metric_display"]},
            "units": {SPEC["metric"]: "%"},
            "dimensions": dimensions,
            "dimension_labels": labels,
            "dimension_synonyms": synonyms,
            "dimension_values": values,
            "time_dimensions": [SPEC["time"]],
        }],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


class HttpSyntheticService:
    def __init__(self, *, ambiguous: bool = False):
        self.mdl_version = "mdl-day5-synthetic"
        self.ambiguous = ambiguous
        self.query_calls = 0
        self.dry_calls = 0
        self.principals = []

    def schema(self):
        return schema(ambiguous=self.ambiguous)

    def cube_sql(self, cube_query: dict) -> str:
        # Transport-only encoding for this fixture; assertions never inspect SQL.
        return "SYNTH:" + json.dumps(cube_query, ensure_ascii=False, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        self.dry_calls += 1
        self.principals.append(("dry", principal))
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        self.principals.append(("query", principal))
        query = json.loads(sql.removeprefix("SYNTH:"))
        dims = list(query.get("dimensions") or ())
        measures = list(query.get("measures") or ())
        columns = [*dims, *measures]

        members = [SPEC["entity"], "CELL-R8"]
        for flt in query.get("filters") or ():
            if flt.get("operator") == "eq":
                members = [flt.get("value")]
            elif flt.get("operator") == "in":
                members = list(flt.get("value") or ())

        rows = []
        for index, member in enumerate(members):
            row = {}
            if dims:
                row[dims[0]] = member
            for metric in measures:
                row[metric] = 82.0 - index * 9.0
            rows.append(row)

        order = query.get("order") or {}
        if order.get("measure"):
            rows.sort(
                key=lambda row: row.get(order["measure"], 0),
                reverse=order.get("direction") == "desc",
            )
        if query.get("limit") is not None:
            rows = rows[: int(query["limit"])]

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "column_types": ["VARCHAR" if c in dims else "DOUBLE" for c in columns],
        }


class SequenceLlm:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = 0

    def structured_text(self, system: str, user: str) -> str:
        self.calls += 1
        if not self.outputs:
            raise AssertionError("unexpected LLM call")
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return json.dumps(output, ensure_ascii=False)


class HttpContracts:
    def __init__(self):
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {
            "id": f"day5-contract-{self.n}",
            "result_hash": result_hash(kwargs["result"]),
            "durability": "db",
            "sealed": True,
        }


@pytest.fixture
def v2_client():
    """Real FastAPI /ask-v2 route without booting the repository's native demo Wren.

    Auth/permission middleware is not the oracle here; a typed Principal is injected through
    FastAPI's own dependency graph so this gate can measure route validation/finalization and
    explicit principal propagation without native-engine teardown noise.
    """
    app = FastAPI()
    app.include_router(ask_v2_router)
    principal = Principal(
        user_id="day5-http-user",
        tenant_id="day5-http-tenant",
        roles=["owner"],
        tenant_slug=get_settings().company,
    )

    # Override only identity. Permission + company dependencies remain real and
    # consume the same Principal through FastAPI's nested dependency graph.
    app.dependency_overrides[get_current_principal] = lambda: principal

    with TestClient(app) as client:
        yield client


def enable_v2(client, monkeypatch, *, service, llm):
    import app.v2.orchestrator as orchestrator_module

    monkeypatch.setattr(get_settings(), "ask_v2_enabled", True)
    monkeypatch.setattr(orchestrator_module, "wren_for_request", lambda request: service)
    monkeypatch.setattr(client.app.state, "llm", llm, raising=False)
    monkeypatch.setattr(client.app.state, "contracts", HttpContracts(), raising=False)


def post_turn(client, question: str, *, conversation=None, token=None):
    body = {
        "question": question,
        "session_id": "day5-http-session",
        "thread_id": "day5-http-thread",
        "conversation": conversation or {},
    }
    if token is not None:
        body["clarification_token"] = token
    return client.post("/ask-v2", json=body)


def test_real_http_product_thread_is_core_mvp_and_keeps_query_policy(v2_client, monkeypatch):
    client = v2_client
    service = HttpSyntheticService()
    llm = SequenceLlm([
        {
            "dialogue_act": "ANALYTIC_NEW",
            "analytical_request": {
                "metric_mentions": [{"text": "çıktı verimi", "kind": "metric"}],
                "dimension_mentions": [{"text": "üretim hattı", "kind": "dimension"}],
                "time_mentions": [{"text": "bu yıl", "kind": "time"}],
            },
        },
        {
            "dialogue_act": "ANALYTIC_REFINE",
            "analytical_request": {
                "filter_mentions": [{"text": "CELL-Q9", "kind": "filter"}],
            },
        },
        {
            "dialogue_act": "USER_REPAIR",
            "analytical_request": {
                "time_mentions": [{"text": "son üç ay", "kind": "time"}],
            },
            "user_repair": {"correction_spans": ["yok", "son üç ay"]},
        },
        {
            "dialogue_act": "RESULT_EXPLAIN",
            "references": [{"text": "bu sonucu", "kind": "prior_result"}],
            "presentation_request": "explain",
        },
        {"dialogue_act": "SOCIAL"},
    ])
    enable_v2(client, monkeypatch, service=service, llm=llm)

    state = {}
    expected = [
        ("bu yıl üretim hattı bazında çıktı verimi", "answer", 1),
        ("yalnız CELL-Q9", "answer", 1),
        ("yok son üç ay olsun", "answer", 1),
        ("bu sonucu açıklar mısın?", "explain", 0),
        ("teşekkürler", "talk", 0),
    ]
    for question, kind, query_count in expected:
        response = post_turn(client, question, conversation=state)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["status"] == "core_mvp"
        assert data["stage"] == "day5_core_mvp"
        assert data["response"]["kind"] == kind
        assert data["response"]["text"].strip()
        assert data["query_execution_count"] == query_count
        assert data["legacy_semantic_path_called"] is False
        state = data["conversation"]

    assert service.query_calls == 3
    assert service.dry_calls == 3
    assert len(service.principals) == 6
    assert all(principal is not None for _, principal in service.principals)


def test_real_http_ambiguity_signed_resume_and_malformed_token_fail_closed(v2_client, monkeypatch):
    client = v2_client
    service = HttpSyntheticService(ambiguous=True)
    llm = SequenceLlm([
        {
            "dialogue_act": "ANALYTIC_NEW",
            "analytical_request": {
                "metric_mentions": [{"text": "çıktı verimi", "kind": "metric"}],
                "filter_mentions": [{"text": "Prime", "kind": "filter"}],
            },
        }
    ])
    enable_v2(client, monkeypatch, service=service, llm=llm)

    first = post_turn(client, "Prime için çıktı verimi")
    assert first.status_code == 200, first.text
    data = first.json()
    assert data["response"]["kind"] == "clarify"
    assert data["query_execution_count"] == 0
    assert service.query_calls == 0
    chips = data["response"]["clarification_chips"]
    assert len(chips) == 2

    malformed = post_turn(
        client,
        "ilk seçenek",
        conversation=data["conversation"],
        token="tampered-token",
    )
    assert malformed.status_code == 409
    assert malformed.json()["detail"]["code"] == "clarification_token_invalid"
    assert service.query_calls == 0

    chosen = next(chip for chip in chips if chip["label"].startswith("Üretim Hattı"))
    resumed = post_turn(
        client,
        chosen["label"],
        conversation=data["conversation"],
        token=chosen["token"],
    )
    assert resumed.status_code == 200, resumed.text
    resumed_data = resumed.json()
    assert resumed_data["response"]["kind"] == "answer"
    assert resumed_data["query_execution_count"] == 1
    assert resumed_data["official_verified"] is True
    assert service.query_calls == 1


def test_real_http_stale_context_refine_is_typed_failure_and_never_queries(v2_client, monkeypatch):
    client = v2_client
    service = HttpSyntheticService()
    llm = SequenceLlm([
        {
            "dialogue_act": "ANALYTIC_REFINE",
            "analytical_request": {
                "time_mentions": [{"text": "son üç ay", "kind": "time"}],
            },
        }
    ])
    enable_v2(client, monkeypatch, service=service, llm=llm)

    stale = {
        "has_prior_analytical_request": True,
        "topic": {
            "topic_id": "old-topic",
            "cube": SPEC["cube"],
            "context_version": "ctx-stale",
        },
        "last_ir": {
            "cube": SPEC["cube"],
            "metrics": [{
                "candidate_id": "old-m",
                "target_kind": "metric",
                "canonical_name": SPEC["metric"],
                "cube_names": [SPEC["cube"]],
            }],
            "context_version": "ctx-stale",
        },
    }
    response = post_turn(client, "son üç ay olsun", conversation=stale)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["response"]["kind"] == "failure"
    assert data["failure"]["code"] == "context_version_mismatch"
    assert data["query_execution_count"] == 0
    assert service.query_calls == 0


def test_real_http_provider_failure_is_503_and_cannot_reach_data(v2_client, monkeypatch):
    client = v2_client
    service = HttpSyntheticService()
    llm = SequenceLlm([RuntimeError("provider unavailable")])
    enable_v2(client, monkeypatch, service=service, llm=llm)

    response = post_turn(client, "üretim hatlarına göre çıktı verimi")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "llm_unavailable"
    assert service.query_calls == 0
    assert service.dry_calls == 0


def test_real_http_day6_research_brief_ready_stops_before_data_execution(v2_client, monkeypatch):
    client = v2_client
    service = HttpSyntheticService()
    llm = SequenceLlm([
        {
            "dialogue_act": "REPORT_REQUEST",
            "research_request": {
                "time_mentions": [{"text": "bu yıl", "kind": "time"}],
                "goals": [],
                "relationships": [
                    {
                        "text": "üretim hattı ile çıktı verimi ilişkisini incele",
                        "focus_mentions": [{"text": "çıktı verimi", "kind": "metric"}],
                        "counterpart_mentions": [
                            {"text": "üretim hattı", "kind": "dimension"}
                        ],
                    }
                ],
                "deliverables": [{"kind": "report", "text": "raporla"}],
            },
            "presentation_request": "report",
        }
    ])
    enable_v2(client, monkeypatch, service=service, llm=llm)

    response = post_turn(
        client,
        "bu yıl üretim hattı ile çıktı verimi ilişkisini incele ve raporla",
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "research_brief"
    assert data["stage"] == "day6_research_brief"
    assert data["dialogue_action"] == "RESEARCH_BRIEF"
    assert data["response"]["kind"] == "research_brief"
    assert "bu yıl" in data["response"]["text"]
    assert data["research_brief"]["scope"]["time_surfaces"] == ["bu yıl"]
    assert data["research_brief"]["status"] == "READY_FOR_RESEARCH"
    assert len(data["research_brief"]["questions"]) == 1
    assert len(data["research_brief"]["deliverables"]) == 1
    assert data["research_brief"]["deliverables"][0]["kind"] == "report"
    assert data["research_brief"]["must_requirement_ids"] == ["g1", "d1"]
    assert data["query_execution_count"] == 0
    assert data["next_stage"] == "research_ready_day7"
    assert data["official_verified"] is False
    assert service.dry_calls == 0
    assert service.query_calls == 0


def test_real_http_day6_blocked_goal_is_preserved_without_query(v2_client, monkeypatch):
    client = v2_client
    service = HttpSyntheticService()
    llm = SequenceLlm([
        {
            "dialogue_act": "REPORT_REQUEST",
            "research_request": {
                "goals": [],
                "relationships": [
                    {
                        "text": "çıktı verimi ile vardiya ilişkisini incele",
                        "focus_mentions": [{"text": "çıktı verimi", "kind": "metric"}],
                        "counterpart_mentions": [
                            {"text": "vardiya", "kind": "dimension"}
                        ],
                    }
                ],
                "deliverables": [{"kind": "report", "text": "raporla"}],
            },
            "presentation_request": "report",
        }
    ])
    enable_v2(client, monkeypatch, service=service, llm=llm)

    response = post_turn(
        client,
        "çıktı verimi ile vardiya ilişkisini incele ve raporla",
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "research_brief"
    assert data["response"]["kind"] == "semantic_gap"
    assert data["research_brief"]["status"] == "BLOCKED"
    assert data["research_brief"]["blocking_goal_ids"] == ["g1"]
    assert len(data["research_brief"]["questions"]) == 1
    assert data["research_brief"]["questions"][0]["status"] == "BLOCKED"
    assert len(data["research_brief"]["deliverables"]) == 1
    assert data["research_brief"]["deliverables"][0]["kind"] == "report"
    assert data["research_brief"]["must_requirement_ids"] == ["g1", "d1"]
    assert data["query_execution_count"] == 0
    assert data["next_stage"] == "research_brief_blocked"
    assert data["response"]["clarification_chips"] == []
    assert service.dry_calls == 0
    assert service.query_calls == 0
