"""/sadmin/tenants — tenant listeleme + oluşturma + durum + sektör yapılandırması.

Sektör/modül seçimi TenantConfig satırına yazılır (KAYNAK DB'dir); dima-api bunu
company.yml'e materialize eder (≤60 sn) — iki servis disk paylaşmaz (onaylı tasarım).
"""

from __future__ import annotations

import json
import uuid as _uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from control_plane import audit
from control_plane.db import get_session
from control_plane.models import Role, Tenant, TenantConfig

from admin_app.schemas import TenantConfigUpdate, TenantCreate, TenantOut, TenantStatusUpdate

router = APIRouter(prefix="/sadmin/tenants", tags=["sadmin-tenants"])

# Faz 2d (31 Temmuz 2026) — Discovery→Promote ölçü-onay iş akışı analyst/admin rolü
# GEREKTİRİYOR (bkz. plan "Faz 2'nin ön koşulu": dar kapsamlı, genel RBAC açılışı DEĞİL).
# admin/analyst artık HER tenant'ta Role satırı olarak var — owner hâlâ TEK ürün-genel rol
# (viewer'ı herkese açmak hâlâ ertelenir, bkz. authorize.py ROLE_RANK/CLAUDE.md "rol matrisi
# uykuda"). users.py yalnız owner/admin/analyst'ı kabul eder (viewer hâlâ 400).
_DEFAULT_ROLES = ("owner", "admin", "analyst")


def _known_pack_keys() -> tuple[set[str], set[str], dict[str, bool]]:
    """(sektör, modül anahtarları, kaynak→onekli) — bozuk seçim sessizce çürümesin."""
    try:
        from app.config import get_settings
        from app.packs import list_packs

        packs = list_packs(get_settings().resolved_project_dir().parent)
        return ({p["key"] for p in packs["sektorler"]},
                {p["key"] for p in packs["moduller"]},
                {p["key"]: bool(p.get("onekli")) for p in packs.get("kaynaklar", [])})
    except Exception:
        return set(), set(), {}


def _validate_packs(sektorler: list[str], moduller: list[str] | None,
                    kaynaklar: list[str] | None = None,
                    firma_no: int | None = None) -> None:
    known_s, known_m, known_k = _known_pack_keys()
    bad = [s for s in sektorler if s not in known_s]
    if bad:
        raise HTTPException(status_code=400, detail=f"Bilinmeyen sektör paketi: {bad}")
    if moduller:
        bad = [m for m in moduller if m not in known_m]
        if bad:
            raise HTTPException(status_code=400, detail=f"Bilinmeyen modül paketi: {bad}")
    if kaynaklar:
        bad = [k for k in kaynaklar if k not in known_k]
        if bad:
            raise HTTPException(status_code=400, detail=f"Bilinmeyen kaynak paketi: {bad}")
        # Önekli şema (Logo LG_FFF_*): firma kapsamı olmadan model bağlanamaz.
        onekli = [k for k in kaynaklar if known_k.get(k)]
        if onekli and firma_no is None:
            raise HTTPException(
                status_code=400,
                detail=f"Kaynak {onekli} firma/dönem kapsamı ister (firma_no verin)")


# Desteklenen diller (§7b) — şu an tr (yerel) + en (teknik). Cube-based desteklenen dil
# ileride; o seviyede değiliz. Admin firma ayarlarından bu kümeden seçer.
SUPPORTED_LANGS = ("tr", "en")


def _validate_langs(diller: list[str] | None) -> None:
    if diller:
        bad = [d for d in diller if d not in SUPPORTED_LANGS]
        if bad:
            raise HTTPException(status_code=400,
                                detail=f"Desteklenmeyen dil: {bad} (desteklenen: {list(SUPPORTED_LANGS)})")


def _config_of(session: Session, tenant_id) -> TenantConfig | None:
    return session.exec(select(TenantConfig).where(
        TenantConfig.tenant_id == tenant_id)).first()


def _out(t: Tenant, cfg: TenantConfig | None = None) -> TenantOut:
    return TenantOut(
        id=str(t.id), slug=t.slug, name=t.name, status=t.status,
        sektorler=json.loads(cfg.sektorler_json) if cfg else None,
        moduller=json.loads(cfg.moduller_json) if cfg and cfg.moduller_json else None,
        kaynaklar=json.loads(cfg.kaynaklar_json) if cfg and cfg.kaynaklar_json else None,
        firma_no=cfg.firma_no if cfg else None,
        donem_no=cfg.donem_no if cfg else None,
        diller=json.loads(cfg.diller_json) if cfg and cfg.diller_json else None,
    )


@router.get("", response_model=list[TenantOut])
def list_tenants(session: Session = Depends(get_session)) -> list[TenantOut]:
    return [_out(t, _config_of(session, t.id))
            for t in session.exec(select(Tenant)).all()]


