"""/sadmin/contracts — Query Contract kanıtı görüntüleme (superadmin-only).

Kaynak: Postgres `contract_log` (ADR-0010). Faz 3'te contracts.jsonl → DB'ye taşındı;
admin plane AYRI servis olduğundan replay/denetim kanıtı ancak DB'den görülebilir. Her
başarılı raporun soru + CubeQuery + SQL + sonuç-hash + şema-sürümü mührü."""

from __future__ import annotations

import json
import uuid as _uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, col, select

from control_plane.db import get_session
from control_plane.models import ContractLog, Tenant

router = APIRouter(prefix="/sadmin/contracts", tags=["sadmin-contracts"])


def _loads(v: str | None):
    if not v:
        return None
    try:
        return json.loads(v)
    except (ValueError, TypeError):
        return None


@router.get("")
def list_contracts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session_id: str | None = None,
    tenant: str | None = None,       # tenant_id (tam eşleşme)
    q: str | None = None,            # soru metni (ILIKE)
    session: Session = Depends(get_session),
) -> dict:
    """Filtrelenmiş + sayfalanmış rapor sözleşmeleri + toplam + facet'ler (SQL-backed)."""
    conds = []
    if session_id:
        conds.append(ContractLog.session_id == session_id)
    if tenant:
        conds.append(ContractLog.tenant_id == tenant)
    if q:
        conds.append(col(ContractLog.question).ilike(f"%{q}%"))

    count_stmt = select(func.count()).select_from(ContractLog)
    page_stmt = select(ContractLog).order_by(col(ContractLog.ts).desc())
    for c in conds:
        count_stmt = count_stmt.where(c)
        page_stmt = page_stmt.where(c)
    total = session.exec(count_stmt).one()
    rows = session.exec(page_stmt.offset(offset).limit(limit)).all()

    # tenant_id (str(uuid)) → slug; facet için tüm distinct tenant'lar.
    facet_tids = [t for t in session.exec(select(ContractLog.tenant_id).distinct()).all() if t]
    slug: dict[str, str] = {}
    for tid in set(facet_tids) | {r.tenant_id for r in rows if r.tenant_id}:
        try:
            t = session.get(Tenant, _uuid.UUID(tid))
            if t:
                slug[tid] = t.slug
        except (ValueError, TypeError):
            pass

    return {
        "total": total, "offset": offset, "limit": limit,
        "facets": {
            "tenants": [{"id": t, "slug": slug.get(t, t)} for t in sorted(facet_tids)],
        },
        "items": [{
            "id": r.id,
            "ts": r.ts.isoformat(timespec="seconds"),
            "session_id": r.session_id,
            "tenant_id": r.tenant_id,
            "tenant": slug.get(r.tenant_id or "", r.tenant_id),
            "question": r.question,
            "source": r.source,
            "row_count": r.row_count,
            "schema_version": r.schema_version,
            "result_hash": r.result_hash,
            "sql": r.sql,
            "cube_query": _loads(r.cube_query_json),
        } for r in rows],
    }
