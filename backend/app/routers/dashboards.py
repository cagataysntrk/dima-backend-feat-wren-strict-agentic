"""Kullanıcı panoları (§9 canlı-izleme, PULL ayağı) — PER-USER, ≤10/user.

Widget = kayıtlı `cube_query` + göreli dönem (schedule/VQR ile aynı "kayıtlı sorgu"
soyutlaması; dönem SAKLANMAZ, /data'da yeniden çözülür). Chat sonucundan doğar
(cube_query+view_hint zaten yanıtta) → "panoya ekle". Soft-delete (ADR-0019).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, col, select

from app import cube_router, viz, yoy
from app.auth.dependencies import require_company
from app.company_registry import wren_for_request
from control_plane.db import get_session
from control_plane.models import Dashboard, DashboardWidget

router = APIRouter(tags=["dashboards"])

_MAX_PER_USER = 10


def _principal(request: Request):
    p = getattr(request.state, "principal", None)
    if p is None:
        raise HTTPException(status_code=401, detail="Kimlik gerekli")
    return p


class DashboardCreate(BaseModel):
    title: str = ""


class DashboardPatch(BaseModel):
    title: str | None = None
    visibility: str | None = None  # private | tenant
    layout: dict | None = None


class WidgetCreate(BaseModel):
    title: str = ""
    cube_query: dict
    view_hint: str | None = None
    period: str | None = None
    pos: dict | None = None
    refresh: str = "onview"


def _get_owned(session: Session, did: str, principal, *, write: bool = False) -> Dashboard:
    """Panoyu getirir + erişim kontrolü. write=True → yalnız SAHİBİ (tenant-görünür
    salt-okunur). Başka kullanıcının panosu 404 (varlığı sızmaz)."""
    try:
        d = session.get(Dashboard, uuid.UUID(did))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz pano id")
    if d is None or d.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Pano bulunamadı")
    own = d.user_id == principal.user_id
    visible = own or (d.visibility == "tenant" and d.tenant_id == principal.tenant_id)
    if not visible:
        raise HTTPException(status_code=404, detail="Pano bulunamadı")
    if write and not own:
        raise HTTPException(status_code=403, detail="Yalnız pano sahibi düzenleyebilir")
    return d


def _widget_dict(w: DashboardWidget) -> dict:
    return {"id": str(w.id), "title": w.title,
            "cube_query": json.loads(w.cube_query_json),
            "view_hint": w.view_hint, "period": w.period,
            "pos": json.loads(w.pos_json) if w.pos_json else None, "refresh": w.refresh}


def _widgets_of(session: Session, dashboard_id) -> list[DashboardWidget]:
    return list(session.exec(select(DashboardWidget).where(
        DashboardWidget.dashboard_id == dashboard_id,
        col(DashboardWidget.deleted_at).is_(None),
    ).order_by(col(DashboardWidget.created_at))).all())


@router.get("/dashboards")
def list_dashboards(request: Request, session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    rows = session.exec(select(Dashboard).where(
        col(Dashboard.deleted_at).is_(None),
        (col(Dashboard.user_id) == p.user_id)
        | ((col(Dashboard.visibility) == "tenant") & (col(Dashboard.tenant_id) == p.tenant_id)),
    ).order_by(col(Dashboard.updated_at).desc())).all()
    out = []
    for d in rows:
        n = len(_widgets_of(session, d.id))
        out.append({"id": str(d.id), "title": d.title, "visibility": d.visibility,
                    "widget_count": n, "own": d.user_id == p.user_id,
                    "updated_at": d.updated_at.isoformat(timespec="seconds")})
    return {"dashboards": out, "max_per_user": _MAX_PER_USER}


@router.post("/dashboards")
def create_dashboard(request: Request, body: DashboardCreate,
                     session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    n = len(session.exec(select(Dashboard.id).where(
        col(Dashboard.user_id) == p.user_id, col(Dashboard.deleted_at).is_(None))).all())
    if n >= _MAX_PER_USER:
        raise HTTPException(status_code=409,
                            detail=f"En fazla {_MAX_PER_USER} pano oluşturabilirsiniz")
    d = Dashboard(tenant_id=p.tenant_id, user_id=p.user_id, title=body.title or "Yeni pano")
    session.add(d)
    session.commit()
    session.refresh(d)
    return {"id": str(d.id), "title": d.title}


@router.get("/dashboards/{did}")
def get_dashboard(request: Request, did: str, session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    d = _get_owned(session, did, p)
    return {"id": str(d.id), "title": d.title, "visibility": d.visibility,
            "own": d.user_id == p.user_id,
            "widgets": [_widget_dict(w) for w in _widgets_of(session, d.id)]}


@router.patch("/dashboards/{did}")
def patch_dashboard(request: Request, did: str, body: DashboardPatch,
                    session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    d = _get_owned(session, did, p, write=True)
    if body.title is not None:
        d.title = body.title
    if body.visibility in ("private", "tenant"):
        d.visibility = body.visibility
    if body.layout is not None:
        d.layout_json = json.dumps(body.layout, ensure_ascii=False)
    d.updated_at = datetime.utcnow()
    session.add(d)
    session.commit()
    return {"id": str(d.id), "title": d.title, "visibility": d.visibility}


@router.delete("/dashboards/{did}")
def delete_dashboard(request: Request, did: str, session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    d = _get_owned(session, did, p, write=True)
    d.deleted_at = datetime.utcnow()  # soft-delete (ADR-0019)
    session.add(d)
    session.commit()
    return {"removed": True}


@router.post("/dashboards/{did}/widgets", dependencies=[Depends(require_company)])
def add_widget(request: Request, did: str, body: WidgetCreate,
               session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    d = _get_owned(session, did, p, write=True)
    # cube_query katalog doğrulaması (bozuk widget çürümesin) — schedules ile aynı.
    # wren_for_request KULLAN (request.app.state.wren DEĞİL) — önceden non-default tenant'ın
    # widget'ı YANLIŞ (varsayılan şirket) katalogla doğrulanıyordu (cross-tenant sızıntı sınıfı,
    # bkz. schedules.py aynı hatanın düzeltmesi). NOT (31 Temmuz 2026 — canlı testle yakalandı):
    # `wren_for_request` TEK BAŞINA yetmez — `request.state.wren`'i YALNIZ `require_company`
    # dependency'si doldurur; bu router `require_company`'yi hiç çağırmıyordu, bu yüzden
    # önceki "düzeltme" fiilen HİÇBİR ZAMAN devreye girmiyordu (statik regex-kilit
    # test_no_default_tenant_leak.py bunu YAKALAYAMAZ — yalnız `request.app.state.wren`
    # doğrudan kullanımını arar, eksik dependency'yi değil). Router-seviyesinde DEĞİL,
    # endpoint-seviyesinde eklendi (dashboards.py'de query-tabanlı GET'ler tenant-bağımsız
    # kalabilir; yalnız wren_for_request çağıran iki endpoint gerçekten ihtiyaç duyuyor).
    service = wren_for_request(request)
    _, index = cube_router.build_catalog(service.schema())
    cq = cube_router.parse_cube_query(json.dumps(body.cube_query, ensure_ascii=False), index)
    if not cq:
        raise HTTPException(status_code=400, detail="Geçersiz cube sorgusu")
    # parse compare'ı düşürür → geri ekle ki YoY/MoM grafiği panoda BİRE BİR aynı gelsin
    # (yoksa /data düz cube_sql koşar, geçen-yıl serisi kaybolur).
    _cmp = (body.cube_query or {}).get("compare")
    if _cmp in ("yoy", "mom"):
        cq["compare"] = _cmp
    w = DashboardWidget(
        dashboard_id=d.id, title=body.title or "",
        cube_query_json=json.dumps(cq, ensure_ascii=False), view_hint=body.view_hint,
        period=body.period, refresh=body.refresh,
        pos_json=json.dumps(body.pos, ensure_ascii=False) if body.pos else None)
    session.add(w)
    d.updated_at = datetime.utcnow()
    session.add(d)
    session.commit()
    session.refresh(w)
    return {"id": str(w.id)}


class WidgetPatch(BaseModel):
    # Pano widget'ının GÖRÜNÜM durumunu kalıcılaştır (kullanıcı panoda tip/görünüm değiştirince):
    # view_hint = table | pivot | <grafik-tipi>. Opsiyonel period/title de düzenlenebilir.
    view_hint: str | None = None
    period: str | None = None
    title: str | None = None
    # Doğrulama turu düzeltmesi (1 Ağustos 2026, P2-22): `DashboardWidget.pos_json`/`refresh`
    # (control_plane/models.py) VE `_widget_dict()`'in OKUMA tarafı ZATEN vardı (grep ile
    # doğrulandı) — yalnız bu YAZMA ucu iki alanı hiç KABUL ETMİYORDU, bu yüzden kullanıcı
    # ne widget genişliğini/yerleşimini ne de yenileme sıklığını hiç KAYDEDEMİYORDU.
    pos: dict | None = None                # {x,y,w,h} — bu sürümde yalnız "w" (genişlik) kullanılır
    refresh: str | None = None             # onview | live | cache:<saniye>


@router.patch("/dashboards/{did}/widgets/{wid}")
def patch_widget(request: Request, did: str, wid: str, body: WidgetPatch,
                 session: Session = Depends(get_session)) -> dict:
    """Widget görünüm durumunu KAYDET (view_hint/period/title). Pano'nun o hâlini kalıcılaştırır →
    yeniden yüklemede aynı grafik/tip/dönem gelir. Yalnız gönderilen alanlar güncellenir."""
    p = _principal(request)
    d = _get_owned(session, did, p, write=True)
    try:
        w = session.get(DashboardWidget, uuid.UUID(wid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz widget id")
    if w is None or w.deleted_at is not None or str(w.dashboard_id) != did:
        raise HTTPException(status_code=404, detail="Widget bulunamadı")
    data = body.model_dump(exclude_unset=True)
    if "view_hint" in data:
        w.view_hint = data["view_hint"]
    if "period" in data:
        w.period = data["period"]
    if "title" in data:
        w.title = data["title"] or ""
    if "pos" in data:
        w.pos_json = json.dumps(data["pos"], ensure_ascii=False) if data["pos"] else None
    if "refresh" in data and data["refresh"]:
        w.refresh = data["refresh"]
    session.add(w)
    d.updated_at = datetime.utcnow()
    session.add(d)
    session.commit()
    return {"updated": True}


@router.delete("/dashboards/{did}/widgets/{wid}")
def delete_widget(request: Request, did: str, wid: str,
                  session: Session = Depends(get_session)) -> dict:
    p = _principal(request)
    _get_owned(session, did, p, write=True)
    try:
        w = session.get(DashboardWidget, uuid.UUID(wid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz widget id")
    if w is None or w.deleted_at is not None or str(w.dashboard_id) != did:
        raise HTTPException(status_code=404, detail="Widget bulunamadı")
    w.deleted_at = datetime.utcnow()  # soft-delete
    session.add(w)
    session.commit()
    return {"removed": True}


@router.get("/dashboards/{did}/data", dependencies=[Depends(require_company)])
def dashboard_data(request: Request, did: str, session: Session = Depends(get_session)) -> dict:
    """Her widget'ın göreli dönemini çözer + cube_query'yi KOŞAR → sonuç. Cache MVP
    sonraki katman (Redis/§9); şimdilik doğrudan icra."""
    p = _principal(request)
    d = _get_owned(session, did, p)
    # wren_for_request KULLAN — ÖNCEDEN burada `request.app.state.wren` (süreç varsayılanı)
    # kullanılıyordu: non-default tenant'ın pano widget'ları YANLIŞ tenant'ın veritabanını
    # sorguluyordu (kanıtlanmış cross-tenant veri sızıntısı — schedules.py'deki ile AYNI hata
    # sınıfı, bkz. app/schedules.py:_wren_for_schedule). `_get_owned` zaten `d`'nin `p`'ye ait
    # olduğunu doğruluyor; sorguyu ÇALIŞTIRAN servis de aynı tenant'a ait olmalı.
    # NOT (31 Temmuz 2026): bu wren_for_request çağrısı `require_company` (üstteki endpoint
    # dependency'si) ÇALIŞMADAN `request.state.wren`'i hiç dolduramaz — router bunu daha önce
    # hiç çağırmıyordu, yani "düzeltme" yalnız yorumda vardı, çalışma zamanında etkisizdi
    # (canlı testle doğrulandı: atiksan tenant'ı demo-boyahane'nin `oee` cube'unu widget'a
    # ekleyebiliyordu). Şimdi gerçekten bağlı.
    svc = wren_for_request(request)
    schema = svc.schema()
    cubes = {c.get("name"): c for c in (schema.get("cubes") or [])}
    out = []
    for w in _widgets_of(session, d.id):
        cq = json.loads(w.cube_query_json)
        period = (w.period or "").strip()
        if period:
            dfs = cube_router.date_filters(cube_router._norm(period), "tarih")
            kept = [f for f in cq.get("filters", []) if f.get("dimension") != "tarih"]
            cq = {**cq, "filters": kept + dfs}
        try:
            # DÖNEMSEL KIYAS (YoY/MoM): widget cube_query'sinde compare varsa yoy.compute ile çöz
            # (chip yolu ile AYNI) — yoksa "panoya ekle" geçen-yıl serisini KAYBEDER (düz cube_sql
            # compare'ı yok sayar). base_cq'yu viz için kullan (compare eklenmiş cq'yu döndür).
            _cmp = cq.get("compare")
            if _cmp in ("yoy", "mom"):
                tdn = yoy.time_dim_of(schema, cq.get("cube"))
                o = yoy.compute(svc, cq, _cmp, tdn, limit=1000)
                result = {"columns": o["columns"], "rows": o["rows"], "row_count": o["row_count"]}
                viz_cq = {**o["base_cq"], "compare": _cmp}
            else:
                sql = svc.cube_sql(cq)
                result = svc.query(sql, limit=1000)
                viz_cq = cq
            # VİZ ÖNERİSİ (ADR-0024): pano widget'ı da backend grafik/tablo/pivot kararını taşır
            # (cross-surface: chat ile AYNI görünüm). Widget'ın kendi view_hint'i FE'de üstüne biner.
            cmeta = cubes.get(cq.get("cube")) or {}
            # NOT (31 Temmuz 2026): "measure_units" YANLIŞ anahtardı — schema() dict'i ölçü
            # birimlerini "units" adıyla taşıyor (bkz. app/wren_service.py:236); bu yüzden
            # `recommend()`'in birim-farkındalığı burada da HİÇ devreye giremiyordu (`/cube`
            # ve `/ask`'teki AYNI hata sınıfı, bkz. app/routers/ask.py `_attach_viz`).
            wviz = viz.recommend(result, cube_query=viz_cq, **viz.meta_args(cmeta))
            # PII maskeleme (doğrulama turu düzeltmesi, 1 Ağustos 2026): panonun CANLI veri
            # ucu daha önce HİÇ maskelemiyordu — `/ask` üzerinden maskeli görülen bir sorgu
            # panoya widget olarak eklenince maskesiz görünüyordu. `/query` ile AYNI paylaşılan
            # yardımcı (app/pii.py::mask_query_result).
            from app.pii import mask_query_result

            result, unmasked_pii_shown = mask_query_result(result, p)
            if unmasked_pii_shown:
                from control_plane import audit
                audit.record(p, "pii_view", nl_question=f"pano widget · {w.id}",
                            ip=request.client.host if request.client else None)
            out.append({"id": str(w.id), "result": result, "viz": wviz, "error": None})
        except Exception as exc:  # noqa: BLE001 — tek widget hatası panoyu düşürmesin
            out.append({"id": str(w.id), "result": None, "viz": None, "error": str(exc)[:200]})
    return {"widgets": out}
