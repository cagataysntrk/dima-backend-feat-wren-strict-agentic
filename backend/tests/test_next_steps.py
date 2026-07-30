"""K2 suggest_next_steps birim testleri — deterministik, DB yok. Katalog index'ten
kırılım (boyut) / ölçek (measure) / zaman granülerliği önerileri türetir; her öneri
TAM cube_query taşır (FE /cube ile LLM'siz koşar)."""

from app.cube_router import suggest_next_steps

_INDEX = {
    "parti": {
        "name": "parti",
        "measures": ["toplam_ciro", "toplam_adet", "ort_fiyat"],
        "dimensions": ["sehir", "musteri_adi", "musteri_kodu"],
        "time_dimensions": ["tarih"],
        "dimension_labels": {"sehir": "şehir", "musteri_adi": "müşteri",
                             "musteri_kodu": "müşteri kodu"},
        "measure_synonyms_display": {"toplam_ciro": "ciro", "toplam_adet": "adet",
                                     "ort_fiyat": "ortalama fiyat"},
    }
}


def _kinds(steps):
    return [s["kind"] for s in steps]


def test_unknown_cube_returns_empty():
    assert suggest_next_steps({"cube": "yok"}, _INDEX) == []
    assert suggest_next_steps({}, _INDEX) == []


def test_dimension_measure_and_time_suggested():
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": []}
    steps = suggest_next_steps(cq, _INDEX)
    labels = [s["label"] for s in steps]
    # kırılım: şehir + müşteri (musteri_kodu, _adi kardeşi varken elenir)
    assert "şehir kırılımı" in labels
    assert "müşteri kırılımı" in labels
    assert "müşteri kodu kırılımı" not in labels
    # ölçek: kullanılmayan ölçüler
    assert "+ adet" in labels and "+ ortalama fiyat" in labels
    # zaman: trend yok → aylık trend
    assert "Aylık trend" in labels


def test_kirilim_carries_full_cube_query():
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": [],
          "filters": [{"dimension": "tarih", "operator": "gte", "values": ["2026-01-01"]}]}
    steps = suggest_next_steps(cq, _INDEX)
    sehir = next(s for s in steps if s["label"] == "şehir kırılımı")
    # mevcut ölçü + filtre KORUNUR, sadece boyut eklenir → deterministik /cube
    assert sehir["cube_query"]["dimensions"] == ["sehir"]
    assert sehir["cube_query"]["measures"] == ["toplam_ciro"]
    assert sehir["cube_query"]["filters"] == cq["filters"]


def test_two_dims_no_more_kirilim():
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["sehir", "musteri_adi"]}
    steps = suggest_next_steps(cq, _INDEX)
    assert "dimension" not in _kinds(steps)  # 2 kırılım → satır patlaması, dur


def test_time_granularity_drills_finer():
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": [],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    steps = suggest_next_steps(cq, _INDEX)
    time_step = next(s for s in steps if s["kind"] == "time")
    assert time_step["label"] == "Haftalık detay"
    assert time_step["cube_query"]["timeDimensions"][0]["granularity"] == "week"


def test_caps_suggestion_count():
    cq = {"cube": "parti", "measures": [], "dimensions": []}
    steps = suggest_next_steps(cq, _INDEX)
    assert len(steps) <= 6
    assert len([s for s in steps if s["kind"] == "measure"]) <= 2
