"""FAZ I1 — semantik metadata GÖRSELLEŞTİRMEYE ulaşıyor: "bedava doğruluk".

## Ölçülen sessiz-yanlış (2 Ağustos 2026)

Cube metadata'sı `additive: full | semi | non` **beyan ediyor** ve `WrenService.schema()`
bunu `semi_additive` / `non_additive` listeleri olarak **zaten taşıyordu**. Ama
`viz.recommend()` onları **hiç almıyordu**; yerine bir ad/birim regex'i kullanıyordu:

    viz._additive("bakiye", "₺")  →  True     ← YIĞMA ÖNERİLİR

`bakiye` iki cube'da (`cari`, `mizan`) `additive: semi` beyan edilmiş. Bakiye bir **STOK**
büyüklüğüdür: dönemler arasında **toplanamaz** (Ocak bakiyesi + Şubat bakiyesi bir şey
ifade etmez). Yığılmış grafik, matematiksel olarak yanlış bir görseli *"deterministik"*
rozetiyle sunardı — `viz.py`'nin varlık sebebine (ADR-0024) aykırı.

## İkinci kusur: altı çağıran, altı elle toplanmış argüman listesi

`recommend()`'in altı çağıranı vardı (`/ask` iki kez, `/report`, `dashboards`,
`schedules`, `conversations`) ve **her biri argümanları elle topluyordu**. Sonuç kodda
zaten kayıtlı: bir yerde anahtar `measure_units` diye **yanlış yazılmış** ve birim
farkındalığı o yolda hiç devreye girmemişti. `semi_additive` aynı sınıfın ikinci örneği
oldu — üretiliyor, hiç geçirilmiyor.

`viz.meta_args(cube_meta)` tek kaynaktır: yeni bir metadata alanı görselleştirmeye
bağlandığında **tek bir yer** değişir ve beşinci çağıranı unutmak imkânsız hale gelir.
"""

from __future__ import annotations

import pytest

from app import viz

_SATIRLAR = [{"ay": f"2026-0{i}", "sube": s, "bakiye": 100.0 * i, "toplam_ciro": 50.0 * i}
             for i in range(1, 7) for s in ("A", "B", "C", "D", "E", "F")]
SONUC = {"columns": ["ay", "sube", "bakiye", "toplam_ciro"], "rows": _SATIRLAR,
         "row_count": len(_SATIRLAR)}


def _spec(measure: str, non_additive=None):
    r = {"columns": ["ay", "sube", measure],
         "rows": [{"ay": s["ay"], "sube": s["sube"], measure: s[measure]} for s in _SATIRLAR],
         "row_count": len(_SATIRLAR)}
    return viz.recommend(r, units={measure: "₺"}, non_additive=non_additive or [])


# --- ASIL KAPI: beyan sezgiyi EZER ----------------------------------------------

def test_BEYAN_yigmayi_yasaklar():
    """`bakiye` bir STOK büyüklüğüdür; dönemler arası toplanamaz. Beyan geçirilmediğinde
    birim (₺) yüzünden regex ona "additive" diyor ve yığma öneriliyordu."""
    beyansiz = _spec("bakiye")
    beyanli = _spec("bakiye", non_additive=["bakiye"])
    assert beyansiz["stackable"] is True, "test ön koşulu: beyansız yol yığma öneriyordu"
    assert beyanli["stackable"] is False, "BEYAN yok sayıldı — toplanamaz ölçü yığıldı"
    assert beyanli["kind"] != "stacked"


def test_BEYAN_pay_grafigini_de_yasaklar():
    """Pay (pie/treemap) grafiği de toplanabilirlik varsayar: dilimlerin toplamı bütünü
    vermelidir. Toplanamaz bir ölçüde pasta grafiği aynı yalanı yuvarlak çizer."""
    r = {"columns": ["sube", "bakiye"],
         "rows": [{"sube": s, "bakiye": 10.0 * i} for i, s in enumerate("ABCD", 1)],
         "row_count": 4}
    assert viz.recommend(r, units={"bakiye": "₺"})["partition"] is True
    kisitli = viz.recommend(r, units={"bakiye": "₺"}, non_additive=["bakiye"])
    assert kisitli["partition"] is False
    assert not kisitli.get("alternatives"), "pasta/treemap önerisi sızdı"


