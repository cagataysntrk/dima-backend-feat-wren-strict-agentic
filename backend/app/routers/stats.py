"""Faz 4.13c (1 Ağustos 2026) — dış yol haritası 2.18 "meta-güven şeridi": son-kullanıcıya
"bugün soruların %X'i yapay zekaya hiç gitmeden cevaplandı" özeti.

`admin_app/routers/interactions.py::route_distribution`'ın (superadmin, TÜM tenant'lar,
7-90 gün) KÜÇÜK, KULLANICI-görünür karşılığı: yalnız KENDİ tenant'ı, yalnız BUGÜN
(varsayılan) — aynı `interaction_log` kaynağından, aynı sınıflandırma ilkesiyle."""

from __future__ import annotations

from datetime import datetime, timedelta

import uuid as _uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session, func, select

from app.auth.dependencies import require, require_company


def _uuid_or_none(val):
    """str(uuid) → UUID (InteractionLog.tenant_id UUID kolonu — ham principal.tenant_id
    string'i doğrudan bind edilirse SQLAlchemy UUID adaptörü patlıyordu). Geçersiz/boş →
    None (aynı desen: app/routers/ask.py::_uuid_or_none)."""
    try:
        return _uuid.UUID(val) if val else None
    except (ValueError, TypeError):
        return None

router = APIRouter(prefix="/stats", tags=["stats"])


def _llm_free(kind: str | None) -> bool:
    """`_source_kind()`'ın (app/routers/ask.py) ürettiği normalize kind — LLM'e HİÇ
    düşmeyen yollar: cube/vqr/rule/meta/catalog/statement/upload. Yalnız 'llm' gerçek
    bir LLM çağrısı anlamına gelir."""
    return kind is not None and kind != "llm"


@router.get("/today", dependencies=[Depends(require("query:run")), Depends(require_company)])
def stats_today(request: Request, days: int = Query(1, ge=1, le=30)) -> dict:
    """Bugünkü (ya da son `days` gündeki) /ask cevaplarının kaçının LLM'e hiç gitmeden
    (deterministik cube/VQR/kural/meta/katalog) yanıtlandığı — KENDİ tenant'ına özel."""
    from control_plane.db import engine
    from control_plane.models import InteractionLog

    principal = getattr(request.state, "principal", None)
    tenant_id = _uuid_or_none(getattr(principal, "tenant_id", None))
    since = datetime.utcnow() - timedelta(days=days)

    with Session(engine) as s:
        stmt = select(InteractionLog.kind, func.count()).where(InteractionLog.ts >= since)
        if tenant_id:
            stmt = stmt.where(InteractionLog.tenant_id == tenant_id)
        stmt = stmt.group_by(InteractionLog.kind)
        rows = s.exec(stmt).all()

    total = sum(c for _, c in rows)
    llm_free = sum(c for k, c in rows if _llm_free(k))
    pct = round(llm_free / total * 100) if total else None
    message = (
        f"Bugün {pct}% soru yapay zekaya hiç gitmeden cevaplandı." if pct is not None
        else "Henüz bugüne ait bir soru yok."
    )
    return {"total": total, "llm_free": llm_free, "llm_free_pct": pct, "message": message}
