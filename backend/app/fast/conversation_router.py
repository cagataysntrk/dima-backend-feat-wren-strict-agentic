"""HTTP surface for FT-005 Fast conversation/turn lineage."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_principal
from app.fast.conversation_models import (
    FastConversationCreateRequest,
    FastConversationDetail,
    FastConversationSnapshot,
    FastTurnCreateRequest,
    FastTurnSnapshot,
)
from app.fast.conversation_service import (
    FastConversationConflict,
    FastConversationService,
)
from app.fast.conversation_store import FastConversationNotFound
from control_plane.authorize import Principal


router = APIRouter(prefix="/fast/conversations", tags=["fast-conversations"])


def _service(request: Request) -> FastConversationService:
    service = getattr(request.app.state, "fast_conversation_service", None)
    if not isinstance(service, FastConversationService):
        raise RuntimeError("FastConversationService is not configured")
    return service


def _not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Conversation bulunamadı")


@router.post("", response_model=FastConversationSnapshot, status_code=201)
def create_conversation(
    payload: FastConversationCreateRequest,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastConversationSnapshot:
    return _service(request).create_conversation(
        principal=principal,
        title=payload.title,
    )


@router.get("/{conversation_id}", response_model=FastConversationDetail)
def get_conversation(
    conversation_id: str,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastConversationDetail:
    try:
        return _service(request).conversation(
            conversation_id,
            principal=principal,
        )
    except FastConversationNotFound:
        raise _not_found()


@router.post(
    "/{conversation_id}/turns",
    response_model=FastTurnSnapshot,
    status_code=202,
)
def create_turn(
    conversation_id: str,
    payload: FastTurnCreateRequest,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastTurnSnapshot:
    try:
        return _service(request).submit_turn(
            conversation_id,
            payload,
            principal=principal,
        )
    except FastConversationNotFound:
        raise _not_found()
    except FastConversationConflict as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": exc.code, "message": exc.message},
        ) from exc


@router.get(
    "/{conversation_id}/turns/{turn_id}",
    response_model=FastTurnSnapshot,
)
def get_turn(
    conversation_id: str,
    turn_id: str,
    request: Request,
    principal: Principal = Depends(get_current_principal),
) -> FastTurnSnapshot:
    try:
        turn = _service(request).turn(turn_id, principal=principal)
        if turn.conversation_id != conversation_id:
            raise FastConversationNotFound("turn not found")
        return turn
    except FastConversationNotFound:
        raise _not_found()
