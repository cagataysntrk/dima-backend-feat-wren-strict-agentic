"""dima-admin-api — FastAPI app (superadmin control-plane, ADR-0015).

Ağ izolasyonu deploy katmanında (Cloudflare + statik IP + mTLS, ADR-0015 Karar 4);
uygulama katmanında her /sadmin route'u superadmin-only.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from admin_app import __version__, auth_router
from admin_app.dependencies import get_superadmin_principal
from admin_app.routers import audit as audit_router
from admin_app.routers import (
    clone,
    connections,
    contracts,
    features,
    health,
    interactions,
    notifications,
    packs,
    synonyms,
    tenants,
    users,
)
from control_plane.config import get_auth_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from control_plane.audit import replay_spool
    from control_plane.bootstrap import ensure_bootstrap_superadmin
    from control_plane.db import init_db

    init_db()
    replay_spool()  # DB-down sırasında spool'lanan bekleyen audit'leri DB'ye boşalt
    ensure_bootstrap_superadmin()
    yield


def create_app() -> FastAPI:
    s = get_auth_settings()
    app = FastAPI(
        title="dima-admin-api",
        version=__version__,
        description="dima superadmin control-plane API — tenant/user yönetimi (ADR-0015).",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.admin_cors_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Public: health + admin auth. Diğer her şey superadmin-only.
    app.include_router(health.router)
    app.include_router(auth_router.router)
    protected = [Depends(get_superadmin_principal)]
    app.include_router(tenants.router, dependencies=protected)
    app.include_router(users.router, dependencies=protected)
    app.include_router(features.router, dependencies=protected)
    app.include_router(packs.router, dependencies=protected)
    app.include_router(connections.router, dependencies=protected)
    app.include_router(clone.router, dependencies=protected)
    app.include_router(clone.jobs_router, dependencies=protected)
    app.include_router(clone.overview_router, dependencies=protected)
    app.include_router(synonyms.router, dependencies=protected)
    app.include_router(audit_router.router, dependencies=protected)
    app.include_router(interactions.router, dependencies=protected)
    app.include_router(notifications.router, dependencies=protected)
    app.include_router(contracts.router, dependencies=protected)
    return app


app = create_app()
