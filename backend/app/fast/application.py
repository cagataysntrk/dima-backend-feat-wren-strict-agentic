"""Wren-free Fast-only application factory used by Fast Track proofs and deployment."""

from __future__ import annotations

from fastapi import FastAPI

from app import __version__
from app.fast.ask_service import FastAskService
from app.fast.router import router as fast_router
from app.fast.run_manager import FastRunManager
from app.fast.run_router import router as fast_run_router


def create_fast_application(
    *,
    service: FastAskService,
    run_manager: FastRunManager | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Dima Fast Track",
        version=__version__,
    )
    manager = run_manager or FastRunManager(service=service)
    app.state.fast_ask_service = service
    app.state.fast_run_manager = manager
    app.include_router(fast_router)
    app.include_router(fast_run_router)

    @app.on_event("shutdown")
    def _shutdown_fast_runs() -> None:
        manager.shutdown(interrupt=True)

    return app
