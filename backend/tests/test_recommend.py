"""K4 recommend_actions birim testleri — sinyal→aksiyon önerisi. Deterministik.
trend/anomali → 'sürükleyeni bul' drill'i (kullanılmayan ilk boyut); yoğunlaşma → metin."""

from app.cube_router import recommend_actions

_SPEC = {"dimensions": ["sehir", "musteri_adi"],
         "dimension_labels": {"sehir": "şehir", "musteri_adi": "müşteri"}}


def test_trend_yields_drill_action():
    cq = {"cube": "parti", "measures": ["fire"], "dimensions": []}
    recs = recommend_actions([{"kind": "trend"}], cq, _SPEC)
    assert len(recs) == 1
    assert "şehir" in recs[0]["text"]
    assert recs[0]["action"]["cube_query"]["dimensions"] == ["sehir"]  # ilk kullanılmayan boyut


def test_trend_and_anomaly_dedup():
    cq = {"cube": "parti", "measures": ["fire"], "dimensions": []}
    recs = recommend_actions([{"kind": "trend"}, {"kind": "anomaly"}], cq, _SPEC)
    assert len(recs) == 1  # aynı sürükleyen drill → tek öneri


def test_concentration_is_text_only():
    cq = {"cube": "parti", "measures": ["ciro"], "dimensions": ["sehir"]}
    recs = recommend_actions([{"kind": "concentration"}], cq, _SPEC)
    assert len(recs) == 1 and recs[0].get("action") is None


def test_no_driver_when_all_dims_used():
    cq = {"cube": "parti", "measures": ["fire"], "dimensions": ["sehir", "musteri_adi"]}
    recs = recommend_actions([{"kind": "trend"}], cq, _SPEC)
    assert recs == []  # kırılacak boyut kalmadı → drill önerisi yok


def test_no_signals_empty():
    assert recommend_actions([], {"cube": "parti", "dimensions": []}, _SPEC) == []
