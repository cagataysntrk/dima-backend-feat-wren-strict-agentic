"""Non-secret structured-cognition request/response identity.

Telemetry only. No semantic, routing, retry, or provider authority lives here.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class StructuredRequestIdentity(_Frozen):
    owner: str = Field(min_length=1, max_length=160)
    model: str = Field(min_length=1, max_length=300)
    schema_name: str = Field(min_length=1, max_length=300)
    schema_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    system_prompt_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    user_prompt_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    request_envelope_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    response_format_family: str = Field(min_length=1, max_length=80)
    max_tokens: int = Field(ge=1)
    provider_routing_policy_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    call_ordinal_by_role: int = Field(ge=1)


class StructuredCallTrace(StructuredRequestIdentity):
    provider_request_id: str | None = Field(default=None, max_length=512)
    provider_backend_identity: str | None = Field(default=None, max_length=512)
    http_status: int | None = None
    provider_error_code: str | None = Field(default=None, max_length=512)
    provider_error_message: str | None = Field(default=None, max_length=2048)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def json_fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def text_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_provider_bound_payload(
    *,
    model: str,
    system: str,
    user: str,
    schema: dict[str, Any],
    schema_name: str,
    max_tokens: int,
    provider_routing_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the exact credential-free JSON body sent to OpenRouter."""

    provider = (
        copy.deepcopy(dict(provider_routing_policy))
        if provider_routing_policy is not None
        else {"require_parameters": True}
    )
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema,
            },
        },
        "provider": provider,
        "reasoning": {"enabled": False},
        "max_tokens": int(max_tokens),
    }


def request_identity(
    *,
    owner: str,
    payload: dict[str, Any],
    schema_name: str,
    schema: dict[str, Any],
    system: str,
    user: str,
    call_ordinal_by_role: int,
) -> StructuredRequestIdentity:
    response_format = payload.get("response_format")
    family = (
        str(response_format.get("type"))
        if isinstance(response_format, dict)
        and response_format.get("type")
        else "unknown"
    )
    provider_policy = payload.get("provider")
    return StructuredRequestIdentity(
        owner=owner,
        model=str(payload.get("model") or ""),
        schema_name=schema_name,
        schema_fingerprint=json_fingerprint(schema),
        system_prompt_hash=text_fingerprint(system),
        user_prompt_hash=text_fingerprint(user),
        request_envelope_fingerprint=json_fingerprint(payload),
        response_format_family=family,
        max_tokens=int(payload.get("max_tokens") or 0),
        provider_routing_policy_fingerprint=json_fingerprint(provider_policy),
        call_ordinal_by_role=call_ordinal_by_role,
    )


def provider_backend_identity(
    *,
    headers: Mapping[str, str],
    body: Any | None,
) -> str | None:
    for key in (
        "x-openrouter-provider",
        "x-provider",
        "x-model-provider",
    ):
        value = headers.get(key)
        if value and str(value).strip():
            return str(value).strip()[:512]
    if isinstance(body, dict):
        for key in ("provider", "backend", "provider_name"):
            value = body.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:512]
    return None
