"""🔴🔴 `§28.3` satır 2 + `§28.4` — **GARSON KARARSIZSA KOŞMAZ, ONAYA DÜŞER.**

## Planın tablosu (birebir)

```
3/3 aynı cevap   → marj YÜKSEK  → koş
2/3              → marj DÜŞÜK   → pill'leri onaya düşür
1/1/1 (dağıldı)  → marj YOK     → adayları göster, cevaplama
```

## Ölçülen boşluk (kod okundu)

Planın kendi teşhisi: *«garsonun güven sinyali de **HESAPLANIYOR, ama bir KAPIYA
bağlanmıyor**»*. `_select_consistent` `uyum_orani` döndürüyor ve üç yere gidiyordu:

| nereye | ne yapıyor |
|---|---|
| uyuşmazlık chip'i | `1/1/1` hâli — **zaten vardı** |
| iz notu (*«%67 uyum»*) | bir **yazı**, bir kapı değil |
| `oylama_cogunluk` bayrağı | 🔴 **doğrudan koşum** |

Yani `2/3` **sessizce koşuyordu**.

## Bu kapının beş yüklemi

| # | savunulan |
|---|---|
| 1 | kararsızda (`uyum < 1`) **koşmaz** — `source="onizleme"` |
| 2 | 🆃 **oy birliğinde koşar** — kapı özelliği öldürmesin |
| 3 | `k <= 1`'de sinyal **yok** → karar da yok 🆕 |
| 4 | 🔴 `KURAL B`: katman kapalıyken `None` |
| 5 | önizleme **onaylanabilir**: tek adımlı **plan** taşır (`/plan/kos` onu koşar) |
"""

from __future__ import annotations

from unittest.mock import patch

from app import plan_tuketici as pt

_CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}


def _cagir(uyum: float, k: int = 3, katman: bool = True):
    with patch("app.features.oneri_katmani_acik", return_value=katman):
        return pt.kararsiz_onizleme(_CQ, "OEE ne kadar?", uyum, k)


def test_KARARSIZDA_ONAYA_DUSER():
    """🔴 **ASIL DEĞİŞMEZ.** `2/3` bir cevap değil, bir **teklif**tir."""
    y = _cagir(2 / 3)
    assert y is not None and y.source == "onizleme", f"🔴 kararsız garson koştu: {y}"
    assert y.result is None, "🔴 önizleme sonuç taşıyor — demek ki koşmuş"


def test_ZIT_OLCUT_OY_BIRLIGINDE_KOSAR():
    """🆃 Kapının kurbanı: her cevabı onaya düşürmek `§24`'ün çözdüğü sorunu geri getirir
    (*«uzman yavaşlıyor»*). `3/3` **koşmalı**."""
    assert _cagir(1.0) is None, "🔴 oy birliği de onaya düştü — her soru iki tıka çıkar"


def test_OY_YOKSA_KARAR_DA_YOK():
    """🆕 `k <= 1`'de kararsızlık **ölçülmemiştir**; ölçülmemiş bir sinyalden karar
    üretmek, bilmediğini biliyormuş gibi davranmaktır."""
    assert _cagir(0.0, k=1) is None, "🔴 tek örneklemde 'kararsız' ilan edildi"


def test_KURAL_B_KATMAN_KAPALIYKEN_YOK():
    assert _cagir(2 / 3, katman=False) is None, (
        "🔴 katman kapalıyken davranış değişti (`KURAL B`)")


def test_ONIZLEME_ONAYLANABILIR():
    """Önizleme **onaylanabilir** olmalı: `/plan/kos` bir **plan** koşar, fiş değil."""
    y = _cagir(2 / 3)
    plan = y.plan_taslagi
    assert plan and plan["adimlar"][0]["fiil"] == "SORGU", f"🔴 plan yok/bozuk: {plan}"
    assert plan["adimlar"][0]["cube_query"] == _CQ, "🔴 onaylanan fiş, anlaşılan fiş değil"
    assert y.adimlar and y.adimlar[0]["metin"], "🔴 kullanıcı neyi onayladığını göremiyor"
    # ⚠ Sayı **beyan edilir**: *«emin değilim»* bir özür değil bir ölçüdür 🅜.
    assert "%67" in (y.note or ""), f"🔴 uyum oranı beyan edilmemiş: {y.note!r}"
