from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.fast.application import create_fast_application
from app.fast.ask_models import (
    AggregationKind,
    AskDraft,
    AskOutcomeStatus,
    DraftTemporalIntent,
    SelectionDecision,
    SelectionPurpose,
    TemporalKind,
)
from app.fast.ask_service import FastAskService
from app.fast.auth_context import FastAccessFingerprint
from app.fast.metabase_models import (
    ConstructedQuery,
    ExecutionResponse,
    ExecutionStatus,
    FastMetabaseRuntimePolicy,
    ReadResourceResponse,
    ResourceContent,
    ResourceItem,
    SearchResponse,
)
from control_plane.security import create_access_token


QUESTION_COUNT = "Son 30 günde kaç sipariş var?"
QUESTION_SUM = "Son 30 gündeki sipariş tutarı ne kadar?"
QUESTION_BREAKDOWN = "Son 30 günde bölgelere göre sipariş tutarı"


class ScriptedCognition:
    def __init__(self, question: str) -> None:
        self.question = question

    def draft(self, *, question: str) -> AskDraft:
        assert question == self.question
        if question == QUESTION_COUNT:
            aggregation = AggregationKind.COUNT
            measure = None
            breakdown = None
        elif question == QUESTION_SUM:
            aggregation = AggregationKind.SUM
            measure = "amount"
            breakdown = None
        elif question == QUESTION_BREAKDOWN:
            aggregation = AggregationKind.SUM
            measure = "amount"
            breakdown = "region"
        else:
            raise AssertionError(question)
        return AskDraft(
            search_terms=("orders",),
            aggregation=aggregation,
            measure_hint=measure,
            breakdown_hint=breakdown,
            temporal=DraftTemporalIntent(
                kind=TemporalKind.LAST_N_DAYS,
                days=30,
                start_date=None,
                end_date=None,
            ),
        )

    def select_resource(self, *, question, candidates):
        selected = next(item for item in candidates if item.name.lower() == "orders")
        return SelectionDecision(selected_handle=selected.handle)

    def select_field(self, *, question, purpose, hint, candidates):
        target = {
            SelectionPurpose.MEASURE: "amount",
            SelectionPurpose.TEMPORAL: "order_date",
            SelectionPurpose.BREAKDOWN: "region",
        }[purpose]
        selected = next(item for item in candidates if item.name.lower() == target)
        return SelectionDecision(selected_handle=selected.handle)


def _table_details():
    return {
        "result-type": "entity",
        "id": 1,
        "type": "table",
        "name": "orders",
        "database_id": 1,
        "database_name": "Dima Lab Analytics",
        "database_schema": "public",
        "portable_fk": ["Dima Lab Analytics", "public", "orders"],
        "fields": [
            {"name": "id", "base_type": "type/Integer"},
            {"name": "order_date", "base_type": "type/Date"},
            {"name": "region", "base_type": "type/Text"},
            {"name": "channel", "base_type": "type/Text"},
            {"name": "amount", "base_type": "type/Float"},
        ],
    }


