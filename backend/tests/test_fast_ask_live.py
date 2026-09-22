from __future__ import annotations

import json
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.fast.application import create_fast_application
from app.fast.ask_models import (
    AggregationKind,
    AskDraft,
    DraftTemporalIntent,
    SelectionDecision,
    SelectionPurpose,
    TemporalKind,
)
from app.fast.ask_service import FastAskService
from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import FastMetabaseRuntimePolicy
from control_plane.security import create_access_token


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_FAST_ASK_LIVE") != "1",
    reason="FT-003 pinned Metabase lab required",
)

QUESTION_COUNT = "Son 30 günde kaç sipariş var?"
QUESTION_SUM = "Son 30 gündeki sipariş tutarı ne kadar?"
QUESTION_BREAKDOWN = "Son 30 günde bölgelere göre sipariş tutarı"


class LabCognition:
    def draft(self, *, question: str) -> AskDraft:
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
            raise AssertionError(f"unexpected live question: {question}")

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


def _metabase_login(base_url: str) -> str:
    response = httpx.post(
        base_url + "/api/session",
        json={
            "username": os.environ["MB_ADMIN_EMAIL"],
            "password": os.environ["MB_ADMIN_PASSWORD"],
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("id")
    assert token
    return str(token)


def _number(value) -> Decimal:
    return Decimal(str(value))


def _answer_number(answer: str) -> Decimal:
    prefix = "Sonuç: "
    assert answer.startswith(prefix), answer
    payload = answer[len(prefix):].strip()
    assert payload.endswith("."), answer
    return Decimal(payload[:-1])


def test_ft003_real_count_sum_breakdown_match_independent_db_oracle():
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    metabase_session = _metabase_login(base_url)

    def gateway_factory(principal):
        return FastMetabaseGateway(
            base_url=base_url,
            auth=FastMetabaseAuthContext(
                tenant_id=principal.tenant_id or "__superadmin__",
                dima_user_id=principal.user_id,
                principal_id="metabase-lab-admin",
                mode=FastMetabaseAuthMode.SESSION,
                secret=metabase_session,
                role_scope_digest="ft003-synthetic-lab",
            ),
            policy=FastMetabaseRuntimePolicy(
                max_page_rows=200,
                max_total_rows_per_run=1000,
            ),
        )

    service = FastAskService(
        cognition=LabCognition(),
        gateway_factory=gateway_factory,
    )
    app = create_fast_application(service=service)
    client = TestClient(app)

    payload_base = {"as_of_date": "2026-09-07"}

    assert client.post(
        "/fast/ask",
        json={"question": QUESTION_COUNT, **payload_base},
    ).status_code == 401

    dima_token = create_access_token(
        sub="fast-live-user",
        tenant_id=None,
        is_superadmin=True,
        roles=["superadmin"],
    )
    headers = {"Authorization": f"Bearer {dima_token}"}

    responses = {}
    for name, question in (
        ("count", QUESTION_COUNT),
        ("sum", QUESTION_SUM),
        ("breakdown", QUESTION_BREAKDOWN),
    ):
        response = client.post(
            "/fast/ask",
            json={"question": question, **payload_base},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["status"] == "SUCCESS", body
        assert body["evidence"]["exact_time_bounds"] == {
            "start": "2026-08-09",
            "end_exclusive": "2026-09-08",
            "kind": "LAST_N_DAYS",
        }
        assert body["evidence"]["metabase_runtime_version"] == "v0.63.18"
        assert body["evidence"]["access_fingerprint"]
        assert body["evidence"]["query_fingerprint"]
        assert body["evidence"]["result_digest"]
        query_text = json.dumps(body["evidence"]["portable_query"]).lower()
        assert "native" not in query_text
        assert "join" not in query_text
        responses[name] = body

    expected_count = int(os.environ["FT003_EXPECTED_COUNT"])
    expected_sum = Decimal(os.environ["FT003_EXPECTED_SUM"])
    expected_breakdown = {
        key: Decimal(str(value))
        for key, value in json.loads(os.environ["FT003_EXPECTED_BREAKDOWN"]).items()
    }

    count_body = responses["count"]
    assert count_body["answer"] == f"Sonuç: {expected_count} kayıt."
    assert _number(count_body["result"]["rows"][0]["count"]) == expected_count

    sum_body = responses["sum"]
    assert _number(sum_body["result"]["rows"][0]["sum"]) == expected_sum
    assert _answer_number(sum_body["answer"]) == expected_sum

    breakdown_body = responses["breakdown"]
    observed_breakdown = {
        str(row["region"]): _number(row["sum"])
        for row in breakdown_body["result"]["rows"]
    }
    assert observed_breakdown == expected_breakdown
    assert breakdown_body["answer"] == f"{len(expected_breakdown)} kırılım döndü."

    receipt_path = os.getenv("DIMA_FAST_ASK_LIVE_RECEIPT")
    if receipt_path:
        Path(receipt_path).write_text(
            json.dumps(
                {
                    "status": "GREEN",
                    "anchor": "2026-09-07",
                    "window": ["2026-08-09", "2026-09-08"],
                    "expected": {
                        "count": expected_count,
                        "sum": str(expected_sum),
                        "breakdown": {
                            key: str(value)
                            for key, value in expected_breakdown.items()
                        },
                    },
                    "responses": responses,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
