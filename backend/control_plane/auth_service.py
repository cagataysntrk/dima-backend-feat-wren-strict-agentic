"""Shared auth service: login, refresh rotation (+reuse detection), logout.

ADR-0015 Karar 1: ortak kod ``control_plane``'de → hem public ``app`` hem ``admin_app``
buradan kullanır (drift yok). saka-standards 02: rotation + reuse + fingerprint.
Day-1 store = Postgres/SQLite (Redis sonra — bilinçli sapma).

Plane ayrımı: her çağrı ``plane`` ("public" | "admin") taşır — token'lar plane'e özel
secret'la imzalanır/çözülür (ADR-0015 izolasyonu). Public plane superadmin girişini
REDDeder (superadmin yalnız IP+mTLS arkasındaki admin plane'den girer).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlmodel import Session, col, select

from control_plane.authorize import Principal
from control_plane.config import get_auth_settings
from control_plane.models import AuditLog, Membership, RefreshToken, Role, Tenant, User
from control_plane.ratelimit import login_limiter
from control_plane.security import (
    DUMMY_HASH,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_token,
    new_family_id,
    verify_fingerprint,
    verify_password,
    verify_totp,
)


class AuthError(Exception):
    """Kimlik/oturum reddi → router 401'e çevirir. Mesaj kullanıcıya sızmaz (generic)."""


class RateLimited(AuthError):
    """Pencere içinde çok fazla başarısız deneme → router 429'a çevirir."""


class MfaRequired(AuthError):
    """Parola doğru ama TOTP kodu gerekli → router bunu ayırt edip OTP ister.

    Yalnız DOĞRU paroladan sonra fırlatılır — parola bilmeyen saldırgana hesabın
    MFA'lı olduğu sızmaz.
    """


class TenantSuspended(AuthError):
    """Firma hesabı askıda → router 403 + açık mesaj döner (gizlenecek bilgi değil;
    kullanıcı desteğe başvurmalı). Yalnız DOĞRU paroladan sonra fırlatılır."""


def _check_tenant_active(session: Session, user: User) -> None:
    if not user.tenant_id:
        return  # superadmin tenant'sız
    tenant = session.get(Tenant, user.tenant_id)
    if tenant is None or tenant.status != "active":
        raise TenantSuspended("tenant suspended")


def _now() -> datetime:
    return datetime.utcnow()


def principal_from_user(session: Session, user: User) -> Principal:
    if user.is_superadmin:
        return Principal(user_id=str(user.id), tenant_id=None, is_superadmin=True,
                         roles=["superadmin"])
    memberships = session.exec(select(Membership).where(Membership.user_id == user.id)).all()
    role_ids = {m.role_id for m in memberships}
    roles = (
        [r.key for r in session.exec(select(Role).where(col(Role.id).in_(role_ids))).all()]
        if role_ids else []
    )
    branch_ids = [str(m.branch_id) for m in memberships if m.branch_id]
    tenant = session.get(Tenant, user.tenant_id) if user.tenant_id else None
    return Principal(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        is_superadmin=False,
        roles=roles,
        branch_ids=branch_ids,
        tenant_slug=tenant.slug if tenant else None,
    )


def _issue_tokens(session: Session, user: User, fingerprint: str | None,
                  plane: str) -> tuple[str, str]:
    s = get_auth_settings()
    principal = principal_from_user(session, user)
    family = new_family_id()
    refresh_raw, _ = create_refresh_token(sub=str(user.id), family_id=family, plane=plane)
    session.add(RefreshToken(
        user_id=user.id,
        family_id=uuid.UUID(family),
        token_hash=hash_token(refresh_raw),
        fingerprint=fingerprint,
        expires_at=_now() + timedelta(seconds=s.refresh_ttl_seconds),
    ))
    access = create_access_token(
        sub=str(user.id),
        tenant_id=principal.tenant_id,
        is_superadmin=user.is_superadmin,
        roles=principal.roles,
        plane=plane,
        tenant_slug=principal.tenant_slug,
    )
    return access, refresh_raw


def _audit_security(action: str, *, ip: str | None, detail: str | None = None) -> None:
    """Güvenlik olayını (best-effort) audit'e yaz — auth akışını ASLA bloklamaz.
    audit.record durable spool'a düşer (kayıp yok); logging hatası login'i kırmaz."""
    try:
        from control_plane import audit

        audit.record(None, action, ip=ip, nl_question=detail)
    except Exception:  # noqa: BLE001 — güvenlik telemetrisi auth erişilebilirliğinden önce gelmez
        pass


