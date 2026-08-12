"""🔴🔴 `§YS-plan` — *«TEMSİL EDEMEDİM»* İDDİASI **PLAN YOLUNDA DA** KONUŞMALI.

## Ölçülen kusur (canlı curl, 2026-08-12)

    «müşteri kohort analizi yap»
      → plan koştu: SORGU · SORGU · MATRIS  (3 adımlık makbuz)
      → teslim edilen: **müşteri × dönem PİVOTU**, 8 satır
      → *«kohort metodolojisi uygulanmadı»* beyanı: **YOK**

⊙ Bir **pivot**, bir **kohort** değildir: kohort, varlıkları **ilk görüldükleri döneme**
göre gruplar ve o gruba **görece** zamanı izler. İkisini birbirinin yerine koymak, farklı
bir soruyu cevaplayıp aynı soruymuş gibi teslim etmektir.

## Kök — ve iki katmanlı

| katman | durum |
|---|---|
| **çağrı** | `uyum.yok_sayilan_beyani` **yalnız** küp yolunda (`ask.py:3151`); plan yolu ondan önce dönüyor (`ask.py:4222`) |
| 🔴 **girdi** | plan şemasında `yok_sayilan` alanı **hiç yoktu** — plan garsonu *«temsil edemedim»* **diyemiyordu bile** |

⚠ `uyum.denetle` bunu göremez: o bir **CubeQuery** denetleyicisidir (ölçü · boyut ·
sıralama); *«kohort»* bir **metodoloji** sözcüğüdür, hiçbir küp eksenine karşılık gelmez.

> *Bir menüde olmayan yemek, mutfakta pişebiliyor olsa da sipariş edilemez.* (`§EŞ`)

## Çözüm bir kelime listesi DEĞİL (`ADR-0008`)

Hangi sözcüğün temsil edilemediğini bilen tek merci **garsonun kendisidir**; iddiası
`uyum.yok_sayilan_beyani`'nin **iki deterministik süzgecinden** geçer — sözcük soruda
**geçmeli**, teslim edilen fişte **geçmemeli**. Sahip değişmiyor: küp yolunun kullandığı
**aynı gövde** plan yoluna da besleniyor (`KAT-1`).

⚠ Ve plan **çok bloklu**: bir sözcük *«fişte geçmiyor»* sayılmadan önce **bütün**
blokların taşıdıkları birleştirilir. *Bir cevabın neyi içerdiğini bir parçasına
sorarsanız, öbür parçadakini eksik ilan edersiniz* (`§Cİ-belge`).
"""

from __future__ import annotations

import types

from app import plan_semasi, uyum

_SEMA = {"cubes": [{"name": "ticaret",
                    "measures": ["toplam_ciro"], "dimensions": ["musteri"],
                    "time_dimensions": ["tarih"],
                    "measure_synonyms": {"toplam_ciro": ["ciro", "hasilat"]},
                    "dimension_synonyms": {"musteri": ["musteri", "alici"]},
                    "synonyms": ["ticaret", "satis"]}]}


def test_ALAN_SEMADA_VAR_ve_ISTENIYOR():
    """🔴 İki katman birden: alan **şemada** olmalı (yoksa şema-kısıtlı sağlayıcı onu
    hiç üretemez) **ve istemde istenmeli** (yoksa model onu yazmaz — `C3`'ün ilk
    yazımında model alanı üç turda da hiç doldurmadı)."""
    # ⚠ İlk yazımda fonksiyon adını **varsaydım** (`plan_semasi.plan_semasi`) ve
    # `StopIteration` aldım; gerçek ad `plan_json_schema` (ders ⑤: *şekli ölç, varsayma*).
    sema = plan_semasi.plan_json_schema({"ticaret": _SEMA["cubes"][0]})
    assert "yok_sayilan" in (sema.get("properties") or {}), (
        "🔴 plan şemasında `yok_sayilan` YOK → plan garsonu *«temsil edemedim»* "
        "diyemez. *Bir menüde olmayan yemek sipariş edilemez.*")
    assert "yok_sayilan" not in (sema.get("required") or []), (
        "alan ZORUNLU olmamalı: her plan bir şeyi ıskalamaz.")


def test_ISTEM_METNI_ALANI_ISTIYOR():
    """Şemada olup istemde istenmeyen bir alan, yazılmayan bir alandır."""
    import pathlib

    kaynak = (pathlib.Path(plan_semasi.__file__)).read_text(encoding="utf-8")
    assert "yok_sayilan" in kaynak and "atlamak bir hatadır" in kaynak, (
        "🔴 istem metni alanı istemiyor — ölçüldü: istenmeyen alan hiç yazılmıyor.")


