"""Canonical structured cognition transport for Dima v3.

This is a provider transport only. Semantic authority stays with typed callers.
It never executes analytics, SQL, Metabase queries, or business side effects.
"""
from __future__ import annotations

import copy
import json
import time
from typing import Any

import httpx
from pydantic import BaseModel


class StructuredProviderError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


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
        # Current GPT-5/o-series OpenRouter endpoints do not require temperature
        # and may reject it. Keep the canonical Luna path parameter-minimal.
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
            )
        try:
            body = response.json()
        except json.JSONDecodeError as exc:
            raise StructuredProviderError(
                "COGNITION_RESPONSE_INVALID",
                "provider response is not JSON",
            ) from exc
        return self._content(body)
