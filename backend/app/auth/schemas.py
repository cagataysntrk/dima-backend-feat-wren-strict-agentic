"""Auth request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)
    otp: str | None = None  # TOTP kodu (mfa_secret'lı hesaplarda zorunlu)


class UserOut(BaseModel):
    id: str
    email: str
    tenant_id: str | None
    is_superadmin: bool
    roles: list[str]
    # İzinli aksiyonlar (authorize matrisi) — UI buton görünürlüğünü buradan okur.
    permissions: list[str] = []


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class MeResponse(BaseModel):
    user_id: str
    tenant_id: str | None
    is_superadmin: bool
    roles: list[str]
    branch_ids: list[str]
    permissions: list[str] = []
