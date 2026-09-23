"""Authoritative feature-flagged Dima V2 product front door."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_principal, require, require_company
from app.config import get_settings
from app.v2.models import AskV2Request
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_models import ProductResponse
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
    body: AskV2Request,
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
