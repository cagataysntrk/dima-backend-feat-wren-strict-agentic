"""/sadmin/interactions — sorgu telemetrisi görüntüleme (ADR-0020 interaction yüzeyi, superadmin-only).

Kaynak: Postgres `interaction_log` tablosu. NEDEN DB (dosya değil): admin API AYRI servis
(ADR-0015) → Railway volume çapraz-servis okunmaz; iki servisin ortak store'u Postgres. Ayrıca
filtre+pagination+total = SQL'in işi (index + LIMIT/OFFSET + COUNT). Audit'ten AYRI yüzey
(compliance değil; kalite izleme + log madenciliği). Ham sonuç satırı tutulmaz (KVKK)."""

from __future__ import annotations

import json
import uuid as _uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, col, select

from control_plane.db import get_session
from control_plane.models import InteractionLog, Tenant

router = APIRouter(prefix="/sadmin/interactions", tags=["sadmin-interactions"])


def _loads(v: str | None):
    if not v:
        return None
    try:
        return json.loads(v)
    except (ValueError, TypeError):
        return None


@router.get("")
def list_interactions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    source: str | None = None,       # kind: cube | llm | rule | none | other
    tenant: str | None = None,       # tenant_id (tam eşleşme)
    user: str | None = None,         # user_id
    session_id: str | None = None,
    q: str | None = None,            # soru metni (ILIKE)
    has_note: bool | None = None,    # yalnız not taşıyanlar (route-yok/clarify)
    session: Session = Depends(get_session),
) -> dict:
    """Filtrelenmiş + sayfalanmış etkileşim + toplam + filtre facet'leri (SQL-backed)."""
    def _uuid_or_none(v):
        try:
            return _uuid.UUID(v) if v else None
        except (ValueError, TypeError):
            return None

    conds = []
    if source:
        conds.append(InteractionLog.kind == source)
    if tenant and (_t := _uuid_or_none(tenant)) is not None:  # aktör kolonları UUID
        conds.append(InteractionLog.tenant_id == _t)
    if user and (_u := _uuid_or_none(user)) is not None:
        conds.append(InteractionLog.user_id == _u)
    if session_id:
        conds.append(InteractionLog.session_id == session_id)
    if has_note is not None:
        conds.append(col(InteractionLog.note).is_not(None) if has_note
                     else col(InteractionLog.note).is_(None))
    if q:
        conds.append(col(InteractionLog.question).ilike(f"%{q}%"))

    count_stmt = select(func.count()).select_from(InteractionLog)
    page_stmt = select(InteractionLog).order_by(col(InteractionLog.ts).desc())
    for c in conds:
        count_stmt = count_stmt.where(c)
        page_stmt = page_stmt.where(c)
    total = session.exec(count_stmt).one()
    rows = session.exec(page_stmt.offset(offset).limit(limit)).all()

    # tenant_id (UUID) → slug (okunabilirlik). Anahtarlar str(uuid) — JSON'da tutarlı str.
    tids = {r.tenant_id for r in rows if r.tenant_id}
    facet_tids = [t for t in session.exec(
        select(InteractionLog.tenant_id).distinct()).all() if t]
    slug: dict[str, str] = {}
    for tid in set(tids) | set(facet_tids):  # tid: UUID
        t = session.get(Tenant, tid)  # Tenant PK zaten UUID
        if t:
            slug[str(tid)] = t.slug

    kinds = sorted({k for k in session.exec(
        select(InteractionLog.kind).distinct()).all() if k})

    def _sid(u):  # UUID | None → str | None
        return str(u) if u else None

    return {
        "total": total, "offset": offset, "limit": limit,
        "items": [{
            "ts": r.ts.isoformat(timespec="seconds"),
            "session_id": r.session_id,
            "user_id": _sid(r.user_id),
            "tenant_id": _sid(r.tenant_id),
            "tenant": slug.get(_sid(r.tenant_id) or "", _sid(r.tenant_id)),
            "question": r.question,
            "source": r.source,
            "kind": r.kind,
            "rows": r.rows,
            "note": r.note,
            "follow_up": r.follow_up,
            "duration_ms": r.duration_ms,
            # Faz 2b LLM telemetrisi (yalnız LLM yoluna düşen istekte dolu; maliyet görünürlüğü)
            "llm_model": r.llm_model,
            "llm_input_tokens": r.llm_input_tokens,
            "llm_output_tokens": r.llm_output_tokens,
            "llm_latency_ms": r.llm_latency_ms,
            "has_interpretation": bool(r.interpretation_json),
            "cube_query": _loads(r.cube_query_json),
            "trace": _loads(r.trace_json),
            "interpretation": _loads(r.interpretation_json),
        } for r in rows],
        "facets": {
            "sources": kinds,
            "tenants": [{"id": str(t), "slug": slug.get(str(t), str(t))}
                        for t in sorted(facet_tids, key=str)],
        },
    }
