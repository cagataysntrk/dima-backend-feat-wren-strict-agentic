"""Feature-flagged HTTP entrypoint for the greenfield Dima V2 island."""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_principal, require, require_company
from app.config import get_settings
from app.v2.finalizer import ConversationFinalizerV0
from app.v2.interpreter import TurnInterpreterError
from app.v2.models import AskV2CoreResponse, AskV2Request, ResearchBriefStatus
from app.v2.orchestrator import V2Orchestrator
from app.v2.resolver import ClarificationTokenError
from app.v2.runtime_boundary import request_ref as v2_request_ref
from app.v3.research import ResearchStateError
from app.v3.research_product import (
    ResearchAskResponse,
    ResearchProductError,
    ResearchProductRuntimeUnavailable,
)
from app.v3.research_store import ResearchPersistenceError
from control_plane.authorize import Principal


router = APIRouter(tags=["ask-v2"])
_orchestrator = V2Orchestrator()
_finalizer = ConversationFinalizerV0()


def _research_product(request: Request):
    product = getattr(request.app.state, "research_product", None)
    if product is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "P14_RESEARCH_PRODUCT_NOT_CONFIGURED",
                "message": "durable Research product boundary is not configured",
            },
        )
    return product


def _raise_research_http(exc: Exception) -> None:
    code = getattr(exc, "code", type(exc).__name__)
    detail = getattr(exc, "detail", str(exc))
    if isinstance(exc, ResearchProductRuntimeUnavailable):
        status = 503
    elif (
        isinstance(exc, ResearchPersistenceError)
        and code == "P14_RESEARCH_SESSION_NOT_FOUND"
    ):
        status = 404
    else:
        status = 409
    raise HTTPException(
        status_code=status,
        detail={"code": code, "message": detail},
    ) from exc


@router.post(
    "/ask-v2",
    response_model=AskV2CoreResponse | ResearchAskResponse,
    dependencies=[Depends(require("query:run")), Depends(require_company)],
)
def ask_v2(
    request: Request,
    body: AskV2Request,
    principal: Principal = Depends(get_current_principal),
) -> AskV2CoreResponse | ResearchAskResponse:
    if not get_settings().ask_v2_enabled:
        raise HTTPException(status_code=404, detail="ask-v2 kapalı")

    if body.research_session_id is not None:
        # Durable resume precedes language interpretation. The old prompt is not
        # reparsed into a new semantic authority.
        try:
            return _research_product(request).run_next(
                session_id=body.research_session_id,
                principal=principal,
                obligation_id=body.research_obligation_id,
                native_session_token=request.headers.get("x-metabase-session"),
            )
        except (
            ResearchPersistenceError,
            ResearchProductError,
            ResearchStateError,
        ) as exc:
            _raise_research_http(exc)

    try:
        core = _orchestrator.handle(request, body, principal)
        finalized = _finalizer.finalize(core)
        brief = core.research_brief
        if (
            brief is not None
            and brief.status == ResearchBriefStatus.READY_FOR_RESEARCH
        ):
            try:
                session = _research_product(request).start_from_brief(
                    brief=brief,
                    request_ref=v2_request_ref(body),
                    source_message_hash=hashlib.sha256(
                        body.question.encode("utf-8")
                    ).hexdigest(),
                    principal=principal,
                )
            except (
                ResearchPersistenceError,
                ResearchProductError,
                ResearchStateError,
            ) as exc:
                _raise_research_http(exc)
            finalized = finalized.model_copy(
                update={
                    "research_session_id": session.session_id,
                    "research_session_revision": session.revision,
                    "research_stopping_status": session.stopping.status.value,
                }
            )
        return finalized
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