def login(session: Session, email: str, password: str, fingerprint: str | None,
          ip: str | None = None, *, otp: str | None = None,
          allow_superadmin: bool = True, require_superadmin: bool = False,
          plane: str = "public") -> tuple[str, str, User]:
    s = get_auth_settings()
    email_key = f"{plane}:{(email or '').strip().lower()}"
    ip_key = f"{plane}:ip:{ip or '-'}"
    if login_limiter.blocked(email_key) or login_limiter.blocked(ip_key):
        # brute-force kapısı: engellenen deneme de audit'e düşer (saldırı görünürlüğü).
        _audit_security("rate_limited", ip=ip, detail=f"email={email_key}")
        raise RateLimited("too many attempts")

    def _fail(reason: str = "bad_credentials") -> AuthError:
        login_limiter.failure(email_key)
        login_limiter.failure(ip_key)
        _audit_security("login_failed", ip=ip, detail=f"email={email_key} reason={reason}")
        return AuthError("invalid credentials")

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        # Timing-safe: bilinmeyen e-postada da Argon2 koşulur (hesap-enumerasyonu yok).
        verify_password(password, DUMMY_HASH)
        raise _fail()
    if user.status != "active" or not verify_password(password, user.password_hash):
        raise _fail()

    # Plane kapıları — parola doğrulandıktan sonra bile GENERIC redle döner
    # (yanlış plane'i yoklayan saldırgana hesap türü sızmaz).
    if user.is_superadmin and not allow_superadmin:
        raise _fail()
    if require_superadmin and not user.is_superadmin:
        raise _fail()

    # Firma askıda mı? (Yalnız doğru paroladan sonra — açık 403 mesajı döner.)
    _check_tenant_active(session, user)

    # MFA: secret'ı olan HERKESTE doğrulanır; admin plane'de bayrak açıksa
    # secret'sız superadmin hiç giremez (ADR-0015: 2FA zorunlu).
    if plane == "admin" and s.require_superadmin_mfa and not user.mfa_secret:
        _audit_security("mfa_enrollment_required", ip=ip, detail=f"user={user.id}")
        raise AuthError("mfa enrollment required")
    if user.mfa_secret:
        if not otp:
            raise MfaRequired("otp required")
        if not verify_totp(user.mfa_secret, otp):
            raise _fail("mfa_invalid")

    login_limiter.reset(email_key)
    login_limiter.reset(ip_key)
    access, refresh_raw = _issue_tokens(session, user, fingerprint, plane)
    session.add(AuditLog(
        tenant_id=user.tenant_id, actor_user_id=user.id,
        actor_kind="superadmin" if user.is_superadmin else "user",
        action="login", ip=ip,
    ))
    session.commit()
    return access, refresh_raw, user


def _revoke_family(session: Session, family_id: uuid.UUID) -> None:
    rows = session.exec(
        select(RefreshToken).where(
            RefreshToken.family_id == family_id,
            col(RefreshToken.revoked_at).is_(None),
        )
    ).all()
    for r in rows:
        r.revoked_at = _now()
        session.add(r)
    session.commit()


def rotate(session: Session, raw_refresh: str, fingerprint: str | None,
           plane: str = "public") -> tuple[str, str]:
    s = get_auth_settings()
    try:
        payload = decode_refresh_token(raw_refresh, plane=plane)
    except Exception as exc:  # invalid signature / expired
        raise AuthError("invalid refresh token") from exc
    if payload.get("typ") != "refresh":
        raise AuthError("wrong token type")

    row = session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_refresh))
    ).first()
    if not row or row.revoked_at is not None:
        raise AuthError("token not found or revoked")
    if row.expires_at < _now():
        raise AuthError("refresh token expired")

    # Family mutlak ömrü: rotation her seferinde 7 günü tazeler ama oturum
    # sonsuza kayamaz — ilk token'dan itibaren üst sınır.
    first = session.exec(
        select(RefreshToken)
        .where(RefreshToken.family_id == row.family_id)
        .order_by(col(RefreshToken.issued_at).asc())
    ).first()
    if first and _now() - first.issued_at > timedelta(seconds=s.refresh_family_max_seconds):
        _revoke_family(session, row.family_id)
        raise AuthError("session lifetime exceeded")

    if row.is_used:
        # Paralel sekme hoşgörüsü: halef token grace penceresi içinde üretildiyse
        # bu meşru bir yarıştır (iki sekme aynı anda refresh attı) — hırsızlık değil.
        successor = session.exec(
            select(RefreshToken)
            .where(
                RefreshToken.family_id == row.family_id,
                col(RefreshToken.issued_at) > row.issued_at,
            )
            .order_by(col(RefreshToken.issued_at).asc())
        ).first()
        in_grace = (
            successor is not None
            and _now() - successor.issued_at <= timedelta(seconds=s.refresh_grace_seconds)
        )
        if not in_grace:
            # REUSE DETECTION: kullanılmış token pencere dışında geldi → tüm family iptal.
            _revoke_family(session, row.family_id)
            _audit_security("token_reuse", ip=None, detail=f"family={row.family_id} user={row.user_id}")
            raise AuthError("token reuse detected")

    if row.fingerprint and fingerprint and not verify_fingerprint(row.fingerprint, fingerprint):
        raise AuthError("device mismatch")

    user = session.get(User, row.user_id)
    if not user or user.status != "active":
        raise AuthError("user inactive")
    # Askıya alınan firmanın oturumu YENİLENMEZ → frontend refresh'i düşer,
    # kullanıcı login'e yönlenir (auto-logout akışı).
    _check_tenant_active(session, user)

    row.is_used = True
    session.add(row)

    new_raw, _ = create_refresh_token(sub=str(user.id), family_id=row.family_id.hex,
                                      plane=plane)
    session.add(RefreshToken(
        user_id=user.id,
        family_id=row.family_id,
        token_hash=hash_token(new_raw),
        fingerprint=fingerprint,
        expires_at=_now() + timedelta(seconds=s.refresh_ttl_seconds),
    ))
    principal = principal_from_user(session, user)
    access = create_access_token(
        sub=str(user.id), tenant_id=principal.tenant_id,
        is_superadmin=user.is_superadmin, roles=principal.roles, plane=plane,
        tenant_slug=principal.tenant_slug,
    )
    session.commit()
    return access, new_raw


def logout(session: Session, raw_refresh: str | None, ip: str | None = None) -> None:
    if not raw_refresh:
        return
    row = session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_refresh))
    ).first()
    if not row:
        return
    # Tüm family iptal: logout "bu oturumu bitir" demektir — rotation zincirinde
    # sarkan (henüz kullanılmamış) kardeş token da ölmeli.
    _revoke_family(session, row.family_id)
    user = session.get(User, row.user_id)
    session.add(AuditLog(
        tenant_id=user.tenant_id if user else None,
        actor_user_id=row.user_id,
        actor_kind="superadmin" if user and user.is_superadmin else "user",
        action="logout", ip=ip,
    ))
    session.commit()
