"""Alarm değerlendirme birim testleri — detect_anomalies + check_alert (deterministik,
client gerekmez). Anomali (z-score) sabit eşiğin aksine baseline'dan öğrenir; şema
değişmeden aynı ``threshold`` alanı iki şekli de taşır."""

from app.schedules import check_alert, detect_anomalies


def _rows(*vals: float, measure: str = "tuketim") -> dict:
    return {"rows": [{"gun": f"g{i}", measure: v} for i, v in enumerate(vals)]}


_BASELINE = (10, 11, 9, 10, 10, 11, 9, 10)  # 8 nokta ~10; std'yi tek aykırı domine etmez


def test_anomaly_flags_outlier():
    # Düz bir baseline + tek sıçrama → yalnız aykırı nokta ihlal.
    out = detect_anomalies(_rows(*_BASELINE, 50), "tuketim", k=2.0)
    assert len(out) == 1
    assert "50" in out[0]
    assert "yüksek" in out[0]


def test_anomaly_flat_series_none():
    # Std=0 → istatistik anlamsız, ihlal yok.
    assert detect_anomalies(_rows(10, 10, 10, 10), "tuketim") == []


def test_anomaly_short_series_none():
    # < 4 nokta → güvenilir baseline yok, ihlal yok.
    assert detect_anomalies(_rows(1, 99, 2), "tuketim") == []


def test_anomaly_ignores_nonnumeric():
    r = {"rows": [{"tuketim": v} for v in (*_BASELINE, None, "x", 50)]}
    out = detect_anomalies(r, "tuketim", k=2.0)
    assert len(out) == 1 and "50" in out[0]


def test_check_alert_dispatches_zscore():
    cfg = {"measure": "tuketim", "method": "zscore", "k": 2.0}
    kind, viol = check_alert(cfg, _rows(*_BASELINE, 50))
    assert kind == "anomaly" and len(viol) == 1


def test_check_alert_dispatches_threshold():
    cfg = {"measure": "tuketim", "op": "gt", "value": 40}
    kind, viol = check_alert(cfg, _rows(*_BASELINE, 50))
    assert kind == "threshold" and len(viol) == 1 and "50" in viol[0]


def test_check_alert_empty_config():
    assert check_alert(None, _rows(1, 2, 3)) == ("", [])
    assert check_alert({}, _rows(1, 2, 3)) == ("", [])
    assert check_alert({"method": "zscore"}, _rows(1, 2, 3)) == ("", [])  # measure yok
