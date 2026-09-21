"""Feature-flagged HTTP entrypoint for the greenfield Dima V2 island."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_principal, require, require_company
from app.config import get_settings
from app.v2.interpreter import TurnInterpreterError
from app.v2.models import AskV2Day4Response, AskV2Request
from app.v2.orchestrator import V2Orchestrator
from app.v2.resolver import ClarificationTokenError
from control_plane.authorize import Principal

router = APIRouter(tags=["ask-v2"])
_orchestrator = V2Orchestrator()


@router.post(
    "/ask-v2",
    response_model=AskV2Day4Response,
    dependencies=[Depends(require("query:run")), Depends(require_company)],
)
def ask_v2(
    request: Request,
    body: AskV2Request,
    principal: Principal = Depends(get_current_principal),
) -> AskV2Day4Response:
    if not get_settings().ask_v2_enabled:
        raise HTTPException(status_code=404, detail="ask-v2 kapalı")

    try:
        return _orchestrator.handle(request, body, principal)
    except TurnInterpreterError as exc:
        status = 503 if exc.failure.code == "llm_unavailable" else 502
        raise HTTPException(
            status_code=status,
            detail=exc.failure.model_dump(mode="json"),
        ) from exc
    except ClarificationTokenError as exc:
        # Stale/tampered continuation state never falls back to a different meaning.
        raise HTTPException(
            status_code=409,
            detail={
                "code": "clarification_token_invalid",
                "message": str(exc),
            },
        ) from exc
