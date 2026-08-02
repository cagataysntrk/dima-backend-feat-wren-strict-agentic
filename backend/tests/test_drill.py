"""Faz 4.10 (1 Ağustos 2026) — app/drill.py birim testleri: formül açıklaması, z-skoru
anomali tespiti (app/schedules.py::detect_anomalies İLE AYNI yöntem), dallanma-durumu
geçişleri (expand/select), ilişkili-cube keşfi, ve GÜVENLİ ham-satır SQL üretimi (enjeksiyon
testleri dahil). Hepsi SAF/deterministik — yeni bir LLM çağrısı YOK."""

from __future__ import annotations

import pytest

from app.drill import (
    UnsafeDrillError,
    available_dimensions,
    build_raw_row_sql,
    expand_cube_query,
    flag_outliers,
    formula_explanation,
    jump_to_related_cube,
    kpi_components,
    related_cubes,
    select_cube_query,
    sql_literal,
)

_CUBE_META = {
    "name": "oee",
    "dimensions": ["makine", "vardiya", "hat"],
    "dimension_labels": {"makine": "makine", "vardiya": "vardiya", "hat": "hat"},
    "measure_synonyms_display": {"ort_oee": "ortalama OEE"},
    "time_dimensions": ["tarih"],
}

_MAKINE_DURUSLARI_META = {
    "name": "makine_duruslari",
    "dimensions": ["makine", "vardiya", "hat", "neden"],
    "dimension_labels": {"neden": "duruş nedeni"},
    "time_dimensions": ["tarih"],
    "measures": ["toplam_sure_dk", "duruş_sayisi"],
}

_CARI_META = {"name": "cari", "dimensions": ["cari_kodu", "cari_tip"], "time_dimensions": ["tarih"]}


# --- formula_explanation -----------------------------------------------------

def test_formula_explanation_no_filters_no_dims():
    cq = {"cube": "oee", "measures": ["ort_oee"]}
    text = formula_explanation(cq, _CUBE_META)
    assert "ortalama OEE" in text
    assert "kayıtlar üzerinden" in text


def test_formula_explanation_with_dimension_breakdown():
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
    assert "makine bazında kırılımıdır" in formula_explanation(cq, _CUBE_META)


def test_formula_explanation_with_date_filter():
    cq = {"cube": "oee", "measures": ["ort_oee"],
         "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    assert "2026-01-01" in formula_explanation(cq, _CUBE_META)


def test_formula_explanation_with_category_filter():
    cq = {"cube": "oee", "measures": ["ort_oee"],
         "filters": [{"dimension": "vardiya", "operator": "eq", "value": "sabah"}]}
    assert "vardiya = sabah olan" in formula_explanation(cq, _CUBE_META)


# --- flag_outliers (z-skoru, app/schedules.py::detect_anomalies İLE AYNI yöntem) --------

def test_flag_outliers_detects_low_shift_zscore():
    """Kullanıcının somut senaryosu: sabah vardiyası OEE'si diğerlerinden BELİRGİN düşük."""
    rows = [
        {"vardiya": "sabah", "ort_oee": 0.30},
        {"vardiya": "ogle", "ort_oee": 0.78},
        {"vardiya": "gece", "ort_oee": 0.80},
        {"vardiya": "ekstra", "ort_oee": 0.79},
    ]
    out = flag_outliers(rows, "vardiya", "ort_oee", k=1.0)
    assert out
    assert out[0]["value"] == "sabah"
    assert out[0]["direction"] == "below"
    assert out[0]["z_score"] < 0


def test_flag_outliers_empty_when_too_few_categories():
    rows = [{"vardiya": "sabah", "ort_oee": 0.4}, {"vardiya": "ogle", "ort_oee": 0.8},
            {"vardiya": "gece", "ort_oee": 0.75}]
    assert flag_outliers(rows, "vardiya", "ort_oee") == []  # < 4 kategori


def test_flag_outliers_empty_when_all_similar():
    rows = [{"makine": f"M{i}", "ort_oee": 0.70 + i * 0.001} for i in range(5)]
    assert flag_outliers(rows, "makine", "ort_oee") == []


# --- available_dimensions / related_cubes -------------------------------------

def test_available_dimensions_excludes_used():
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
         "filters": [{"dimension": "vardiya", "operator": "eq", "value": "sabah"}]}
    names = {d["name"] for d in available_dimensions(_CUBE_META, cq)}
    assert names == {"hat"}


