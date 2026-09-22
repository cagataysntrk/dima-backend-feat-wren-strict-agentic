from __future__ import annotations

import time
from datetime import date

from fastapi.testclient import TestClient

from app.fast.application import create_fast_application
from app.fast.ask_service import FastAskService
from app.fast.ask_models import (
    AskOutcomeStatus,
    FastAskResponse,
    FastEvidence,
    FastQueryResult,
)
from control_plane.security import create_access_token


QUESTION = "Son 30 günde kaç sipariş var?"


class ApiStubService(FastAskService):
    def __init__(self) -> None:
        # Focused HTTP fixture: preserve the sealed FastAskService owner type
        # without constructing cognition/Metabase dependencies.
        pass

    def ask(self, payload, *, principal):
        result = FastQueryResult(
            columns=("count",),
            rows=({"count": 20},),
            row_count=1,
        )
        return FastAskResponse(
            status=AskOutcomeStatus.SUCCESS,
            question=payload.question,
            answer="Sonuç: 20 kayıt.",
            result=result,
            evidence=FastEvidence(
                evidence_id="ev_" + "a" * 20,
                question=payload.question,
                resource_handle="fast_res_001",
                resource_ref="metabase://table/1",
                field_refs={"temporal": "order_date"},
                exact_time_bounds={
                    "start": "2026-08-09",
                    "end_exclusive": "2026-09-08",
                    "kind": "LAST_N_DAYS",
                },
                portable_query={"lib/type": "mbql/query", "stages": []},
                query_fingerprint="b" * 64,
                access_fingerprint="c" * 64,
                metabase_runtime_version="v0.63.18",
                result=result,
                result_digest="d" * 64,
            ),
        )


def token(user_id):
    return create_access_token(
        sub=user_id,
        tenant_id=None,
        is_superadmin=True,
        roles=["superadmin"],
    )


def auth(user_id):
    return {"Authorization": f"Bearer {token(user_id)}"}


def wait_completed(client, run_id, headers):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        response = client.get(f"/fast/runs/{run_id}", headers=headers)
        assert response.status_code == 200
        body = response.json()
        if body["state"] == "COMPLETED":
            return body
        time.sleep(0.01)
    raise AssertionError("run did not complete")


def test_run_api_requires_auth_and_owner_is_non_enumerating():
    app = create_fast_application(service=ApiStubService())
    with TestClient(app) as client:
        payload = {"question": QUESTION, "as_of_date": "2026-09-07"}
        assert client.post("/fast/runs", json=payload).status_code == 401

        created = client.post(
            "/fast/runs",
            json=payload,
            headers=auth("owner-a"),
        )
        assert created.status_code == 202
        run_id = created.json()["run_id"]

        assert client.get(
            f"/fast/runs/{run_id}",
            headers=auth("owner-b"),
        ).status_code == 404
        assert client.post(
            f"/fast/runs/{run_id}/cancel",
            headers=auth("owner-b"),
        ).status_code == 404
        assert client.get(
            f"/fast/runs/{run_id}/events",
            headers=auth("owner-b"),
        ).status_code == 404


def test_run_api_snapshot_and_sse_replay():
    app = create_fast_application(service=ApiStubService())
    headers = auth("owner-a")
    with TestClient(app) as client:
        created = client.post(
            "/fast/runs",
            json={"question": QUESTION, "as_of_date": "2026-09-07"},
            headers=headers,
        )
        assert created.status_code == 202
        run_id = created.json()["run_id"]
        final = wait_completed(client, run_id, headers)
        assert final["response"]["answer"] == "Sonuç: 20 kayıt."
        assert final["terminal_event_id"] == 3

        stream = client.get(
            f"/fast/runs/{run_id}/events",
            headers=headers,
        )
        assert stream.status_code == 200
        assert stream.headers["content-type"].startswith("text/event-stream")
        text = stream.text
        assert "event: RUN_CREATED" in text
        assert "event: RUN_STARTED" in text
        assert "event: RUN_COMPLETED" in text

        replay = client.get(
            f"/fast/runs/{run_id}/events",
            headers={**headers, "Last-Event-ID": "2"},
        )
        assert replay.status_code == 200
        assert "event: RUN_CREATED" not in replay.text
        assert "event: RUN_STARTED" not in replay.text
        assert "event: RUN_COMPLETED" in replay.text


def test_fast_ask_compatibility_endpoint_remains_available():
    app = create_fast_application(service=ApiStubService())
    with TestClient(app) as client:
        response = client.post(
            "/fast/ask",
            json={"question": QUESTION, "as_of_date": "2026-09-07"},
            headers=auth("owner-a"),
        )
        assert response.status_code == 200
        assert response.json()["answer"] == "Sonuç: 20 kayıt."

        paths = set(app.openapi()["paths"])
        assert "/fast/ask" in paths
        assert "/fast/runs" in paths
        assert "/fast/runs/{run_id}" in paths
        assert "/fast/runs/{run_id}/events" in paths
        assert "/fast/runs/{run_id}/cancel" in paths
        assert "/ask" not in paths
        assert "/ask-v2" not in paths
