"""Feature-flagged HTTP entrypoint for the greenfield Dima V2 island."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_principal, require, require_company
from app.config import get_settings
from app.v2.models import AskV2BootstrapRequest, AskV2BootstrapResponse
from app.v2.orchestrator import V2BootstrapOrchestrator
from control_plane.authorize import Principal

router = APIRouter(tags=["ask-v2"])
_bootstrap = V2BootstrapOrchestrator()


@router.post(
    "/ask-v2",
    response_model=AskV2BootstrapResponse,
    dependencies=[Depends(require("query:run")), Depends(require_company)],
)
def ask_v2(
    request: Request,
    body: AskV2BootstrapRequest,
    principal: Principal = Depends(get_current_principal),
) -> AskV2BootstrapResponse:
    if not get_settings().ask_v2_enabled:
        # Rollback is route-level and explicit. There is intentionally no request-level
        # fallback to legacy /ask: a V2 failure must remain visible.
        raise HTTPException(status_code=404, detail="ask-v2 kapalı")

    return _bootstrap.bootstrap(request, body, principal)
