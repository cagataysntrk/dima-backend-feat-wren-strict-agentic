"""Admin auth: /auth/login, /auth/refresh, /auth/logout (superadmin-only).

Ortak servis ``control_plane.auth_service``. Login yalnız superadmin'e izin verir —
tenant kullanıcısı admin plane'e giremez.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import Session

from admin_app.dependencies import ADMIN_COOKIE, get_fingerprint
from admin_app.schemas import LoginRequest, TokenResponse
from control_plane import auth_service
from control_plane.config import get_auth_settings
from control_plane.db import get_session

router = APIRouter(prefix="/auth", tags=["admin-auth"])


def _set_cookie(response: Response, token: str) -> None:
    s = get_auth_settings()
    response.set_cookie(
        key=ADMIN_COOKIE, value=token, httponly=True, secure=s.cookie_secure,
        samesite=s.admin_cookie_samesite,  # canlı admin-api + lokal UI → "none" (bkz. config)
        path="/auth", domain=s.cookie_domain or None,
        max_age=s.refresh_ttl_seconds,
    )


def _clear_cookie(response: Response) -> None:
    s = get_auth_settings()
    response.delete_cookie(key=ADMIN_COOKIE, path="/auth", domain=s.cookie_domain or None)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, response: Response,
          session: Session = Depends(get_session)) -> TokenResponse:
    ip = request.client.host if request.client else None
    try:
        # require_superadmin: token/cookie ÜRETİLMEDEN reddedilir (yarım oturum kalmaz).
        access, refresh_raw, _user = auth_service.login(
            session, body.email, body.password, get_fingerprint(request), ip,
            otp=body.otp, require_superadmin=True, plane="admin")
    except auth_service.RateLimited:
        raise HTTPException(status_code=429, detail="Çok fazla deneme — bir süre bekleyin")
    except auth_service.MfaRequired:
        # Yalnız doğru paroladan sonra döner; frontend OTP alanını açar.
        raise HTTPException(status_code=401, detail="OTP gerekli")
    except auth_service.AuthError:
        raise HTTPException(status_code=401, detail="E-posta veya parola hatalı")
    _set_cookie(response, refresh_raw)
    return TokenResponse(access_token=access)


@router.post("/refresh")
def refresh(request: Request, response: Response,
            session: Session = Depends(get_session)) -> dict:
    raw = request.cookies.get(ADMIN_COOKIE)
    if not raw:
        raise HTTPException(status_code=401, detail="Refresh token bulunamadı")
    try:
        access, new_raw = auth_service.rotate(session, raw, get_fingerprint(request),
                                              plane="admin")
    except auth_service.AuthError:
        _clear_cookie(response)
        raise HTTPException(status_code=401, detail="Oturum yenilenemedi")
    _set_cookie(response, new_raw)
    return {"access_token": access, "token_type": "bearer"}


@router.post("/logout")
def logout(request: Request, response: Response,
           session: Session = Depends(get_session)) -> dict:
    ip = request.client.host if request.client else None
    auth_service.logout(session, request.cookies.get(ADMIN_COOKIE), ip)
    _clear_cookie(response)
    return {"ok": True}
