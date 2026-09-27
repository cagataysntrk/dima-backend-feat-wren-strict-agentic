"""Authoritative feature-flagged Dima V2 product front door."""

from __future__ import annotations

import json
import queue
import threading

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_principal, require, require_company
from app.config import get_settings
from app.v2.persistence import DurableCheckpointStore
from app.v2.pilot import evaluate_pilot
from app.v2.product_control import ProductControlError, ProductRunControlRegistry
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_events import ProductEventSink
from app.v2.product_models import (
    ProductAskRequest,
    ProductControlAction,
    ProductControlReceipt,
    ProductControlRequest,
    ProductEventKind,
    ProductResponse,
    mint_product_turn_ref,
)
from app.v2.report_continuation import StaleReportContinuationError
from app.v2.runtime_boundary import request_ref
from control_plane.authorize import Principal


router = APIRouter(tags=["ask-v2"])
_settings = get_settings()
_coordinator = ProductCoordinator(
    checkpoint_store=DurableCheckpointStore(
        _settings.ask_v2_checkpoint_dir
    )
)
_controls = ProductRunControlRegistry()


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
    if not evaluate_pilot(get_settings(), principal).enabled:
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
    if not evaluate_pilot(get_settings(), principal).enabled:
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
    req_ref = request_ref(body)
    turn_ref = mint_product_turn_ref()
    principal_subject = str(principal.user_id)
    principal_tenant = (
        f"id:{principal.tenant_id}"
        if principal.tenant_id is not None
        else f"slug:{principal.tenant_slug or ''}"
    )
    try:
        control = _controls.register(
            principal_subject=principal_subject,
            tenant_binding=principal_tenant,
        )
    except ProductControlError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "product_control_unavailable",
                "message": str(exc),
            },
        ) from exc

    frames.put(
        {
            "type": "control",
            "control_ref": control.control_ref,
        }
    )

    def on_event(event) -> None:
        frames.put(
            {
                "type": "event",
                "event": event.model_dump(mode="json"),
            }
        )

    sink = ProductEventSink(
        request_ref=req_ref,
        turn_ref=turn_ref,
        on_event=on_event,
    )

    def run_product() -> None:
        try:
            response = _coordinator.handle(
                request=request,
                body=body,
                principal=principal,
                event_sink=sink,
                turn_ref=turn_ref,
                cancel_check=control.cancelled,
                answer_now_check=control.answer_now_requested,
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

    worker = threading.Thread(target=run_product, daemon=True)
    worker.start()

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
            # Transport disconnect signals the same live cancel control. Existing
            # ResearchTaskRegistry remains lifecycle authority and rejects late commits.
            if worker.is_alive():
                control.signal(ProductControlAction.CANCEL)
            _controls.release(control.control_ref)

    return StreamingResponse(
        stream(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache"},
    )


@router.post(
    "/ask-v2/runs/{control_ref}/control",
    response_model=ProductControlReceipt,
    dependencies=[Depends(require("query:run")), Depends(require_company)],
)
def ask_v2_control(
    control_ref: str,
    body: ProductControlRequest,
    principal: Principal = Depends(get_current_principal),
) -> ProductControlReceipt:
    """Signal a currently attached live Product stream; this does not mutate run truth."""

    # Rollback blocks NEW Ask-V2 work at /ask-v2 and /stream. Existing attached
    # runs remain controllable so operators/users can cancel or answer-now safely.
    # ProductRunControlRegistry still enforces exact principal + tenant ownership.
    principal_subject = str(principal.user_id)
    principal_tenant = (
        f"id:{principal.tenant_id}"
        if principal.tenant_id is not None
        else f"slug:{principal.tenant_slug or ''}"
    )
    try:
        _controls.signal(
            control_ref,
            principal_subject=principal_subject,
            tenant_binding=principal_tenant,
            action=body.action,
        )
    except ProductControlError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "product_control_not_found",
                "message": str(exc),
            },
        ) from exc

    return ProductControlReceipt(
        control_ref=control_ref,
        action=body.action,
    )
