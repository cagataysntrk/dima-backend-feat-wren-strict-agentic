"""Thread-safe in-process canonical run/event store for FT-004."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Condition, RLock
from typing import Any
from uuid import uuid4

from app.fast.ask_models import FastAskResponse
from app.fast.run_models import (
    FastRunCreateRequest,
    FastRunErrorPayload,
    FastRunEvent,
    FastRunEventType,
    FastRunSnapshot,
    FastRunState,
    QUIESCENT_RUN_STATES,
    TERMINAL_RUN_STATES,
)


class FastRunNotFound(LookupError):
    pass


class FastRunTransitionError(RuntimeError):
    pass


@dataclass(frozen=True)
class FastRunOwner:
    """Durable run ownership identity, separate from mutable authorization claims."""

    user_id: str
    tenant_id: str | None

    @classmethod
    def from_principal(cls, principal: Any) -> "FastRunOwner":
        return cls(
            user_id=str(principal.user_id),
            tenant_id=(
                None
                if getattr(principal, "tenant_id", None) is None
                else str(principal.tenant_id)
            ),
        )


@dataclass
class _RunRecord:
    run_id: str
    owner: FastRunOwner
    request: FastRunCreateRequest
    state: FastRunState
    created_at: datetime
    updated_at: datetime
    retry_of_run_id: str | None
    root_run_id: str
    attempt: int
    response: FastAskResponse | None = None
    error: FastRunErrorPayload | None = None
    events: list[FastRunEvent] = field(default_factory=list)
    dedupe: dict[str, int] = field(default_factory=dict)
    terminal_event_id: int | None = None


_ALLOWED: dict[FastRunState, frozenset[FastRunState]] = {
    FastRunState.CREATED: frozenset(
        {
            FastRunState.RUNNING,
            FastRunState.CANCEL_REQUESTED,
            FastRunState.CANCELLED,
            FastRunState.INTERRUPTED,
        }
    ),
    FastRunState.RUNNING: frozenset(
        {
            FastRunState.PARTIAL,
            FastRunState.WAITING_CLARIFICATION,
            FastRunState.COMPLETED,
            FastRunState.FAILED,
            FastRunState.CANCEL_REQUESTED,
            FastRunState.INTERRUPTED,
        }
    ),
    FastRunState.PARTIAL: frozenset(
        {
            FastRunState.RUNNING,
            FastRunState.WAITING_CLARIFICATION,
            FastRunState.COMPLETED,
            FastRunState.FAILED,
            FastRunState.CANCEL_REQUESTED,
            FastRunState.INTERRUPTED,
        }
    ),
    FastRunState.WAITING_CLARIFICATION: frozenset(
        {
            FastRunState.CANCEL_REQUESTED,
            FastRunState.CANCELLED,
            FastRunState.INTERRUPTED,
        }
    ),
    FastRunState.CANCEL_REQUESTED: frozenset(
        {
            FastRunState.CANCELLED,
            FastRunState.INTERRUPTED,
        }
    ),
    FastRunState.COMPLETED: frozenset(),
    FastRunState.FAILED: frozenset(),
    FastRunState.CANCELLED: frozenset(),
    FastRunState.INTERRUPTED: frozenset(),
}


class FastRunStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._condition = Condition(self._lock)
        self._records: dict[str, _RunRecord] = {}

    def create(
        self,
        *,
        request: FastRunCreateRequest,
        owner: FastRunOwner,
        retry_of_run_id: str | None = None,
        root_run_id: str | None = None,
        attempt: int = 1,
    ) -> FastRunSnapshot:
        with self._condition:
            run_id = "run_" + uuid4().hex
            now = datetime.now(timezone.utc)
            record = _RunRecord(
                run_id=run_id,
                owner=owner,
                request=request,
                state=FastRunState.CREATED,
                created_at=now,
                updated_at=now,
                retry_of_run_id=retry_of_run_id,
                root_run_id=root_run_id or run_id,
                attempt=attempt,
            )
            self._records[run_id] = record
            self._append_locked(
                record,
                event_type=FastRunEventType.RUN_CREATED,
                state=FastRunState.CREATED,
                payload={"attempt": attempt},
                dedupe_key="run-created",
            )
            return self._snapshot_locked(record)

    def _record_locked(self, run_id: str) -> _RunRecord:
        try:
            return self._records[run_id]
        except KeyError as exc:
            raise FastRunNotFound("run not found") from exc

    def _authorized_locked(self, run_id: str, owner: FastRunOwner) -> _RunRecord:
        record = self._record_locked(run_id)
        if record.owner != owner:
            raise FastRunNotFound("run not found")
        return record

    def _snapshot_locked(self, record: _RunRecord) -> FastRunSnapshot:
        return FastRunSnapshot(
            run_id=record.run_id,
            state=record.state,
            question=record.request.question,
            as_of_date=record.request.as_of_date,
            created_at=record.created_at,
            updated_at=record.updated_at,
            response=record.response,
            error=record.error,
            last_event_id=record.events[-1].event_id,
            terminal_event_id=record.terminal_event_id,
            retry_of_run_id=record.retry_of_run_id,
            root_run_id=record.root_run_id,
            attempt=record.attempt,
        )

    def snapshot(self, run_id: str, owner: FastRunOwner) -> FastRunSnapshot:
        with self._lock:
            return self._snapshot_locked(self._authorized_locked(run_id, owner))

    def internal_snapshot(self, run_id: str) -> FastRunSnapshot:
        with self._lock:
            return self._snapshot_locked(self._record_locked(run_id))

    def retry_lineage(
        self,
        source_run_id: str,
        owner: FastRunOwner,
        request: FastRunCreateRequest,
    ) -> tuple[str, int]:
        with self._lock:
            record = self._authorized_locked(source_run_id, owner)
            if record.state not in {
                FastRunState.FAILED,
                FastRunState.CANCELLED,
                FastRunState.INTERRUPTED,
            }:
                raise FastRunTransitionError(
                    "retry source must be FAILED, CANCELLED, or INTERRUPTED"
                )
            if (
                request.question != record.request.question
                or request.as_of_date != record.request.as_of_date
            ):
                raise FastRunTransitionError(
                    "retry request must match source question and as_of_date"
                )
            return record.root_run_id, record.attempt + 1

    def _append_locked(
        self,
        record: _RunRecord,
        *,
        event_type: FastRunEventType,
        state: FastRunState,
        payload: dict[str, Any],
        dedupe_key: str,
    ) -> FastRunEvent:
        existing = record.dedupe.get(dedupe_key)
        if existing is not None:
            return record.events[existing - 1]
        event = FastRunEvent(
            event_id=len(record.events) + 1,
            run_id=record.run_id,
            type=event_type,
            state=state,
            occurred_at=datetime.now(timezone.utc),
            payload=payload,
            dedupe_key=dedupe_key,
        )
        record.events.append(event)
        record.dedupe[dedupe_key] = event.event_id
        record.updated_at = event.occurred_at
        if state in TERMINAL_RUN_STATES:
            if record.terminal_event_id is not None:
                raise FastRunTransitionError("terminal event already exists")
            record.terminal_event_id = event.event_id
        self._condition.notify_all()
        return event

    def transition(
        self,
        run_id: str,
        *,
        state: FastRunState,
        event_type: FastRunEventType,
        payload: dict[str, Any] | None = None,
        dedupe_key: str,
        response: FastAskResponse | None = None,
        error: FastRunErrorPayload | None = None,
    ) -> tuple[FastRunEvent, FastRunSnapshot]:
        with self._condition:
            record = self._record_locked(run_id)
            existing = record.dedupe.get(dedupe_key)
            if existing is not None:
                return record.events[existing - 1], self._snapshot_locked(record)
            if record.state in TERMINAL_RUN_STATES:
                raise FastRunTransitionError("terminal run is immutable")
            if state not in _ALLOWED[record.state]:
                raise FastRunTransitionError(
                    f"invalid transition {record.state.value}->{state.value}"
                )
            record.state = state
            if response is not None:
                record.response = response
            if error is not None:
                record.error = error
            event = self._append_locked(
                record,
                event_type=event_type,
                state=state,
                payload=dict(payload or {}),
                dedupe_key=dedupe_key,
            )
            return event, self._snapshot_locked(record)

    def events_after(
        self,
        run_id: str,
        owner: FastRunOwner,
        *,
        after_event_id: int = 0,
    ) -> tuple[tuple[FastRunEvent, ...], FastRunSnapshot]:
        with self._lock:
            record = self._authorized_locked(run_id, owner)
            events = tuple(
                event for event in record.events if event.event_id > after_event_id
            )
            return events, self._snapshot_locked(record)

    def wait_for_change(
        self,
        run_id: str,
        owner: FastRunOwner,
        *,
        after_event_id: int,
        timeout: float,
    ) -> FastRunSnapshot:
        with self._condition:
            record = self._authorized_locked(run_id, owner)
            self._condition.wait_for(
                lambda: (
                    record.events[-1].event_id > after_event_id
                    or record.state in QUIESCENT_RUN_STATES
                ),
                timeout=timeout,
            )
            return self._snapshot_locked(record)

    def interrupt_nonterminal_runs(self) -> tuple[str, ...]:
        interrupted: list[str] = []
        with self._condition:
            for record in list(self._records.values()):
                if record.state in TERMINAL_RUN_STATES:
                    continue
                try:
                    self.transition(
                        record.run_id,
                        state=FastRunState.INTERRUPTED,
                        event_type=FastRunEventType.RUN_INTERRUPTED,
                        payload={"reason": "runtime_interrupted"},
                        dedupe_key="run-interrupted",
                        error=FastRunErrorPayload(
                            code="RUN_INTERRUPTED",
                            message="run was interrupted by runtime shutdown/recovery",
                        ),
                    )
                    interrupted.append(record.run_id)
                except FastRunTransitionError:
                    continue
        return tuple(interrupted)
