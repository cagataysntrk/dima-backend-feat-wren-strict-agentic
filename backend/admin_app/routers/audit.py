"""/sadmin/audit — erişim kanıtı görüntüleme (ADR-0014 Karar 6, superadmin-only).

Audit'i yazmak yetmez; superadmin okuyabilmeli (KVKK erişim-izi raporu + operasyon).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlmodel import Session, col, select

from control_plane.db import get_session
from control_plane.models import AuditLog, Tenant, User

router = APIRouter(prefix="/sadmin/audit", tags=["sadmin-audit"])


@router.get("")
def list_audit(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    action: str | None = None,
    tenant: str | None = None,        # tenant_id (tam eşleşme)
    q: str | None = None,             # soru/SQL metni (ILIKE)
    session: Session = Depends(get_session),
) -> dict:
    """Filtrelenmiş + sayfalanmış erişim kanıtı + toplam + facet'ler (diğer log yüzeyleriyle
    tutarlı: interactions/notifications/contracts gibi offset/total/firma/arama)."""
    conds = []
    if action:
        conds.append(AuditLog.action == action)
    if tenant:
        try:
            conds.append(AuditLog.tenant_id == uuid.UUID(tenant))
        except (ValueError, TypeError):
            pass
    if q:
        conds.append(or_(col(AuditLog.nl_question).ilike(f"%{q}%"),
                         col(AuditLog.generated_sql).ilike(f"%{q}%")))

    count_stmt = select(func.count()).select_from(AuditLog)
    page_stmt = select(AuditLog).order_by(col(AuditLog.ts).desc())
    for c in conds:
        count_stmt = count_stmt.where(c)
        page_stmt = page_stmt.where(c)
    total = session.exec(count_stmt).one()
    rows = session.exec(page_stmt.offset(offset).limit(limit)).all()

    # İnsanca etiketler: aktör e-postası + tenant slug'ı (id yerine).
    user_ids = {r.actor_user_id for r in rows if r.actor_user_id}
    emails = {
        u.id: u.email
        for u in session.exec(select(User).where(col(User.id).in_(user_ids))).all()
    } if user_ids else {}

    # tenant_id (UUID) → slug; facet için tüm distinct tenant'lar.
    facet_tids = [t for t in session.exec(select(AuditLog.tenant_id).distinct()).all() if t]
    slugs: dict = {}
    for tid in set(facet_tids) | {r.tenant_id for r in rows if r.tenant_id}:
        t = session.get(Tenant, tid)  # AuditLog.tenant_id zaten UUID
        if t:
            slugs[tid] = t.slug

    actions = sorted({a for a in session.exec(
        select(AuditLog.action).distinct()).all() if a})

    return {
        "total": total, "offset": offset, "limit": limit,
        "actions": actions,  # geriye dönük uyum
        "facets": {
            "actions": actions,
            "tenants": [{"id": str(t), "slug": slugs.get(t, str(t))}
                        for t in sorted(facet_tids, key=str)],
        },
        "entries": [
            {
                "ts": r.ts.isoformat(timespec="seconds"),
                "actor": emails.get(r.actor_user_id) or (
                    str(r.actor_user_id)[:8] if r.actor_user_id else None),
                "actor_kind": r.actor_kind,
                "tenant_id": str(r.tenant_id) if r.tenant_id else None,
                "tenant": slugs.get(r.tenant_id),
                "action": r.action,
                "role_key": r.role_key,
                "question": r.nl_question,
                "sql": r.generated_sql,
                "rows": r.rows_returned,
                "contract_id": r.contract_id,
                "ip": r.ip,
            }
            for r in rows
        ],
    }
