"""/conversations — kullanıcı sohbet geçmişi (per-user, tenant-izole).

Sohbetler /ask + /cube sırasında OTOMATİK kaydedilir (ask._persist_message); bu router
yalnız OKUMA + silme sağlar: liste (kenar çubuğu), getir (resume), sil. İzolasyon: yalnız
Principal.user_id'e ait sohbetler görünür/silinir (sahiplik kontrolü her uçta)."""

from __future__ import annotations

import json
import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from sqlmodel import Session, select

from app.schemas import ConversationDetail, ConversationOut
from control_plane.db import engine
from control_plane.models import Conversation, ConversationMessage

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _uid(request: Request) -> str | None:
    p = getattr(request.state, "principal", None)
    return getattr(p, "user_id", None) if p else None


@router.get("", response_model=list[ConversationOut])
def list_conversations(request: Request) -> list[ConversationOut]:
    """Kullanıcının sohbetleri, en son güncellenene göre (geçmiş kenar çubuğu)."""
    uid = _uid(request)
    if not uid:
        return []
    with Session(engine) as s:
        rows = s.exec(select(Conversation).where(
            Conversation.user_id == uid,
            Conversation.deleted_at.is_(None))  # soft-delete: silinmiş sohbetler gizli
            .order_by(Conversation.updated_at.desc())).all()
    return [ConversationOut(
        id=str(c.id), title=c.title or "(başlıksız)", session_id=c.session_id,
        message_count=c.message_count, updated_at=c.updated_at.isoformat()) for c in rows]


def _owned(request: Request, cid: str) -> Conversation:
    uid = _uid(request)
    try:
        conv = None
        with Session(engine) as s:
            conv = s.get(Conversation, _uuid.UUID(cid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz sohbet id")
    # sahiplik + soft-delete: başkasının ya da silinmiş sohbet 404 (varlık sızdırma yok)
    if conv is None or conv.user_id != uid or conv.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Sohbet bulunamadı")
    return conv


@router.get("/{cid}", response_model=ConversationDetail)
def get_conversation(cid: str, request: Request) -> ConversationDetail:
    """Bir sohbet + tüm mesajları (resume): kayıtlı AskResponse payload'ları sırayla."""
    conv = _owned(request, cid)
    with Session(engine) as s:
        msgs = s.exec(select(ConversationMessage)
                      .where(ConversationMessage.conversation_id == conv.id)
                      .order_by(ConversationMessage.seq)).all()
    payloads = []
    for m in msgs:
        try:
            payloads.append(json.loads(m.payload_json))
        except (ValueError, TypeError):
            continue
    return ConversationDetail(id=str(conv.id), title=conv.title, session_id=conv.session_id,
                              messages=payloads)


@router.delete("/{cid}", status_code=204)
def delete_conversation(cid: str, request: Request) -> None:
    """SOFT DELETE (proje kuralı: hard-delete YOK): deleted_at damgası. Kayıt+mesajlar kalır
    (audit/kurtarma); liste/getir onları süzer."""
    conv = _owned(request, cid)
    with Session(engine) as s:
        c = s.get(Conversation, conv.id)
        if c is not None and c.deleted_at is None:
            c.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
            s.add(c); s.commit()
