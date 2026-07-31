"""Zamanlanmış rapor + bildirim uçları (ADR-0011)."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app import cube_router
from app.auth.dependencies import require, require_company
from app.company_registry import wren_for_request
from app.config import get_settings
from app.schedules import run_schedule
from control_plane.authorize import Principal, can

router = APIRouter(tags=["schedules"])


def _visible(rec: dict, principal: Principal | None) -> bool:
    """Tenant-RLS: kayıt sahibi tenant eşleşmeli; tenant_id'siz (RLS-öncesi/seed)
    kayıtlar yalnız aktif şirketin tenant'ına görünür. Superadmin hepsini görür
    (log-only doktrini — erişim engellenmez, audit'lenir)."""
    if principal is None:
        return False
    if principal.is_superadmin:
        return True
    rt = rec.get("tenant_id")
    if rt is None:
        return principal.tenant_slug == get_settings().company
    return rt == principal.tenant_id


class ScheduleRequest(BaseModel):
    label: str
    cube_query: dict
    # GÖRELİ dönem ("dün", "son 7 gün", "bu ay") — her koşumda tarih motoruyla çözülür.
    period: str | None = None
    every: str = Field(default="day", pattern="^(hour|day|week)$")
    at: str | None = "08:00"
    weekday: int | None = None  # 1=Pzt..7=Paz (every=week)
    threshold: dict | None = None  # {measure, op: gt|gte|lt|lte, value} | {method:zscore,k}
    delivery: dict | None = None  # ek teslim kanalları {email:{to:[...]}}


@router.get("/schedules", dependencies=[Depends(require("schedule:read"))])
def list_schedules(request: Request) -> dict:
    principal = getattr(request.state, "principal", None)
    return {"schedules": [s for s in request.app.state.schedules.list()
                          if _visible(s, principal)]}


@router.post("/schedules", dependencies=[Depends(require("schedule:create")),
                                         Depends(require_company)])
def create_schedule(request: Request, body: ScheduleRequest) -> dict:
    # CubeQuery katalog doğrulamasından geçmeli (bozuk zamanlama sessizce çürümesin).
    # wren_for_request KULLAN — ÖNCEDEN `request.app.state.wren` (süreç varsayılanı)
    # kullanılıyordu: non-default tenant'ın zamanlaması YANLIŞ katalogla doğrulanıyordu
    # (aynı hata sınıfı — bkz. app/schedules.py:_wren_for_schedule, dashboards.py).
    service = wren_for_request(request)
    _, index = cube_router.build_catalog(service.schema())
    cq = cube_router.parse_cube_query(json.dumps(body.cube_query, ensure_ascii=False), index)
    if not cq:
        raise HTTPException(status_code=400, detail="Geçersiz cube sorgusu.")
    if body.threshold and body.threshold.get("measure") not in (cq.get("measures") or []):
        raise HTTPException(status_code=400, detail="Eşik ölçüsü raporun ölçülerinden biri olmalı.")
    if body.delivery is not None:
        emails = (body.delivery.get("email") or {}).get("to") or []
        if any("@" not in str(a) for a in emails):
            raise HTTPException(status_code=400, detail="Geçersiz e-posta adresi.")
    principal = getattr(request.state, "principal", None)
    sched = request.app.state.schedules.add({
        "label": body.label,
        "cube_query": cq,
        "period": body.period,
        "every": body.every,
        "at": body.at,
        **({"weekday": body.weekday} if body.weekday else {}),
        **({"threshold": body.threshold} if body.threshold else {}),
        **({"delivery": body.delivery} if body.delivery else {}),
        **({"created_by": principal.user_id} if principal else {}),
        **({"tenant_id": principal.tenant_id} if principal else {}),
    })
    from control_plane import audit

    audit.record(principal, "schedule_create", nl_question=body.label,
                 ip=request.client.host if request.client else None)
    return {"schedule": sched}


@router.delete("/schedules/{sid}")
def delete_schedule(request: Request, sid: str) -> dict:
    principal = getattr(request.state, "principal", None)
    sched = request.app.state.schedules.get(sid)
    if sched is None or not _visible(sched, principal):
        # Başka tenant'ın kaydı: varlığı da sızmaz.
        raise HTTPException(status_code=404, detail="Zamanlama bulunamadı.")
    # admin+ herkesinkini; analyst yalnız KENDİ oluşturduğunu silebilir.
    own = (principal is not None and sched.get("created_by") == principal.user_id
           and can(principal, "schedule:create"))
    if not (principal is not None and (can(principal, "schedule:delete") or own)):
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    if not request.app.state.schedules.remove(sid):
        raise HTTPException(status_code=404, detail="Zamanlama bulunamadı.")
    from control_plane import audit

    audit.record(getattr(request.state, "principal", None), "schedule_delete",
                 nl_question=sid, ip=request.client.host if request.client else None)
    return {"removed": True}


@router.post("/schedules/{sid}/run", dependencies=[Depends(require("schedule:run")),
                                                   Depends(require_company)])
def run_now(request: Request, sid: str) -> dict:
    """Manuel tetik — demo ve doğrulama için: koşar, bildirim + sözleşme üretir."""
    sched = request.app.state.schedules.get(sid)
    if sched is None or not _visible(sched, getattr(request.state, "principal", None)):
        raise HTTPException(status_code=404, detail="Zamanlama bulunamadı.")
    try:
        note = run_schedule(request.app.state, sched, manual=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Koşum hatası: {exc}") from exc
    return {"notification": note}


@router.get("/notifications", dependencies=[Depends(require("notification:read"))])
def notifications(request: Request, limit: int = 20) -> dict:
    principal = getattr(request.state, "principal", None)
    include_legacy = (principal is not None
                      and principal.tenant_slug == get_settings().company)
    return {"notifications": request.app.state.schedules.notifications(
        limit=min(limit, 100),
        tenant_id=getattr(principal, "tenant_id", None),
        include_legacy=include_legacy,
    )}
