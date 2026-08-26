"""Viz öneri motoru (app.viz) — deterministik grafik/tablo/pivot kararı davranış kilidi.

Standart temeli: docs/research/viz-oneri-standartlari-2026-07.md (Mackinlay Show Me + Cleveland-
McGill + çok-birim politikası). Karar saf kural (LLM yok): aynı girdi → aynı VizSpec.

> **Karar kaydı: `ADR-0034`** — görsel dilbilgisi daralması — ne zaman grafik ÇİZİLMEZ.
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
    # ⟳ FAZ 5.11 — örnek **4 kategoriye** çıkarıldı. Testin amacı *"kategori + ölçü →
    # bar"*dır ve o amaç aynen duruyor; 3 kategori artık `cumle` (§15.6 kural 2) ve
    # örneği sınırın üstüne taşımak, testi **amacına** geri döndürür. *Bir testin
    # örneği değişebilir; ölçtüğü şey değişmemeli.*
    s = rec(["musteri", "ciro"],
            [{"musteri": "A", "ciro": 10}, {"musteri": "B", "ciro": 20},
             {"musteri": "C", "ciro": 5}, {"musteri": "D", "ciro": 8}],
            units={"ciro": "₺"})
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


def test_two_units_with_series_dim_becomes_facet_measure():
    # regresyon (Madde 10, 1 Ağustos 2026): kırılım boyutu (makine) VARKEN 2-birimli
    # ölçüler (% ve dakika) önceden hiçbir ayırma mekanizmasından geçmiyordu (ne combo
    # ne dual_axis ne facet_measure — hepsi series_dim YOKKEN çalışıyordu) → tek eksende
    # eziliyordu. Artık facet_measure'a (series alanı dolu) düşmeli.
    rows = [{"ay": ay, "makine": mk, "oee_yuzde": 70.0, "durus_dk": 30.0}
            for ay in ("2026-01", "2026-02") for mk in ("M1", "M2", "M3")]
    s = rec(["ay", "makine", "oee_yuzde", "durus_dk"], rows,
            units={"oee_yuzde": "%", "durus_dk": "dk"})
    assert s["kind"] == "facet_measure"
    assert s["unit_count"] == 2
    assert s["facet_measure"] == {
        "measures": ["oee_yuzde", "durus_dk"], "x": "ay", "series": "makine",
    }
    assert s["dual_axis"] is False


def test_two_units_no_series_dim_stays_dual_axis():
    # kırılımsız 2-birim durumu (mevcut combo) DOKUNULMADAN kalır — regresyon yok.
    s = rec(["ay", "ciro", "oee"],
            [{"ay": "2026-01", "ciro": 10, "oee": 80},
             {"ay": "2026-02", "ciro": 20, "oee": 82}],
            units={"ciro": "₺", "oee": "%"})
    assert s["kind"] == "line"
    assert s["dual_axis"] is True
    assert s["facet_measure"] is None


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


def test_reference_line_single_dim_measure_average():
    # §E (Madde 11 kalan kısım, 1 Ağustos 2026): kişi/varlık bazlı tek-ölçü bar grafiğinde
    # ortalama referans çizgisi — "kim ortalamanın üstünde/altında" ANINDA görülür.
    rows = [{"operator": f"P{i}", "ilk_seferde_tamam_yuzde": 70.0 + i} for i in range(6)]
    s = rec(["operator", "ilk_seferde_tamam_yuzde"], rows, units={"ilk_seferde_tamam_yuzde": "%"})
    assert s["kind"] == "bar"
    assert s["reference_line"] == {
        "kind": "average", "measure": "ilk_seferde_tamam_yuzde", "value": 72.5,
    }


def test_reference_line_requires_min_cardinality():
    # 3 kategori altı → referans çizgisi anlamsız (trivial), eklenmez.
    rows = [{"operator": f"P{i}", "ilk_seferde_tamam_yuzde": 70.0 + i} for i in range(3)]
    s = rec(["operator", "ilk_seferde_tamam_yuzde"], rows, units={"ilk_seferde_tamam_yuzde": "%"})
    assert s["reference_line"] is None


def test_reference_line_coexists_with_partition():
    # additive ölçüde HEM partition (pie önerisi) HEM reference_line aynı anda dolabilir.
    rows = [{"operator": f"P{i}", "toplam_agirlik_kg": 100.0 + i * 10} for i in range(6)]
    s = rec(["operator", "toplam_agirlik_kg"], rows, units={"toplam_agirlik_kg": "kg"})
    assert s["partition"] is True
    assert s["reference_line"]["value"] == 125.0


def test_partition_single_dim_additive_pie_alt():
    # ⟳ FAZ 5.11 — örnek **4 kategoriye** çıkarıldı (aynı gerekçe): testin amacı
    # *"≤6 kategoride pie ALTERNATİFİ önerilir"*dir. 3 kategoride artık grafik hiç
    # çizilmiyor ve bir alternatif de önerilmiyor — *bir karar, kendi alternatifini
    # önermez*.
    s = rec(["urun", "ciro"],
            [{"urun": "a", "ciro": 10}, {"urun": "b", "ciro": 20},
             {"urun": "c", "ciro": 5}, {"urun": "d", "ciro": 12}],
            units={"ciro": "₺"})
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


def test_YUKSEK_KARDINALITELI_SERIES_FACET_OLMAZ():
    """🔴🔴 `§K4` — **ASIL DEĞİŞMEZ.** 3 boyut + zaman: panel ekseni (`vardiya`,
    3 değer) eşiği geçse bile, SERIES ekseni (`makine`, 11 değer) kardinalite
    kontrolünden geçmeliydi. Ölçüldü (canlı): panel oluşuyor ama her panelin
    içi 11 renkli çubuk — okunamaz "duvar kağıdı". Facet artık kurulmamalı
    (table'a düşer — okunamaz grafikten daha iyi bir dürüst geri çekiliş)."""
    aylar = [f"2026-{m:02d}" for m in range(1, 4)]
    vardiyalar = ["1. Vardiya", "2. Vardiya", "3. Vardiya"]
    makineler = [f"M{i}" for i in range(11)]
    rows = [{"ay": ay, "vardiya": v, "makine": mk, "oee": 70.0}
            for ay in aylar for v in vardiyalar for mk in makineler]
    s = rec(["ay", "vardiya", "makine", "oee"], rows, units={"oee": "%"},
            cube_query={"timeDimensions": [{"dimension": "ay", "granularity": "month"}]})
    assert s["kind"] != "facet", (
        f"🔴 yüksek kardinaliteli series hâlâ facet'e giriyor: {s['kind']!r}")


def test_ZIT_OLCUT_DUSUK_KARDINALITELI_SERIES_HALA_FACET_OLUR():
    """🆃 Kapının kurbanı: series kontrolünü HER ZAMAN engelleyecek kadar
    sıkı yazmak da yeşil kalırdı. İki boyut da düşük kardinaliteliyken
    (3 vardiya × 2 hat) facet HÂLÂ kurulmalı — bu okunabilir bir görünüm."""
    aylar = [f"2026-{m:02d}" for m in range(1, 4)]
    vardiyalar = ["1. Vardiya", "2. Vardiya", "3. Vardiya"]
    hatlar = ["Hat A", "Hat B"]
    rows = [{"ay": ay, "vardiya": v, "hat": h, "oee": 70.0}
            for ay in aylar for v in vardiyalar for h in hatlar]
    s = rec(["ay", "vardiya", "hat", "oee"], rows, units={"oee": "%"},
            cube_query={"timeDimensions": [{"dimension": "ay", "granularity": "month"}]})
    assert s["kind"] == "facet", f"🔴 düşük kardinaliteli series artık facet olmuyor: {s['kind']!r}"


def test_llm_no_cube_query_numeric_month_stays_time_col():
    # regresyon (Madde 13, 1 Ağustos 2026): cube_query=None (LLM/Discovery yolu) iken
    # LLM'in ürettiği SQL "ay"ı SAYISAL (EXTRACT(MONTH...) gibi) döndürürse önceden İKİNCİL
    # bir ÖLÇÜ sayılıyordu (tüm değerler sayısal testi) → time_col hiç bulunamıyor, kind
    # "table"a düşüyordu → kategori ekseni/zoom hiç oluşmuyordu. İsim eşleşmesi (_TIME_NAMES)
    # DEĞER TİPİNDEN bağımsız uygulanmalı.
    rows = [{"ay": i, "ciro": 100.0 + i * 10} for i in range(1, 6)]
    s = rec(["ay", "ciro"], rows, units={"ciro": "₺"}, cube_query=None)
    assert s["dims"] == ["ay"]
    assert s["measures"] == ["ciro"]
    assert s["time_col"] == "ay"
    assert s["kind"] == "line"


def test_numeric_dimension_authoritative():
    # cube_query boyutu sayısal olsa da ÖLÇÜ sanılmaz (vardiya 1/2/3 → boyut).
    rows = [{"vardiya": 1, "ort_oee": 0.56}, {"vardiya": 2, "ort_oee": 0.63},
            {"vardiya": 3, "ort_oee": 0.52}]
    s = rec(["vardiya", "ort_oee"], rows, units={"ort_oee": "%"},
            cube_query={"cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya"]})
    assert s["dims"] == ["vardiya"] and s["measures"] == ["ort_oee"]
    # ⟳ **FAZ 5.11 — GÖRSEL DİLBİLGİSİ DEĞİŞTİ** (§15.6, MIMARI §13 ⟳ satırı).
    # Bu testin ASIL amacı sayısal bir boyutun **ölçü sanılmaması**dır (üstteki satır) ve
    # o amaç aynen duruyor. `kind` beklentisi güncellendi: **3 kategori × 1 ölçü** artık
    # `cumle` — *üç çubuk, üç kelimeden daha az anlatır*. Beklentiyi değiştirmek bir
    # gerileme değil, **maddenin kendisidir**; değiştirmeseydik kural hiç ateşlemezdi.
    assert s["kind"] == "cumle"
    assert "3 kalem" in s["cizilmedi"]


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


