"""Liveness / readiness endpoints (+ kimlikli /features)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Liveness: süreç ayakta mı? Her zaman 200 (bağımlılık kontrolü YAPMAZ)."""
    return {"status": "ok"}


def _db_ping() -> tuple[bool, str | None]:
    """Control-plane DB'ye hafif bir SELECT 1 — bağlantı canlı mı?"""
    from sqlalchemy import text

    from control_plane.db import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:  # noqa: BLE001 — probe: her hatayı degraded say
        return False, str(exc)


def _features_principal():
    # İç import: health router'ı auth modülünden bağımsız import edilebilir kalsın.
    from app.auth.dependencies import get_current_principal

    return Depends(get_current_principal)


@router.get("/features")
def features(request: Request, principal=_features_principal()) -> dict:
    """Etkin özellik bayrakları (ADR-0009): fabrika ayarı (sektör ⊕ şirket YAML)
    + admin panel override'ları, PRINCIPAL'a özel çözülür (en spesifik kazanır).
    Client login sonrası okur; alpha/beta aşamaları rozetle gösterilir."""
    from app.config import get_settings
    from app.features import resolve_for

    return {"features": resolve_for(get_settings(), principal)}


@router.get("/health/ready")
def ready(request: Request, response: Response) -> dict:
    """Readiness: MDL derlenmiş VE control-plane DB erişilebilir olduğunda hazır.
    Hazır değilse HTTP 503 döner (load balancer/orkestrasyon trafiği yönlendirmesin;
    prod'da Postgres down artık sessizce 200 dönmez)."""
    service = request.app.state.wren
    mdl_ready = service.mdl_path.exists()
    db_ready, db_error = _db_ping()
    ok = mdl_ready and db_ready
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    body = {
        "status": "ok" if ok else "degraded",
        "mdl": str(service.mdl_path),
        "mdl_ready": mdl_ready,
        "db_ready": db_ready,
    }
    if db_error:
        body["db_error"] = db_error
    # 🔴 `Ö5` — GUARD DÜŞME ORANI. Sağlık yüzeyinde çünkü bu bir **iş kaydı değil sağlık
    # sinyalidir**: geçmişe dönük sorgulanması değil, ŞİMDİ görünmesi gerekir.
    # ⚠ `status`'ü **etkilemez** — anlatının soğuması bir kesinti değildir; sistem doğru
    # cevap vermeye devam eder. Alarmı hazır-değil saymak, bir üslup sorununu bir
    # kullanılabilirlik sorunu gibi raporlardı. *Bir sinyali yanlış şiddette çalmak, onu
    # susturmanın bir başka yoludur.*
    try:
        from app.guard_alarmi import durum as _guard_durum

        body["guard"] = _guard_durum()
    except Exception:                                       # noqa: BLE001
        pass
    return body
