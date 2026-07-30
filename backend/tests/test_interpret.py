"""Evrensel çıktı yorumlama (app.interpret) — deterministik davranış kilidi.

Yorum TAMAMEN deterministik olmalı (LLM yok): aynı girdi → aynı çıktı, ham veri dışa çıkmaz.
"""

from __future__ import annotations

from app.interpret import interpret


def _r(columns, rows):
    return {"columns": columns, "rows": rows, "row_count": len(rows)}


def test_time_series_trend_direction_and_pct():
    r = _r(["ay", "satis"], [{"ay": "2024-01", "satis": 100}, {"ay": "2024-02", "satis": 130}])
    out = interpret(r, {"measures": ["satis"]})
    assert out is not None
    # ilk→son %30 arttı; tepe/dip kova
    assert "%30" in out["summary"] and "arttı" in out["summary"]
    assert any(f["type"] == "trend" for f in out["facts"])


def test_top_n_share_of_total():
    r = _r(["cari", "tutar"], [{"cari": "A", "tutar": 700}, {"cari": "B", "tutar": 300}])
    out = interpret(r, {"measures": ["tutar"]})
    assert "En yüksek" in out["summary"] and "A" in out["summary"]
    # A toplamın %70'i
    assert "%70" in out["summary"]


def test_single_value():
    out = interpret(_r(["toplam"], [{"toplam": 1234}]), units={"toplam": "₺"})
    assert out["facts"][0]["type"] == "single"
    assert "₺1.234" in out["summary"]


def test_kpi_value_and_components():
    kpi = {"kpi": "ccc", "label": "CCC", "unit": "gün", "value": 47.3,
           "components": [{"key": "dso", "label": "DSO", "value": 32.1, "unit": "gün"}]}
    out = interpret(None, kpi=kpi)
    assert "CCC" in out["summary"] and "DSO" in out["summary"]


def test_empty_result_returns_none():
    assert interpret(_r(["x"], []), {"measures": []}) is None
    assert interpret(None) is None


def test_lower_is_better_frames_direction():
    # DSO (düşük=iyi) artışı → OLUMSUZ çerçevelenir
    r = _r(["ay", "dso"], [{"ay": "2024-01", "dso": 30}, {"ay": "2024-02", "dso": 45}])
    out = interpret(r, {"measures": ["dso"]}, lower_is_better={"dso"})
    assert "olumsuz" in out["summary"].lower()
    trend = next(f for f in out["facts"] if f["type"] == "trend")
    assert trend["favorable"] is False


def test_lower_is_better_decrease_is_improvement():
    r = _r(["ay", "ccc"], [{"ay": "2024-01", "ccc": 60}, {"ay": "2024-02", "ccc": 40}])
    out = interpret(r, {"measures": ["ccc"]}, lower_is_better={"ccc"})
    assert "iyileşti" in out["summary"].lower()


def test_neutral_measure_no_value_judgment():
    # lower_is_better DEĞİL → "yüksek=iyi" varsayılmaz, nötr kalır (yanıltma yok)
    r = _r(["ay", "adet"], [{"ay": "2024-01", "adet": 30}, {"ay": "2024-02", "adet": 45}])
    out = interpret(r, {"measures": ["adet"]})
    assert "olumsuz" not in out["summary"].lower() and "iyileşti" not in out["summary"].lower()


def test_deterministic_same_input_same_output():
    r = _r(["ay", "satis"], [{"ay": "2024-01", "satis": 50}, {"ay": "2024-02", "satis": 40}])
    assert interpret(r) == interpret(r)  # aynı girdi → aynı çıktı (LLM yok)
