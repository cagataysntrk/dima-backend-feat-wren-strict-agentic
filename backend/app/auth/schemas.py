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
    #: 🔴 FAZ 7.7 — **kimlik asimetrisi kapandı.** Frontend'in `AuthUser` tipi `email`i
    #: **zorunlu** ilan ediyordu ama `/auth/me` onu **hiç göndermiyordu**: TypeScript
    #: `me.email`in var olduğuna inanıyor, çalışma zamanında `undefined` geliyordu.
    #: *Bir tipin telde karşılığı yoksa, o tip bir belge değil bir yanlış beyandır.*
    #:
    #: ⚠ `Principal`e **eklenmedi**: onun sözleşmesi *"tümü token'dan türetilir"*
    #: (ADR-0014 Karar 1) ve e-postayı token'a koymak, her istekte taşınan bir PII
    #: demek olurdu. Burada **tek bir okuma** ile çözülür ve token şekli korunur.
    #:
    #: ⚠ `None` olabilir: superadmin'in tenant'ı olmayabilir ve kullanıcı kaydı
    #: silinmiş olabilir. *Bulunamayan bir e-postayı boş dizgeyle doldurmak, "yok" ile
    #: "boş" ayrımını siler.*
    email: str | None = None
    tenant_id: str | None
    is_superadmin: bool
    roles: list[str]
    branch_ids: list[str]
    permissions: list[str] = []
