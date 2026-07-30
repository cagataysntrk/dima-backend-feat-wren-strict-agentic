"""FastAPI application: HTTP bridge over the Wren semantic SQL engine."""

from __future__ import annotations

import threading
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.auth import router as auth_router
from app.auth.dependencies import get_current_principal
from app.config import get_settings
from app.llm import build_generator
from app.routers import ask, health, query
from app.routers import contracts as contracts_router
from app.routers import conversations as conversations_router
from app.routers import dashboards as dashboards_router
from app.routers import schedules as schedules_router
from app.vqr import VQR
from app.wren_service import WrenService


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.logging_setup import configure_logging

    configure_logging()  # system/app log (ADR-0020) — sessiz-yutma yerine warning
    settings = get_settings()
    # Control-plane (auth) DB: lokal SQLite'ı hazırla; Postgres'te Alembic devralır (ADR-0015).
    from control_plane.audit import replay_spool
    from control_plane.bootstrap import ensure_bootstrap_superadmin
    from control_plane.db import init_db

    # Control-plane şeması (SQLite'ta oluştur; Postgres'te Alembic sahibi) + superadmin seed.
    init_db()
    replay_spool()  # DB-down sırasında spool'lanan bekleyen audit'leri DB'ye boşalt
    from app.contracts import replay_spool as replay_contract_spool
    replay_contract_spool()  # bekleyen contract kanıtlarını DB'ye boşalt (audit deseni)
    ensure_bootstrap_superadmin()
    # ADR-0005: şirket ⊕ sektör paketi ⊕ konu modülleri → wren-project (derlenmiş) + mdl.
    # Önce TenantConfig materializer'ı: admin panelden yazılan sektör/modül seçimi
    # company.yml'e iner (DB kazanır) — compose bu dosyayı okur.
    from app.compose import compose_and_build
    from app.materialize import materialize_tenant_configs

    materialize_tenant_configs(settings)
    compose_and_build(settings)
    app.state.wren = WrenService(
        project_dir=settings.resolved_project_dir(),
        datasource=settings.datasource,
        connection_info=settings.connection_dict(),
        company_slug=settings.company,
    )
    app.state.llm = build_generator(settings)
    # Çok-şirketli runtime v1: varsayılan-dışı tenant'ların projeleri talep üzerine
    # derlenir (require_company → registry). Materializer değişen tenant'ı düşürür.
    from app.company_registry import CompanyRegistry

    app.state.company_registry = CompanyRegistry(settings)
    # Verified Query Repository (A#4): onaylı soru→CubeQuery çiftleri. Postgres'te
    # (verified_query, şirket kapsamlı) — eski JSONL redeploy'da siliniyordu (ADR-0005/0008).
    app.state.vqr = VQR(settings.company)

    # Query Contract deposu (ADR-0010) — kanıt TEK-KAYNAK DB'de (contract_log).
    from app.contracts import ContractStore

    app.state.contracts = ContractStore()

    # Zamanlanmış raporlar (ADR-0011): tanım + koşum durumu (last_run) + bildirim HEPSİ
    # tek-kaynak DB'de (schedule_definition + notification_log) — dosya-state yok (double-fire fix).
    from app.schedules import ScheduleStore, run_due

    app.state.schedules = ScheduleStore(settings.company)
    if settings.scheduler_enabled:
        from app.materialize import materialize_and_recompose

        def _scheduler_loop():
            import time

            while True:
                time.sleep(60)
                try:
                    run_due(app.state)
                except Exception:
                    pass
                try:
                    # Admin panelden gelen tenant sektör/modül değişikliği ≤60 sn'de
                    # diske iner; aktif şirketse yeniden derlenir (TenantConfig).
                    materialize_and_recompose(app.state, settings)
                except Exception as exc:
                    import sys

                    print(f"[materialize] döngü hatası: {exc}", file=sys.stderr)

        threading.Thread(target=_scheduler_loop, daemon=True).start()

    # SOĞUK BAŞLANGIÇ ISITMA (arka plan): ilk soru 12sn beklemesin — şema zenginleştirme
    # (kategorik değer probu) ve e5 embedder yüklemesi startup'ta paralel başlar.
    def _warm(fn):
        threading.Thread(target=fn, daemon=True).start()

    _warm(app.state.wren.schema)
    from app.vqr import _embedder

    _warm(_embedder)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="dima-backend",
        version=__version__,
        description="Wren (dima) semantic SQL engine over HTTP — NL→SQL, validate, execute.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Public: health + auth (login/refresh/logout). Diğer her router korumalıdır —
    # geçerli Bearer access token olmadan hiçbir veri ucu çalışmaz ("dev bypass" YOK).
    app.include_router(health.router)
    app.include_router(auth_router.router)
    _protected = [Depends(get_current_principal)]
    app.include_router(query.router, dependencies=_protected)
    app.include_router(ask.router, dependencies=_protected)
    app.include_router(contracts_router.router, dependencies=_protected)
    app.include_router(schedules_router.router, dependencies=_protected)
    app.include_router(conversations_router.router, dependencies=_protected)
    app.include_router(dashboards_router.router, dependencies=_protected)
    return app


app = create_app()
