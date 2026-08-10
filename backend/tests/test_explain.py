"""Faz 3 — birleşik `explain` nesnesi ({path, confidence, assumptions}): EKLEYİCİ
(trace/source SİLİNMEDİ, ikisi paralel durur) — bkz. app/routers/ask.py::_build_explain."""

from __future__ import annotations

from tests.conftest import ask


def test_explain_cube_path_full_confidence_no_assumptions(client):
    d1 = ask(client, "makine bazında ortalama oee")
    assert any(s["label"] == "Tümü" for s in d1["suggestions"])
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    assert d["source"] == "cube"
    assert d["explain"] is not None
    assert d["explain"]["path"].startswith("cube (route()")
    assert d["explain"]["confidence"] == 1.0
    assert d["explain"]["assumptions"] == []  # dönem AÇIKÇA belirtildi ("bu yıl")


def test_explain_all_time_chip_records_assumption(client):
    d1 = ask(client, "makine bazında ortalama oee")
    d = ask(client, "tüm zamanlar", cube_query=d1["cube_query"])
    assert d["source"] == "cube"
    assert d["explain"] is not None
    # Faz 4.13a (1 Ağustos 2026): sessiz bir varsayım yapıldığında (burada "tüm zamanlar")
    # confidence artık BİR KADEME DÜŞÜRÜLÜR (1.0 → 0.85) — dış yol haritası 2.17 "güven
    # rozeti"nin varsayımlı/varsayımsız aynı-source yanıtları ayırt edebilmesi için.
    # Önceden (Faz 3) assumptions confidence'ı ETKİLEMİYORDU — bu BİLİNÇLİ bir davranış
    # değişikliği (bkz. app/routers/ask.py::_build_explain), eski değer (1.0) değil.
    assert d["explain"]["confidence"] == 0.85
    assert len(d["explain"]["assumptions"]) == 1
    assert "tüm zamanlar" in d["explain"]["assumptions"][0].lower()


def test_explain_none_for_clarification_response(client):
    """⟳ **POLİTİKA DEVRİ (`D3`): dönemsiz soru artık NETLEŞTİRME DEĞİL, BEYANLI CEVAP.**

    Eski sözleşme: dönem yoksa `source=None` + soru → makbuz yok, çünkü rapor yok.
    Yeni sözleşme (`varsayilan_donem` `beta`, korpus A/B'yle ölçüldü — doğru-cube
    %94,9→%95,0, `sessiz_yanlis` **8→8 değişmedi**): rapor **üretilir**, varsayım
    **beyan edilir** ve `§TZ` ile **tek tıkla** düzeltilebilir.

    🔴 O hâlde makbuzun `None` olması artık bir kusur olurdu: ortada bir rapor var ve
    **bir varsayım** taşıyor — makbuzun var olma sebebi tam olarak budur. Kapı bu yüzden
    tersine çevrildi: *«makbuz yok»* yerine *«makbuz VAR ve varsayımı YAZIYOR»*.

    ⊙ Eski beklenti silinmedi, **devredildi**: netleştirme yolu hâlâ yaşıyor (bayrak
    kapalıyken, `KURAL B`) ve orada `explain` yine `None`dır.

    *Bir sözleşmeyi değiştirmek, onu koruyan kapıyı kaldırmak değil, kapının neyi
    koruduğunu yeniden yazmaktır.*
    """
    d1 = ask(client, "makine bazında ortalama oee")
    assert d1["source"] == "cube", "🔴 beyanlı varsayım bir CEVAP üretmeli"
    assert d1["explain"] is not None, "🔴 rapor varsa makbuz da olmalı"
    assert d1["explain"]["assumptions"], (
        "🔴 varsayım YAPILDI ama makbuz onu yazmıyor — sessiz varsayım en pahalı kusurdur")
    assert any(s["label"] == "Tümü" for s in d1["suggestions"]), (
        "🔴 `§TZ`: beyanın yanında tek-tık düzeltme olmalı")


def test_explain_meta_question_has_no_assumptions(client):
    d = ask(client, "dima nedir")
    assert d["source"] == "meta"
    assert d["explain"] is not None
    assert d["explain"]["path"].startswith("meta")
    assert d["explain"]["confidence"] == 1.0
