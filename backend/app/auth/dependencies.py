"""FastAPI authentication dependencies for the canonical Platform.

Principal identity is derived only from a validated access token. Data/authority
owners apply the central control-plane authorization matrix; no Wren/company
runtime is part of this boundary.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import istek_kimligi
from control_plane.authorize import AuthzError, Principal, authorize
from control_plane.security import decode_access_token, make_fingerprint

bearer_scheme = HTTPBearer(
    auto_error=False,
    bearerFormat="JWT",
    description="Access token returned by /auth/login.",
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
    if principal.tenant_id and not _tenant_active(principal.tenant_id):
        raise HTTPException(status_code=401, detail="Firma hesabı askıya alınmış")
    request.state.principal = principal
    istek_kimligi.ayarla(principal)
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
        with Session(engine) as session:
            tenant = session.get(Tenant, _uuid.UUID(tenant_id))
        active = tenant is not None and tenant.status == "active"
    except Exception:
        # Existing security doctrine: transient control-plane read failure does not
        # silently revoke already-issued sessions.
        active = True
    _tenant_status_cache[tenant_id] = (now, active)
    return active


def require(action: str):
    def dependency(
        principal: Principal = Depends(get_current_principal),
    ) -> Principal:
        try:
            authorize(principal, action, f"data:{action.split(':', 1)[0]}")
        except AuthzError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        return principal

    return dependency
