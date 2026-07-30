"""Control-plane database engine + session (SQLModel).

Postgres (prod) veya SQLite (lokal/demo). Migration sahibi admin-api'dir (ADR-0015
Karar 3); ``create_all`` yalnız SQLite/lokal kolaylığı içindir, Postgres'te Alembic
kullanılır.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from control_plane.config import get_auth_settings

_settings = get_auth_settings()
_db_url = _settings.effective_database_url()
_is_sqlite = _db_url.startswith("sqlite")

engine = create_engine(
    _db_url,
    echo=False,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
)


def init_db() -> None:
    """Lokal/SQLite kolaylığı: tabloları oluştur. Postgres'te Alembic devralır."""
    if _is_sqlite:
        # logs/ klasörü zaten var; SQLite dosyası orada yaşar.
        SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: istek başına bir Session."""
    with Session(engine) as session:
        yield session