def test_related_cubes_finds_shared_dimension_cubes():
    """Kullanıcının somut senaryosu: OEE düşükken 'makine'/'vardiya' boyutunu PAYLAŞAN
    makine_duruslari (duruş nedeni) cube'u kök-neden adayı olarak bulunmalı; cari (ortak
    boyutu olmayan) BULUNMAMALI."""
    all_cubes = [_CUBE_META, _MAKINE_DURUSLARI_META, _CARI_META]
    result = related_cubes("oee", {"makine", "vardiya"}, all_cubes)
    names = {r["cube"] for r in result}
    assert "makine_duruslari" in names
    assert "cari" not in names
    md = next(r for r in result if r["cube"] == "makine_duruslari")
    assert set(md["shared_dimensions"]) == {"makine", "vardiya"}


def test_related_cubes_excludes_self():
    result = related_cubes("oee", {"makine"}, [_CUBE_META, _MAKINE_DURUSLARI_META])
    assert all(r["cube"] != "oee" for r in result)


# --- expand_cube_query / select_cube_query (durum geçişleri, saf) -------------

def test_expand_cube_query_adds_dimension_without_mutating_input():
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
    new_cq = expand_cube_query(cq, "vardiya")
    assert new_cq["dimensions"] == ["makine", "vardiya"]
    assert cq["dimensions"] == ["makine"]  # girdi DEĞİŞMEDİ


def test_expand_cube_query_no_duplicate():
    cq = {"cube": "oee", "dimensions": ["makine"]}
    new_cq = expand_cube_query(cq, "makine")
    assert new_cq["dimensions"] == ["makine"]


def test_select_cube_query_moves_dimension_to_filter():
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya"]}
    new_cq = select_cube_query(cq, "vardiya", "sabah")
    assert new_cq["dimensions"] == []
    assert new_cq["filters"] == [{"dimension": "vardiya", "operator": "eq", "value": "sabah"}]
    assert cq["dimensions"] == ["vardiya"]  # girdi DEĞİŞMEDİ


def test_select_cube_query_replaces_existing_filter_for_same_dimension():
    cq = {"cube": "oee", "dimensions": ["vardiya"],
         "filters": [{"dimension": "vardiya", "operator": "eq", "value": "gece"}]}
    new_cq = select_cube_query(cq, "vardiya", "sabah")
    assert new_cq["filters"] == [{"dimension": "vardiya", "operator": "eq", "value": "sabah"}]


# --- jump_to_related_cube (yalnız PAYLAŞILAN boyutlar taşınır) ----------------

