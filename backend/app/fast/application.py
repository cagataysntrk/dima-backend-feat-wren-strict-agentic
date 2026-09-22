"""Wren-free Fast-only application factory used by FT-003 proof and future deployment."""

from __future__ import annotations

from fastapi import FastAPI

from app import __version__
from app.fast.ask_service import FastAskService
from app.fast.router import router as fast_router


def create_fast_application(*, service: FastAskService) -> FastAPI:
    app = FastAPI(
        title="Dima Fast Track",
        version=__version__,
    )
    app.state.fast_ask_service = service
    app.include_router(fast_router)
    return app
