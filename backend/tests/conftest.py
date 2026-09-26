"""Canonical Dima Metabase Platform pytest environment.

No global Wren/demo compose fixture exists in the canonical repository. Tests that
need Metabase transport inject deterministic transports explicitly.
"""
from __future__ import annotations

import base64
import os
import tempfile

import pytest

# Isolate the control-plane database before any application module imports it.
os.environ.setdefault(
    "DIMA_DATABASE_URL",
    "sqlite:///" + os.path.join(tempfile.mkdtemp(prefix="dima-cp-"), "control_plane.db"),
)
os.environ.setdefault("DIMA_SUPERADMIN_IP_ALLOWLIST", "testclient")
os.environ.setdefault("DIMA_JWT_SECRET", "test-public-access-secret-0123456789abcdef")
os.environ.setdefault("DIMA_JWT_REFRESH_SECRET", "test-public-refresh-secret-0123456789abcdef")
os.environ.setdefault("DIMA_ADMIN_JWT_SECRET", "test-admin-access-secret-0123456789abcdef")
os.environ.setdefault("DIMA_ADMIN_JWT_REFRESH_SECRET", "test-admin-refresh-secret-0123456789abcdef")
os.environ.setdefault(
    "DIMA_CRED_KEK",
    base64.b64encode(b"test-kek-32-byte-0123456789abcd!").decode(),
)
os.environ.setdefault("DIMA_METABASE_NATIVE_BASE_URL", "")

TEST_USER = {"email": "test@dima.local", "password": "test-parola-123"}
TEST_SUPERADMIN = {"email": "root@dima.local", "password": "root-parola-123"}


def make_tenant_user(
    email: str,
    password: str,
    role_key: str = "owner",
    tenant_slug: str = "test-tenant",
) -> None:
    """Create an isolated control-plane tenant user for HTTP/auth tests."""

    from sqlmodel import Session, select

    from control_plane.db import engine, init_db
    from control_plane.models import Membership, Role, Tenant, User
    from control_plane.security import hash_password

    init_db()
    with Session(engine) as session:
        if session.exec(select(User).where(User.email == email)).first():
            return
        tenant = session.exec(select(Tenant).where(Tenant.slug == tenant_slug)).first()
        if tenant is None:
            tenant = Tenant(slug=tenant_slug, name=tenant_slug)
            session.add(tenant)
            session.commit()
            session.refresh(tenant)
            for key in ("owner", "admin", "analyst", "viewer"):
                session.add(Role(tenant_id=tenant.id, key=key, name=key.capitalize()))
            session.commit()
        role = session.exec(
            select(Role).where(Role.tenant_id == tenant.id, Role.key == role_key)
        ).one()
        user = User(
            tenant_id=tenant.id,
            email=email,
            password_hash=hash_password(password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        session.add(
            Membership(
                tenant_id=tenant.id,
                user_id=user.id,
                role_id=role.id,
            )
        )
        session.commit()


def _ensure_test_users() -> None:
    from sqlmodel import Session, select

    from control_plane.db import engine, init_db
    from control_plane.models import User
    from control_plane.security import hash_password

    make_tenant_user(TEST_USER["email"], TEST_USER["password"])
    init_db()
    with Session(engine) as session:
        if not session.exec(
            select(User).where(User.email == TEST_SUPERADMIN["email"])
        ).first():
            session.add(
                User(
                    email=TEST_SUPERADMIN["email"],
                    password_hash=hash_password(TEST_SUPERADMIN["password"]),
                    is_superadmin=True,
                )
            )
            session.commit()


@pytest.fixture(scope="session")
def client():
    """Authenticated canonical FastAPI TestClient for retained HTTP tests."""

    from fastapi.testclient import TestClient

    from app.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    with TestClient(create_app()) as test_client:
        _ensure_test_users()
        response = test_client.post("/auth/login", json=TEST_USER)
        assert response.status_code == 200, response.text
        test_client.headers["Authorization"] = (
            f"Bearer {response.json()['access_token']}"
        )
        yield test_client