def test_jump_to_related_cube_keeps_only_shared_dimensions():
    cq = {"cube": "oee", "measures": ["ort_oee"], "dimensions": [],
         "filters": [{"dimension": "makine", "operator": "eq", "value": "M3"},
                    {"dimension": "vardiya", "operator": "eq", "value": "sabah"}],
         "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    new_cq = jump_to_related_cube(cq, "makine_duruslari", _MAKINE_DURUSLARI_META)
    assert new_cq["cube"] == "makine_duruslari"
    assert new_cq["measures"] == _MAKINE_DURUSLARI_META["measures"]
    assert {f["dimension"] for f in new_cq["filters"]} == {"makine", "vardiya"}
    assert new_cq["timeDimensions"] == [{"dimension": "tarih", "granularity": "month"}]


def test_jump_to_related_cube_drops_unshared_filter():
    cq = {"cube": "oee", "filters": [{"dimension": "hat", "operator": "eq", "value": "H1"},
                                     {"dimension": "makine", "operator": "eq", "value": "M3"}]}
    target = {"name": "sadece_makine", "dimensions": ["makine"], "measures": ["x"]}
    new_cq = jump_to_related_cube(cq, "sadece_makine", target)
    assert {f["dimension"] for f in new_cq["filters"]} == {"makine"}


# --- sql_literal / build_raw_row_sql (GÜVENLİK-KRİTİK: enjeksiyon testleri) ---
#
# `columns` Faz A2'de ZORUNLU oldu: eskiden `SELECT *` üretiliyordu ve ham satır demek
# cube'un yayımlamadığı HER kolon demekti (`personel_ozluk.tc_kimlik` dahil). Aşağıdaki
# testlerin amacı değişmedi (şekil / IN / enjeksiyon kaçışı / tarih atlama + limit tavanı);
# yalnız yeni sözleşmeye uyduruldu. Kolon seçiminin KENDİ testleri:
# `tests/test_drill_raw_guvenlik.py`.
_KOL = ["makine", "vardiya"]

def test_sql_literal_escapes_single_quote():
    assert sql_literal("it's") == "'it''s'"


def test_sql_literal_numbers_unquoted():
    assert sql_literal(42) == "42"
    assert sql_literal(3.14) == "3.14"


def test_build_raw_row_sql_basic_shape():
    sql = build_raw_row_sql("oee_vardiya", [{"dimension": "makine", "operator": "eq", "value": "M3"}],
                            columns=_KOL)
    assert sql == "SELECT makine, vardiya FROM oee_vardiya WHERE makine = 'M3' LIMIT 50"


def test_build_raw_row_sql_in_operator():
    sql = build_raw_row_sql("oee_vardiya",
                            [{"dimension": "makine", "operator": "in", "value": ["M1", "M2"]}],
                            columns=_KOL)
    assert "makine IN ('M1', 'M2')" in sql


def test_build_raw_row_sql_injection_attempt_in_value_is_escaped():
    """Kötü niyetli bir DEĞER (ör. bir kategori adı gibi görünen ama SQL enjeksiyonu
    deneyen bir string) asla ham SQL'e sızmamalı — tek tırnak katlanarak escape edilir."""
    malicious = "M3'; DROP TABLE oee_vardiya; --"
    sql = build_raw_row_sql("oee_vardiya", [{"dimension": "makine", "operator": "eq",
                                             "value": malicious}], columns=_KOL)
    assert "DROP TABLE" in sql  # literal İÇİNDE zararsızca durur
    assert sql.count("'") % 2 == 0  # tüm tırnaklar dengeli (kaçış çalıştı)
    assert "--" in sql and sql.strip().endswith("LIMIT 50")  # yorum satırı SQL'i KESMEDİ


def test_build_raw_row_sql_rejects_unsafe_base_object():
    with pytest.raises(UnsafeDrillError):
        build_raw_row_sql("oee_vardiya; DROP TABLE x", [], columns=_KOL)


def test_build_raw_row_sql_rejects_unsafe_dimension_name():
    with pytest.raises(UnsafeDrillError):
        build_raw_row_sql("oee_vardiya", [{"dimension": "makine; DROP TABLE x", "operator": "eq",
                                           "value": "M3"}], columns=_KOL)


def test_build_raw_row_sql_skips_date_filters_and_caps_limit():
    sql = build_raw_row_sql("oee_vardiya",
                            [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}],
                            limit=99999, columns=_KOL)
    assert "tarih" not in sql  # tarih filtresi bu sürümde atlanır (dialect-özel, ayrı ele alınmalı)
    assert "LIMIT 500" in sql  # üst sınıra (500) kırpıldı


# --- kpi_components ------------------------------------------------------------

def test_kpi_components_none_when_no_kpi():
    assert kpi_components(None) is None
    assert kpi_components({}) is None


def test_kpi_components_normalizes_shape():
    kpi = {"kpi": "ccc", "components": [
        {"key": "dso", "label": "DSO", "value": 45.0, "unit": "gün"},
        {"key": "dio", "label": "DIO", "value": None, "unit": "gün"},
    ]}
    assert kpi_components(kpi) == [{"name": "dso", "label": "DSO", "value": 45.0, "unit": "gün"}]
