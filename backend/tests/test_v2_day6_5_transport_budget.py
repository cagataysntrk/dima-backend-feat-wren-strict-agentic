"""Provider-free transport invariants for Day 6.5 certification."""

from __future__ import annotations

from app.llm import OpenAICompatibleSqlGenerator


class _FakeResponse:
    text = ""

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return {
            "choices": [
                {
                    "message": {"content": '{"ok":true}'},
                    "finish_reason": "stop",
                }
            ],
            "usage": {},
        }


def test_native_structured_transport_has_bounded_output_reservation(monkeypatch):
    captured = {}

    def fake_post(url, *, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _FakeResponse()

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    generator = OpenAICompatibleSqlGenerator(
        "https://example.invalid/v1",
        "test-key",
        "openai/gpt-5.6-sol",
        "openrouter",
        structured_reasoning_enabled=True,
        structured_max_tokens=16384,
    )
    result = generator.structured_json(
        "system",
        "user",
        schema={
            "type": "object",
            "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"],
            "additionalProperties": False,
        },
        schema_name="day65_transport_probe",
    )

    assert result == '{"ok":true}'
    assert captured["json"]["max_tokens"] == 16384
    assert captured["json"]["reasoning"] == {"enabled": True}
    assert captured["json"]["response_format"]["type"] == "json_schema"
    assert captured["json"]["provider"] == {"require_parameters": True}


def test_non_structured_transport_does_not_gain_structured_token_cap(monkeypatch):
    captured = {}

    def fake_post(url, *, json, headers, timeout):
        captured["json"] = json
        return _FakeResponse()

    import requests

    monkeypatch.setattr(requests, "post", fake_post)

    generator = OpenAICompatibleSqlGenerator(
        "https://example.invalid/v1",
        "test-key",
        "plain-model",
        "openrouter",
        structured_max_tokens=16384,
    )
    generator.structured_text("system", "user")

    assert "max_tokens" not in captured["json"]
