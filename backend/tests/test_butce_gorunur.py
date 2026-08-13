"""🔴 `§68` — **BÜTÇE EKRANDA**: onay isteyip gerekçesini göstermemek, onayı tören yapar.

`§28.3` çok adımlı planın önizlenme gerekçesini iki şeye bağlıyor: **bütçe**
(`adim · saniye · sorgu`) ve **%25 onarım tutma**. Ama sayı yalnız **doğrulayıcıda**
yaşıyordu: plan sınırı aşarsa red gelir, aşmazsa kullanıcı sınıra ne kadar yaklaştığını
**hiç görmez**.

## ⚠ Ölçülen ikinci bulgu — bayat bir yorum ⑳

`plan_kosucu.AZAMI_SORGU`'nun şerhi *«`plan_semasi.AZAMI_ADIM` ile **aynı sayı** olması
tesadüf değil»* diyordu. Ölçüldü: **`AZAMI_SORGU = 8`**, **`AZAMI_ADIM = 12`**. Şema 12
adıma izin veriyor ama hepsi `SORGU` olan bir plan koşum kapısında düşer.

🔴 **Hizalanmadı, KAYDEDİLDİ:** hangisinin doğru olduğu bir **ürün kararıdır** (bütçe mi
gevşer, şema mı daralır) ve kör bir hizalama, ölçülmemiş bir davranış değişikliğidir ㊸.
Bu kapı **bugünkü** sayıları savunur, ikisinin eşitliğini değil.

## Bu kapının dört yüklemi

| # | savunulan |
|---|---|
| 1 | önizleme notu **adet ve sınırı** taşır |
| 2 | sayının **tek sahibi** `plan_kosucu.sorgu_sayisi` ㊲ |
| 3 | 🆃 sayaç **gerçekten sayıyor** (sabit bir metin değil) |
| 4 | ⊘ süre **yazılmıyor** ve bu bilinçli 🅖 — koşmadan bilinmiyor |
"""

from __future__ import annotations

import re

from app import plan_kosucu, plan_tuketici as pt
from app.plan_semasi import AZAMI_ADIM

_CQ = {"cube": "oee", "measures": ["ort_oee"]}


def _plan(n_sorgu: int, n_diger: int = 0) -> dict:
    return {"adimlar": [{"fiil": "SORGU", "cube_query": _CQ} for _ in range(n_sorgu)]
                       + [{"fiil": "ANLAT", "kaynaklar": ["$1"]} for _ in range(n_diger)]}


def test_NOT_ADET_VE_SINIR_TASIR():
    not_ = pt.onizleme_notu(_plan(3, 1))
    assert "4 adım" in not_, f"🔴 adım sayısı yok: {not_!r}"
    assert str(AZAMI_ADIM) in not_, f"🔴 adım tavanı yok: {not_!r}"
    assert "3 sorgu" in not_, f"🔴 sorgu sayısı yok: {not_!r}"
    assert str(plan_kosucu.AZAMI_SORGU) in not_, f"🔴 sorgu bütçesi yok: {not_!r}"


def test_SAYIMIN_TEK_SAHIBI_VAR():
    """㊲ Gösterilen sayı ile **kapıda uygulanan** sayı aynı kaynaktan gelmeli."""
    import inspect

    kaynak = inspect.getsource(pt.onizleme_notu)
    assert "plan_kosucu.sorgu_sayisi" in kaynak, (
        "🔴 not kendi sayacını yazıyor — bir gün ekrandaki sayı kapıdakinden ayrışır")
    dg = inspect.getsource(plan_kosucu.dogrula)
    assert "sorgu_sayisi(plan)" in dg, (
        "🔴 doğrulayıcı kendi sayıyor — iki sayaç, iki farklı sınır demektir")


def test_ZIT_OLCUT_SAYAC_GERCEKTEN_SAYIYOR():
    """🆃 Kapının kurbanı: sabit bir metin de ilk yüklemi geçerdi."""
    az, cok = pt.onizleme_notu(_plan(1)), pt.onizleme_notu(_plan(5))
    assert az != cok, "🔴 not plandan bağımsız — bir süs, bir ölçü değil"
    assert plan_kosucu.sorgu_sayisi(_plan(5, 2)) == 5, "🔴 sayım yanlış"
    assert plan_kosucu.sorgu_sayisi({}) == 0 and plan_kosucu.sorgu_sayisi(None) == 0


def test_SURE_YAZILMIYOR():
    """🅖 **Bilmediğimiz sayıyı yazmayız.** `Butce`'nin saniye ayağı koşum anında ölçülür;
    bir planın ne kadar süreceğini koşmadan bilmiyoruz."""
    not_ = pt.onizleme_notu(_plan(2))
    assert not re.search(r"\bsaniye\b|\bsn\b", not_), (
        f"🔴 koşmadan süre beyan edildi — ölçülmemiş bir sayı yayımlanamaz: {not_!r}")
