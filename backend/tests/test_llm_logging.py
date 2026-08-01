"""1 Ağustos 2026 — kapsamlı log-görünürlük denetimi (kullanıcı talebi: "llm mi patladı
api mi docker mı front mu net şekilde görelim"). ÖNCEDEN `app/llm.py`'de HİÇ log YOKTU;
`FailoverSqlGenerator` bir sağlayıcı hata verip SONRAKİ başarılı olduğunda ARA hatayı
SESSİZCE yutuyordu. Bu testler: (1) her sağlayıcının BAŞARI/HATA'sının `dima.llm`
logger'ına düştüğünü, (2) davranışın (dönen değer/fırlatılan exception) HİÇ değişmediğini
kanıtlar — log-and-rethrow deseni saf ek, regresyon değil."""

from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from app.llm import AnthropicSqlGenerator, FailoverSqlGenerator, OpenAICompatibleSqlGenerator


class _FakeMessages:
    def __init__(self, result=None, exc: Exception | None = None):
        self._result = result
        self._exc = exc

    def create(self, **kwargs):
        if self._exc is not None:
            raise self._exc
        return self._result


def _make_anthropic(result=None, exc: Exception | None = None) -> AnthropicSqlGenerator:
    gen = AnthropicSqlGenerator(api_key="test-key", model="claude-sonnet-4-6")
    gen._client = SimpleNamespace(messages=_FakeMessages(result, exc))
    return gen


def test_anthropic_ask_success_logs_info(caplog):
    ok = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="SELECT 1")],
        usage=SimpleNamespace(input_tokens=3, output_tokens=2),
    )
    gen = _make_anthropic(result=ok)
    with caplog.at_level(logging.INFO, logger="dima.llm"):
        out = gen._ask("system", "user")
    assert out == "SELECT 1"
    assert any("Anthropic API başarılı" in r.message for r in caplog.records)


def test_anthropic_ask_failure_logs_warning_and_reraises(caplog):
    boom = RuntimeError("429 rate limited")
    gen = _make_anthropic(exc=boom)
    with caplog.at_level(logging.WARNING, logger="dima.llm"):
        with pytest.raises(RuntimeError, match="429 rate limited"):
            gen._ask("system", "user")
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("Anthropic API çağrısı başarısız" in r.message for r in warnings)
    # exc_info olmalı — traceback görünürlüğü (kullanıcının "net şekilde" talebi).
    assert warnings[0].exc_info is not None


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_openai_compatible_chat_success_logs_info(monkeypatch, caplog):
    import requests

    payload = {"choices": [{"message": {"content": "SELECT 1"}}],
              "usage": {"prompt_tokens": 3, "completion_tokens": 2}}
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResponse(payload))
    gen = OpenAICompatibleSqlGenerator("https://api.groq.com/openai/v1", "key",
                                       "openai/gpt-oss-120b", "groq")
    with caplog.at_level(logging.INFO, logger="dima.llm"):
        out = gen._chat("system", "user")
    assert out == "SELECT 1"
    assert any("groq API başarılı" in r.message for r in caplog.records)


def test_openai_compatible_chat_failure_logs_warning_and_reraises(monkeypatch, caplog):
    import requests

    def fake_post(*a, **k):
        raise requests.exceptions.ConnectionError("docker: connection refused")

    monkeypatch.setattr(requests, "post", fake_post)
    gen = OpenAICompatibleSqlGenerator("http://localhost:11434/v1", "", "llama3", "ollama")
    with caplog.at_level(logging.WARNING, logger="dima.llm"):
        with pytest.raises(requests.exceptions.ConnectionError):
            gen._chat("system", "user")
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("ollama API çağrısı başarısız" in r.message for r in warnings)


def test_failover_logs_error_when_all_providers_fail(caplog):
    """FailoverSqlGenerator: her sağlayıcı tükendiğinde TEK bir ÖZET ERROR logu —
    ayrı ayrı sağlayıcı uyarıları zaten alt-seviyede (_ask/_chat) düşer, burası
    zincirin TAMAMEN tükendiğini gösteren üst-seviye sinyal."""
    gen1 = _make_anthropic(exc=RuntimeError("anthropic kota doldu"))
    gen2 = _make_anthropic(exc=RuntimeError("anthropic 2 de düştü"))
    fo = FailoverSqlGenerator([gen1, gen2])
    with caplog.at_level(logging.WARNING, logger="dima.llm"):
        with pytest.raises(RuntimeError, match="Tüm LLM sağlayıcıları başarısız"):
            fo.generate_sql("toplam ciro", {"cubes": []})
    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert any("TÜM sağlayıcılar başarısız" in r.message for r in errors)


def test_failover_succeeds_on_second_provider_after_first_fails(caplog):
    """Davranış değişmedi kilidi: ilk sağlayıcı patlarsa ikinci denenir ve SONUÇ
    başarıyla döner — log eklemesi bu akışı BOZMAZ, yalnız ara-hatayı görünür kılar."""
    ok = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="SELECT 2")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
    )
    gen1 = _make_anthropic(exc=RuntimeError("anthropic kota doldu"))
    gen2 = _make_anthropic(result=ok)
    fo = FailoverSqlGenerator([gen1, gen2])
    with caplog.at_level(logging.WARNING, logger="dima.llm"):
        out = fo.generate_sql("toplam ciro", {"cubes": []})
    assert out == "SELECT 2"
    # İlk sağlayıcının hatası GÖRÜNÜR olmalı (ÖNCEDEN sessizce yutuluyordu — kök sorun).
    assert any("Anthropic API çağrısı başarısız" in r.message for r in caplog.records)
