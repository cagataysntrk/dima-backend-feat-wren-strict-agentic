"""Bootstrap helpers — ilk superadmin seed'i (app + admin_app ortak).

Yalnız env verilmiş ve DB'de superadmin yoksa oluşturur. İdempotent.
"""

from __future__ import annotations

from sqlmodel import Session, select

from control_plane.config import get_auth_settings
from control_plane.db import engine
from control_plane.models import User
from control_plane.security import hash_password

_DEFAULT_ROLE_KEYS = ("owner", "admin", "analyst", "viewer")


def ensure_bootstrap_superadmin() -> None:
    s = get_auth_settings()
    if not (s.bootstrap_superadmin_email and s.bootstrap_superadmin_password):
        return
    with Session(engine) as session:
        if session.exec(select(User).where(User.is_superadmin.is_(True))).first():
            return
        session.add(User(
            email=s.bootstrap_superadmin_email,
            password_hash=hash_password(s.bootstrap_superadmin_password),
            is_superadmin=True,
        ))
        session.commit()
