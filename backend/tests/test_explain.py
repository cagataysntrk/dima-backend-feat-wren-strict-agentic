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
    assert d["explain"]["confidence"] == 1.0
    assert len(d["explain"]["assumptions"]) == 1
    assert "tüm zamanlar" in d["explain"]["assumptions"][0].lower()


def test_explain_none_for_clarification_response(client):
    d1 = ask(client, "makine bazında ortalama oee")
    assert d1["source"] is None  # yalnız netleştirme, henüz rapor yok
    assert d1["explain"] is None


def test_explain_meta_question_has_no_assumptions(client):
    d = ask(client, "dima nedir")
    assert d["source"] == "meta"
    assert d["explain"] is not None
    assert d["explain"]["path"].startswith("meta")
    assert d["explain"]["confidence"] == 1.0
