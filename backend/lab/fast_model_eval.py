"""Eval-only structured-output observability for Fast Track model benchmarks.

Never import this module from production app.fast code.
It records only requested structured-action JSON and transport/validation telemetry.
It does not record chain-of-thought or reasoning text.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
from typing import Any

import httpx
from pydantic import ValidationError

from app.llm import get_llm_usage, reset_llm_usage


class RecordingStructuredGenerator:
    def __init__(
        self,
        inner,
        *,
        model_role: str,
        exact_model_id: str,
        provider: str,
        validator_model=None,
        reasoning_effort: str = "disabled",
    ) -> None:
        self._inner = inner
        self._model_role = model_role
        self._model_id = exact_model_id
        self._provider = provider
        self._validator_model = validator_model
        self._reasoning_effort = reasoning_effort
        self._case_id = "unassigned"
        self.records: list[dict[str, Any]] = []

    def set_case(self, case_id: str) -> None:
        self._case_id = case_id

    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str:
        started = time.monotonic()
        reset_llm_usage()
        record: dict[str, Any] = {
            "case_id": self._case_id,
            "model_role": self._model_role,
            "exact_model_id": self._model_id,
            "provider": self._provider,
            "reasoning_effort": self._reasoning_effort,
            "schema_name": schema_name,
            "transport_success": False,
            "parse_success": False,
            "structured_valid": False,
            "provider_error_type": None,
            "provider_error_message": None,
            "validation_error_type": None,
            "validation_error_paths": [],
            "raw_structured_output": None,
            "raw_output_digest": None,
            "latency_ms": None,
            "input_tokens": None,
            "output_tokens": None,
        }
        try:
            raw = self._inner.structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )
            record["transport_success"] = True
            record["raw_structured_output"] = raw
            record["raw_output_digest"] = hashlib.sha256(
                raw.encode("utf-8")
            ).hexdigest()

            try:
                payload = json.loads(raw)
                record["parse_success"] = True
            except json.JSONDecodeError as exc:
                record["validation_error_type"] = type(exc).__name__
                record["validation_error_paths"] = [
                    f"json:{exc.lineno}:{exc.colno}"
                ]
                return raw

            if self._validator_model is None:
                record["structured_valid"] = True
            else:
                try:
                    self._validator_model.model_validate(payload)
                    record["structured_valid"] = True
                except ValidationError as exc:
                    record["validation_error_type"] = type(exc).__name__
                    record["validation_error_paths"] = [
                        ".".join(str(part) for part in error.get("loc", ()))
                        for error in exc.errors()
                    ]
            return raw
        except Exception as exc:
            record["provider_error_type"] = type(exc).__name__
            record["provider_error_message"] = str(exc)[:500]
            raise
        finally:
            usage = getattr(self._inner, "last_usage", None) or get_llm_usage() or {}
            transport = getattr(self._inner, "last_transport", None) or {}
            record["latency_ms"] = usage.get(
                "latency_ms",
                int((time.monotonic() - started) * 1000),
            )
            record["input_tokens"] = usage.get("input_tokens")
            record["output_tokens"] = usage.get("output_tokens")
            record["cost"] = usage.get("cost")
            record["transport_provider"] = transport.get("transport_provider", self._provider)
            record["request_model_id"] = transport.get("request_model_id", self._model_id)
            record["canonical_model"] = transport.get("canonical_model")
            record["response_model_id"] = transport.get("response_model_id")
            record["response_id"] = transport.get("response_id")
            record["provider_fallbacks"] = transport.get("provider_fallbacks")
            record["http_status"] = transport.get("http_status")
            self.records.append(record)



OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


def strict_schema_for_benchmark(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Pydantic JSON schema for strict provider transport.

    Eval-only. The product Pydantic contract remains unchanged.
    """

    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties") or {}
                node["required"] = list(properties.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


class OpenRouterStructuredBenchmarkGenerator:
    """Exact eval-only structured transport for frozen Fast model benchmarks."""

    def __init__(
        self,
        *,
        api_key: str,
        request_model_id: str,
        canonical_model: str,
        model_role: str,
        reasoning_policy: str,
        max_tokens: int = 4096,
        timeout_s: float = 45.0,
    ) -> None:
        if not api_key.strip():
            raise RuntimeError("BLOCKED_NO_CREDENTIAL:DIMA_OPENROUTER_API_KEY")
        if not request_model_id.startswith("openai/gpt-5.6-"):
            raise ValueError("benchmark request model must be an exact OpenRouter OpenAI model id")
        if canonical_model not in {"gpt-5.6-luna", "gpt-5.6-sol"}:
            raise ValueError("unsupported canonical Fast benchmark model")
        if reasoning_policy not in {"disabled", "ceiling_enabled"}:
            raise ValueError("reasoning_policy must be disabled or ceiling_enabled")
        self._api_key = api_key.strip()
        self._request_model_id = request_model_id
        self._canonical_model = canonical_model
        self._model_role = model_role
        self._reasoning_policy = reasoning_policy
        self._max_tokens = max(256, int(max_tokens))
        self._timeout_s = float(timeout_s)
        self.last_usage: dict[str, Any] = {}
        self.last_transport: dict[str, Any] = {}

    @property
    def benchmark_identity(self) -> dict[str, Any]:
        return {
            "transport_provider": "OPENROUTER",
            "request_model_id": self._request_model_id,
            "canonical_model": self._canonical_model,
            "model_role": self._model_role,
            "reasoning_policy": self._reasoning_policy,
            "provider_fallbacks": False,
            "max_tokens": self._max_tokens,
        }

    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str:
        normalized_schema = strict_schema_for_benchmark(schema)
        reasoning = {"enabled": self._reasoning_policy == "ceiling_enabled"}
        payload = {
            "model": self._request_model_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": normalized_schema,
                },
            },
            "provider": {"allow_fallbacks": False},
            "reasoning": reasoning,
            "max_tokens": self._max_tokens,
        }

        started = time.monotonic()
        try:
            with httpx.Client(timeout=self._timeout_s) as client:
                response = client.post(
                    OPENROUTER_CHAT_URL,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            latency_ms = int((time.monotonic() - started) * 1000)
            if response.status_code != 200:
                self.last_transport = {
                    **self.benchmark_identity,
                    "transport_success": False,
                    "http_status": response.status_code,
                    "latency_ms": latency_ms,
                    "error": response.text[:500],
                }
                raise RuntimeError(
                    f"TRANSPORT_PROVIDER_FAILURE: HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )

            raw = response.json()
            choices = raw.get("choices") or []
            if not choices:
                raise RuntimeError("TRANSPORT_PROVIDER_FAILURE: response choices missing")
            message = (choices[0] or {}).get("message") or {}
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("TRANSPORT_PROVIDER_FAILURE: structured content missing")

            usage = raw.get("usage") or {}
            self.last_usage = {
                "input_tokens": usage.get("input_tokens", usage.get("prompt_tokens")),
                "output_tokens": usage.get("output_tokens", usage.get("completion_tokens")),
                "cost": usage.get("cost"),
                "latency_ms": latency_ms,
            }
            self.last_transport = {
                **self.benchmark_identity,
                "transport_success": True,
                "http_status": response.status_code,
                "latency_ms": latency_ms,
                "response_model_id": raw.get("model"),
                "response_id": raw.get("id"),
            }
            return content.strip()
        except Exception:
            if not self.last_transport:
                self.last_transport = {
                    **self.benchmark_identity,
                    "transport_success": False,
                    "latency_ms": int((time.monotonic() - started) * 1000),
                }
            raise