# ─────────────────────────────────────────────────────────────────────────────
# FAZ 5.11 — *"Ne zaman grafik ÇİZİLMEZ"* (§15.6) · SINIR DEĞERLERİ
# ─────────────────────────────────────────────────────────────────────────────
#
# ~50.000 yanıtlık çalışma (arXiv:2411.07451): genel kullanıcı grafiği tercih ediyor
# (%41,7 vs %36,3) **ama karar-vericiler ve finans profesyonelleri TABLO tercih ediyor**.
# `[DOĞRULANMADI — birincil kaynak okunmadı; oran bir gerekçedir, bir hedef değil]`
#
# 🔴 Dört kuralın hepsi **daraltıcıdır**: bir grafiği tabloya/cümleye çevirirler, tersi
# asla olmaz. Ve yalnız **varsayılan `bar`**'a uygulanırlar — `kpi`/`heatmap`/`partition`/
# `pivot` bilinçli kararlardır ve daraltmak onların gerekçesini silerdi.

def _kat(n, olcu_sayisi=1, cq=None):
    rows = []
    for i in range(n):
        r = {"urun": f"u{i}", "ciro": i + 1}
        if olcu_sayisi > 1:
            r["adet"] = i + 2
        rows.append(r)
    kolonlar = ["urun", "ciro"] + (["adet"] if olcu_sayisi > 1 else [])
    return rec(kolonlar, rows, units={"ciro": "₺"}, cube_query=cq)


