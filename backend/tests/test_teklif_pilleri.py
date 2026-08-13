"""🔴 `§68`/`§28.1` — **TEKLİF PILL OLARAK OKUNUR**: yuvalar, cümle değil.

Planın cümlesi birebir: *«öngörüden **seçilmeyenler** için **pill satırını** ve adımları
hazırlamak ve onaya düşürmek»*. `§67` kararı kurdu (kararsız garson koşmaz, onaya düşer)
ama teklifi **cümle** olarak gösteriyordu — *«ort_oee · makine kırılımında»*. Karar
doğruydu, **gösterim yarımdı** 🅖; bu bölüm onu kapatır.

## ⊘ İkinci bir pill üreteci YAZILMADI ㊲

Zincir **var olan** iki halkadan kuruldu ㊷:

    cube_query ──niyet.fisten──▶ Niyet ──pill.pillerden──▶ [Pill]
                (🆕 çeviri)              (mevcut çizici)

`coz(soru, schema)` metinden okur; `fisten(cq, schema)` fişten. Çıktı aynı `Niyet`'tir,
o yüzden pill satırı **tek** yerde biçimlenir.

## Ölçülen tuzak ⑯ — dönem sınırı bir «varlık» değildir

Canlı fiş (`enerji_makine`): dönem süzgeci `filters` içinde ve boyut adı küpe göre
değişiyor (`donem_tarih`, başka küpte `tarih`). `pillerden` yalnız `"tarih"`i eliyor —
ham bir çeviri iki sınır satırını **iki varlık pill'i** olarak çizerdi (*«2026-07-01»* ·
*«2026-07-31»*). Ayrım iki **okumadan** yapılır: önce `cube_meta["time_dimensions"]`,
sonra değerin **şekli** (`YYYY-AA-GG`) ⑤.

## Bu kapının beş yüklemi

| # | savunulan |
|---|---|
| 1 | fişten `Niyet` doğuyor (ölçü · kırılım) |
| 2 | dönem sınırı **dönem** pill'i olur, iki varlık pill'i değil ⑯ |
| 3 | değer süzgeci **varlık** pill'i olur 🆃 — kural dönemi kayırmasın |
| 4 | kararsız teklif `piller` **taşır** |
| 5 | ⊘ tek adımlı olmayan yolda `piller` **yok** (kapsam beyanı 🆂) |
"""

from __future__ import annotations

from unittest.mock import patch

from app import niyet, pill, plan_tuketici as pt

_CQ = {
    "cube": "enerji_makine",
    "measures": ["toplam_elektrik_kwh"],
    "dimensions": ["makine"],
    "filters": [{"dimension": "donem_tarih", "operator": "gte", "value": "2026-07-01"},
                {"dimension": "donem_tarih", "operator": "lte", "value": "2026-07-31"}],
    "period_expr": "geçen ay",
}


def _alanlar(cq, schema=None):
    n = niyet.fisten(cq, schema)
    return [p.alan for p in pill.pillerden(n, schema)]


def test_FISTEN_NIYET_DOGAR():
    n = niyet.fisten(_CQ, None)
    assert n is not None, "🔴 geçerli fişten niyet çıkmadı"
    assert n.olcu_adaylari == [("enerji_makine", "toplam_elektrik_kwh")]
    assert n.kirilimlar == ["makine"]


def test_DONEM_SINIRI_VARLIK_PILLI_OLMAZ():
    """🔴 **ASIL DEĞİŞMEZ** ⑯ — iki sınır satırı **bir** dönem pill'idir."""
    alanlar = _alanlar(_CQ)
    assert alanlar.count(pill.ALAN_DONEM) == 1, f"🔴 dönem pill'i tek değil: {alanlar}"
    assert pill.ALAN_VARLIK not in alanlar, (
        f"🔴 dönem sınırı varlık pill'i olarak çizildi: {alanlar}")


def test_ZIT_OLCUT_DEGER_SUZGECI_VARLIK_OLUR():
    """🆃 Kapının kurbanı: *«süzgeçleri döneme say»* demek de yeşil bırakırdı — o zaman
    `makine=RAM-3` görünmezdi."""
    cq = dict(_CQ, filters=_CQ["filters"] + [{"dimension": "makine", "operator": "eq",
                                              "value": "RAM-3"}])
    alanlar = _alanlar(cq)
    assert pill.ALAN_VARLIK in alanlar, f"🔴 değer süzgeci kayboldu: {alanlar}"


def test_KARARSIZ_TEKLIF_PILL_TASIR():
    with patch("app.features.oneri_katmani_acik", return_value=True):
        y = pt.kararsiz_onizleme(_CQ, "enerji ne kadar?", 2 / 3, 3)
    assert y is not None and y.piller, f"🔴 teklif pill taşımıyor: {y}"
    alanlar = [p["alan"] for p in y.piller]
    assert pill.ALAN_OLCU in alanlar and pill.ALAN_KIRILIM in alanlar, (
        f"🔴 teklifin yuvaları eksik: {alanlar}")


def test_BOZUK_FIS_NIYET_URETMEZ():
    """⚠ `cube`'suz bir fiş bir sorgu değildir; ondan pill üretmek **uydurmak** olurdu."""
    for bozuk in (None, {}, {"measures": ["x"]}, "metin"):
        assert niyet.fisten(bozuk, None) is None, f"🔴 bozuk fişten niyet doğdu: {bozuk!r}"
