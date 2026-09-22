from __future__ import annotations

import hashlib
import threading
import time

from fastapi.testclient import TestClient

from app.fast.application import create_fast_application
from app.fast.ask_models import (
    AggregationKind,
    AskDraft,
    AskOutcomeStatus,
    DraftStatus,
    DraftTemporalIntent,
    FastAskErrorPayload,
    FastAskResponse,
    FastEvidence,
    FastQueryResult,
    TemporalKind,
)
from app.fast.ask_service import FastAskService
from app.fast.conversation_models import (
    FastFollowupResolution,
    FastFollowupStatus,
)
from app.fast.conversation_service import FastConversationService
from app.fast.conversation_store import FastConversationStore
from app.fast.run_manager import FastRunManager
from control_plane.security import create_access_token


QUESTION = "Son 30 günde kaç sipariş var?"


class ApiAskService(FastAskService):
    def __init__(self) -> None:
        pass

    def ask(self, request, *, principal):
        return FastAskResponse(
            status=AskOutcomeStatus.FAILED,
            question=request.question,
            error=FastAskErrorPayload(code="DEFAULT_UNUSED", message="unexpected"),
        )


class ApiFollowup:
    def resolve(
        self,
        *,
        question,
        accepted_context,
        source_questions,
        clarification_question,
    ):
        return FastFollowupResolution(
            status=FastFollowupStatus.SELF_CONTAINED,
            effective_draft=AskDraft(
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
            ),
        )


class ApiOperation:
    def __init__(self, *, started=None, release=None) -> None:
        self.started = started
        self.release = release

    def ask(self, request, *, principal):
        if self.started is not None:
            self.started.set()
        if self.release is not None:
            assert self.release.wait(timeout=3)
        result = FastQueryResult(
            columns=("count",),
            rows=({"count": 20},),
            row_count=1,
        )
        digest = hashlib.sha256(request.question.encode()).hexdigest()
        return FastAskResponse(
            status=AskOutcomeStatus.SUCCESS,
            question=request.question,
            answer="Sonuç: 20 kayıt.",
            result=result,
            evidence=FastEvidence(
                evidence_id="ev_" + digest[:20],
                question=request.question,
                resource_handle="fast_res_001",
                resource_ref="metabase://table/1",
                field_refs={"temporal": "order_date"},
                exact_time_bounds={
                    "start": "2026-08-09",
                    "end_exclusive": "2026-09-08",
                    "kind": "LAST_N_DAYS",
                },
                portable_query={
                    "lib/type": "mbql/query",
                    "stages": [{"aggregation": [["count", {}]]}],
                },
                query_fingerprint=digest,
                access_fingerprint="a" * 64,
                metabase_runtime_version="v0.63.18",
                result=result,
                result_digest=hashlib.sha256((digest + "result").encode()).hexdigest(),
            ),
        )


class ApiFactory:
    def __init__(self, *, started=None, release=None):
        self.started = started
        self.release = release

    def build(self, **kwargs):
        return ApiOperation(started=self.started, release=self.release)


def token(user_id: str):
    return create_access_token(
        sub=user_id,
        tenant_id=None,
        is_superadmin=True,
        roles=["superadmin"],
    )


def auth(user_id: str):
    return {"Authorization": f"Bearer {token(user_id)}"}


def app_bundle(*, started=None, release=None):
    ask = ApiAskService()
    manager = FastRunManager(service=ask, max_workers=1)
    conversation = FastConversationService(
        store=FastConversationStore(),
        run_manager=manager,
        followup_cognition=ApiFollowup(),
        operation_factory=ApiFactory(started=started, release=release),
    )
    app = create_fast_application(
        service=ask,
        run_manager=manager,
        conversation_service=conversation,
    )
    return app, manager


def wait_turn(client, conversation_id, turn_id, headers):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        response = client.get(
            f"/fast/conversations/{conversation_id}/turns/{turn_id}",
            headers=headers,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        if body["status"] == "COMPLETED":
            return body
        time.sleep(0.01)
    raise AssertionError("turn did not complete")


def test_conversation_http_requires_auth_and_is_owner_isolated():
    app, _ = app_bundle()
    with TestClient(app) as client:
        assert client.post("/fast/conversations", json={}).status_code == 401

        created = client.post(
            "/fast/conversations",
            json={"title": "Orders"},
            headers=auth("owner-a"),
        )
        assert created.status_code == 201
        conversation_id = created.json()["conversation_id"]

        assert client.get(
            f"/fast/conversations/{conversation_id}",
            headers=auth("owner-b"),
        ).status_code == 404


def test_conversation_http_turn_creates_separate_run_and_canonical_detail():
    app, _ = app_bundle()
    headers = auth("owner-a")
    with TestClient(app) as client:
        conversation = client.post(
            "/fast/conversations",
            json={},
            headers=headers,
        ).json()
        conversation_id = conversation["conversation_id"]

        created = client.post(
            f"/fast/conversations/{conversation_id}/turns",
            json={"question": QUESTION, "as_of_date": "2026-09-07"},
            headers=headers,
        )
        assert created.status_code == 202, created.text
        turn = created.json()
        assert turn["run_id"].startswith("run_")
        assert turn["turn_id"].startswith("turn_")

        final = wait_turn(
            client,
            conversation_id,
            turn["turn_id"],
            headers,
        )
        assert final["status"] == "COMPLETED"
        assert final["accepted_context"]["evidence_ids"]

        detail = client.get(
            f"/fast/conversations/{conversation_id}",
            headers=headers,
        )
        assert detail.status_code == 200
        payload = detail.json()
        assert payload["conversation"]["turn_count"] == 1
        assert payload["turns"][0]["run_id"] == turn["run_id"]

        run = client.get(
            f"/fast/runs/{turn['run_id']}",
            headers=headers,
        )
        assert run.status_code == 200
        assert run.json()["state"] == "COMPLETED"


def test_conversation_http_active_run_conflict_is_409():
    started = threading.Event()
    release = threading.Event()
    app, _ = app_bundle(started=started, release=release)
    headers = auth("owner-a")
    try:
        with TestClient(app) as client:
            conversation_id = client.post(
                "/fast/conversations",
                json={},
                headers=headers,
            ).json()["conversation_id"]

            first = client.post(
                f"/fast/conversations/{conversation_id}/turns",
                json={"question": QUESTION},
                headers=headers,
            )
            assert first.status_code == 202
            assert started.wait(timeout=2)

            second = client.post(
                f"/fast/conversations/{conversation_id}/turns",
                json={"question": "Peki geçen ay?"},
                headers=headers,
            )
            assert second.status_code == 409
            assert second.json()["detail"]["code"] == "ACTIVE_RUN_EXISTS"
    finally:
        release.set()


def test_fast_app_without_conversation_service_preserves_sealed_surface():
    app = create_fast_application(service=ApiAskService())
    with TestClient(app) as client:
        response = client.post(
            "/fast/conversations",
            json={},
            headers=auth("owner-a"),
        )
        assert response.status_code == 404
