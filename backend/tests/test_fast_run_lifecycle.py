from __future__ import annotations

import threading
import time
from datetime import date
from types import SimpleNamespace

import pytest

from app.fast.ask_models import (
    AskOutcomeStatus,
    FastAskErrorPayload,
    FastAskResponse,
    FastQueryResult,
)
from app.fast.run_manager import FastRunManager
from app.fast.run_models import (
    FastRunCreateRequest,
    FastRunEventType,
    FastRunState,
)
from app.fast.run_store import (
    FastRunOwner,
    FastRunStore,
    FastRunTransitionError,
)


def principal(user_id="user-a"):
    return SimpleNamespace(
        user_id=user_id,
        tenant_id="tenant-a",
        is_superadmin=False,
        roles=["analyst"],
        tenant_slug="tenant-a",
    )


def request(retry_of_run_id=None):
    return FastRunCreateRequest(
        question="Son 30 günde kaç sipariş var?",
        as_of_date=date(2026, 9, 7),
        retry_of_run_id=retry_of_run_id,
    )


def success_response():
    return FastAskResponse(
        status=AskOutcomeStatus.SUCCESS,
        question="Son 30 günde kaç sipariş var?",
        answer="Sonuç: 20 kayıt.",
        result=FastQueryResult(
            columns=("count",),
            rows=({"count": 20},),
            row_count=1,
        ),
        evidence=__import__(
            "app.fast.ask_models", fromlist=["FastEvidence"]
        ).FastEvidence(
            evidence_id="ev_" + "a" * 20,
            question="Son 30 günde kaç sipariş var?",
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
            query_fingerprint="b" * 64,
            access_fingerprint="c" * 64,
            metabase_runtime_version="v0.63.18",
            result=FastQueryResult(
                columns=("count",),
                rows=({"count": 20},),
                row_count=1,
            ),
            result_digest="d" * 64,
        ),
    )


class StubService:
    def __init__(self, response, *, started=None, release=None):
        self.response = response
        self.calls = 0
        self.started = started
        self.release = release

    def ask(self, payload, *, principal):
        self.calls += 1
        if self.started is not None:
            self.started.set()
        if self.release is not None:
            assert self.release.wait(timeout=3)
        return self.response


def wait_state(manager, run_id, expected, *, p=None, timeout=3):
    p = p or principal()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        snapshot = manager.get_run(run_id, principal=p)
        if snapshot.state in expected:
            return snapshot
        time.sleep(0.01)
    raise AssertionError(manager.get_run(run_id, principal=p))


def test_success_terminal_exactly_once_and_events_monotonic():
    manager = FastRunManager(service=StubService(success_response()), max_workers=1)
    try:
        created = manager.create_run(request(), principal=principal())
        final = wait_state(manager, created.run_id, {FastRunState.COMPLETED})

        assert final.terminal_event_id == 3
        events, snapshot = manager.events_after(
            created.run_id,
            principal=principal(),
        )
        assert [event.event_id for event in events] == [1, 2, 3]
        assert [event.type for event in events] == [
            FastRunEventType.RUN_CREATED,
            FastRunEventType.RUN_STARTED,
            FastRunEventType.RUN_COMPLETED,
        ]
        assert snapshot.response is not None
        assert snapshot.response.answer == "Sonuç: 20 kayıt."

        before = len(events)
        cancelled = manager.cancel_run(created.run_id, principal=principal())
        events_after, _ = manager.events_after(created.run_id, principal=principal())
        assert cancelled.state == FastRunState.COMPLETED
        assert len(events_after) == before
    finally:
        manager.shutdown(interrupt=False)


def test_clarification_waits_then_can_be_cancelled():
    response = FastAskResponse(
        status=AskOutcomeStatus.CLARIFICATION_REQUIRED,
        question="Siparişleri say.",
        error=FastAskErrorPayload(
            code="AMBIGUOUS_RESOURCE",
            message="resource selection requires clarification",
        ),
    )
    manager = FastRunManager(service=StubService(response), max_workers=1)
    try:
        created = manager.create_run(
            FastRunCreateRequest(question="Siparişleri say."),
            principal=principal(),
        )
        waiting = wait_state(
            manager,
            created.run_id,
            {FastRunState.WAITING_CLARIFICATION},
        )
        assert waiting.terminal_event_id is None

        cancelled = manager.cancel_run(created.run_id, principal=principal())
        assert cancelled.state == FastRunState.CANCELLED
        assert cancelled.terminal_event_id is not None
        events, _ = manager.events_after(created.run_id, principal=principal())
        assert [event.type for event in events][-2:] == [
            FastRunEventType.CANCEL_REQUESTED,
            FastRunEventType.RUN_CANCELLED,
        ]
    finally:
        manager.shutdown(interrupt=False)


