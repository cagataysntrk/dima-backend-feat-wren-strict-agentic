"""Canonical liveness/readiness endpoints for the headless Platform."""
from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "product": "dima-metabase-platform",
        "ui": "not_implemented",
    }


def _db_ping() -> tuple[bool, str | None]:
    from sqlalchemy import text
    from control_plane.db import engine

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:  # probe: degrade rather than hide the failure
        return False, str(exc)


@router.get("/health/ready")
def ready(response: Response) -> dict:
    settings = get_settings()
    db_ready, db_error = _db_ping()
    if not db_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    body = {
        "status": "ok" if db_ready else "degraded",
        "control_plane_db_ready": db_ready,
        "canonical_engine": "metabase-metabot",
        "engine_sha": settings.metabase_engine_sha,
        "engine_release": settings.metabase_engine_runtime_tag,
        "engine_digest": settings.metabase_engine_image_digest,
        "native_runtime_configured": bool(settings.metabase_native_base_url.strip()),
        "external_execution": "deferred",
        "ui": "not_implemented",
    }
    if db_error:
        body["db_error"] = db_error
    return body
