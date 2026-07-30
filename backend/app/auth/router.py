"""Auth endpoints: /auth/login, /auth/refresh, /auth/logout, /auth/me.

Refresh token HTTP-only cookie'de (saka-standards 02): JS erişemez. path="/" —
frontend rewrite-proxy arkasında same-origin olduğundan (ADR-0012 alternatifi) Next
middleware cookie'yi okuyabilsin ve her istekte gönderilsin. Access token gövdede döner
(frontend memory'de tutar).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import Session

from app.auth import service
from app.auth.dependencies import get_current_principal, get_fingerprint
from app.auth.schemas import LoginRequest, MeResponse, TokenResponse, UserOut
from control_plane.authorize import Principal, permissions_for
from control_plane.config import get_auth_settings
from control_plane.db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    s = get_auth_settings()
    response.set_cookie(
        key=s.cookie_name,
        value=token,
        httponly=True,
        secure=s.cookie_secure,
        samesite="lax",
        path="/",
        domain=s.cookie_domain or None,
        max_age=s.refresh_ttl_seconds,
    )


def _clear_refresh_cookie(response: Response) -> None:
    s = get_auth_settings()
    response.delete_cookie(key=s.cookie_name, path="/", domain=s.cookie_domain or None)


def _client_ips(request: Request) -> list[str]:
    """Aday istemci IP'leri: doğrudan bağlantı + (güvenilir proxy varsa) X-Forwarded-For."""
    ips = [request.client.host] if request.client else []
    if get_auth_settings().trust_forwarded_for:
        xff = request.headers.get("x-forwarded-for", "")
        ips += [p.strip() for p in xff.split(",") if p.strip()]
    return ips


def _superadmin_ip_ok(request: Request) -> bool:
    allow = get_auth_settings().superadmin_ip_list()
    return bool(allow) and any(ip in allow for ip in _client_ips(request))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, response: Response,
          session: Session = Depends(get_session)) -> TokenResponse:
    fp = get_fingerprint(request)
    ip = request.client.host if request.client else None
    try:
        # Superadmin public plane'e YALNIZ statik IP allowlist'inden girebilir
        # (ADR-0015 K7: log-only + IP kapısı). Liste boş = fail-closed. Tenant
        # kullanıcıları etkilenmez. İçeri girince her eylem superadmin damgasıyla
        # audit'lenir; ayrıca rate limit + (prod'da) TOTP geçerlidir.
        access, refresh_raw, user = service.login(
            session, body.email, body.password, fp, ip, otp=body.otp,
            allow_superadmin=_superadmin_ip_ok(request))
    except service.RateLimited:
        raise HTTPException(status_code=429, detail="Çok fazla deneme — bir süre bekleyin")
    except service.MfaRequired:
        raise HTTPException(status_code=401, detail="OTP gerekli")
    except service.TenantSuspended:
        # Yalnız doğru paroladan sonra düşer — gizlenecek bilgi değil, yol gösterilir.
        raise HTTPException(
            status_code=403,
            detail="Firma hesabınız askıya alınmış — lütfen yetkilinizle iletişime geçin",
        )
    except service.AuthError:
        raise HTTPException(status_code=401, detail="E-posta veya parola hatalı")
    _set_refresh_cookie(response, refresh_raw)
    principal = service.principal_from_user(session, user)
    return TokenResponse(
        access_token=access,
        user=UserOut(
            id=str(user.id),
            email=user.email,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            is_superadmin=user.is_superadmin,
            roles=principal.roles,
            permissions=permissions_for(principal),
        ),
    )


@router.post("/refresh")
def refresh(request: Request, response: Response,
            session: Session = Depends(get_session)) -> dict:
    s = get_auth_settings()
    raw = request.cookies.get(s.cookie_name)
    if not raw:
        raise HTTPException(status_code=401, detail="Refresh token bulunamadı")
    try:
        access, new_raw = service.rotate(session, raw, get_fingerprint(request))
    except service.AuthError:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Oturum yenilenemedi")
    _set_refresh_cookie(response, new_raw)
    return {"access_token": access, "token_type": "bearer"}


@router.post("/logout")
def logout(request: Request, response: Response,
           session: Session = Depends(get_session)) -> dict:
    s = get_auth_settings()
    ip = request.client.host if request.client else None
    service.logout(session, request.cookies.get(s.cookie_name), ip)
    _clear_refresh_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=MeResponse)
def me(principal: Principal = Depends(get_current_principal)) -> MeResponse:
    return MeResponse(
        user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        is_superadmin=principal.is_superadmin,
        roles=principal.roles,
        branch_ids=principal.branch_ids,
        permissions=permissions_for(principal),
    )
