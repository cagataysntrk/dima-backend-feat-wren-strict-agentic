from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "lab" / "fast_model_eval.py"
SPEC = importlib.util.spec_from_file_location("fast_model_eval_test_target", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

OpenRouterStructuredBenchmarkGenerator = MODULE.OpenRouterStructuredBenchmarkGenerator
strict_schema_for_benchmark = MODULE.strict_schema_for_benchmark


class _FakeResponse:
    def __init__(self, *, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class _FakeClient:
    captured = []
    response = _FakeResponse(
        payload={
            "id": "or-test",
            "model": "openai/gpt-5.6-luna",
            "choices": [{"message": {"content": '{"status":"ok"}'}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 4,
                "cost": 0.001,
            },
        }
    )

    def __init__(self, *, timeout):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, *, headers, json):
        self.__class__.captured.append(
            {"url": url, "headers": headers, "json": json}
        )
        return self.__class__.response


@pytest.fixture(autouse=True)
def _reset_fake(monkeypatch):
    _FakeClient.captured = []
    _FakeClient.response = _FakeResponse(
        payload={
            "id": "or-test",
            "model": "openai/gpt-5.6-luna",
            "choices": [{"message": {"content": '{"status":"ok"}'}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 4,
                "cost": 0.001,
            },
        }
    )
    monkeypatch.setattr(MODULE.httpx, "Client", _FakeClient)


def _schema():
    return {
        "type": "object",
        "properties": {
            "status": {"type": "string", "default": "ok"},
            "nested": {
                "anyOf": [
                    {
                        "type": "object",
                        "properties": {
                            "value": {"type": ["string", "null"], "default": None},
                        },
                    },
                    {"type": "null"},
                ],
                "default": None,
            },
        },
    }


def test_strict_schema_normalization_is_recursive_and_product_schema_is_untouched():
    original = _schema()
    normalized = strict_schema_for_benchmark(original)

    assert original["properties"]["status"]["default"] == "ok"
    assert normalized["required"] == ["status", "nested"]
    assert normalized["additionalProperties"] is False
    assert "default" not in normalized["properties"]["status"]

    nested_obj = normalized["properties"]["nested"]["anyOf"][0]
    assert nested_obj["required"] == ["value"]
    assert nested_obj["additionalProperties"] is False
    assert "default" not in nested_obj["properties"]["value"]


def test_openrouter_benchmark_payload_locks_model_schema_fallback_and_reasoning():
    generator = OpenRouterStructuredBenchmarkGenerator(
        api_key="secret",
        request_model_id="openai/gpt-5.6-luna",
        canonical_model="gpt-5.6-luna",
        model_role="LUNA_BASELINE",
        reasoning_policy="disabled",
        max_tokens=512,
    )

    raw = generator.structured_json(
        "system",
        "user",
        schema=_schema(),
        schema_name="ft005_smoke",
    )
    assert json.loads(raw) == {"status": "ok"}

    captured = _FakeClient.captured[-1]
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    payload = captured["json"]
    assert payload["model"] == "openai/gpt-5.6-luna"
    assert payload["provider"] == {"allow_fallbacks": False}
    assert payload["reasoning"] == {"enabled": False}
    assert payload["max_tokens"] == 512
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert payload["response_format"]["json_schema"]["schema"]["additionalProperties"] is False

    assert generator.last_transport["transport_success"] is True
    assert generator.last_transport["request_model_id"] == "openai/gpt-5.6-luna"
    assert generator.last_transport["canonical_model"] == "gpt-5.6-luna"
    assert generator.last_transport["provider_fallbacks"] is False
    assert generator.last_transport["response_model_id"] == "openai/gpt-5.6-luna"
    assert generator.last_usage["input_tokens"] == 10
    assert generator.last_usage["output_tokens"] == 4


def test_sol_ceiling_reasoning_is_explicit_and_separate():
    _FakeClient.response = _FakeResponse(
        payload={
            "id": "or-sol",
            "model": "openai/gpt-5.6-sol",
            "choices": [{"message": {"content": '{"status":"ok"}'}}],
        }
    )
    generator = OpenRouterStructuredBenchmarkGenerator(
        api_key="secret",
        request_model_id="openai/gpt-5.6-sol",
        canonical_model="gpt-5.6-sol",
        model_role="SOL_CEILING",
        reasoning_policy="ceiling_enabled",
    )

    generator.structured_json(
        "system",
        "user",
        schema=_schema(),
        schema_name="ft005_smoke",
    )
    assert _FakeClient.captured[-1]["json"]["reasoning"] == {"enabled": True}


def test_provider_http_failure_is_transport_failure_not_model_wrong():
    _FakeClient.response = _FakeResponse(
        status_code=429,
        payload={"error": {"message": "rate limited"}},
        text="rate limited",
    )
    generator = OpenRouterStructuredBenchmarkGenerator(
        api_key="secret",
        request_model_id="openai/gpt-5.6-luna",
        canonical_model="gpt-5.6-luna",
        model_role="LUNA_BASELINE",
        reasoning_policy="disabled",
    )

    with pytest.raises(RuntimeError, match="TRANSPORT_PROVIDER_FAILURE"):
        generator.structured_json(
            "system",
            "user",
            schema=_schema(),
            schema_name="ft005_smoke",
        )

    assert generator.last_transport["transport_success"] is False
    assert generator.last_transport["http_status"] == 429


def test_benchmark_generator_rejects_unapproved_model_identity():
    with pytest.raises(ValueError):
        OpenRouterStructuredBenchmarkGenerator(
            api_key="secret",
            request_model_id="google/gemini-2.5-flash-lite",
            canonical_model="gpt-5.6-luna",
            model_role="LUNA_BASELINE",
            reasoning_policy="disabled",
        )
