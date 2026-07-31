"""/sadmin/users — kullanıcı listeleme + oluşturma (superadmin-only).

Tenant kullanıcısı: (tenant_id + role_key) zorunlu → Membership kurulur.
Superadmin: is_superadmin=True, tenant'sız.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from control_plane import audit
from control_plane.db import get_session
from control_plane.models import Membership, Role, Tenant, User
from control_plane.security import hash_password

from admin_app.schemas import SAUserCreate, SAUserOut

router = APIRouter(prefix="/sadmin/users", tags=["sadmin-users"])


def _out(u: User) -> SAUserOut:
    return SAUserOut(
        id=str(u.id), email=u.email,
        tenant_id=str(u.tenant_id) if u.tenant_id else None,
        is_superadmin=u.is_superadmin,
    )


def _parse_uuid(value: str, what: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Geçersiz {what}")


@router.get("", response_model=list[SAUserOut])
def list_users(tenant_id: str | None = None,
               session: Session = Depends(get_session)) -> list[SAUserOut]:
    stmt = select(User)
    if tenant_id:
        stmt = stmt.where(User.tenant_id == _parse_uuid(tenant_id, "tenant_id"))
    return [_out(u) for u in session.exec(stmt).all()]


@router.post("", response_model=SAUserOut, status_code=201)
def create_user(body: SAUserCreate, request: Request,
                session: Session = Depends(get_session)) -> SAUserOut:
    if session.exec(select(User).where(User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="Bu e-posta zaten kayıtlı")
    ip = request.client.host if request.client else None
    principal = getattr(request.state, "principal", None)

    if body.is_superadmin:
        user = User(email=body.email, password_hash=hash_password(body.password),
                    is_superadmin=True)
        session.add(user)
        session.commit()
        session.refresh(user)
        audit.record(principal, "user_create", nl_question=f"superadmin: {user.email}", ip=ip)
        return _out(user)

    if not body.tenant_id:
        raise HTTPException(status_code=400, detail="Tenant kullanıcısı için tenant_id gerekli")
    # Faz 2d (31 Temmuz 2026): owner + admin/analyst (ölçü-onay reviewer rolü için DAR
    # KAPSAMLI açılış — bkz. tenants._DEFAULT_ROLES). viewer hâlâ ürünleştirilmedi (400) —
    # rol matrisinin GENEL açılışı hâlâ ertelenir, yalnız bu somut kullanım durumu aktif.
    if body.role_key not in ("owner", "admin", "analyst"):
        raise HTTPException(
            status_code=400,
            detail="Bu fazda yalnız 'owner', 'admin' ya da 'analyst' rolü kullanılabilir")
    tid = _parse_uuid(body.tenant_id, "tenant_id")
    if not session.get(Tenant, tid):
        raise HTTPException(status_code=404, detail="Tenant bulunamadı")
    role = session.exec(
        select(Role).where(Role.tenant_id == tid, Role.key == body.role_key)
    ).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Rol bulunamadı: {body.role_key}")

    user = User(tenant_id=tid, email=body.email, password_hash=hash_password(body.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    session.add(Membership(tenant_id=tid, user_id=user.id, role_id=role.id))
    session.commit()
    audit.record(principal, "user_create",
                 nl_question=f"user: {user.email} ({body.role_key})", ip=ip)
    return _out(user)
