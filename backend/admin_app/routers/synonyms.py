"""/sadmin/synonyms — canlı sinonim overlay yönetimi (ADR-0018 katman 3).

Overlay = pack YAML (kod) + arketip (platform) ÜSTÜNE deploy'suz binen additive
sinonim katmanı. Yalnız approved=True satırlar dima-api schema()'sında uygulanır;
onaysız aday kuyrukta bekler. Onay/silme audit'lenir. Öneri kaynağı: route-edilemeyen
soru madenciliği (mine ucu — LLM'siz iskelet; LLM önerici ikinci adımda takılır).
"""

from __future__ import annotations

import json
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel as _BaseModel
from sqlmodel import Session, select

from admin_app.schemas import SynonymCreate, SynonymOut
from control_plane import audit
from control_plane.db import get_session
from control_plane.models import SynonymOverride

router = APIRouter(prefix="/sadmin/synonyms", tags=["sadmin-synonyms"])


def _out(o: SynonymOverride) -> SynonymOut:
    try:
        syns = json.loads(o.synonyms_json)
    except ValueError:
        syns = []
    return SynonymOut(
        id=str(o.id), scope_type=o.scope_type, scope_id=o.scope_id, cube=o.cube,
        field_kind=o.field_kind, field_name=o.field_name, synonyms=syns,
        lang=o.lang, approved=o.approved, source=o.source,
    )


def _known_cubes() -> dict[str, dict]:
    """Aktif kataloğun cube→{measures,dimensions} haritası (hedef doğrulaması için)."""
    try:
        from app.config import get_settings
        from app.wren_service import WrenService

        s = get_settings()
        svc = WrenService(s.resolved_project_dir(), s.datasource, {}, company_slug=s.company)
        return {c["name"]: c for c in svc.schema().get("cubes", [])}
    except Exception:
        return {}


@router.get("", response_model=list[SynonymOut])
def list_synonyms(only_pending: bool = False,
                  session: Session = Depends(get_session)) -> list[SynonymOut]:
    q = select(SynonymOverride)
    if only_pending:
        q = q.where(SynonymOverride.approved == False)
    return [_out(o) for o in session.exec(q).all()]


@router.post("", response_model=SynonymOut, status_code=201)
def create_synonym(body: SynonymCreate, request: Request,
                   session: Session = Depends(get_session)) -> SynonymOut:
    if body.scope_type not in ("global", "tenant"):
        raise HTTPException(status_code=400, detail="scope_type: global|tenant")
    if body.scope_type == "tenant" and not body.scope_id:
        raise HTTPException(status_code=400, detail="tenant kapsamı için scope_id (slug) gerekli")
    if body.field_kind not in ("cube", "measure", "dimension"):
        raise HTTPException(status_code=400, detail="field_kind: cube|measure|dimension")
    if body.field_kind != "cube" and not body.field_name:
        raise HTTPException(status_code=400, detail="measure/dimension için field_name gerekli")
    # Hedef katalogda var mı? (bozuk overlay sessizce çürümesin)
    cubes = _known_cubes()
    meta = cubes.get(body.cube)
    if meta is None:
        raise HTTPException(status_code=400, detail=f"Bilinmeyen cube: {body.cube}")
    if body.field_kind == "measure" and body.field_name not in (meta.get("measures") or []):
        raise HTTPException(status_code=400, detail=f"'{body.field_name}' ölçüsü {body.cube}'da yok")
    if body.field_kind == "dimension" and body.field_name not in (meta.get("dimensions") or []):
        raise HTTPException(status_code=400, detail=f"'{body.field_name}' boyutu {body.cube}'da yok")
    if not body.synonyms:
        raise HTTPException(status_code=400, detail="En az bir sinonim gerekli")

    principal = getattr(request.state, "principal", None)
    o = SynonymOverride(
        scope_type=body.scope_type, scope_id=body.scope_id, cube=body.cube,
        field_kind=body.field_kind, field_name=body.field_name,
        synonyms_json=json.dumps(body.synonyms),
        lang=(body.lang or None),  # §7b: dil-etiketli overlay (tr/en/…); None = yerel/belirsiz
        approved=bool(body.approved), source=body.source or "manual",
        updated_by=_uuid.UUID(principal.user_id) if principal else None,
    )
    session.add(o)
    session.commit()
    session.refresh(o)
    audit.record(principal, "synonym_create",
                 nl_question=f"{body.cube}.{body.field_name or '*'} += {body.synonyms} "
                 f"(scope {body.scope_type}/{body.scope_id or '-'}, "
                 f"{'onaylı' if body.approved else 'aday'})",
                 ip=request.client.host if request.client else None)
    return _out(o)


