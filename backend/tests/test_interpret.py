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


# --- FAZ 0.10b · GÖRÜNEN ADLAR ---------------------------------------------------

def test_FAZ_0_10b_HAM_KOLON_ADI_BASILMAZ():
    """🔴 **Canlı kullanıcı turunda ölçüldü.** Ekranda şu görünüyordu:

        *"En yüksek tarih__year: 2026-01-01 00:00:00 (454.477,90, toplamın %100.0'i)"*

    Kullanıcının tepkisi: *"Ben yıl sordum, bana **veritabanı sütun adı** ve **saat
    00:00** gösteriliyor."*

    🔴 **Kritik yan etki:** bu metin `answer.py::_anlati_ekle`'de LLM'e `gercekler`
    **GİRDİSİ** oluyor → `t2_anlatici` açılırsa model `toplam_fire_kg` **etrafında cümle
    kurar**. Akıcı ama iç adlı bir cümle robotikliği kaldırmaz, **üstüne para ödetir** —
    bu yüzden `0.10b`, `t2_anlatici`'nin **sert ön koşuludur**."""
    r = _r(["makine", "toplam_fire_kg"],
           [{"makine": "RAM-1", "toplam_fire_kg": 700},
            {"makine": "RAM-2", "toplam_fire_kg": 300}])
    out = interpret(r, {"measures": ["toplam_fire_kg"], "dimensions": ["makine"]},
                    etiketler={"makine": "Makine", "toplam_fire_kg": "Fire (kg)"})
    assert "toplam_fire_kg" not in out["summary"], \
        f"HAM KOLON ADI ekrana basıldı: {out['summary']}"
    assert "Makine" in out["summary"], f"görünen ad kullanılmadı: {out['summary']}"


def test_FAZ_0_10b_ETIKET_YOKSA_BIREBIR_BUGUNKU():
    """**Geriye uyum:** `etiketler=None` iken metin **birebir bugünkü**. Bir iyileştirme,
    kendi yokluğunda davranışı değiştirmemelidir."""
    r = _r(["makine", "toplam_fire_kg"],
           [{"makine": "RAM-1", "toplam_fire_kg": 700},
            {"makine": "RAM-2", "toplam_fire_kg": 300}])
    eski = interpret(r, {"measures": ["toplam_fire_kg"], "dimensions": ["makine"]})
    assert "toplam_fire_kg" in eski["summary"] or "makine" in eski["summary"], \
        "etiketsiz çağrıda davranış DEĞİŞMİŞ — geriye uyum kırıldı"


def test_FAZ_0_10b_ETIKET_YOKSA_ALT_CIZGI_BOSLUGA():
    """Sözlükte olmayan bir ad için de ham hâli basmak yerine **okunabilir** hâli
    basılır: `tarih__year` → `tarih · year`. Kullanıcıya veritabanı şeması okutulmaz."""
    r = _r(["tarih__year", "toplam_fire_kg"],
           [{"tarih__year": "2026", "toplam_fire_kg": 700},
            {"tarih__year": "2025", "toplam_fire_kg": 300}])
    out = interpret(r, {"measures": ["toplam_fire_kg"], "dimensions": ["tarih__year"]},
                    etiketler={"toplam_fire_kg": "Fire (kg)"})
    assert "tarih__year" not in out["summary"], \
        f"ham çift-alt-çizgili kolon adı basıldı: {out['summary']}"


def test_FAZ_0_10b_IKINCI_ETIKET_KAYNAGI_ACILMADI():
    """🔴 `eylem.py:241`'in kendi uyarısı: *"bu depoda «ikinci bir etiket kaynağı» deseni
    **beş kez** ayrışmayla sonuçlandı."* Etiketler `build_catalog`'dan gelir — aynı
    kaynak `eylem._rapor_adi` ve `cube_router.next_step_chips` tarafından da kullanılır."""
    import inspect

    from app import answer as answer_mod

    govde = inspect.getsource(answer_mod._maybe_interpret)
    assert "build_catalog" in govde, "etiketler tek kaynaktan (build_catalog) GELMİYOR"
    assert "measure_synonyms_display" in govde and "dimension_labels" in govde, \
        "etiket sözlüğü kataloğun KENDİ alanlarından kurulmuyor"
    src = inspect.getsource(__import__("app.interpret", fromlist=["x"]))
    assert "measure_synonyms_display" not in src, \
        "`interpret.py` KENDİ etiket kaynağını kurmuş — ikinci sahip"
