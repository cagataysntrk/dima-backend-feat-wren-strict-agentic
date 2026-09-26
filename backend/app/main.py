"""Canonical pre-UI Dima Metabase Platform FastAPI shell."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.auth import router as auth_router
from app.config import get_settings
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.logging_setup import configure_logging, get_logger
    from control_plane import models as _control_plane_models  # noqa: F401
    from control_plane.bootstrap import ensure_bootstrap_superadmin
    from control_plane.db import init_db

    configure_logging()
    log = get_logger("platform")
    settings = get_settings()

    # Canonical durable authority database.
    init_db()
    ensure_bootstrap_superadmin()

    # P14/P16 owner graph is instantiated once for later headless product contracts.
    from app.v3.claim_lineage import ClaimLineageStore
    from app.v3.research_product import ResearchAskOrchestrator
    from app.v3.research_store import ResearchSessionStore

    research_store = ResearchSessionStore()
    app.state.research_store = research_store
    app.state.research_product = ResearchAskOrchestrator(store=research_store)
    app.state.claim_lineage = ClaimLineageStore(research_store=research_store)
    app.state.research_exploration = None

    # Native Metabot/Metabase is the only analytical engine. No Wren fallback exists.
    if settings.metabase_native_base_url.strip():
        from app.v3.research_exploration import (
            NativeResearchExploration,
            ResearchExplorationStore,
        )
        from app.v3.research_native_gateway import (
            NativeResearchMaterialExecutor,
            NativeSubjectSessionProvider,
        )
        from app.v3.substrate.metabase.native_models import NativeEngineIdentity

        identity = NativeEngineIdentity(
            engine_sha=settings.metabase_engine_sha,
            upstream_base_sha=settings.metabase_engine_upstream_sha,
            runtime_tag=settings.metabase_engine_runtime_tag,
            runtime_image_digest=settings.metabase_engine_image_digest,
            build_identity=settings.metabase_engine_build_identity,
            runtime_image_identity=settings.metabase_engine_image_identity,
        )
        subjects = NativeSubjectSessionProvider(
            base_url=settings.metabase_native_base_url,
            expected_identity=identity,
        )
        app.state.research_product.configure_native_runtime(
            bridge_factory=subjects,
            material_executor=NativeResearchMaterialExecutor(
                subject_provider=subjects,
                store=research_store,
                expected_identity=identity,
            ),
        )
        app.state.research_exploration = NativeResearchExploration(
            research_store=research_store,
            subject_provider=subjects,
            material_store=ResearchExplorationStore(),
        )

    log.info(
        "canonical Platform ready: engine=%s sha=%s ui=not-implemented",
        "metabase-metabot",
        settings.metabase_engine_sha,
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Dima Metabase Platform",
        version=__version__,
        description=(
            "Headless Dima organizational intelligence layer over the canonical "
            "Metabase / Metabot analytical engine."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(auth_router.router)
    return app


app = create_app()
