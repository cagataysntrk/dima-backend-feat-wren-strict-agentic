"""Lokal demo fixture — YALNIZ geliştirme (canlıda çalıştırılmaz).

İdempotent: tenant/kullanıcı zaten varsa atlar, ASLA duplicate oluşturmaz.
Çalıştır: ``PYTHONPATH=. .venv/bin/python -m control_plane.cli seed-demo``
"""

from __future__ import annotations

from sqlmodel import Session, select

from control_plane.db import engine, init_db
from control_plane.models import Membership, Role, Tenant, User
from control_plane.security import hash_password

# Local dev fixture parolası (owner kullanıcıları). Yalnız geliştirme.
DEMO_OWNER_PASSWORD = "dima-demo-1234"

DEMO_TENANTS: list[tuple[str, str]] = [
    ("demo-boyahane", "Demo Boyahane"),
    ("demo-geri-donusum", "Demo Geri Dönüşüm"),
]

_DEFAULT_ROLES = ("owner",)  # bu fazda tek rol (rol matrisi uykuda)


def _ensure_tenant(session: Session, slug: str, name: str) -> Tenant:
    tenant = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
    if tenant:
        print(f"tenant zaten var:   {slug}")
        return tenant
    tenant = Tenant(slug=slug, name=name)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    for key in _DEFAULT_ROLES:
        session.add(Role(tenant_id=tenant.id, key=key, name=key.capitalize()))
    session.commit()
    print(f"tenant oluşturuldu: {slug}")
    return tenant


def _ensure_owner(session: Session, tenant: Tenant, email: str) -> None:
    if session.exec(select(User).where(User.email == email)).first():
        print(f"owner zaten var:    {email}")
        return
    user = User(tenant_id=tenant.id, email=email,
                password_hash=hash_password(DEMO_OWNER_PASSWORD))
    session.add(user)
    session.commit()
    session.refresh(user)
    owner_role = session.exec(
        select(Role).where(Role.tenant_id == tenant.id, Role.key == "owner")
    ).first()
    session.add(Membership(tenant_id=tenant.id, user_id=user.id, role_id=owner_role.id))
    session.commit()
    print(f"owner oluşturuldu:  {email}  (parola: {DEMO_OWNER_PASSWORD})")


def seed_demo() -> int:
    """2 demo firması + owner kullanıcılarını (idempotent) oluşturur."""
    init_db()  # SQLite'ta tabloları kurar; Postgres'te Alembic sahibi → no-op.
    with Session(engine) as session:
        for slug, name in DEMO_TENANTS:
            tenant = _ensure_tenant(session, slug, name)
            _ensure_owner(session, tenant, f"{slug}@usedima.com")
    print(f"seed-demo tamam. (backend: {engine.url.get_backend_name()})")
    return 0