def test_failed_ask_maps_to_failed_run():
    response = FastAskResponse(
        status=AskOutcomeStatus.FAILED,
        question="Hatalı alan",
        error=FastAskErrorPayload(
            code="COGNITION_INVALID",
            message="blocked",
        ),
    )
    manager = FastRunManager(service=StubService(response), max_workers=1)
    try:
        created = manager.create_run(
            FastRunCreateRequest(question="Hatalı alan"),
            principal=principal(),
        )
        final = wait_state(manager, created.run_id, {FastRunState.FAILED})
        assert final.error is not None
        assert final.error.code == "COGNITION_INVALID"
    finally:
        manager.shutdown(interrupt=False)


def test_running_cancel_discards_late_success_and_emits_one_terminal():
    started = threading.Event()
    release = threading.Event()
    service = StubService(success_response(), started=started, release=release)
    manager = FastRunManager(service=service, max_workers=1)
    try:
        created = manager.create_run(request(), principal=principal())
        assert started.wait(timeout=2)
        cancelled = manager.cancel_run(created.run_id, principal=principal())
        assert cancelled.state == FastRunState.CANCEL_REQUESTED
        release.set()

        final = wait_state(manager, created.run_id, {FastRunState.CANCELLED})
        assert final.response is None
        events, _ = manager.events_after(created.run_id, principal=principal())
        terminal = [
            event for event in events if event.state in {
                FastRunState.COMPLETED,
                FastRunState.FAILED,
                FastRunState.CANCELLED,
                FastRunState.INTERRUPTED,
            }
        ]
        assert [event.type for event in terminal] == [FastRunEventType.RUN_CANCELLED]
    finally:
        release.set()
        manager.shutdown(interrupt=False)


def test_store_dedupes_duplicate_transition_event():
    store = FastRunStore()
    owner = FastRunOwner.from_principal(principal())
    created = store.create(request=request(), owner=owner)

    first, _ = store.transition(
        created.run_id,
        state=FastRunState.RUNNING,
        event_type=FastRunEventType.RUN_STARTED,
        dedupe_key="run-started",
    )
    second, snapshot = store.transition(
        created.run_id,
        state=FastRunState.RUNNING,
        event_type=FastRunEventType.RUN_STARTED,
        dedupe_key="run-started",
    )

    assert first.event_id == second.event_id == 2
    assert snapshot.last_event_id == 2


def test_terminal_store_transition_is_immutable():
    store = FastRunStore()
    owner = FastRunOwner.from_principal(principal())
    created = store.create(request=request(), owner=owner)
    store.transition(
        created.run_id,
        state=FastRunState.RUNNING,
        event_type=FastRunEventType.RUN_STARTED,
        dedupe_key="run-started",
    )
    store.transition(
        created.run_id,
        state=FastRunState.COMPLETED,
        event_type=FastRunEventType.RUN_COMPLETED,
        dedupe_key="run-completed",
    )
    with pytest.raises(FastRunTransitionError):
        store.transition(
            created.run_id,
            state=FastRunState.CANCELLED,
            event_type=FastRunEventType.RUN_CANCELLED,
            dedupe_key="run-cancelled",
        )


def test_interrupt_nonterminal_is_terminal_exactly_once():
    started = threading.Event()
    release = threading.Event()
    manager = FastRunManager(
        service=StubService(success_response(), started=started, release=release),
        max_workers=1,
    )
    try:
        created = manager.create_run(request(), principal=principal())
        assert started.wait(timeout=2)
        interrupted = manager.interrupt_nonterminal_runs()
        assert created.run_id in interrupted
        release.set()

        final = wait_state(manager, created.run_id, {FastRunState.INTERRUPTED})
        events, _ = manager.events_after(created.run_id, principal=principal())
        assert sum(
            event.type == FastRunEventType.RUN_INTERRUPTED for event in events
        ) == 1
        assert final.terminal_event_id is not None
    finally:
        release.set()
        manager.shutdown(interrupt=False)


def test_retry_lineage_creates_new_immutable_run():
    failed = FastAskResponse(
        status=AskOutcomeStatus.FAILED,
        question="Hatalı alan",
        error=FastAskErrorPayload(code="BLOCKED", message="blocked"),
    )
    manager = FastRunManager(service=StubService(failed), max_workers=1)
    try:
        first = manager.create_run(
            FastRunCreateRequest(question="Hatalı alan"),
            principal=principal(),
        )
        first_final = wait_state(manager, first.run_id, {FastRunState.FAILED})

        retry = manager.create_run(
            FastRunCreateRequest(
                question="Hatalı alan",
                retry_of_run_id=first.run_id,
            ),
            principal=principal(),
        )
        second_final = wait_state(manager, retry.run_id, {FastRunState.FAILED})

        assert second_final.run_id != first_final.run_id
        assert second_final.retry_of_run_id == first_final.run_id
        assert second_final.root_run_id == first_final.root_run_id
        assert second_final.attempt == 2
        assert manager.get_run(first.run_id, principal=principal()).attempt == 1
    finally:
        manager.shutdown(interrupt=False)
