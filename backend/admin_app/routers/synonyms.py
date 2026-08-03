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


def _known_cubes(slug: str | None = None) -> dict[str, dict]:
    """Hedef kataloğun cube→{measures,dimensions} haritası (hedef doğrulaması için).

    ÖNCEDEN her zaman süreç varsayılanının (`settings.company`) kataloğunu döndürüyordu —
    `tenant`-kapsamlı bir sinonim adayı (`scope_id`=başka bir tenant slug'ı) incelenirken
    YANLIŞ tenant'ın cube/ölçü/boyut listesine karşı doğrulanıyordu (aynı hata sınıfı: bkz.
    app/schedules.py, app/routers/dashboards.py düzeltmeleri — burada veri sızıntısı değil,
    ama yanlış-kabul/yanlış-ret riski). `slug` verilmişse VE varsayılandan farklıysa, o
    tenant'ın ZATEN DERLENMİŞ projesini kullanmayı dener (admin_app kendi compose/build
    tetiklemez — Wren'siz ince imaj ilkesi); derlenmiş proje yoksa süreç varsayılanına düşer."""
    try:
        from app.config import get_settings
        from app.wren_service import WrenService

        s = get_settings()
        project_dir = s.resolved_project_dir()
        if slug and slug != s.company:
            candidate = project_dir.parent / "wren-projects" / slug
            if (candidate / "target" / "mdl.json").exists():
                project_dir = candidate
        svc = WrenService(project_dir, s.datasource, {}, company_slug=slug or s.company)
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
    # Hedef katalogda var mı? (bozuk overlay sessizce çürümesin) — tenant-kapsamlı adaylar
    # KENDİ tenant'larının kataloğuna karşı doğrulanır (bkz. _known_cubes docstring).
    cubes = _known_cubes(body.scope_id if body.scope_type == "tenant" else None)
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

    from app.cube_router import RED_KODLARI
    from control_plane.models import InteractionLog

    rows = session.exec(
        select(InteractionLog.question, InteractionLog.kind, InteractionLog.cube_query_json,
               InteractionLog.note, InteractionLog.reject_reason)
        .where(or_(col(InteractionLog.sql).is_(None), InteractionLog.kind == "llm"),
               col(InteractionLog.follow_up).is_(False), col(InteractionLog.kind) != "upload")
        .order_by(col(InteractionLog.ts).desc()).limit(3000)).all()

    groups: dict = {}
    for question, kind, cq_json, note, red in rows:
        q = (question or "").strip()
        if not q or len(q) > 80 or re.search(r"\b(dima|merhaba|selam)\b", q.lower()):
            continue
        g = groups.setdefault(q.lower(), {"question": q, "count": 0, "cube_query": None,
                                          "kinds": set(), "note": None, "red": None})
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
        if red and not g["red"]:
            g["red"] = red

    ranked = sorted(groups.values(), key=lambda x: -x["count"])[:limit]
    return {"candidates": [{
        "question": g["question"], "count": g["count"],
        "triage": "vqr" if g["cube_query"] else "synonym",
        "kinds": sorted(g["kinds"]), "note": g["note"], "cube_query": g["cube_query"],
        # FAZ 2b — RED GEREKÇESİ TRİYAJA GİRİYOR. Faz 0 `reject_reason`'ı ölçülebilir
        # yaptı ama tüketicisi YOKTU; planın K2(ii) şartı ("önceliği Faz 0'ın
        # red-gerekçesi telemetrisi belirler") bu alanı KULLANMAYI gerektirir.
        "red_kodu": g["red"], "red_gerekcesi": RED_KODLARI.get(g["red"] or "", None),
        # "en çok HANGİ KELİME kapıya takıldı" — planın literal cümlesi. Kapsam kapısında
        # (R10) ve kimlik eşleşmesinde (R1) AÇIKLANAMAYAN kelimeler bir sinonim adayının
        # ta kendisidir; admin bunu görmeden HANGİ kelimeyi ekleyeceğini bilemez.
        # `slug=None` → AKTİF şirketin kataloğu. Bu uç tenant-kapsamlı DEĞİL
        # (`interaction_log` çok-tenantlıdır ama gruplama soru metnine göredir);
        # kapsamı burada uydurmak, yanlış katalogla "tanınıyor" demek olurdu.
        "takilan_kelimeler": sorted(_takilan_kelimeler(g["question"])),
    } for g in ranked]}


