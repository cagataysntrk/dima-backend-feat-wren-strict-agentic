"""Faz 4.13a (1 Ağustos 2026) — dış yol haritası görev 2.17 "güven rozeti" (kabul testi
UC-2.21: "Aynı tip sorgu iki kez yapılır → Her ikisinde de AYNI güven rozeti verilir;
rozetin gerekçesi açıklanabilir"): `explain.confidence` sessiz bir varsayım (ör. "tüm
zamanlar" otomatik/chip'le onaylandı) yapıldığında bir kademe DÜŞÜRÜLÜR — frontend'in
🥇/🥈/🥉 rozetinin AYNI `source`'tan gelen iki yanıtı (varsayımlı/varsayımsız) ayırt
edebilmesi için somut bir sinyal."""

from __future__ import annotations

from tests.conftest import ask


def test_confidence_lower_when_all_time_assumption_made(client):
    d1 = ask(client, "makine bazında ortalama oee")
    assert "dönem" in (d1["note"] or "").lower()
    d2 = ask(client, "tüm zamanlar", cube_query=d1["cube_query"])
    assert d2["source"] == "cube"
    assert d2["explain"]["assumptions"]  # "tüm zamanlar" varsayımı kayıtlı
    assert d2["explain"]["confidence"] == 0.85  # 1.0 (cube) - 0.15


def test_confidence_full_when_no_assumption_made(client):
    """AYNI cube/kaynak (source='cube') ama AÇIK bir dönem verilince varsayım YOK —
    confidence düşürülmemiş TAM değerinde kalmalı (regresyon kilidi)."""
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    assert d["source"] == "cube"
    assert not d["explain"]["assumptions"]
    assert d["explain"]["confidence"] == 1.0


def test_confidence_same_badge_when_same_question_asked_twice(client):
    """UC-2.21 literal senaryo: "Aynı tip sorgu iki kez yapılır → Her ikisinde de AYNI
    güven rozeti verilir." Ayrı oturumlarda/çağrılarda rastgelelik YOK (confidence
    yalnız source+assumptions'ın SAF bir fonksiyonu) — bu, tekrar-sorulmayla determinizmi
    açıkça kanıtlar (yukarıdaki testler bunu YALNIZ ima eder, burada BİREBİR test edilir)."""
    d1 = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    d2 = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    assert d1["source"] == d2["source"] == "cube"
    assert d1["explain"]["confidence"] == d2["explain"]["confidence"] == 1.0


def test_confidence_none_for_rule_path_untouched_by_assumption_logic():
    """`confidence=None` (LLM/rule) yollarında varsayım-düşürme UYGULANMAZ (None - 0.15
    anlamsız olurdu) — bu davranış _build_explain'de `confidence is not None` koşuluyla
    zaten korunuyor; bu test o korumayı BİREBİR sabitler."""
    from app.routers.ask import _build_explain
    from app.schemas import AskResponse

    resp = AskResponse(question="x", source="rule", cube_query={"period_confirmed": True})
    explain = _build_explain(resp)
    assert explain.confidence is None
