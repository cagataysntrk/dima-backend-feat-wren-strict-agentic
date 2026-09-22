"""Bounded asynchronous lifecycle manager around the sealed FT-003 Ask service."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from threading import RLock
from typing import Any

from app.fast.ask_models import AskOutcomeStatus
from app.fast.ask_service import FastAskService
from app.fast.run_models import (
    FastRunCreateRequest,
    FastRunErrorPayload,
    FastRunEventType,
    FastRunSnapshot,
    FastRunState,
    TERMINAL_RUN_STATES,
)
from app.fast.run_store import (
    FastRunNotFound,
    FastRunOwner,
    FastRunStore,
    FastRunTransitionError,
)


class FastRunManager:
    def __init__(
        self,
        *,
        service: FastAskService,
        store: FastRunStore | None = None,
        max_workers: int = 4,
    ) -> None:
        if max_workers < 1 or max_workers > 32:
            raise ValueError("max_workers must be in 1..32")
        self._service = service
        self._store = store or FastRunStore()
        self._max_workers = max_workers
        self._executor: ThreadPoolExecutor | None = None
        self._lock = RLock()
        self._futures: dict[str, Future[None]] = {}

    @property
    def store(self) -> FastRunStore:
        return self._store

    def _executor_for_submit(self) -> ThreadPoolExecutor:
        with self._lock:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix="dima-fast-run",
                )
            return self._executor

    def create_run(
        self,
        payload: FastRunCreateRequest,
        *,
        principal: Any,
    ) -> FastRunSnapshot:
        owner = FastRunOwner.from_principal(principal)
        root_run_id = None
        attempt = 1
        if payload.retry_of_run_id is not None:
            root_run_id, attempt = self._store.retry_lineage(
                payload.retry_of_run_id,
                owner,
                payload,
            )

        snapshot = self._store.create(
            request=payload,
            owner=owner,
            retry_of_run_id=payload.retry_of_run_id,
            root_run_id=root_run_id,
            attempt=attempt,
        )
        future = self._executor_for_submit().submit(
            self._execute,
            snapshot.run_id,
            payload,
            principal,
        )
        with self._lock:
            self._futures[snapshot.run_id] = future
        return snapshot

    def _safe_transition(self, run_id: str, **kwargs) -> FastRunSnapshot:
        try:
            _, snapshot = self._store.transition(run_id, **kwargs)
            return snapshot
        except FastRunTransitionError:
            return self._store.internal_snapshot(run_id)

    def _begin_execution(self, run_id: str) -> bool:
        """Acquire RUNNING authority or close an expected cancel/start race.

        Generic invalid transitions remain errors. The only tolerated race here is a
        cancellation that wins after the worker pre-check but before RUN_STARTED.
        """
        try:
            _, snapshot = self._store.transition(
                run_id,
                state=FastRunState.RUNNING,
                event_type=FastRunEventType.RUN_STARTED,
                payload={},
                dedupe_key="run-started",
            )
        except FastRunTransitionError:
            snapshot = self._store.internal_snapshot(run_id)
            if snapshot.state == FastRunState.CANCEL_REQUESTED:
                try:
                    self._store.transition(
                        run_id,
                        state=FastRunState.CANCELLED,
                        event_type=FastRunEventType.RUN_CANCELLED,
                        payload={"reason": "cancelled_before_execution"},
                        dedupe_key="run-cancelled",
                    )
                except FastRunTransitionError:
                    final = self._store.internal_snapshot(run_id)
                    if final.state not in TERMINAL_RUN_STATES:
                        raise
                return False
            if snapshot.state in TERMINAL_RUN_STATES:
                return False
            raise

        if snapshot.state != FastRunState.RUNNING:
            raise FastRunTransitionError(
                f"RUNNING transition returned unexpected state {snapshot.state.value}"
            )
        return True

    def _execute(
        self,
        run_id: str,
        payload: FastRunCreateRequest,
        principal: Any,
    ) -> None:
        try:
            snapshot = self._store.internal_snapshot(run_id)
            if snapshot.state == FastRunState.CANCEL_REQUESTED:
                self._safe_transition(
                    run_id,
                    state=FastRunState.CANCELLED,
                    event_type=FastRunEventType.RUN_CANCELLED,
                    payload={"reason": "cancelled_before_execution"},
                    dedupe_key="run-cancelled",
                )
                return
            if snapshot.state in TERMINAL_RUN_STATES:
                return

            if not self._begin_execution(run_id):
                return

            response = self._service.ask(
                payload.ask_request(),
                principal=principal,
            )

            snapshot = self._store.internal_snapshot(run_id)
            if snapshot.state == FastRunState.CANCEL_REQUESTED:
                self._safe_transition(
                    run_id,
                    state=FastRunState.CANCELLED,
                    event_type=FastRunEventType.RUN_CANCELLED,
                    payload={"reason": "cancelled_after_bounded_call"},
                    dedupe_key="run-cancelled",
                )
                return
            if snapshot.state in TERMINAL_RUN_STATES:
                return

            response_payload = response.model_dump(mode="json")
            if response.status == AskOutcomeStatus.CLARIFICATION_REQUIRED:
                self._safe_transition(
                    run_id,
                    state=FastRunState.WAITING_CLARIFICATION,
                    event_type=FastRunEventType.RUN_WAITING_CLARIFICATION,
                    payload={"response": response_payload},
                    dedupe_key="run-waiting-clarification",
                    response=response,
                )
            elif response.status == AskOutcomeStatus.FAILED:
                self._safe_transition(
                    run_id,
                    state=FastRunState.FAILED,
                    event_type=FastRunEventType.RUN_FAILED,
                    payload={"response": response_payload},
                    dedupe_key="run-failed",
                    response=response,
                    error=FastRunErrorPayload(
                        code=(
                            response.error.code
                            if response.error is not None
                            else "ASK_FAILED"
                        ),
                        message=(
                            response.error.message
                            if response.error is not None
                            else "Fast Ask failed"
                        ),
                    ),
                )
            else:
                self._safe_transition(
                    run_id,
                    state=FastRunState.COMPLETED,
                    event_type=FastRunEventType.RUN_COMPLETED,
                    payload={"response": response_payload},
                    dedupe_key="run-completed",
                    response=response,
                )
        except Exception:
            snapshot = self._store.internal_snapshot(run_id)
            if snapshot.state == FastRunState.CANCEL_REQUESTED:
                self._safe_transition(
                    run_id,
                    state=FastRunState.CANCELLED,
                    event_type=FastRunEventType.RUN_CANCELLED,
                    payload={"reason": "cancelled_during_failed_call"},
                    dedupe_key="run-cancelled",
                )
            elif snapshot.state not in TERMINAL_RUN_STATES:
                self._safe_transition(
                    run_id,
                    state=FastRunState.FAILED,
                    event_type=FastRunEventType.RUN_FAILED,
                    payload={"code": "RUN_EXECUTION_FAILED"},
                    dedupe_key="run-failed",
                    error=FastRunErrorPayload(
                        code="RUN_EXECUTION_FAILED",
                        message="run execution failed safely",
                    ),
                )
        finally:
            with self._lock:
                self._futures.pop(run_id, None)

    def get_run(self, run_id: str, *, principal: Any) -> FastRunSnapshot:
        return self._store.snapshot(
            run_id,
            FastRunOwner.from_principal(principal),
        )

    def events_after(
        self,
        run_id: str,
        *,
        principal: Any,
        after_event_id: int = 0,
    ):
        return self._store.events_after(
            run_id,
            FastRunOwner.from_principal(principal),
            after_event_id=after_event_id,
        )

    def wait_for_change(
        self,
        run_id: str,
        *,
        principal: Any,
        after_event_id: int,
        timeout: float = 10.0,
    ) -> FastRunSnapshot:
        return self._store.wait_for_change(
            run_id,
            FastRunOwner.from_principal(principal),
            after_event_id=after_event_id,
            timeout=timeout,
        )

    def cancel_run(self, run_id: str, *, principal: Any) -> FastRunSnapshot:
        owner = FastRunOwner.from_principal(principal)
        snapshot = self._store.snapshot(run_id, owner)
        if snapshot.state in TERMINAL_RUN_STATES:
            return snapshot
        if snapshot.state == FastRunState.CANCEL_REQUESTED:
            return snapshot

        pre_cancel_state = snapshot.state
        try:
            _, snapshot = self._store.transition(
                run_id,
                state=FastRunState.CANCEL_REQUESTED,
                event_type=FastRunEventType.CANCEL_REQUESTED,
                payload={},
                dedupe_key="cancel-requested",
            )
        except FastRunTransitionError:
            # A worker may have reached a terminal state between the read above
            # and the cancel transition. Terminal authority wins that race.
            return self._store.snapshot(run_id, owner)

        with self._lock:
            future = self._futures.get(run_id)

        cancelled_before_start = bool(future is not None and future.cancel())
        no_active_worker = (
            future is None
            or future.done()
            or future.cancelled()
        )

        if (
            pre_cancel_state == FastRunState.WAITING_CLARIFICATION
            or cancelled_before_start
            or no_active_worker
        ):
            snapshot = self._safe_transition(
                run_id,
                state=FastRunState.CANCELLED,
                event_type=FastRunEventType.RUN_CANCELLED,
                payload={"reason": "cancelled_without_active_worker"},
                dedupe_key="run-cancelled",
            )
        return snapshot

    def interrupt_nonterminal_runs(self) -> tuple[str, ...]:
        return self._store.interrupt_nonterminal_runs()

    def shutdown(self, *, interrupt: bool = True) -> None:
        if interrupt:
            self.interrupt_nonterminal_runs()
        with self._lock:
            executor = self._executor
            self._executor = None
        if executor is not None:
            executor.shutdown(wait=False, cancel_futures=True)