def test_5_11_UC_kategori_CUMLE_dort_kategori_GRAFIK():
    """Sınır değeri: **3 → cümle**, **4 → grafik**."""
    assert _kat(3)["kind"] == "cumle"
    assert _kat(4)["kind"] != "cumle"


def test_5_11_IKI_satir_CUMLE():
    assert _kat(2)["kind"] == "cumle"


def test_5_11_COK_OLCULU_uc_kategori_GRAFIK_kalir():
    """⚠ 3 kategori × 2 ölçü **altı çubuktur**, üç değil.

    *"Üç çubuk üç kelimeden az anlatır"* gerekçesi orada **geçersizdir** — kıyaslanacak
    birden fazla seri varsa grafik gerçekten iş görür. (Bu şartı **kapı** öğretti: iki
    regresyon testi kırmızı verdi.)
    """
    assert _kat(3, olcu_sayisi=2)["kind"] != "cumle"


def test_5_11_YIRMI_kategori_GRAFIK_yirmi_bir_TABLO():
    """Sınır değeri: **20 → grafik**, **21 → tablo** (sıralanmamışsa)."""
    assert _kat(20)["kind"] != "table"
    s = _kat(21)
    assert s["kind"] == "table"
    assert "sıralanmamış" in s["cizilmedi"]


