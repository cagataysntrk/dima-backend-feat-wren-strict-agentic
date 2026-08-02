"""FastAPI dependencies: request principal (Katman A) + fingerprint.

``get_current_principal`` korunan router'lara dependency olarak takılır. Auth HER ZAMAN
zorunlu — geçerli Bearer (JWT) access token yoksa 401 (kapatma bayrağı YOK; DIMA_AUTH_ENABLED
kaldırıldı). Kimlik yalnız token'dan türetilir (ADR-0014 Karar 1).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.security import decode_access_token, make_fingerprint

# OpenAPI security scheme: Swagger'da "Authorize" düğmesi + korumalı uçların işareti.
# auto_error=False → 401 mesajını (Türkçe) biz veririz, FastAPI'nin 403'ü değil.
bearer_scheme = HTTPBearer(
    auto_error=False,
    bearerFormat="JWT",
    description="Access token — /auth/login yanıtındaki access_token değeri.",
)


def get_fingerprint(request: Request) -> str:
    return make_fingerprint(
        request.headers.get("user-agent", ""),
        request.headers.get("accept-language", ""),
    )


def get_current_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Principal:
    # Auth her zaman zorunlu — korunan her endpoint geçerli bir access token ister.
    if credentials is None:
        raise HTTPException(status_code=401, detail="Kimlik doğrulaması gerekli")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token")
    if payload.get("typ") != "access":
        raise HTTPException(status_code=401, detail="Geçersiz token tipi")
    principal = Principal(
        user_id=payload["sub"],
        tenant_id=payload.get("tid"),
        is_superadmin=payload.get("sa", False),
        roles=payload.get("roles", []),
        tenant_slug=payload.get("tsl"),
    )
    # Askıya alınan firma: access token süresi dolmadan da düşür (60 sn TTL cache).
    # 401 → frontend refresh dener → rotate de reddeder → login'e yönlenir (auto-logout).
    if principal.tenant_id and not _tenant_active(principal.tenant_id):
        raise HTTPException(status_code=401, detail="Firma hesabı askıya alınmış")
    # Endpoint imzalarını değiştirmeden audit/log yazıcılarının kimliğe erişmesi için.
    request.state.principal = principal
    return principal


_TENANT_STATUS_TTL = 60.0
_tenant_status_cache: dict[str, tuple[float, bool]] = {}


def _tenant_active(tenant_id: str) -> bool:
    import time
    import uuid as _uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import Tenant

    now = time.monotonic()
    hit = _tenant_status_cache.get(tenant_id)
    if hit and now - hit[0] < _TENANT_STATUS_TTL:
        return hit[1]
    try:
        with Session(engine) as s:
            tenant = s.get(Tenant, _uuid.UUID(tenant_id))
        active = tenant is not None and tenant.status == "active"
    except Exception:
        active = True  # control-plane geçici hatası oturumları düşürmesin
    _tenant_status_cache[tenant_id] = (now, active)
    return active


def require(action: str):
    """Rol-matrisli endpoint koruması: ``Depends(require("vqr:write"))``.

    Tüm kontrol tek arayüzden (``authorize``, ADR-0014 Karar 3) geçer; endpoint
    kodu user/role tablosuna dokunmaz. Red → 403.
    """

    def dep(principal: Principal = Depends(get_current_principal)) -> Principal:
        try:
            authorize(principal, action, f"data:{action.split(':', 1)[0]}")
        except AuthzError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        return principal

    return dep


def require_company(request: Request,
                    principal: Principal = Depends(get_current_principal)) -> Principal:
    """Veri-düzlemi tenant bağı (ADR-0014 Karar 1 + çok-şirketli runtime v1).

    Varsayılan şirket (settings.company) startup'ta yüklüdür; BAŞKA tenant'ın
    kullanıcısı gelirse şirketi registry'den talep üzerine derlenip
    ``request.state.wren``'e bağlanır — endpoint'ler ``wren_for_request`` ile doğru
    servisi görür. Şirket dizini/config'i olmayan tenant için 403 (varlık sızmaz)."""
    from app.config import get_settings

    if principal.is_superadmin:
        # Log-only doktrini (ADR-0015 K7 güncellemesi): superadmin veri düzlemine
        # ERİŞEBİLİR (varsayılan şirket); her sorgu audit'e superadmin olarak düşer.
        return principal
    if principal.tenant_slug is None:
        # tsl claim'i olmayan ESKİ token (deploy öncesi oturum) → 401: frontend'in
        # refresh zinciri yeni claim'li token'ı basar, kullanıcı takılmaz.
        raise HTTPException(status_code=401, detail="Oturum yenilenmeli")
    if principal.tenant_slug != get_settings().company:
        registry = getattr(request.app.state, "company_registry", None)
        if registry is not None and registry.has_company(principal.tenant_slug):
            try:
                request.state.wren = registry.service_for(principal.tenant_slug)
                return principal
            except Exception as exc:
                import sys

                print(f"[registry] {principal.tenant_slug} yüklenemedi: {exc}",
                      file=sys.stderr)
        raise HTTPException(
            status_code=403,
            detail="Bu firma için veri düzlemi bu sunucuda yüklü değil",
        )
    return principal