def test_TURETILMIS_kiyas_kolonu_kisiti_MIRAS_alir():
    """`bakiye_gecen` de bir stok büyüklüğüdür. Kısıt yalnız baz ölçüye uygulansaydı
    dönemsel kıyas grafiğinde yığma geri gelirdi."""
    assert viz._additive("bakiye_gecen", "₺", {"bakiye", "bakiye_gecen"}) is False


def test_beyansiz_olcu_BUGUNKU_davranisi_korur():
    """Beyanı olmayan ölçüler (henüz `additive:` yazılmamış cube'lar) bugünkü davranışı
    korumalı — beyanı olmayanı yasaklamak, ÖLÇMEDEN kısıtlama getirmek olurdu."""
    assert _spec("toplam_ciro")["stackable"] is True


def test_regex_YEDEGI_calismaya_devam_eder():
    """Yüzde/oran ölçüleri beyan olmasa da toplanamaz sayılır — mevcut koruma bozulmadı."""
    assert viz._additive("fire_orani_yuzde", "%") is False
    assert viz._additive("ort_oee", "") is False
    assert viz._additive("toplam_ciro", "₺") is True


# --- meta_args: TEK KAYNAK -------------------------------------------------------

def test_meta_args_UC_alani_da_tasir():
    m = viz.meta_args({"units": {"a": "₺"}, "lower_is_better": ["fire"],
                       "semi_additive": ["bakiye"], "non_additive": ["ort"]})
    assert m["units"] == {"a": "₺"}
    assert m["lower_set"] == ["fire"]
    assert set(m["non_additive"]) == {"bakiye", "ort"}, "semi VE non birleştirilmeli"


def test_meta_args_BOS_metadata_patlatmaz():
    for girdi in (None, {}, {"units": None}):
        m = viz.meta_args(girdi)
        assert m["units"] == {} and m["lower_set"] == [] and m["non_additive"] == []


def test_TUM_cagiranlar_meta_args_kullaniyor():
    """ASIL KAPI (yapısal). Altı çağıran vardı ve her biri argümanları ELLE topluyordu;
    biri `measure_units` diye yanlış yazmış ve birim farkındalığı o yolda hiç devreye
    girmemişti (kodda kayıtlı). Elle toplama geri gelirse bu test kırılır."""
    import pathlib
    import re

    # ⚠ **BELİRTEÇ AST'YE ÇEVRİLDİ (FAZ 5.12).** Regex taraması `features.py`'nin bayrak
    # **açıklama metnini** yakalayıp yanlış-kırmızı verdi: o metin `viz.recommend()`
    # ifadesini *anlatmak* için içeriyordu. Bu deponun **on ikinci kez** ödediği ders —
    # *beyan ile beyanın anlatımı farklı şeylerdir*, ve bir ölçüm aracının kendisi de bir
    # bağımlılıktır.
    import ast

    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    elle = []
    for f in kok.rglob("*.py"):
        if f.name == "viz.py":
            continue
        agac = ast.parse(f.read_text(encoding="utf-8"))
        for n in ast.walk(agac):
            if not (isinstance(n, ast.Call)
                    and getattr(n.func, "attr", "") == "recommend"
                    and getattr(getattr(n.func, "value", None), "id", "")
                    in ("viz", "_viz")):
                continue
            if not any(k.arg is None
                       and getattr(getattr(k.value, "func", None), "attr", "")
                       == "meta_args"
                       for k in n.keywords):
                elle.append(f"{f.name}:{n.lineno}")
    assert not elle, ("`viz.recommend` argümanları ELLE toplanmış:\n  " + "\n  ".join(elle)
                      + "\n`viz.meta_args(cube_meta)` kullanın — tek kaynak.")


# --- uçtan uca -------------------------------------------------------------------

def test_UCTAN_UCA_schema_beyani_viz_karari(schema):
    """Zincirin tamamı: cube YAML `additive: semi` → `schema()` `semi_additive` →
    `meta_args` → `recommend` → yığma YASAK."""
    cari = next((c for c in schema["cubes"] if c["name"] == "cari"), None)
    if not cari:
        pytest.skip("cari cube'u yok")
    assert "bakiye" in (cari.get("semi_additive") or []), \
        "schema() beyanı taşımıyor — zincirin ilk halkası kopuk"
    assert "bakiye" in viz.meta_args(cari)["non_additive"]
