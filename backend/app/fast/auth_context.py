"""Fast Track identity input for Metabase transport.

This module does not decide permissions. It carries the already-resolved Dima principal
into the gateway and derives a secret-free provenance fingerprint.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class FastMetabaseAuthMode(StrEnum):
    SESSION = "session"
    API_KEY = "api_key"


class FastAccessFingerprint(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str = Field(min_length=1)
    dima_user_id: str = Field(min_length=1)
    principal_id: str = Field(min_length=1)
    auth_mode: FastMetabaseAuthMode
    role_scope_digest: str = ""
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class FastMetabaseAuthContext(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str = Field(min_length=1)
    dima_user_id: str = Field(min_length=1)
    principal_id: str = Field(min_length=1)
    mode: FastMetabaseAuthMode
    secret: SecretStr = Field(repr=False)
    role_scope_digest: str = ""

    def headers(self) -> dict[str, str]:
        value = self.secret.get_secret_value().strip()
        if not value:
            raise ValueError("Metabase auth secret is empty")
        if self.mode == FastMetabaseAuthMode.SESSION:
            return {"X-Metabase-Session": value}
        if self.mode == FastMetabaseAuthMode.API_KEY:
            return {"X-API-Key": value}
        raise ValueError(f"unsupported Metabase auth mode: {self.mode}")

    def access_fingerprint(self) -> FastAccessFingerprint:
        canonical = {
            "tenant_id": self.tenant_id,
            "dima_user_id": self.dima_user_id,
            "principal_id": self.principal_id,
            "auth_mode": self.mode.value,
            "role_scope_digest": self.role_scope_digest,
        }
        digest = hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return FastAccessFingerprint(
            tenant_id=self.tenant_id,
            dima_user_id=self.dima_user_id,
            principal_id=self.principal_id,
            auth_mode=self.mode,
            role_scope_digest=self.role_scope_digest,
            digest=digest,
        )
