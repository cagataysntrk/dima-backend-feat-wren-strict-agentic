from __future__ import annotations

import json
import os
import time
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
    DraftStatus,
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
    os.getenv("DIMA_FAST_RUN_LIVE") != "1",
    reason="FT-004 pinned Metabase lab required",
)

QUESTION = "Son 30 günde kaç sipariş var?"


class LabCognition:
    def draft(self, *, question: str) -> AskDraft:
        assert question == QUESTION
        return AskDraft(
            status=DraftStatus.SUPPORTED,
            unsupported_reason=None,
            search_terms=("orders",),
            aggregation=AggregationKind.COUNT,
            measure_hint=None,
            breakdown_hint=None,
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
        assert purpose == SelectionPurpose.TEMPORAL
        selected = next(item for item in candidates if item.name.lower() == "order_date")
        return SelectionDecision(selected_handle=selected.handle)


class AbstainingResourceCognition(LabCognition):
    def select_resource(self, *, question, candidates):
        assert candidates
        return SelectionDecision(selected_handle=None)


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


def _gateway_factory(base_url: str, session: str):
    def build(principal):
        return FastMetabaseGateway(
            base_url=base_url,
            auth=FastMetabaseAuthContext(
                tenant_id=principal.tenant_id or "__superadmin__",
                dima_user_id=principal.user_id,
                principal_id="metabase-lab-admin",
                mode=FastMetabaseAuthMode.SESSION,
                secret=session,
                role_scope_digest="ft004-synthetic-lab",
            ),
            policy=FastMetabaseRuntimePolicy(
                max_page_rows=200,
                max_total_rows_per_run=1000,
            ),
        )

    return build


def _headers() -> dict[str, str]:
    token = create_access_token(
        sub="ft004-live-user",
        tenant_id=None,
        is_superadmin=True,
        roles=["superadmin"],
    )
    return {"Authorization": f"Bearer {token}"}


def _poll_state(client: TestClient, run_id: str, headers: dict[str, str], expected: set[str]):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        response = client.get(f"/fast/runs/{run_id}", headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        if body["state"] in expected:
            return body
        time.sleep(0.05)
    raise AssertionError(f"run did not reach {expected}")


def _event_types(sse_text: str) -> list[str]:
    return [
        line.removeprefix("event: ").strip()
        for line in sse_text.splitlines()
        if line.startswith("event: ")
    ]


def test_ft004_real_run_lifecycle_over_pinned_metabase():
    base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
    session = _metabase_login(base_url)
    gateway_factory = _gateway_factory(base_url, session)
    headers = _headers()
    expected_count = Decimal(os.environ["FT004_EXPECTED_COUNT"])

    success_service = FastAskService(
        cognition=LabCognition(),
        gateway_factory=gateway_factory,
    )
    success_app = create_fast_application(service=success_service)

    receipt: dict = {
        "status": "RED",
        "anchor": "2026-09-07",
        "window": ["2026-08-09", "2026-09-08"],
        "expected_count": str(expected_count),
    }

    with TestClient(success_app) as client:
        created = client.post(
            "/fast/runs",
            json={"question": QUESTION, "as_of_date": "2026-09-07"},
            headers=headers,
        )
        assert created.status_code == 202, created.text
        created_body = created.json()
        run_id = created_body["run_id"]
        assert created_body["state"] == "CREATED"

        final = _poll_state(client, run_id, headers, {"COMPLETED"})
        assert final["response"]["status"] == "SUCCESS"
        assert Decimal(str(final["response"]["result"]["rows"][0]["count"])) == expected_count
        assert final["response"]["answer"] == f"Sonuç: {int(expected_count)} kayıt."
        evidence = final["response"]["evidence"]
        assert evidence["exact_time_bounds"] == {
            "start": "2026-08-09",
            "end_exclusive": "2026-09-08",
            "kind": "LAST_N_DAYS",
        }
        assert evidence["query_fingerprint"]
        assert evidence["access_fingerprint"]
        assert evidence["result_digest"]
        assert final["terminal_event_id"] == 3

        stream = client.get(f"/fast/runs/{run_id}/events", headers=headers)
        assert stream.status_code == 200, stream.text
        success_events = _event_types(stream.text)
        assert success_events == [
            "RUN_CREATED",
            "RUN_STARTED",
            "RUN_COMPLETED",
        ]

        replay = client.get(
            f"/fast/runs/{run_id}/events",
            headers={**headers, "Last-Event-ID": "2"},
        )
        assert replay.status_code == 200, replay.text
        assert _event_types(replay.text) == ["RUN_COMPLETED"]

        receipt["success_run"] = {
            "run_id": run_id,
            "state": final["state"],
            "terminal_event_id": final["terminal_event_id"],
            "events": success_events,
            "answer": final["response"]["answer"],
            "count": str(final["response"]["result"]["rows"][0]["count"]),
            "query_fingerprint": evidence["query_fingerprint"],
            "access_fingerprint": evidence["access_fingerprint"],
            "result_digest": evidence["result_digest"],
        }

    clarification_service = FastAskService(
        cognition=AbstainingResourceCognition(),
        gateway_factory=gateway_factory,
    )
    clarification_app = create_fast_application(service=clarification_service)

    with TestClient(clarification_app) as client:
        created = client.post(
            "/fast/runs",
            json={"question": QUESTION, "as_of_date": "2026-09-07"},
            headers=headers,
        )
        assert created.status_code == 202, created.text
        run_id = created.json()["run_id"]

        waiting = _poll_state(
            client,
            run_id,
            headers,
            {"WAITING_CLARIFICATION"},
        )
        assert waiting["response"]["status"] == "CLARIFICATION_REQUIRED"
        assert waiting["terminal_event_id"] is None

        cancelled = client.post(
            f"/fast/runs/{run_id}/cancel",
            headers=headers,
        )
        assert cancelled.status_code == 200, cancelled.text
        cancelled_body = cancelled.json()
        assert cancelled_body["state"] == "CANCELLED"
        assert cancelled_body["terminal_event_id"] is not None

        stream = client.get(f"/fast/runs/{run_id}/events", headers=headers)
        assert stream.status_code == 200, stream.text
        clarification_events = _event_types(stream.text)
        assert clarification_events == [
            "RUN_CREATED",
            "RUN_STARTED",
            "RUN_WAITING_CLARIFICATION",
            "CANCEL_REQUESTED",
            "RUN_CANCELLED",
        ]

        receipt["clarification_cancel_run"] = {
            "run_id": run_id,
            "waiting_status": waiting["state"],
            "final_status": cancelled_body["state"],
            "terminal_event_id": cancelled_body["terminal_event_id"],
            "events": clarification_events,
        }

    receipt["status"] = "GREEN"
    path = os.getenv("DIMA_FAST_RUN_LIVE_RECEIPT")
    if path:
        Path(path).write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
        )
