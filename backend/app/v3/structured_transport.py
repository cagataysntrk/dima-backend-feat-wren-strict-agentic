"""Canonical structured cognition transport for Dima v3.

This is a provider transport only. Semantic authority stays with typed callers.
It never executes analytics, SQL, Metabase queries, or business side effects.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import time
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict


_MAX_DIAGNOSTIC_BYTES = 8192
_SECRET_KEY_FRAGMENTS = (
    "authorization",
    "api_key",
    "apikey",
    "token",
    "cookie",
    "password",
    "credential",
    "secret",
    "prompt",
    "messages",
    "system",
    "user",
    "snapshot",
    "governed",
    "database",
)
_BEARER_RE = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+\-/=]+")
_KEYLIKE_RE = re.compile(
    r"(?i)(?:sk|sk-or-v1|or-v1|key)[-_][A-Za-z0-9._~+\-/=]{12,}"
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class StructuredProviderDiagnostic(_Frozen):
    status_code: int
    provider_error_code: str | None = None
    provider_error_message: str | None = None
    provider_error_metadata: Any | None = None
    provider_request_id: str | None = None
    model: str
    schema_name: str
    schema_fingerprint: str
    response_format_family: str = "json_schema"
    bounded_response_excerpt: str | None = None


class StructuredProviderError(RuntimeError):
    def __init__(
        self,
        code: str,
        detail: str,
        *,
        diagnostic: StructuredProviderDiagnostic | None = None,
    ) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.diagnostic = diagnostic


def schema_fingerprint(schema: dict[str, Any]) -> str:
    """Deterministic SHA-256 over canonical JSON schema bytes."""

    raw = json.dumps(
        schema,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _bounded_utf8(value: str, limit: int = _MAX_DIAGNOSTIC_BYTES) -> str:
    raw = value.encode("utf-8", errors="replace")
    if len(raw) <= limit:
        return value
    return raw[:limit].decode("utf-8", errors="ignore")


def _sanitize_text(value: str, *, sensitive_values: tuple[str, ...]) -> str:
    sanitized = value
    for secret in sensitive_values:
        if secret:
            sanitized = sanitized.replace(secret, "[REDACTED]")
    sanitized = _BEARER_RE.sub("Bearer [REDACTED]", sanitized)
    sanitized = _KEYLIKE_RE.sub("[REDACTED_KEY]", sanitized)
    return _bounded_utf8(sanitized)


def _is_secret_key(key: str) -> bool:
    normalized = key.casefold().replace("-", "_")
    return any(fragment in normalized for fragment in _SECRET_KEY_FRAGMENTS)


def _sanitize_value(
    value: Any,
    *,
    sensitive_values: tuple[str, ...],
    depth: int = 0,
) -> Any:
    if depth > 12:
        return "[TRUNCATED_DEPTH]"
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for raw_key, child in value.items():
            key = str(raw_key)
            if _is_secret_key(key):
                out[key] = "[REDACTED]"
            else:
                out[key] = _sanitize_value(
                    child,
                    sensitive_values=sensitive_values,
                    depth=depth + 1,
                )
        serialized = json.dumps(
            out,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        if len(serialized.encode("utf-8")) <= _MAX_DIAGNOSTIC_BYTES:
            return out
        return {
            "_bounded_excerpt": _bounded_utf8(serialized),
            "_truncated": True,
        }
    if isinstance(value, list):
        out = [
            _sanitize_value(
                item,
                sensitive_values=sensitive_values,
                depth=depth + 1,
            )
            for item in value
        ]
        serialized = json.dumps(
            out,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )
        if len(serialized.encode("utf-8")) <= _MAX_DIAGNOSTIC_BYTES:
            return out
        return [_bounded_utf8(serialized), "[TRUNCATED]"]
    if isinstance(value, str):
        return _sanitize_text(value, sensitive_values=sensitive_values)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _sanitize_text(str(value), sensitive_values=sensitive_values)


def _request_id(response: httpx.Response) -> str | None:
    for name in ("x-request-id", "x-openrouter-request-id"):
        value = response.headers.get(name)
        if value and value.strip():
            return _bounded_utf8(value.strip(), 512)
    return None


def _provider_diagnostic(
    response: httpx.Response,
    *,
    model: str,
    schema_name: str,
    schema: dict[str, Any],
    api_key: str,
    system: str,
    user: str,
) -> StructuredProviderDiagnostic:
    sensitive_values = (api_key, system, user)
    provider_error_code: str | None = None
    provider_error_message: str | None = None
    provider_error_metadata: Any | None = None
    bounded_response_excerpt: str | None = None

    try:
        body = response.json()
    except ValueError:
        bounded_response_excerpt = _sanitize_text(
            response.text,
            sensitive_values=sensitive_values,
        )
    else:
        error = body.get("error") if isinstance(body, dict) else None
        if isinstance(error, dict):
            raw_code = error.get("code")
            if raw_code is not None:
                provider_error_code = _bounded_utf8(str(raw_code), 512)
            raw_message = error.get("message")
            if isinstance(raw_message, str):
                provider_error_message = _sanitize_text(
                    raw_message,
                    sensitive_values=sensitive_values,
                )
            if "metadata" in error:
                provider_error_metadata = _sanitize_value(
                    error.get("metadata"),
                    sensitive_values=sensitive_values,
                )
        else:
            provider_error_metadata = _sanitize_value(
                body,
                sensitive_values=sensitive_values,
            )

    return StructuredProviderDiagnostic(
        status_code=response.status_code,
        provider_error_code=provider_error_code,
        provider_error_message=provider_error_message,
        provider_error_metadata=provider_error_metadata,
        provider_request_id=_request_id(response),
        model=model,
        schema_name=schema_name,
        schema_fingerprint=schema_fingerprint(schema),
        response_format_family="json_schema",
        bounded_response_excerpt=bounded_response_excerpt,
    )


def strict_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Return OpenAI/OpenRouter strict JSON-schema without changing semantics."""

    schema = copy.deepcopy(model.model_json_schema())

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            props = node.get("properties")
            if isinstance(props, dict):
                node["additionalProperties"] = False
                node["required"] = list(props)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(schema)
    return schema


