"""Manual-only Day 6.5 Manager validation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_principal, require, require_company
from app.config import get_settings
from app.v2.manager_lab import ManagerLabHarness, ManagerLabResponse
from app.v2.models import AskV2Request
from control_plane.authorize import Principal

router = APIRouter(tags=["v2-manager-lab"])
_harness = ManagerLabHarness()


@router.post(
    "/ask-v2-manager-lab",
    response_model=ManagerLabResponse,
    dependencies=[Depends(require("query:run")), Depends(require_company)],
)
def ask_v2_manager_lab(
    request: Request,
    body: AskV2Request,
    principal: Principal = Depends(get_current_principal),
) -> ManagerLabResponse:
    if not get_settings().v2_manager_lab_enabled:
        raise HTTPException(status_code=404, detail="v2 manager lab kapalı")
    return _harness.run(request=request, body=body, principal=principal)
