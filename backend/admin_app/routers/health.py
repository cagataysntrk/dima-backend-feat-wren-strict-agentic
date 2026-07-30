"""Health check (public): liveness + DB readiness."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Liveness: süreç ayakta mı? Her zaman 200 (bağımlılık kontrolü YAPMAZ)."""
    return {"status": "ok", "service": "dima-admin-api"}


@router.get("/health/ready")
def ready(response: Response) -> dict:
    """Readiness: control-plane DB (auth/log merkezi) erişilebilir mi? Down ise
    HTTP 503 → orkestrasyon down'ı yakalar (sessiz 200 dönmez)."""
    from sqlalchemy import text

    from control_plane.db import engine

    db_ready, db_error = True, None
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 — probe: her hatayı degraded say
        db_ready, db_error = False, str(exc)

    if not db_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    body = {
        "status": "ok" if db_ready else "degraded",
        "service": "dima-admin-api",
        "db_ready": db_ready,
    }
    if db_error:
        body["db_error"] = db_error
    return body
