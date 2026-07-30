"""Public dima-api auth service — ortak mantık ``control_plane.auth_service``'te.

ADR-0015 Karar 1: login/rotate/logout tek kaynakta (control_plane) → admin_app ile
paylaşılır, drift yok. Bu modül geriye-uyum için re-export eder.
"""

from __future__ import annotations

from control_plane.auth_service import (
    AuthError,
    MfaRequired,
    RateLimited,
    TenantSuspended,
    login,
    logout,
    principal_from_user,
    rotate,
)

__all__ = [
    "AuthError", "MfaRequired", "RateLimited", "TenantSuspended",
    "login", "logout", "principal_from_user", "rotate",
]