def _takilan_kelimeler(soru: str, slug: str | None = None) -> set[str]:
    """Sorunun katalogca AÇIKLANAMAYAN kelimeleri — sinonim adayının kendisi.

    `cube_router`'ın kapsam kapısıyla **aynı** dolgu sözlüğünü okur (`_period_hit_words` +
    `_misc_hit_words`); ayrı bir liste tutmak iki tarafı ayrıştırır ve admin'e kapının
    gerçekte takıldığı kelimeden BAŞKA bir şey gösterirdi.

    Bu, `route()`'un kendi kararını **görünür** kılar: R1/R10 telemetride bir SAYIydı,
    burada bir EYLEME dönüşür — *"şu kelime şu cube'a sinonim olarak eklensin mi?"*.
    Boyut/ölçü ayrımını admin yapar (`/sadmin/synonyms/cubes` zaten `field_kind` seçtiriyor)
    — yani **yeni bir uç/panel AÇILMADI**, var olan onay akışı besleniyor.

    ## ⚠️ FAZ 9.15 — KATALOGDA TANINAN KELİMELER ADAY LİSTELENİYORDU

    İlk sürüm `known` kümesine YALNIZ dolgu sözlüğünü veriyordu; cube/ölçü/boyut
    sinonimleri **hiç eklenmiyordu**. Sonuç: admin'e *"`ciro`'yu sinonim olarak ekle"*
    deniyordu — oysa `ciro`, `parti.toplam_ciro`'nun **zaten** sinonimi. Aynı şey
    `borc` ve `musteri` için de ölçüldü.

    Bu, aracın kendi amacını tersine çeviriyordu: triyaj kuyruğu *"kapsam boşluğu"*
    göstermek yerine kataloğun **var olan** sözlüğünü tekrar öneriyor, gerçek boşluklar
    gürültünün içinde kayboluyordu. `route()`'un kapsam kapısı `known`'a cube/ölçü/boyut
    eşleşmelerini ekler (`cube_router.py:~2670`); burada aynı şey yapılmazsa iki taraf
    ayrışır — bu dosyanın kendi docstring'inin *"ayrı liste tutmak iki tarafı ayrıştırır"*
    uyarısı, tam da kendisi için geçerliydi.
    """
    try:
        from app.cube_router import (
            _misc_hit_words, _norm, _period_hit_words, _syn_hit_words, _uncovered,
        )
    except Exception:                      # admin plane Wren'siz koşabilir — sessiz geç
        return set()
    q = _norm(soru or "")
    if not q:
        return set()
    known = _period_hit_words(q) | _misc_hit_words(q)
    # KATALOG SÖZLÜĞÜ: cube kimliği + ölçü + boyut sinonimleri. Kapsam kapısıyla AYNI
    # kaynak; `slug` verilmezse aktif şirketin kataloğu okunur.
    try:
        for _ad, c in (_known_cubes(slug) or {}).items():
            known |= _syn_hit_words(q, [_ad, *(c.get("synonyms") or []),
                                        str(c.get("display") or "")])
            for syns in (c.get("measure_synonyms") or {}).values():
                known |= _syn_hit_words(q, syns)
            for syns in (c.get("dimension_synonyms") or {}).values():
                known |= _syn_hit_words(q, syns)
    except Exception:                      # katalog okunamıyorsa dolgu sözlüğüyle devam
        pass
    return {w for w in _uncovered(q, known) if len(w) >= 3}


@router.get("/cubes")
def synonym_cube_targets(slug: str | None = None) -> dict:
    """Synonym hedef kataloğu (aday kuyruğu formu için): cube → {measures, dimensions}.
    `slug` verilirse (tenant-kapsamlı aday incelenirken) o tenant'ın kataloğu döner."""
    return {"cubes": [{"name": n, "label": c.get("display") or n,
                       "measures": c.get("measures") or [],
                       "dimensions": c.get("dimensions") or []}
                      for n, c in _known_cubes(slug).items()]}


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
