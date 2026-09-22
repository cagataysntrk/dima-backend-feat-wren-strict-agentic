"""HTTP and SSE surface for Dima Fast run lifecycle."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_principal
from app.fast.run_manager import FastRunManager
from app.fast.run_models import (
    FastRunCreateRequest,
    FastRunSnapshot,
    QUIESCENT_RUN_STATES,
)
from app.fast.run_store import FastRunNotFound, FastRunTransitionError
from control_plane.authorize import Principal


router = APIRouter(prefix="/fast", tags=["fast-runs"])


def _manager(request: Request) -> FastRunManager:
    manager = getattr(request.app.state, "fast_run_manager", None)
    if not isinstance(manager, FastRunManager):
        raise RuntimeError("FastRunManager is not configured")
    return manager


def _not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Run bulunamadı")


@router.post("/runs", response_model=FastRunSnapshot, status_code=202)
def create_run(
    payload: FastRunCreateRequest,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastRunSnapshot:
    try:
        return _manager(request).create_run(payload, principal=principal)
    except FastRunNotFound:
        raise _not_found()
    except FastRunTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/runs/{run_id}", response_model=FastRunSnapshot)
def get_run(
    run_id: str,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastRunSnapshot:
    try:
        return _manager(request).get_run(run_id, principal=principal)
    except FastRunNotFound:
        raise _not_found()


@router.post("/runs/{run_id}/cancel", response_model=FastRunSnapshot)
def cancel_run(
    run_id: str,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastRunSnapshot:
    try:
        return _manager(request).cancel_run(run_id, principal=principal)
    except FastRunNotFound:
        raise _not_found()


@router.get("/runs/{run_id}/events")
def stream_run_events(
    run_id: str,
    request: Request,
    after_event_id: int = Query(default=0, ge=0),
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    principal: Principal = Depends(get_current_principal),
):
    manager = _manager(request)
    try:
        manager.get_run(run_id, principal=principal)
    except FastRunNotFound:
        raise _not_found()

    cursor = after_event_id
    if last_event_id:
        try:
            cursor = max(cursor, int(last_event_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Geçersiz Last-Event-ID") from exc

    def generate():
        nonlocal cursor
        while True:
            events, snapshot = manager.events_after(
                run_id,
                principal=principal,
                after_event_id=cursor,
            )
            for event in events:
                payload = json.dumps(
                    event.model_dump(mode="json"),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                yield (
                    f"id: {event.event_id}\n"
                    f"event: {event.type.value}\n"
                    f"data: {payload}\n\n"
                )
                cursor = event.event_id

            if (
                snapshot.state in QUIESCENT_RUN_STATES
                and cursor >= snapshot.last_event_id
            ):
                return

            next_snapshot = manager.wait_for_change(
                run_id,
                principal=principal,
                after_event_id=cursor,
                timeout=10.0,
            )
            if (
                next_snapshot.last_event_id <= cursor
                and next_snapshot.state not in QUIESCENT_RUN_STATES
            ):
                yield ": keep-alive\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
