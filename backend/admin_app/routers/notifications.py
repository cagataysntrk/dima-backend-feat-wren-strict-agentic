"""/sadmin/notifications — bildirim/e-posta teslim logu görüntüleme (ADR-0011/0020,
superadmin-only). Kaynak: Postgres `notification_log`. NEDEN DB (jsonl değil): admin API
AYRI servis (ADR-0015) → public app'in volume'undaki notifications.jsonl çapraz-servis
okunmaz; ortak store Postgres. Filtre+pagination = SQL. delivery = kanal başına teslim
sonucu (email ok/atlandı/başarısız + alıcı + Resend id)."""

from __future__ import annotations

import json
import uuid as _uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, col, select

from control_plane.db import get_session
from control_plane.models import NotificationLog, Tenant

router = APIRouter(prefix="/sadmin/notifications", tags=["sadmin-notifications"])


def _loads(v: str | None):
    if not v:
        return None
    try:
        return json.loads(v)
    except (ValueError, TypeError):
        return None


@router.get("")
def list_notifications(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    kind: str | None = None,          # report | alert | anomaly
    tenant: str | None = None,        # tenant_id (tam eşleşme)
    company: str | None = None,
    delivery: str | None = None,      # "email" (dış kanal) | "inapp" (yalnız in-app) | None (hepsi)
    q: str | None = None,             # mesaj metni (ILIKE)
    session: Session = Depends(get_session),
) -> dict:
    """Filtrelenmiş + sayfalanmış bildirim/teslim logu + toplam + facet'ler (SQL-backed)."""
    conds = []
    if kind:
        conds.append(NotificationLog.kind == kind)
    if tenant:
        conds.append(NotificationLog.tenant_id == tenant)
    if company:
        conds.append(NotificationLog.company == company)
    if delivery == "email":       # dış kanal teslimi kaydı olanlar
        conds.append(col(NotificationLog.delivery_json).is_not(None))
    elif delivery == "inapp":     # yalnız in-app (dış kanal yok)
        conds.append(col(NotificationLog.delivery_json).is_(None))
    if q:
        conds.append(col(NotificationLog.message).ilike(f"%{q}%"))

    count_stmt = select(func.count()).select_from(NotificationLog)
    page_stmt = select(NotificationLog).order_by(col(NotificationLog.ts).desc())
    for c in conds:
        count_stmt = count_stmt.where(c)
        page_stmt = page_stmt.where(c)
    total = session.exec(count_stmt).one()
    rows = session.exec(page_stmt.offset(offset).limit(limit)).all()

    tids = {r.tenant_id for r in rows if r.tenant_id}
    slug: dict[str, str] = {}
    for tid in tids:
        try:
            t = session.get(Tenant, _uuid.UUID(tid))
            if t:
                slug[tid] = t.slug
        except (ValueError, TypeError):
            pass

    kinds = sorted({k for k in session.exec(select(NotificationLog.kind).distinct()).all() if k})
    companies = sorted({c for c in session.exec(
        select(NotificationLog.company).distinct()).all() if c})

    return {
        "total": total, "offset": offset, "limit": limit,
        "items": [{
            "ts": r.ts.isoformat(timespec="seconds"),
            "company": r.company,
            "tenant_id": r.tenant_id,
            "tenant": slug.get(r.tenant_id or "", r.tenant_id),
            "schedule_id": r.schedule_id,
            "kind": r.kind,
            "message": r.message,
            "row_count": r.row_count,
            "contract_id": r.contract_id,
            "delivery": _loads(r.delivery_json),
        } for r in rows],
        "facets": {"kinds": kinds, "companies": companies},
    }
