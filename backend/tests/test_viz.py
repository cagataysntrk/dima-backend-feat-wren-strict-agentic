"""Viz öneri motoru (app.viz) — deterministik grafik/tablo/pivot kararı davranış kilidi.

Standart temeli: docs/research/viz-oneri-standartlari-2026-07.md (Mackinlay Show Me + Cleveland-
McGill + çok-birim politikası). Karar saf kural (LLM yok): aynı girdi → aynı VizSpec.
"""

from __future__ import annotations

from app import viz


def _r(columns, rows):
    return {"columns": columns, "rows": rows, "row_count": len(rows)}


def rec(columns, rows, units=None, lower=None, cube_query=None):
    return viz.recommend(_r(columns, rows), units=units, lower_set=lower, cube_query=cube_query)


# --- taban mark seçimi (Show Me tablosu) ------------------------------------

def test_single_row_measures_kpi():
    s = rec(["ciro"], [{"ciro": 100}], units={"ciro": "₺"})
    assert s["kind"] == "kpi"


def test_category_measure_bar():
    s = rec(["musteri", "ciro"],
            [{"musteri": "A", "ciro": 10}, {"musteri": "B", "ciro": 20},
             {"musteri": "C", "ciro": 5}], units={"ciro": "₺"})
    assert s["kind"] == "bar"


def test_time_measure_line():
    s = rec(["tarih", "ciro"],
            [{"tarih": "2026-01", "ciro": 10}, {"tarih": "2026-02", "ciro": 20}],
            units={"ciro": "₺"})
    assert s["kind"] == "line"
    assert s["time_col"] == "tarih"


def test_two_category_matrix_heatmap():
    rows = [{"vardiya": v, "gun": g, "oee": 70 + i}
            for i, (v, g) in enumerate(
                [(v, g) for v in ("A", "B", "C") for g in ("Pzt", "Sal", "Çar")])]
    s = rec(["vardiya", "gun", "oee"], rows, units={"oee": "%"})
    assert s["kind"] == "heatmap"


def test_no_measure_table():
    s = rec(["musteri", "sehir"],
            [{"musteri": "A", "sehir": "İst"}, {"musteri": "B", "sehir": "Ank"}])
    assert s["kind"] == "table"


# --- çok-birim politikası (§3) ----------------------------------------------

def test_one_unit_stays_single_axis():
    # 2 ölçü AYNI birim → tek eksen (facet_measure DEĞİL), dual_axis değil
    s = rec(["ay", "ciro", "maliyet"],
            [{"ay": "2026-01", "ciro": 10, "maliyet": 6},
             {"ay": "2026-02", "ciro": 20, "maliyet": 9}],
            units={"ciro": "₺", "maliyet": "₺"})
    assert s["kind"] == "line"
    assert s["unit_count"] == 1
    assert s["dual_axis"] is False
    assert s["facet_measure"] is None


def test_two_units_dual_axis():
    s = rec(["ay", "ciro", "oee"],
            [{"ay": "2026-01", "ciro": 10, "oee": 80},
             {"ay": "2026-02", "ciro": 20, "oee": 82}],
            units={"ciro": "₺", "oee": "%"})
    assert s["kind"] == "line"
    assert s["unit_count"] == 2
    assert s["dual_axis"] is True


def test_three_units_facet_measure():
    # ≥3 farklı birim → tek grafiğe BİNMEZ → ölçüye-göre small multiples
    s = rec(["ay", "ciro", "fire_kg", "oee"],
            [{"ay": "2026-01", "ciro": 10, "fire_kg": 5, "oee": 80},
             {"ay": "2026-02", "ciro": 20, "fire_kg": 6, "oee": 82}],
            units={"ciro": "₺", "fire_kg": "kg", "oee": "%"})
    assert s["kind"] == "facet_measure"
    assert s["unit_count"] == 3
    assert s["facet_measure"]["measures"] == ["ciro", "fire_kg", "oee"]
    assert s["facet_measure"]["x"] == "ay"


# --- yeni mark'lar ----------------------------------------------------------