@router.post("/{oid}/approve", response_model=SynonymOut)
def approve_synonym(oid: str, request: Request,
                    session: Session = Depends(get_session)) -> SynonymOut:
    try:
        o = session.get(SynonymOverride, _uuid.UUID(oid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz id")
    if o is None:
        raise HTTPException(status_code=404, detail="Overlay bulunamadı")
    o.approved = True
    session.add(o)
    session.commit()
    session.refresh(o)
    audit.record(getattr(request.state, "principal", None), "synonym_approve",
                 nl_question=f"{o.cube}.{o.field_name or '*'} onaylandı → canlıya iner (≤60sn)",
                 ip=request.client.host if request.client else None)
    return _out(o)


@router.delete("/{oid}", status_code=204)
def delete_synonym(oid: str, request: Request,
                   session: Session = Depends(get_session)) -> None:
    try:
        o = session.get(SynonymOverride, _uuid.UUID(oid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz id")
    if o is None:
        raise HTTPException(status_code=404, detail="Overlay bulunamadı")
    session.delete(o)
    session.commit()
    audit.record(getattr(request.state, "principal", None), "synonym_delete",
                 nl_question=f"{o.cube}.{o.field_name or '*'} overlay silindi",
                 ip=request.client.host if request.client else None)


@router.get("/candidates")
def mine_candidates(limit: int = 50, session: Session = Depends(get_session)) -> dict:
    """Öğrenme döngüsü — route-edilemeyen + LLM'e düşen soruları TRİYAJ eder (ADR-0018).

    Kaynak: `interaction_log` (ADR-0020). Başarısız soruları (SQL yok = route-yok, ya da
    kind=llm = LLM'e düştü) kümeler, sıklıkla sıralar, TRİYAJ eder (deterministik, LLM yok):
      • vqr     → cube_query kaydı VAR → doğrulanmış sorgu adayı (sonraki sefer LLM'siz)
      • synonym → cube_query yok → kelime/eşanlam eksik (~%80; admin cube/alan seçip ekler)
    note (neden başarısız) + kinds gösterilir; admin tek tıkla synonym/VQR'a yükseltir."""
    import json
    import re

    from sqlmodel import col, or_

    from control_plane.models import InteractionLog

    rows = session.exec(
        select(InteractionLog.question, InteractionLog.kind, InteractionLog.cube_query_json,
               InteractionLog.note)
        .where(or_(col(InteractionLog.sql).is_(None), InteractionLog.kind == "llm"),
               col(InteractionLog.follow_up).is_(False), col(InteractionLog.kind) != "upload")
        .order_by(col(InteractionLog.ts).desc()).limit(3000)).all()

    groups: dict = {}
    for question, kind, cq_json, note in rows:
        q = (question or "").strip()
        if not q or len(q) > 80 or re.search(r"\b(dima|merhaba|selam)\b", q.lower()):
            continue
        g = groups.setdefault(q.lower(), {"question": q, "count": 0, "cube_query": None,
                                          "kinds": set(), "note": None})
        g["count"] += 1
        if kind:
            g["kinds"].add(kind)
        if cq_json and not g["cube_query"]:
            try:
                g["cube_query"] = json.loads(cq_json)
            except (ValueError, TypeError):
                pass
        if note and not g["note"]:
            g["note"] = note

    ranked = sorted(groups.values(), key=lambda x: -x["count"])[:limit]
    return {"candidates": [{
        "question": g["question"], "count": g["count"],
        "triage": "vqr" if g["cube_query"] else "synonym",
        "kinds": sorted(g["kinds"]), "note": g["note"], "cube_query": g["cube_query"],
    } for g in ranked]}


@router.get("/cubes")
def synonym_cube_targets() -> dict:
    """Synonym hedef kataloğu (aday kuyruğu formu için): cube → {measures, dimensions}."""
    return {"cubes": [{"name": n, "label": c.get("display") or n,
                       "measures": c.get("measures") or [],
                       "dimensions": c.get("dimensions") or []}
                      for n, c in _known_cubes().items()]}


class VqrPromote(_BaseModel):
    company: str
    question: str
    cube_query: dict
    tenant_id: str | None = None


@router.post("/candidates/promote-vqr", status_code=201)
def promote_vqr(body: VqrPromote, request: Request,
                session: Session = Depends(get_session)) -> dict:
    """Aday → VQR (doğrulanmış sorgu): question→cube_query çiftini control-plane'e yazar.
    Public app başlangıçta VerifiedQuery'yi belleğe yükler (per-company) → sonraki sefer
    aynı soru LLM'siz, deterministik cevaplanır. Dönem filtresi cube_query'den düşürülür
    (VQR sınıf düşer). Soft-delete kuralı: fiziksel silme yok."""
    from app.cube_router import _norm
    from control_plane.models import VerifiedQuery

    cq = {k: v for k, v in (body.cube_query or {}).items() if k != "filters"}
    principal = getattr(request.state, "principal", None)
    row = VerifiedQuery(
        company=body.company, tenant_id=body.tenant_id, question=body.question,
        question_norm=_norm(body.question),
        cube_query_json=json.dumps(cq, ensure_ascii=False), source="mined",
        verified_by=getattr(principal, "user_id", None))
    session.add(row)
    session.commit()
    return {"id": str(row.id), "question": body.question, "company": body.company}