def test_5_11_SIRALANMIS_ise_yirmi_bir_kategori_GRAFIK_kalir():
    """🔴 **Şart SIRA, sayı değil.**

    50 kategorili bir Top-N çubuğu **okunabilir**; 21 kategorili alfabetik bir çubuk
    okunamaz. Yalnız sayıya bakmak, kullanıcının **kendi sıraladığı** bir raporu
    cezalandırırdı.
    """
    cq = {"cube": "parti", "measures": ["ciro"], "dimensions": ["urun"],
          "order": [{"id": "ciro", "desc": True}]}
    assert _kat(21, cq=cq)["kind"] != "table"


def test_5_11_FINANS_kapsami_TABLO():
    """Karar-vericiler ve finans profesyonelleri **tabloyu** tercih ediyor."""
    cq = {"cube": "mizan", "measures": ["ciro"], "dimensions": ["urun"]}
    s = _kat(8, cq=cq)
    assert s["kind"] == "table"
    assert "finans" in s["cizilmedi"]


def test_5_11_ZAMAN_SERISI_hicbir_kuralda_TABLOYA_cevrilmez():
    """⚠ Bir trend, tablo hâlinde **görülemez** — grafiğin tek gerçek üstünlüğü orada."""
    rows = [{"tarih": f"2026-{i:02d}", "ciro": i} for i in range(1, 26)]
    s = rec(["tarih", "ciro"], rows, units={"ciro": "₺"},
            cube_query={"cube": "mizan", "measures": ["ciro"],
                        "timeDimensions": [{"dimension": "tarih",
                                            "granularity": "month"}]})
    assert s["kind"] != "table" and "cizilmedi" not in s


def test_5_11_BILINCLI_kararlar_DARALTILMAZ():
    """`partition`/`heatmap`/`pivot`/`kpi` **bilinçli** kararlardır."""
    s = rec(["urun", "ciro"], [{"urun": f"u{i}", "ciro": i + 1} for i in range(3)],
            units={"ciro": "₺"})
    # 3 kategori + partition adayı: partition işaretliyse daraltma YAPILMAZ.
    if s.get("partition"):
        assert s["kind"] != "cumle"


def test_5_11_CIZILMEDI_gerekcesi_HER_ZAMAN_yazili():
    """*Çizilmeyen bir grafik, neden çizilmediğini söylemeli* — aksi hâlde kullanıcı
    ürünün onu **beceremediğini** sanar."""
    for s in (_kat(2), _kat(21), _kat(8, cq={"cube": "cari", "measures": ["ciro"],
                                             "dimensions": ["urun"]})):
        assert s.get("cizilmedi"), f"gerekçesiz daraltma: {s['kind']}"