def test_scatter_two_measures_identity_dim():
    rows = [{"m": f"M{i}", "ciro": i * 10, "fire": i * 2} for i in range(10)]
    s = rec(["m", "ciro", "fire"], rows, units={"ciro": "₺", "fire": "kg"})
    assert s["kind"] == "scatter"
    assert s["scatter"]["x"] == "ciro" and s["scatter"]["y"] == "fire"
    assert s["scatter"]["color"] == "m"


def test_scatter_size_third_measure():
    rows = [{"m": f"M{i}", "a": i, "b": i * 2, "c": i * 3} for i in range(9)]
    s = rec(["m", "a", "b", "c"], rows, units={"a": "₺", "b": "kg", "c": "L"})
    # 3+ ölçü + kimlik boyutu → scatter, 3. ölçü nokta boyutu
    assert s["kind"] == "scatter"
    assert s["scatter"].get("size") == "c"


def test_scatter_not_for_few_categories():
    # az kategoride (≤~12 ama <8 satır) gruplu bar/kombo daha okunur → scatter DEĞİL
    rows = [{"m": f"M{i}", "ciro": i * 10, "fire": i * 2} for i in range(4)]
    s = rec(["m", "ciro", "fire"], rows, units={"ciro": "₺", "fire": "kg"})
    assert s["kind"] != "scatter"


def test_stacked_midcard_additive_series():
    rows = ([{"ay": "2026-01", "urun": u, "adet": i} for i, u in enumerate("abcde")]
            + [{"ay": "2026-02", "urun": u, "adet": i + 1} for i, u in enumerate("abcde")])
    s = rec(["ay", "urun", "adet"], rows, units={"adet": ""})
    assert s["kind"] == "stacked"
    assert s["stackable"] is True


def test_intensive_measure_not_stacked():
    # oran/% additive değil → yığma YANLIŞ → stacked DEĞİL, stackable False
    rows = ([{"ay": "2026-01", "urun": u, "oee_yuzde": 70 + i} for i, u in enumerate("abcde")]
            + [{"ay": "2026-02", "urun": u, "oee_yuzde": 72 + i} for i, u in enumerate("abcde")])
    s = rec(["ay", "urun", "oee_yuzde"], rows, units={"oee_yuzde": "%"})
    assert s["kind"] != "stacked"
    assert s["stackable"] is False


def test_pivot_two_categories_multi_measure():
    # 2 kategorik boyut + 2 ölçü → heatmap tek ölçü içindir → pivot
    rows = [{"bolge": b, "urun": u, "ciro": 1, "adet": 2}
            for b in ("K", "G", "D") for u in ("a", "b", "c")]
    s = rec(["bolge", "urun", "ciro", "adet"], rows, units={"ciro": "₺", "adet": ""})
    assert s["kind"] == "pivot"
    assert s["pivot"]["measures"] == ["ciro", "adet"]
    assert s["table_mode"] == "pivot"


def test_partition_single_dim_additive_pie_alt():
    s = rec(["urun", "ciro"],
            [{"urun": "a", "ciro": 10}, {"urun": "b", "ciro": 20},
             {"urun": "c", "ciro": 5}], units={"ciro": "₺"})
    assert s["kind"] == "bar"  # Cleveland-McGill: bar varsayılan kalır
    assert s["partition"] is True
    assert s["alternatives"] == ["pie"]  # ≤6 kategori → pie önerisi


def test_partition_many_categories_treemap_alt():
    rows = [{"urun": f"u{i}", "ciro": i + 1} for i in range(10)]
    s = rec(["urun", "ciro"], rows, units={"ciro": "₺"})
    assert s["partition"] is True
    assert s["alternatives"] == ["treemap"]  # >6 kategori → treemap


# --- DÖNEMSEL KIYAS (YoY/MoM) — türetilmiş ölçüler enhancement'ı yanıltmamalı ---------

_YOY_CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya"], "compare": "yoy"}