def test_KOHORT_IDDIASI_SUZGECLERDEN_GECER():
    """🔴 Kusurun ta kendisi: `kohort` soruda **var**, teslim edilen fişte **yok**."""
    kabuk = types.SimpleNamespace(note="", trace=[])
    cq = {"cube": "ticaret", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
          "filters": [], "period_expr": "bu yıl"}
    assert uyum.yok_sayilan_beyani(kabuk, "müşteri kohort analizi yap", cq,
                                   _SEMA["cubes"][0], _SEMA, ["kohort"]) is True
    assert "kohort" in (kabuk.note or "").lower(), (
        f"beyan sözcüğü anmıyor: {kabuk.note!r}")


def test_FISTE_GECEN_SOZCUK_BEYAN_EDILMEZ():
    """⚠ `§101.1` — ikinci süzgeç: fişte karşılanan bir sözcük **eksik sayılmaz**.

    *«müşteri»* fişin `dimensions`'ında var; onu *«yansımadı»* diye yazmak, doğru bir
    cevabı yanlış bir uyarıyla lekelerdi."""
    kabuk = types.SimpleNamespace(note="", trace=[])
    cq = {"cube": "ticaret", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
          "filters": [], "period_expr": ""}
    assert uyum.yok_sayilan_beyani(kabuk, "müşteri kohort analizi yap", cq,
                                   _SEMA["cubes"][0], _SEMA, ["musteri"]) is False
    assert not kabuk.note


def test_SORUDA_GECMEYEN_SOZCUK_BEYAN_EDILMEZ():
    """⚠ İlk süzgeç: model bir sözcük **uydurabilir**; kullanıcının cümlesinde yoksa
    iddia düşer. *Bir hakemin sözünü tartmadan yayımlamak, hakemliği ona devretmektir.*"""
    kabuk = types.SimpleNamespace(note="", trace=[])
    cq = {"cube": "ticaret", "measures": ["toplam_ciro"], "dimensions": [],
          "filters": [], "period_expr": ""}
    assert uyum.yok_sayilan_beyani(kabuk, "müşteri kohort analizi yap", cq,
                                   _SEMA["cubes"][0], _SEMA, ["retention"]) is False


def test_TUKETICI_BEYANI_BIRLESIK_FISLE_OLCUYOR():
    """🔴 Plan **çok bloklu**: sözcük *«fişte yok»* sayılmadan önce BÜTÜN bloklar
    birleştirilmeli. Yüklem yapısal — `plan_tuketici` gövdesinde birleştirme var mı."""
    import pathlib

    from app import plan_tuketici

    kaynak = pathlib.Path(plan_tuketici.__file__).read_text(encoding="utf-8")
    assert "yok_sayilan_beyani" in kaynak, (
        "🔴 plan yolu beyanı ÇAĞIRMIYOR — kural yazıldı ama bir yola bağlanmadı "
        "(bu deponun sekiz kez ölçtüğü desen).")
    # 🔴 **SON** oluşum alınır, ilki değil: ilk oluşum bu düzeltmenin kendi **yorumunda**
    # ve ilk yazımım tam oraya baktı (kapı kendi belgesini ölçtü). *Bir kapı, ölçtüğü
    # şeyin kaç tane olduğunu saymıyorsa yanlış olanı ölçer* — bu turun ⑲/㉖ dersi.
    yerler = [k for k in range(len(kaynak))
              if kaynak.startswith("_uyum.yok_sayilan_beyani(", k)]
    assert len(yerler) == 1, f"beklenen tek ÇAĞRI, bulunan {len(yerler)}"
    govde = kaynak[max(0, yerler[0] - 1400):yerler[0]]
    for parca in ('_bkup["measures"] +=', '_bkup["dimensions"] +=', "for _b in _bolumler"):
        assert parca in govde, (
            f"🔴 birleşik fiş kurulmuyor ({parca!r} yok) → bir blokta karşılanan sözcük "
            "başka bir blok yüzünden «eksik» ilan edilir.")


def test_BEYAN_TURU_DUSURMEZ():
    """⚠ Beyan bir **ek**tir: hesabı çökse bile cevap gider (`ADR-0020` + best-effort)."""
    kabuk = types.SimpleNamespace(note="", trace=[])
    assert uyum.yok_sayilan_beyani(kabuk, "müşteri kohort analizi yap", {}, None,
                                   _SEMA, []) is False
