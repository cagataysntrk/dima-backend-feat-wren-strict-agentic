"""🔴 **TEK KURAL, ALTI KUSUR** — *bir ayrıştırıcı bir kelimeyi tükettiyse, o kelime
kapsam kapısında BİLİNMEYEN sayılamaz.*

## Canlı curl'de bulunan altı örnek

`3'ünü` · `3 tanesi` · `üretildi` · `çeyreklere` · `ocağa` · `5 milyon üzeri` —
hepsinde **ayrıştırıcı ✅** ve **tüketici ✅** çalışıyordu; tur kapsam kapısında ölüyordu.

Kullanıcının bildirdiği **bağlam kopması** tam buydu:

    tur 1  "bu yıl toplam ciro"       ✅
    tur 2  "müşteri bazında göster"   ✅
    tur 3  "en yüksek 3 ünü getir"    🔴 "Bu takip mesajını ilişkilendiremedim"

⊙ İzole edildi: `deterministic_refine(prev, "en yuksek 3")` → ✅ `limit=3`;
`"en yuksek 3 unu getir"` → **None**. Fark **tek kelime**: `unu`.

## ⚠ Ve ilk düzeltmem YANLIŞ KATMANDAYDI

Kuralı önce `route()`'un kapısına yazdım, curl ile doğruladım — **hâlâ kırıktı**.
Takip yolunun **kendi** kapısı var (`:1423`) ve kullanıcının vakası oradan geçiyor.

⊙ `deterministic_refine`'ın kendi şerhi bunu **zaten** uyarıyordu: *"DÖRT tüketicinin
DÖRDÜNDE de dolgu sayılır — biri atlanırsa aynı soru geldiği yola göre farklı davranır."*
Ben beşinci bir dolgu sınıfı ekleyip **yalnız birinde** uyguladım.

*Bir kusuru doğru teşhis edip yanlış katmanda düzeltmek, onu ikinci kez bulmayı
gerektirir.*

## Emsal kodun içindeydi

`cube_router:3636` eşik için bu bağışıklığı **zaten** veriyordu
(`if having: known |= _gecenler(q, _TH_WORDS)`). Yeni sözlük **yok** — `_TOPN_CUE` mevcut.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


def _prev():
    return {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}


@pytest.mark.parametrize("soru,limit", [
    ("en yüksek 3 ünü getir", 3),      # 🔴 kullanıcının bildirdiği vaka
    ("en yüksek 3 tanesi", 3),
    ("ilk 5 ini", 5),
    ("en yüksek 3", 3),                # kontrol: ekli olmayan hâli hep çalışıyordu
])
def test_TAKIP_YOLU_SAYI_EKINI_YUTMUYOR(schema, soru, limit):
    r = cr.deterministic_refine(_prev(), cr._norm(soru), schema)
    assert r is not None, (
        f"🔴 {soru!r} takip düzenlemesi düştü — kullanıcı *«ilişkilendiremedim»* görür")
    assert r.get("limit") == limit, r


def test_HER_IKI_KAPIDA_DA_UYGULANDI():
    """🔴 Kural **iki** kapıda da olmalı: `route()` (taze soru) ve `deterministic_refine`
    (takip). İlk düzeltmem yalnız birindeydi ve vaka **hâlâ kırıktı**."""
    import inspect

    src = inspect.getsource(cr)
    assert src.count("if _top_n(q, cube_meta):") >= 2, (
        "🔴 kural tek kapıda — aynı soru geldiği yola göre farklı davranır")


def test_YENI_SOZLUK_YAZILMADI():
    """`ADR-0008`. Bağışıklık `_TOPN_CUE`'dan ve sayı-eki deseninden geliyor."""
    import inspect

    src = inspect.getsource(cr)
    i = src.index("if _top_n(q, cube_meta):")
    blok = src[i:i + 400]
    assert "_TOPN_CUE" in blok and "\\b\\d+\\s+" in blok.replace("\\\\", "\\")


def test_KAPSAM_DAR_top_n_ESLESMEZSE_BILINMEYEN_KALIR(schema):
    """⚠ Genişlemenin sınırı: `_top_n` eşleşmiyorsa kelime **bilinmeyen kalmalı** —
    aksi hâlde kapı her şeyi geçirirdi. *Bir bağışıklık, sebebi kadar dar olmalı.*"""
    r = cr.deterministic_refine(_prev(), cr._norm("zxqw plmk asdf"), schema)
    assert r is None