def test_yoy_numeric_dim_stays_bar_not_facet():
    # regresyon: sayısal boyut (vardiya 1/2/3) + türetilmiş YoY ölçüleri → panel/facet DEĞİL, bar.
    rows = [{"vardiya": 1, "ort_oee": 0.56, "ort_oee_gecen": 0.54, "ort_oee_degisim_yuzde": 3.7},
            {"vardiya": 2, "ort_oee": 0.63, "ort_oee_gecen": 0.60, "ort_oee_degisim_yuzde": 5.0},
            {"vardiya": 3, "ort_oee": 0.52, "ort_oee_gecen": 0.55, "ort_oee_degisim_yuzde": -5.5}]
    s = rec(["vardiya", "ort_oee", "ort_oee_gecen", "ort_oee_degisim_yuzde"], rows,
            units={"ort_oee": "%"}, cube_query=_YOY_CQ)
    assert s["kind"] == "bar"
    assert s["dims"] == ["vardiya"]  # sayısal ama BOYUT (cube_query otoritesi)
    assert s["measures"] == ["ort_oee", "ort_oee_gecen", "ort_oee_degisim_yuzde"]
    assert s["facet_measure"] is None
    assert s["partition"] is False  # YoY bar'a pay grafiği önerilmez


def test_yoy_identity_dim_not_scatter():
    # regresyon: kimlik-boyut (10 müşteri) + YoY → ciro vs ciro_gecen SERPME değil, bar.
    rows = [{"m": f"M{i}", "ciro": i * 10.0, "ciro_gecen": i * 9.0, "ciro_degisim_yuzde": 11.0}
            for i in range(10)]
    cq = {"cube": "x", "measures": ["ciro"], "dimensions": ["m"], "compare": "yoy"}
    s = rec(["m", "ciro", "ciro_gecen", "ciro_degisim_yuzde"], rows,
            units={"ciro": "₺"}, cube_query=cq)
    assert s["kind"] == "bar"
    assert s["scatter"] is None


def test_yoy_time_series_stays_line():
    rows = [{"ay": f"2026-0{i}", "ciro": i * 100.0, "ciro_gecen": i * 90.0,
             "ciro_degisim_yuzde": 11.0} for i in range(1, 6)]
    cq = {"cube": "x", "measures": ["ciro"], "compare": "yoy",
          "timeDimensions": [{"dimension": "ay", "granularity": "month"}]}
    s = rec(["ay", "ciro", "ciro_gecen", "ciro_degisim_yuzde"], rows,
            units={"ciro": "₺"}, cube_query=cq)
    assert s["kind"] == "line"
    assert s["time_col"] == "ay"
    assert s["facet_measure"] is None


def test_numeric_dimension_authoritative():
    # cube_query boyutu sayısal olsa da ÖLÇÜ sanılmaz (vardiya 1/2/3 → boyut).
    rows = [{"vardiya": 1, "ort_oee": 0.56}, {"vardiya": 2, "ort_oee": 0.63},
            {"vardiya": 3, "ort_oee": 0.52}]
    s = rec(["vardiya", "ort_oee"], rows, units={"ort_oee": "%"},
            cube_query={"cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya"]})
    assert s["dims"] == ["vardiya"] and s["measures"] == ["ort_oee"]
    assert s["kind"] == "bar"


# --- güvenlik / determinizm -------------------------------------------------

def test_empty_result_none():
    assert viz.recommend(None) is None
    assert viz.recommend({"columns": [], "rows": []}) is None


def test_deterministic():
    args = (["ay", "ciro", "oee"],
            [{"ay": "2026-01", "ciro": 10, "oee": 80},
             {"ay": "2026-02", "ciro": 20, "oee": 82}])
    u = {"ciro": "₺", "oee": "%"}
    assert rec(*args, units=u) == rec(*args, units=u)


def test_lower_set_passthrough():
    s = rec(["makine", "fire"],
            [{"makine": "M1", "fire": 3}, {"makine": "M2", "fire": 5}],
            units={"fire": "kg"}, lower=["fire"])
    assert s["lower_set"] == ["fire"]