@router.post("", response_model=TenantOut, status_code=201)
def create_tenant(body: TenantCreate, request: Request,
                  session: Session = Depends(get_session)) -> TenantOut:
    if session.exec(select(Tenant).where(Tenant.slug == body.slug)).first():
        raise HTTPException(status_code=409, detail="Bu slug zaten kullanımda")
    if body.sektorler or body.kaynaklar:
        _validate_packs(body.sektorler, body.moduller, body.kaynaklar, body.firma_no)
    _validate_langs(body.diller)
    tenant = Tenant(slug=body.slug, name=body.name)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    for key in _DEFAULT_ROLES:
        session.add(Role(tenant_id=tenant.id, key=key, name=key.capitalize()))
    principal = getattr(request.state, "principal", None)
    cfg = None
    if body.sektorler or body.kaynaklar or body.diller:
        cfg = TenantConfig(
            tenant_id=tenant.id,
            sektorler_json=json.dumps(body.sektorler),
            moduller_json=json.dumps(body.moduller) if body.moduller is not None else None,
            kaynaklar_json=json.dumps(body.kaynaklar) if body.kaynaklar else None,
            diller_json=json.dumps(body.diller) if body.diller else None,
            firma_no=body.firma_no,
            donem_no=body.donem_no,
            updated_by=_uuid.UUID(principal.user_id) if principal else None,
        )
        session.add(cfg)
    session.commit()
    ip = request.client.host if request.client else None
    audit.record(principal, "tenant_create",
                 nl_question=f"tenant: {tenant.slug}"
                 + (f" · sektorler: {body.sektorler}" if body.sektorler else ""),
                 ip=ip)
    return _out(tenant, cfg)


@router.put("/{tid}/config", response_model=TenantOut)
def update_tenant_config(tid: str, body: TenantConfigUpdate, request: Request,
                         session: Session = Depends(get_session)) -> TenantOut:
    """Sektör/modül setini günceller. dima-api ≤60 sn'de materialize eder; cube
    kaldıran değişiklikte o cube'a bağlı schedule/VQR kayıtları çalışmaz olur —
    panel bu uyarıyı gösterir."""
    try:
        tenant = session.get(Tenant, _uuid.UUID(tid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz tenant id")
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant bulunamadı")
    _validate_packs(body.sektorler, body.moduller, body.kaynaklar, body.firma_no)
    _validate_langs(body.diller)
    principal = getattr(request.state, "principal", None)
    cfg = _config_of(session, tenant.id)
    if cfg is None:
        cfg = TenantConfig(tenant_id=tenant.id, sektorler_json="[]")
    cfg.sektorler_json = json.dumps(body.sektorler)
    cfg.moduller_json = json.dumps(body.moduller) if body.moduller is not None else None
    # diller SEMANTİĞİ (kaynaklar gibi): None = dokunma (eski panel); [] = temizle; liste = ata.
    if body.diller is not None:
        cfg.diller_json = json.dumps(body.diller) if body.diller else None
    # kaynaklar SEMANTİĞİ: None = alanı bilmeyen istemci (eski panel) — DOKUNMA;
    # [] = bilinçli temizle; dolu liste = ata. Kapsam yalnız kaynakla birlikte değişir.
    if body.kaynaklar is not None:
        cfg.kaynaklar_json = json.dumps(body.kaynaklar) if body.kaynaklar else None
        cfg.firma_no = body.firma_no
        cfg.donem_no = body.donem_no
    cfg.updated_by = _uuid.UUID(principal.user_id) if principal else None
    cfg.updated_at = datetime.utcnow()
    session.add(cfg)
    session.commit()
    session.refresh(cfg)
    audit.record(principal, "tenant_config",
                 nl_question=f"tenant: {tenant.slug} → sektorler: {body.sektorler}"
                 + (f", moduller: {body.moduller}" if body.moduller is not None else "")
                 + (f", kaynaklar: {body.kaynaklar}" if body.kaynaklar else "")
                 + (f", kapsam: {body.firma_no}/{body.donem_no}" if body.firma_no else ""),
                 ip=request.client.host if request.client else None)
    return _out(tenant, cfg)


@router.patch("/{tid}", response_model=TenantOut)
def update_tenant_status(tid: str, body: TenantStatusUpdate, request: Request,
                         session: Session = Depends(get_session)) -> TenantOut:
    """Askıya al / aktifleştir. Askıdaki firmanın kullanıcıları: yeni login 403
    (açık mesaj), açık oturumlar ≤60 sn'de düşer (per-request durum kontrolü) ve
    refresh reddedilir → frontend login'e yönlenir (auto-logout)."""
    try:
        tenant = session.get(Tenant, _uuid.UUID(tid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz tenant id")
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant bulunamadı")
    tenant.status = body.status
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    audit.record(getattr(request.state, "principal", None), "tenant_status",
                 nl_question=f"tenant: {tenant.slug} → {tenant.status}",
                 ip=request.client.host if request.client else None)
    return _out(tenant, _config_of(session, tenant.id))