class FakeGateway:
    def __init__(self, *, response: ExecutionResponse) -> None:
        self.response = response
        self.constructed_queries = []
        self.policy = FastMetabaseRuntimePolicy()
        self.access_fingerprint = FastAccessFingerprint(
            tenant_id="tenant-a",
            dima_user_id="user-a",
            principal_id="metabase-user-a",
            auth_mode="session",
            role_scope_digest="scope",
            digest="a" * 64,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def search(self, *, term_queries=(), semantic_queries=()):
        assert term_queries == ("orders",)
        return SearchResponse(
            data=(
                {
                    "type": "table",
                    "id": 1,
                    "uri": "metabase://table/1",
                    "name": "orders",
                    "database_id": 1,
                },
            ),
            total_count=1,
        )

    def read_resource(self, uris):
        assert uris == ("metabase://table/1/fields",)
        return ReadResourceResponse(
            resources=(
                ResourceItem(
                    uri=uris[0],
                    content=ResourceContent(
                        **{"structured-output": _table_details()}
                    ),
                ),
            ),
            output="<resources>ok</resources>",
        )

    def construct_query(self, query):
        self.constructed_queries.append(query)
        return ConstructedQuery(serialized_query="opaque")

    def execute_serialized(self, query):
        assert query.serialized_query == "opaque"
        return self.response


def _response(question):
    if question == QUESTION_COUNT:
        return ExecutionResponse(
            status=ExecutionStatus.COMPLETED,
            data={"cols": [{"name": "count"}], "rows": [[30]]},
            row_count=1,
            running_time=1,
        )
    if question == QUESTION_SUM:
        return ExecutionResponse(
            status=ExecutionStatus.COMPLETED,
            data={"cols": [{"name": "sum"}], "rows": [[25455.0]]},
            row_count=1,
            running_time=1,
        )
    return ExecutionResponse(
        status=ExecutionStatus.COMPLETED,
        data={
            "cols": [{"name": "region"}, {"name": "sum"}],
            "rows": [["West", 6800.0], ["East", 6500.0], ["South", 6200.0], ["North", 5955.0]],
        },
        row_count=4,
        running_time=1,
    )


def service_for(question):
    gateway = FakeGateway(response=_response(question))
    service = FastAskService(
        cognition=ScriptedCognition(question),
        gateway_factory=lambda principal: gateway,
    )
    return service, gateway


def principal():
    return SimpleNamespace(
        user_id="user-a",
        tenant_id="tenant-a",
        is_superadmin=False,
        roles=["analyst"],
        tenant_slug="tenant-a",
    )


def test_happy_count_is_result_derived_and_evidence_bound():
    service, gateway = service_for(QUESTION_COUNT)
    response = service.ask(
        __import__("app.fast.ask_models", fromlist=["FastAskRequest"]).FastAskRequest(
            question=QUESTION_COUNT,
            as_of_date=date(2026, 9, 7),
        ),
        principal=principal(),
    )
    assert response.status == AskOutcomeStatus.SUCCESS
    assert response.answer == "Sonuç: 30 kayıt."
    assert response.evidence is not None
    assert response.evidence.exact_time_bounds == {
        "start": "2026-08-09",
        "end_exclusive": "2026-09-08",
        "kind": "LAST_N_DAYS",
    }
    assert response.evidence.result.rows == ({"count": 30},)
    assert gateway.constructed_queries[0]["stages"][0]["aggregation"] == [["count", {}]]


def test_happy_sum_and_breakdown():
    for question in (QUESTION_SUM, QUESTION_BREAKDOWN):
        service, _ = service_for(question)
        response = service.ask(
            __import__("app.fast.ask_models", fromlist=["FastAskRequest"]).FastAskRequest(
                question=question,
                as_of_date=date(2026, 9, 7),
            ),
            principal=principal(),
        )
        assert response.status == AskOutcomeStatus.SUCCESS
        assert response.evidence is not None

    assert service_for(QUESTION_SUM)[0].ask(
        __import__("app.fast.ask_models", fromlist=["FastAskRequest"]).FastAskRequest(
            question=QUESTION_SUM,
            as_of_date=date(2026, 9, 7),
        ),
        principal=principal(),
    ).answer == "Sonuç: 25455."

    assert service_for(QUESTION_BREAKDOWN)[0].ask(
        __import__("app.fast.ask_models", fromlist=["FastAskRequest"]).FastAskRequest(
            question=QUESTION_BREAKDOWN,
            as_of_date=date(2026, 9, 7),
        ),
        principal=principal(),
    ).answer == "4 kırılım döndü."


class InventingCognition(ScriptedCognition):
    def select_resource(self, *, question, candidates):
        return SelectionDecision(selected_handle="fast_res_999")


def test_invented_resource_handle_fails_closed():
    gateway = FakeGateway(response=_response(QUESTION_COUNT))
    service = FastAskService(
        cognition=InventingCognition(QUESTION_COUNT),
        gateway_factory=lambda principal: gateway,
    )
    request_cls = __import__("app.fast.ask_models", fromlist=["FastAskRequest"]).FastAskRequest
    response = service.ask(
        request_cls(question=QUESTION_COUNT, as_of_date=date(2026, 9, 7)),
        principal=principal(),
    )
    assert response.status == AskOutcomeStatus.FAILED
    assert response.error is not None
    assert response.error.code == "COGNITION_INVALID"


class AbstainingCognition(ScriptedCognition):
    def select_resource(self, *, question, candidates):
        return SelectionDecision(selected_handle=None)


def test_abstention_requires_clarification():
    gateway = FakeGateway(response=_response(QUESTION_COUNT))
    service = FastAskService(
        cognition=AbstainingCognition(QUESTION_COUNT),
        gateway_factory=lambda principal: gateway,
    )
    request_cls = __import__("app.fast.ask_models", fromlist=["FastAskRequest"]).FastAskRequest
    response = service.ask(
        request_cls(question=QUESTION_COUNT, as_of_date=date(2026, 9, 7)),
        principal=principal(),
    )
    assert response.status == AskOutcomeStatus.CLARIFICATION_REQUIRED


def test_fast_http_requires_dima_auth_and_accepts_valid_superadmin_token():
    service, _ = service_for(QUESTION_COUNT)
    app = create_fast_application(service=service)
    client = TestClient(app)

    payload = {
        "question": QUESTION_COUNT,
        "as_of_date": "2026-09-07",
    }
    assert client.post("/fast/ask", json=payload).status_code == 401

    token = create_access_token(
        sub="fast-ci-user",
        tenant_id=None,
        is_superadmin=True,
        roles=["superadmin"],
    )
    response = client.post(
        "/fast/ask",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["answer"] == "Sonuç: 30 kayıt."


def test_fast_only_application_does_not_mount_legacy_ask():
    service, _ = service_for(QUESTION_COUNT)
    app = create_fast_application(service=service)
    paths = {route.path for route in app.routes}
    assert "/fast/ask" in paths
    assert "/fast/health" in paths
    assert "/ask" not in paths
    assert "/ask-v2" not in paths
