"""K3 proaktif sinyaller (interpret._signals) — anomali / yön endişesi / yoğunlaşma.
Deterministik; interpret() üzerinden entegrasyon. Ham veri LLM'e gitmez."""

from app.interpret import interpret


def _ts(measure, vals):
    rows = [{"tarih": f"2026-{i + 1:02d}", measure: v} for i, v in enumerate(vals)]
    return {"columns": ["tarih", measure], "rows": rows, "row_count": len(rows)}


def _sig_kinds(res):
    return {s["kind"] for s in (res or {}).get("signals", [])}


def test_anomaly_signal_on_outlier():
    res = interpret(_ts("tuketim", [10, 11, 9, 10, 10, 11, 9, 10, 60]))
    assert "anomaly" in _sig_kinds(res)


def test_rising_lower_is_better_warns():
    # fire (düşük=iyi) %50 arttı → yön endişesi.
    res = interpret(_ts("fire", [10, 12, 14, 15]), lower_is_better={"fire"})
    kinds = _sig_kinds(res)
    assert "trend" in kinds


def test_rising_normal_measure_no_trend_signal():
    # ciro (yüksek=iyi) artışı KÖTÜ değil → trend sinyali yok.
    res = interpret(_ts("ciro", [100, 120, 140, 160]))
    assert "trend" not in _sig_kinds(res)


def test_concentration_signal():
    res = interpret({"columns": ["sehir", "ciro"],
                     "rows": [{"sehir": "İstanbul", "ciro": 800},
                              {"sehir": "Ankara", "ciro": 120},
                              {"sehir": "İzmir", "ciro": 80}],
                     "row_count": 3})
    assert "concentration" in _sig_kinds(res)


def test_flat_series_no_signals():
    res = interpret(_ts("ciro", [100, 101, 100, 101, 100, 101]))
    assert not (res or {}).get("signals")
