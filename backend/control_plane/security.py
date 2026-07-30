"""Password hashing + JWT + fingerprint + TOTP (saka-standards 02-authentication).

- Argon2id parola hash.
- Access (kısa) + refresh (uzun) JWT; **FARKLI secret**; her token'da **JTI**.
- **Plane ayrımı:** public ve admin token'ları FARKLI secret çiftleriyle imzalanır —
  public sürecin env'i admin-api'ye geçerli token üretemez (ADR-0015 izolasyonu).
- Device fingerprint = hash(User-Agent + Accept-Language); doğrulama sabit-zamanlı.
- TOTP (RFC 6238, SHA1/30sn) bağımlılıksız — superadmin 2FA (ADR-0015).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from control_plane.config import get_auth_settings

_ph = PasswordHasher()  # Argon2id varsayılan parametreler (OWASP uyumlu)

# Bilinmeyen e-postada da Argon2 koşulur → yanıt süresi hesap varlığını sızdırmaz.
DUMMY_HASH = _ph.hash(secrets.token_urlsafe(16))


# --- Password ------------------------------------------------------------
def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


def needs_rehash(hashed: str) -> bool:
    return _ph.check_needs_rehash(hashed)


# --- Fingerprint ---------------------------------------------------------
def make_fingerprint(user_agent: str, accept_language: str) -> str:
    raw = f"{user_agent}|{accept_language}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def verify_fingerprint(stored: str, current: str) -> bool:
    # Sabit-zamanlı karşılaştırma (timing attack koruması, saka-standards 02).
    return hmac.compare_digest(stored, current)


# --- JWT -----------------------------------------------------------------
def _secrets(plane: str = "public") -> tuple[str, str, str]:
    s = get_auth_settings()
    if plane == "admin":
        access = s.admin_jwt_secret or _dev_secret("admin-access")
        refresh = s.admin_jwt_refresh_secret or _dev_secret("admin-refresh")
        # Yanlış yapılandırma guard'ı: admin secret'ı public ile aynıysa plane
        # izolasyonu fiilen yok demektir — sessizce çalışmaya devam etme.
        if s.admin_jwt_secret and s.admin_jwt_secret in (s.jwt_secret, s.jwt_refresh_secret):
            raise RuntimeError("Admin JWT secret public secret'larla AYNI olamaz (ADR-0015).")
    else:
        access = s.jwt_secret or _dev_secret("access")
        refresh = s.jwt_refresh_secret or _dev_secret("refresh")
    if access == refresh:
        raise RuntimeError("JWT access ve refresh secret AYNI olamaz (saka-standards 02).")
    return access, refresh, s.jwt_algorithm


_DEV_SECRETS: dict[str, str] = {}


def _dev_secret(kind: str) -> str:
    # Yalnız lokal/dev: env verilmemişse süreç-ömrü rastgele secret (restart oturumu düşürür).
    if kind not in _DEV_SECRETS:
        _DEV_SECRETS[kind] = secrets.token_urlsafe(48)
    return _DEV_SECRETS[kind]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def new_jti() -> str:
    return secrets.token_hex(16)


def create_access_token(*, sub: str, tenant_id: str | None, is_superadmin: bool,
                        roles: list[str], jti: str | None = None,
                        plane: str = "public", tenant_slug: str | None = None) -> str:
    access, _, alg = _secrets(plane)
    s = get_auth_settings()
    payload = {
        "sub": sub,
        "tid": tenant_id,          # tenant token'dan türetilir (ADR-0014 Karar 1)
        "tsl": tenant_slug,        # dima company bağı (veri-düzlemi RLS)
        "sa": is_superadmin,       # açık flag (saka-standards 08)
        "roles": roles,
        "jti": jti or new_jti(),
        "typ": "access",
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(seconds=s.access_ttl_seconds)).timestamp()),
    }
    return jwt.encode(payload, access, algorithm=alg)


def create_refresh_token(*, sub: str, family_id: str, jti: str | None = None,
                         plane: str = "public") -> tuple[str, str]:
    """Ham refresh token + jti döner. Ham token istemcide (cookie); DB'de yalnız hash'i tutulur."""
    _, refresh, alg = _secrets(plane)
    s = get_auth_settings()
    token_jti = jti or new_jti()
    payload = {
        "sub": sub,
        "fam": family_id,
        "jti": token_jti,
        "typ": "refresh",
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(seconds=s.refresh_ttl_seconds)).timestamp()),
    }
    return jwt.encode(payload, refresh, algorithm=alg), token_jti


def decode_access_token(token: str, plane: str = "public") -> dict:
    access, _, alg = _secrets(plane)
    return jwt.decode(token, access, algorithms=[alg])


def decode_refresh_token(token: str, plane: str = "public") -> dict:
    _, refresh, alg = _secrets(plane)
    return jwt.decode(token, refresh, algorithms=[alg])


def hash_token(token: str) -> str:
    """Refresh token'ı DB'de saklamak için hash (ham token asla saklanmaz)."""
    return hashlib.sha256(token.encode()).hexdigest()


def new_family_id() -> str:
    return uuid.uuid4().hex


# --- TOTP (RFC 6238; SHA1, 30 sn, 6 hane — authenticator uygulamalarıyla uyumlu) ---
def totp_secret() -> str:
    """Yeni base32 TOTP secret'ı (enrollment)."""
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _totp_code(secret: str, counter: int) -> str:
    pad = "=" * (-len(secret) % 8)
    key = base64.b32decode(secret.upper() + pad)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{code:06d}"


def verify_totp(secret: str, code: str, *, window: int = 1, at: float | None = None) -> bool:
    """±window adım (30 sn) saat kayması toleransıyla sabit-zamanlı doğrulama."""
    if not code or not code.strip().isdigit():
        return False
    counter = int((at if at is not None else time.time()) // 30)
    given = code.strip()
    return any(
        hmac.compare_digest(_totp_code(secret, counter + off), given)
        for off in range(-window, window + 1)
    )


def totp_uri(secret: str, email: str) -> str:
    """Authenticator uygulamasına eklenecek otpauth:// provisioning URI'ı."""
    return f"otpauth://totp/dima:{email}?secret={secret}&issuer=dima"
