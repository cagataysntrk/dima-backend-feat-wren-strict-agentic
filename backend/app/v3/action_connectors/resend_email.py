"""Narrow Resend connector certification seam.

This module certifies provider protocol behavior for a future governed Action executor.
It is not an Action executor, owns no durable truth, and is not imported by product hot paths.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.config import get_settings

RESEND_API_ORIGIN = "https://api.resend.com"
_RESEND_SEND_PATH = "/emails"
_IDEMPOTENCY_RETENTION = timedelta(hours=24)
_EMAIL_ID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResendConnectorError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ResendSendState(StrEnum):
    PROVIDER_ACCEPTED = "PROVIDER_ACCEPTED"
    RETRYABLE_SAME_KEY = "RETRYABLE_SAME_KEY"
    UNKNOWN_EXTERNAL_STATE = "UNKNOWN_EXTERNAL_STATE"


class ResendTag(Frozen):
    name: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    value: str = Field(min_length=1, max_length=256)

    @field_validator("value")
    @classmethod
    def no_control_line_breaks(cls, value: str) -> str:
        if "\r" in value or "\n" in value:
            raise ValueError("tag values cannot contain line breaks")
        return value


class ResendEmailRequest(Frozen):
    from_address: str = Field(min_length=3, max_length=320)
    to: tuple[str, ...] = Field(min_length=1, max_length=10)
    subject: str = Field(min_length=1, max_length=998)
    html: str | None = Field(default=None, max_length=1_000_000)
    text: str | None = Field(default=None, max_length=1_000_000)
    tags: tuple[ResendTag, ...] = Field(default=(), max_length=20)

    @field_validator("from_address")
    @classmethod
    def validate_from(cls, value: str) -> str:
        value = value.strip()
        if "\r" in value or "\n" in value or "@" not in value:
            raise ValueError("invalid from address")
        return value

    @field_validator("to")
    @classmethod
    def validate_recipients(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        out: list[str] = []
        for raw in values:
            value = str(raw).strip()
            if (
                not value
                or "\r" in value
                or "\n" in value
                or "@" not in value
            ):
                raise ValueError("invalid recipient")
            out.append(value)
        if len(out) != len(set(out)):
            raise ValueError("duplicate recipients are not allowed")
        return tuple(out)

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        if "\r" in value or "\n" in value:
            raise ValueError("subject cannot contain line breaks")
        return value

    @model_validator(mode="after")
    def require_body(self):
        if self.html is None and self.text is None:
            raise ValueError("html or text body is required")
        if self.html == "" or self.text == "":
            raise ValueError("body fields cannot be blank")
        names = [tag.name for tag in self.tags]
        if len(names) != len(set(names)):
            raise ValueError("tag names must be unique")
        return self


class ResendIdempotencyIdentity(Frozen):
    attempt_id: str = Field(min_length=1, max_length=200)
    key_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime
    expires_at: datetime


class ResendSendResult(Frozen):
    state: ResendSendState
    provider_email_id: str | None = None
    payload_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    idempotency_key_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    http_status: int | None = None
    provider_error_name: str | None = None


class ResendRetrieveResult(Frozen):
    provider_email_id: str
    message_id: str | None = None
    to: tuple[str, ...]
    from_address: str
    subject: str
    last_event: str | None = None
    reconciled: bool = True


def _canonical_json(value: Any) -> tuple[str, str]:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ResendConnectorError(
            "RESEND_PAYLOAD_NOT_CANONICAL",
            "provider payload is not deterministic JSON",
        ) from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def canonical_provider_payload(request: ResendEmailRequest) -> tuple[dict[str, Any], str]:
    payload: dict[str, Any] = {
        "from": request.from_address,
        "to": list(request.to),
        "subject": request.subject,
    }
    if request.html is not None:
        payload["html"] = request.html
    if request.text is not None:
        payload["text"] = request.text
    if request.tags:
        payload["tags"] = [tag.model_dump(mode="json") for tag in request.tags]
    return payload, _canonical_json(payload)[1]


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ResendConnectorError(
            "RESEND_TIMEZONE_REQUIRED",
            "idempotency timestamp must be timezone-aware",
        )
    return stamp


def idempotency_identity(
    *,
    attempt_id: str,
    created_at: datetime | None = None,
) -> tuple[str, ResendIdempotencyIdentity]:
    attempt = str(attempt_id).strip()
    if not attempt or len(attempt) > 200:
        raise ResendConnectorError(
            "RESEND_ATTEMPT_ID_INVALID",
            "attempt identity must be 1..200 characters",
        )
    digest = hashlib.sha256(attempt.encode("utf-8")).hexdigest()
    key = f"dima-action/{digest}"
    if len(key) > 256:
        raise ResendConnectorError(
            "RESEND_IDEMPOTENCY_KEY_INVALID",
            "derived idempotency key exceeds provider limit",
        )
    stamp = _aware(created_at)
    return key, ResendIdempotencyIdentity(
        attempt_id=attempt,
        key_fingerprint=hashlib.sha256(key.encode("utf-8")).hexdigest(),
        created_at=stamp,
        expires_at=stamp + _IDEMPOTENCY_RETENTION,
    )


def _error_name(response: httpx.Response) -> str | None:
    try:
        body = response.json()
    except ValueError:
        return None
    if not isinstance(body, dict):
        return None
    direct = body.get("name")
    if isinstance(direct, str):
        return direct
    nested = body.get("error")
    if isinstance(nested, dict) and isinstance(nested.get("name"), str):
        return nested["name"]
    return None


def _provider_id(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError as exc:
        raise ResendConnectorError(
            "RESEND_PROVIDER_RESPONSE_INVALID",
            "provider response is not JSON",
        ) from exc
    provider_id = body.get("id") if isinstance(body, dict) else None
    if not isinstance(provider_id, str) or not provider_id.strip():
        raise ResendConnectorError(
            "RESEND_PROVIDER_ID_MISSING",
            "successful provider response did not contain an email id",
        )
    return provider_id.strip()


class ResendEmailConnector:
    """Fixed-origin Resend client with deterministic idempotency and reconciliation."""

    def __init__(
        self,
        *,
        settings=None,
        transport: httpx.BaseTransport | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        trusted_settings = settings or get_settings()
        self._api_key = str(trusted_settings.resend_api_key or "").strip()
        self._client = httpx.Client(
            base_url=RESEND_API_ORIGIN,
            transport=transport,
            timeout=timeout_seconds,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        if not self._api_key:
            raise ResendConnectorError(
                "RESEND_CREDENTIAL_UNAVAILABLE",
                "trusted Resend API credential is not configured",
            )
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def send(
        self,
        *,
        request: ResendEmailRequest,
        attempt_id: str,
        idempotency_created_at: datetime | None = None,
    ) -> ResendSendResult:
        payload, payload_fingerprint = canonical_provider_payload(request)
        key, identity = idempotency_identity(
            attempt_id=attempt_id,
            created_at=idempotency_created_at,
        )
        try:
            response = self._client.post(
                _RESEND_SEND_PATH,
                headers=self._headers(key),
                json=payload,
            )
        except (httpx.TimeoutException, httpx.TransportError):
            return ResendSendResult(
                state=ResendSendState.UNKNOWN_EXTERNAL_STATE,
                payload_fingerprint=payload_fingerprint,
                idempotency_key_fingerprint=identity.key_fingerprint,
            )

        if 200 <= response.status_code < 300:
            return ResendSendResult(
                state=ResendSendState.PROVIDER_ACCEPTED,
                provider_email_id=_provider_id(response),
                payload_fingerprint=payload_fingerprint,
                idempotency_key_fingerprint=identity.key_fingerprint,
                http_status=response.status_code,
            )

        name = _error_name(response)
        if response.status_code == 400 and name == "invalid_idempotency_key":
            raise ResendConnectorError(
                "RESEND_IDEMPOTENCY_KEY_REJECTED",
                "provider rejected deterministic idempotency key",
            )
        if response.status_code == 409 and name == "invalid_idempotent_request":
            raise ResendConnectorError(
                "RESEND_IDEMPOTENCY_IDENTITY_VIOLATION",
                "same idempotency key was used with a different provider payload",
            )
        if response.status_code == 409 and name == "concurrent_idempotent_requests":
            return ResendSendResult(
                state=ResendSendState.RETRYABLE_SAME_KEY,
                payload_fingerprint=payload_fingerprint,
                idempotency_key_fingerprint=identity.key_fingerprint,
                http_status=response.status_code,
                provider_error_name=name,
            )
        raise ResendConnectorError(
            "RESEND_PROVIDER_REJECTED",
            f"provider rejected request with status {response.status_code}"
            + (f" ({name})" if name else ""),
        )

    def retrieve_email(
        self,
        *,
        email_id: str,
        expected_request: ResendEmailRequest,
    ) -> ResendRetrieveResult:
        raw_id = str(email_id).strip()
        if not _EMAIL_ID_RE.fullmatch(raw_id):
            try:
                raw_id = str(UUID(raw_id))
            except ValueError as exc:
                raise ResendConnectorError(
                    "RESEND_EMAIL_ID_INVALID",
                    "provider email id must be a UUID",
                ) from exc
        try:
            response = self._client.get(
                f"/emails/{raw_id}",
                headers=self._headers(),
            )
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise ResendConnectorError(
                "RESEND_RECONCILIATION_UNAVAILABLE",
                "provider retrieve state is unavailable",
            ) from exc
        if not 200 <= response.status_code < 300:
            raise ResendConnectorError(
                "RESEND_RETRIEVE_REJECTED",
                f"provider retrieve failed with status {response.status_code}",
            )
        try:
            body = response.json()
        except ValueError as exc:
            raise ResendConnectorError(
                "RESEND_RETRIEVE_INVALID",
                "provider retrieve response is not JSON",
            ) from exc
        if not isinstance(body, dict):
            raise ResendConnectorError(
                "RESEND_RETRIEVE_INVALID",
                "provider retrieve response is not an object",
            )

        provider_id = body.get("id")
        raw_to = body.get("to")
        provider_from = body.get("from")
        provider_subject = body.get("subject")
        if isinstance(raw_to, str):
            provider_to = (raw_to,)
        elif isinstance(raw_to, list) and all(isinstance(v, str) for v in raw_to):
            provider_to = tuple(raw_to)
        else:
            provider_to = ()

        if (
            provider_id != raw_id
            or provider_to != expected_request.to
            or provider_from != expected_request.from_address
            or provider_subject != expected_request.subject
        ):
            raise ResendConnectorError(
                "RESEND_RECONCILIATION_MISMATCH",
                "retrieved provider identity does not match expected canonical request",
            )

        message_id = body.get("message_id")
        return ResendRetrieveResult(
            provider_email_id=raw_id,
            message_id=message_id if isinstance(message_id, str) else None,
            to=provider_to,
            from_address=provider_from,
            subject=provider_subject,
            last_event=body.get("last_event") if isinstance(body.get("last_event"), str) else None,
        )
