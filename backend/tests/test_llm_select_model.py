"""Faz 4.2 (31 Temmuz 2026) — Intent-JSON seçimi (select_cube/refine_cube) için opsiyonel
ucuz/hızlı model sınıfı (dış yol haritası 2.11 "model sınıfı seçimi" karşılığı).

`select_model` verilmezse (varsayılan, mevcut TÜM canlı yapılandırmalar) davranış BİREBİR
eskisiyle aynı — bu testler hem YENİ ayrımı hem de bu geriye-uyumu kanıtlar."""

from __future__ import annotations

from types import SimpleNamespace

from app.llm import AnthropicSqlGenerator, OpenAICompatibleSqlGenerator


class _FakeMessages:
    def __init__(self, calls: list[dict]):
        self._calls = calls

    def create(self, **kwargs):
        self._calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text="SELECT 1")],
            usage=SimpleNamespace(input_tokens=3, output_tokens=2),
        )


def _make_anthropic(select_model: str | None) -> tuple[AnthropicSqlGenerator, list[dict]]:
    gen = AnthropicSqlGenerator(api_key="test-key", model="claude-sonnet-4-6",
                                select_model=select_model)
    calls: list[dict] = []
    gen._client = SimpleNamespace(messages=_FakeMessages(calls))  # gerçek Anthropic() atlanır
    return gen, calls


def test_anthropic_select_cube_uses_select_model_when_set():
    gen, calls = _make_anthropic("claude-haiku-4-5-20251001")
    gen.select_cube("makine bazında oee", "CUBE katalog metni")
    assert calls[-1]["model"] == "claude-haiku-4-5-20251001"


def test_anthropic_refine_cube_uses_select_model_when_set():
    gen, calls = _make_anthropic("claude-haiku-4-5-20251001")
    gen.refine_cube("{}", "bu yıl göster", "CUBE katalog metni")
    assert calls[-1]["model"] == "claude-haiku-4-5-20251001"


def test_anthropic_generate_sql_and_repair_ignore_select_model():
    """Discovery (ham-SQL) HER ZAMAN ana modeli kullanır — yalnız Intent-JSON ucuzlar."""
    gen, calls = _make_anthropic("claude-haiku-4-5-20251001")
    gen.generate_sql("toplam ciro", {"cubes": []})
    assert calls[-1]["model"] == "claude-sonnet-4-6"
    gen.repair("toplam ciro", {"cubes": []}, "SELECT x", "hata")
    assert calls[-1]["model"] == "claude-sonnet-4-6"


def test_anthropic_no_select_model_falls_back_to_main_model():
    """Geriye-uyum kilidi: select_model verilmezse (mevcut TÜM canlı yapılandırmalar,
    testler) select_cube de ANA modeli kullanır — davranış eskisiyle BİREBİR aynı."""
    gen, calls = _make_anthropic(None)
    gen.select_cube("makine bazında oee", "CUBE katalog metni")
    assert calls[-1]["model"] == "claude-sonnet-4-6"


class _FakeResponse:
    def __init__(self, model: str):
        self._model = model

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": "SELECT 1"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2}}


def test_openai_compatible_select_cube_uses_select_model_when_set(monkeypatch):
    calls: list[dict] = []

    def fake_post(url, json, headers, timeout):  # noqa: A002 - requests.post imzasıyla eşleşir
        calls.append(json)
        return _FakeResponse(json["model"])

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    gen = OpenAICompatibleSqlGenerator(
        "https://api.groq.com/openai/v1", "key", "openai/gpt-oss-120b", "groq",
        select_model="llama-3.1-8b-instant",
    )
    gen.select_cube("makine bazında oee", "CUBE katalog metni")
    assert calls[-1]["model"] == "llama-3.1-8b-instant"
    gen.generate_sql("toplam ciro", {"cubes": []})
    assert calls[-1]["model"] == "openai/gpt-oss-120b"


def test_openai_compatible_no_select_model_falls_back_to_main_model(monkeypatch):
    calls: list[dict] = []

    def fake_post(url, json, headers, timeout):
        calls.append(json)
        return _FakeResponse(json["model"])

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    gen = OpenAICompatibleSqlGenerator(
        "https://api.groq.com/openai/v1", "key", "openai/gpt-oss-120b", "groq",
    )
    gen.select_cube("makine bazında oee", "CUBE katalog metni")
    assert calls[-1]["model"] == "openai/gpt-oss-120b"
