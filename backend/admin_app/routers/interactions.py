"""/sadmin/interactions — sorgu telemetrisi görüntüleme (ADR-0020 interaction yüzeyi, superadmin-only).

Kaynak: Postgres `interaction_log` tablosu. NEDEN DB (dosya değil): admin API AYRI servis
(ADR-0015) → Railway volume çapraz-servis okunmaz; iki servisin ortak store'u Postgres. Ayrıca
filtre+pagination+total = SQL'in işi (index + LIMIT/OFFSET + COUNT). Audit'ten AYRI yüzey
(compliance değil; kalite izleme + log madenciliği). Ham sonuç satırı tutulmaz (KVKK)."""

from __future__ import annotations

import json
import uuid as _uuid
from datetime import datetime, timedelta

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


def _uuid_or_none(v):
    try:
        return _uuid.UUID(v) if v else None
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


# path kategorisi → hangi ham `source` değerleri kapsar. Faz 1 KPI'sı: "Intent-payı" —
# route()/LLM-Intent-JSON'ın (SQL yazmadan) ham-SQL Discovery'ye göre payı gerçekten arttı mı?
def _route_path(source: str | None) -> str:
    s = (source or "").lower()
    if s.startswith("cube"):
        return "intent"       # cube (route(), sıfır-LLM) + cube+llm (LLM Intent-JSON seçimi)
    if s == "vqr":
        return "cache"        # önceden doğrulanmış SQL tekrar oynatıldı
    if s.startswith("llm:"):
        return "discovery"    # ham-SQL üretimi (Intent kapsamadı / takip mesajı)
    if s == "rule":
        return "rule"         # LLM'siz kural-tabanlı yedek
    if s in ("meta", "catalog"):
        return "meta_katalog"
    if s == "statement":
        return "intent"        # GL yapısal rapor — deterministik, sıfır-LLM (Faz 2a)
    # SORU-DIŞI aksiyonlar (2 Ağustos 2026): bunlar bir NL sorusunun yönlendirilmesi DEĞİL,
    # zaten verilmiş bir cevabın üstüne yapılan kullanıcı aksiyonlarıdır. Önceden "other"a
    # düşüyorlardı ve KPI paydasını sessizce şişiriyorlardı (Intent-payı olduğundan düşük
    # görünür). `_KPI_PATHS` bunları paydadan dışlar; `by_path` yine de göstersin ki
    # aksiyon hacmi görünür kalsın.
    if s == "drill":
        return "drill"         # /ask/drill — deterministik dallanma, cube_query ZORUNLU
    if s == "upload":
        return "upload"        # /ask/upload — Excel/CSV oto-cube (ADR-0021)
    if s == "verify":
        return "verify"        # /verify + /ask/verify — kullanıcı doğrulama aksiyonu
    return "other"


# KPI paydası: bir VERİ cevabı beklenen sorular. meta/katalog (selamlama, "neler
# sorabilirim") ve soru-dışı aksiyonlar (drill/upload/verify) HARİÇ — aksi halde
# "Intent ≥%70 / Discovery <%30" hedefi ölçülen şeyden farklı bir şeyi ölçer.
_KPI_PATHS = ("intent", "cache", "discovery", "rule")


@router.get("/route-distribution")
def route_distribution(
    days: int = Query(7, ge=1, le=90),
    tenant: str | None = None,
    session: Session = Depends(get_session),
) -> dict:
    """Faz 1 KPI: son N gündeki /ask cevaplarının yolu — intent (route()+LLM-Intent-JSON,
    SQL yazmadan) / cache (VQR) / discovery (ham-SQL) / diğer. "Intent-first flip trafiği
    gerçekten kaydırdı mı" sorusunun ölçülebilir cevabı (bkz. Faz 1 yol haritası — rota-
    dağılımı telemetrisi flip'ten ÖNCE/yanında kurulmalı gereksinimi). Ham `source` kırılımı
    da döner (cube vs cube+llm ayrımı — route()'un tek başına ne kadarını kapsadığı görünür
    olsun, LLM-Intent-JSON adımının canary'de ne kadar tetiklendiği de)."""
    since = datetime.utcnow() - timedelta(days=days)
    conds = [InteractionLog.ts >= since]
    if tenant and (_t := _uuid_or_none(tenant)) is not None:
        conds.append(InteractionLog.tenant_id == _t)

    stmt = select(InteractionLog.source, func.count()).group_by(InteractionLog.source)
    for c in conds:
        stmt = stmt.where(c)
    rows = session.exec(stmt).all()
    total = sum(c for _, c in rows)

    def _pct(c: int) -> float:
        return round(c / total * 100, 1) if total else 0.0

    by_source = sorted(
        [{"source": s or "(yok)", "count": c, "pct": _pct(c)} for s, c in rows],
        key=lambda r: -r["count"],
    )
    path_counts: dict[str, int] = {}
    for s, c in rows:
        p = _route_path(s)
        path_counts[p] = path_counts.get(p, 0) + c
    by_path = sorted(
        [{"path": p, "count": c, "pct": _pct(c)} for p, c in path_counts.items()],
        key=lambda r: -r["count"],
    )

    # KPI'yı BURADA hesapla — çağıranın aritmetik yapmasına bırakma. Strateji belgesinin
    # hedefi "Intent ≥%70 · Discovery <%30" ve bu, ürünün maliyet/denetlenebilirlik tezinin
    # tek sayısal ifadesi. Payda = veri cevabı beklenen sorular (`_KPI_PATHS`).
    kpi_total = sum(path_counts.get(p, 0) for p in _KPI_PATHS)

    def _kpi_pct(p: str) -> float:
        return round(path_counts.get(p, 0) / kpi_total * 100, 1) if kpi_total else 0.0

    intent_pct, discovery_pct = _kpi_pct("intent"), _kpi_pct("discovery")
    return {
        "since": since.isoformat(timespec="seconds"), "days": days, "total": total,
        "by_path": by_path,      # intent|cache|discovery|rule|meta_katalog|drill|upload|verify|other
        "by_source": by_source,  # ham source kırılımı ("cube" vs "cube+llm" ayrımı dahil)
        "kpi": {
            # Payda soru-dışı aksiyonları ve meta/katalogu DIŞLAR (bkz. _KPI_PATHS).
            "denominator": kpi_total,
            "intent_pct": intent_pct,
            "cache_pct": _kpi_pct("cache"),
            "discovery_pct": discovery_pct,
            "rule_pct": _kpi_pct("rule"),
            "intent_target": 70.0,
            "discovery_target": 30.0,
            # Yeterli örneklem yokken "hedef tutuyor" demek yanıltıcı olur (n=7 ile %100
            # Intent görmek mümkün). 30 altı örneklemde karar VERİLMEZ — dürüst None.
            "meets_target": (
                None if kpi_total < 30
                else (intent_pct >= 70.0 and discovery_pct < 30.0)
            ),
        },
    }
