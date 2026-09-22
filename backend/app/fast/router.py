"""HTTP surface for the Fast Ask vertical slice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_principal
from app.fast.ask_models import FastAskRequest, FastAskResponse
from app.fast.ask_service import FastAskService
from control_plane.authorize import Principal


router = APIRouter(prefix="/fast", tags=["fast"])


def _service(request: Request) -> FastAskService:
    service = getattr(request.app.state, "fast_ask_service", None)
    if not isinstance(service, FastAskService):
        raise RuntimeError("FastAskService is not configured")
    return service


@router.get("/health")
def fast_health() -> dict[str, str]:
    return {"status": "ok", "runtime": "fast-track"}


@router.post("/ask", response_model=FastAskResponse)
def fast_ask(
    payload: FastAskRequest,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastAskResponse:
    return _service(request).ask(payload, principal=principal)
