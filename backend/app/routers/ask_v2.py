"""Authoritative feature-flagged Dima V2 product front door."""

from __future__ import annotations

import json
import queue
import threading

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_principal, require, require_company
from app.config import get_settings
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_events import ProductEventSink
from app.v2.product_models import ProductAskRequest, ProductEventKind, ProductResponse
from app.v2.report_continuation import (
    ReportContinuationNotAdmissibleError,
    StaleReportContinuationError,
)
from app.v2.runtime_boundary import request_ref
from control_plane.authorize import Principal


router = APIRouter(tags=["ask-v2"])
_coordinator = ProductCoordinator()


@router.post(
    "/ask-v2",
    response_model=ProductResponse,
    dependencies=[Depends(require("query:run")), Depends(require_company)],
)
def ask_v2(
    request: Request,
    body: ProductAskRequest,
    principal: Principal = Depends(get_current_principal),
) -> ProductResponse:
    if not get_settings().ask_v2_enabled:
        raise HTTPException(status_code=404, detail="ask-v2 kapalı")

    if body.clarification_token is not None:
        # Historical Day2 SemanticResolver tokens are intentionally not authoritative on
        # the Day10 product graph. A future product clarification continuation must have
        # its own typed/current-context contract rather than silently falling back.
        raise HTTPException(
            status_code=409,
            detail={
                "code": "legacy_clarification_continuation_not_authoritative",
                "message": "Bu continuation yeni /ask-v2 product authority ile yeniden bağlanmalı.",
            },
        )

    try:
        return _coordinator.handle(
            request=request,
            body=body,
            principal=principal,
        )
    except StaleReportContinuationError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "stale_report_section_continuation",
                "message": str(exc),
            },
        ) from exc
    except ReportContinuationNotAdmissibleError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "section_followup_binding_not_admissible",
                "message": str(exc),
            },
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        # No stack/provider payload crosses the product HTTP boundary.
        raise HTTPException(
            status_code=503,
            detail={
                "code": "product_unavailable",
                "message": f"Product coordinator unavailable ({type(exc).__name__}).",
            },
        ) from exc


@router.post(
    "/ask-v2/stream",
    dependencies=[Depends(require("query:run")), Depends(require_company)],
)
def ask_v2_stream(
    request: Request,
    body: ProductAskRequest,
    principal: Principal = Depends(get_current_principal),
):
    if not get_settings().ask_v2_enabled:
        raise HTTPException(status_code=404, detail="ask-v2 kapalı")
    if body.clarification_token is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "legacy_clarification_continuation_not_authoritative",
                "message": "Bu continuation yeni /ask-v2 product authority ile yeniden bağlanmalı.",
            },
        )

    frames: queue.Queue = queue.Queue()
    cancelled = threading.Event()
    req_ref = request_ref(body)

    def on_event(event) -> None:
        frames.put(
            {
                "type": "event",
                "event": event.model_dump(mode="json"),
            }
        )

    sink = ProductEventSink(
        request_ref=req_ref,
        on_event=on_event,
    )

    def run_product() -> None:
        try:
            response = _coordinator.handle(
                request=request,
                body=body,
                principal=principal,
                event_sink=sink,
                cancel_check=cancelled.is_set,
            )
            frames.put(
                {
                    "type": "response",
                    "response": response.model_dump(mode="json"),
                }
            )
        except Exception as exc:
            frames.put(
                {
                    "type": "error",
                    "error": {
                        "code": "product_unavailable",
                        "message": f"Product coordinator unavailable ({type(exc).__name__}).",
                    },
                }
            )
        finally:
            frames.put(None)

    threading.Thread(target=run_product, daemon=True).start()

    def stream():
        keepalive_ix = 0
        try:
            while True:
                try:
                    frame = frames.get(timeout=7.0)
                except queue.Empty:
                    keepalive_ix += 1
                    sink.emit(
                        ProductEventKind.KEEPALIVE,
                        transition_ref=f"keepalive:{keepalive_ix}",
                    )
                    continue
                if frame is None:
                    break
                yield (
                    json.dumps(
                        frame,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    + "\n"
                )
        finally:
            # This is only a cancellation signal. Existing ResearchTaskRegistry remains
            # the lifecycle authority and rejects any late Evidence commit.
            cancelled.set()

    return StreamingResponse(
        stream(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache"},
    )
