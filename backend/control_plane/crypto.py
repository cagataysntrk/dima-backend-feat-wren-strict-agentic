"""Müşteri DB kimlik bilgisi şifrelemesi (ADR-0017; upcyman encryption.util deseni).

AES-256-GCM: her şifrelemede rastgele 12 baytlık nonce; blob = nonce || ciphertext+tag.
KEK yalnız admin-api ortamında yaşar (``DIMA_CRED_KEK``, base64 32 bayt) — public
süreç ele geçse bile sırlar çözülemez (control-plane-sema.md garanti #4).
"""

from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NONCE_LEN = 12


class CredKeyError(RuntimeError):
    """KEK eksik/bozuk — sır yazılamaz/çözülemez (fail-closed)."""


def _key(kek_b64: str) -> bytes:
    if not kek_b64.strip():
        raise CredKeyError("DIMA_CRED_KEK tanımlı değil")
    try:
        key = base64.b64decode(kek_b64.strip(), validate=True)
    except Exception as exc:
        raise CredKeyError("DIMA_CRED_KEK base64 çözülemedi") from exc
    if len(key) != 32:
        raise CredKeyError("DIMA_CRED_KEK 32 bayt olmalı (base64 öncesi)")
    return key


def encrypt_secret(plaintext: str, kek_b64: str) -> bytes:
    nonce = os.urandom(_NONCE_LEN)
    ct = AESGCM(_key(kek_b64)).encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ct


def decrypt_secret(blob: bytes, kek_b64: str) -> str:
    if len(blob) <= _NONCE_LEN:
        raise CredKeyError("Şifreli blob bozuk (çok kısa)")
    try:
        pt = AESGCM(_key(kek_b64)).decrypt(blob[:_NONCE_LEN], blob[_NONCE_LEN:], None)
    except CredKeyError:
        raise
    except Exception as exc:  # InvalidTag: yanlış anahtar ya da kurcalanmış blob
        raise CredKeyError("Sır çözülemedi (anahtar yanlış ya da veri bozuk)") from exc
    return pt.decode("utf-8")
