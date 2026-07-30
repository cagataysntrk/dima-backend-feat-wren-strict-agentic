"""Admin dependencies: superadmin principal (her zaman zorunlu).

Admin_app her zaman Bearer token + ``sa`` claim ister (ADR-0015: admin plane hiç
auth'suz kalmaz). Token'lar admin plane'in KENDİ secret'ıyla çözülür — public
plane'de basılmış token burada geçersizdir.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from control_plane.authorize import Principal
from control_plane.security import decode_access_token, make_fingerprint

ADMIN_COOKIE = "dima_admin_refresh"  # public cookie ile çakışmasın (localhost port-agnostik)

# OpenAPI security scheme (Swagger "Authorize") — ADMIN plane'in KENDİ token'ı:
# public /auth/login token'ı burada GEÇERSİZDİR (ayrı secret çifti, ADR-0015).
bearer_scheme = HTTPBearer(
    auto_error=False,
    bearerFormat="JWT",
    description="Admin access token — admin-api /auth/login yanıtındaki access_token.",
)


def get_fingerprint(request: Request) -> str:
    return make_fingerprint(
        request.headers.get("user-agent", ""),
        request.headers.get("accept-language", ""),
    )


def get_superadmin_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Principal:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Kimlik doğrulaması gerekli")
    try:
        payload = decode_access_token(credentials.credentials, plane="admin")
    except Exception:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token")
    if payload.get("typ") != "access":
        raise HTTPException(status_code=401, detail="Geçersiz token tipi")
    if not payload.get("sa"):
        raise HTTPException(status_code=403, detail="Superadmin yetkisi gerekli")
    principal = Principal(
        user_id=payload["sub"],
        tenant_id=None,
        is_superadmin=True,
        roles=payload.get("roles", []),
    )
    request.state.principal = principal  # audit yazıcıları buradan okur
    return principal