class OpenRouterStructuredJSONTransport:
    """Minimal bounded OpenRouter JSON-schema transport.

    No key rotation, fallback model, provider cascade, or silent free-form fallback.
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
        max_tokens: int = 4096,
        timeout_seconds: float = 60.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        key = str(api_key or "").strip()
        if not key:
            raise StructuredProviderError(
                "COGNITION_CREDENTIAL_REQUIRED",
                "OpenRouter credential is required",
            )
        chosen = str(model or "").strip()
        if not chosen:
            raise StructuredProviderError(
                "COGNITION_MODEL_REQUIRED",
                "model identifier is required",
            )
        self._key = key
        self.model = chosen
        self._max_tokens = max(256, int(max_tokens))
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            transport=transport,
        )
        self.call_count = 0
        self.total_latency_ms = 0

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OpenRouterStructuredJSONTransport":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb
        self.close()

    @staticmethod
    def _content(body: Any) -> str:
        try:
            value = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise StructuredProviderError(
                "COGNITION_RESPONSE_INVALID",
                "provider response has no message content",
            ) from exc
        if not isinstance(value, str) or not value.strip():
            raise StructuredProviderError(
                "COGNITION_RESPONSE_EMPTY",
                "provider returned empty structured content",
            )
        return value

    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str:
        if not system.strip() or not user.strip():
            raise StructuredProviderError(
                "COGNITION_PROMPT_INVALID",
                "system and user prompts are required",
            )
        payload: dict[str, Any] = {
            "model": self.model,
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
            "provider": {"require_parameters": True},
            "reasoning": {"enabled": False},
            "max_tokens": self._max_tokens,
        }
        started = time.monotonic()
        self.call_count += 1
        try:
            response = self._client.post(
                "/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        except httpx.TimeoutException as exc:
            raise StructuredProviderError(
                "COGNITION_TIMEOUT",
                "structured cognition request timed out",
            ) from exc
        except httpx.RequestError as exc:
            raise StructuredProviderError(
                "COGNITION_TRANSPORT_FAILED",
                "structured cognition transport failed",
            ) from exc
        finally:
            self.total_latency_ms += max(
                0,
                int((time.monotonic() - started) * 1000),
            )
        if response.status_code < 200 or response.status_code >= 300:
            raise StructuredProviderError(
                "COGNITION_PROVIDER_REJECTED",
                f"provider returned HTTP {response.status_code}",
                diagnostic=_provider_diagnostic(
                    response,
                    model=self.model,
                    schema_name=schema_name,
                    schema=schema,
                    api_key=self._key,
                    system=system,
                    user=user,
                ),
            )
        try:
            body = response.json()
        except json.JSONDecodeError as exc:
            raise StructuredProviderError(
                "COGNITION_RESPONSE_INVALID",
                "provider response is not JSON",
            ) from exc
        return self._content(body)
