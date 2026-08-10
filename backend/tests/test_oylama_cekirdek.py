"""🔴 `D4`/`F7` — **`oylama_cekirdek`: `beta` AMA 0 TEST.**

Rapor `F7`: *"Bu bayrak `beta`'da testsiz duruyor — yani bir gerilemeyi **hiçbir kapı
görmez**. `F7.1` **kapı yaz** (öncelik)."*

## Ne düzeltiyor — ve ölçülmüş bedeli

*"Oylama zenginliği **CEZALANDIRIYORDU**"*: `order`/`limit`/`pencere` yazmayan iki oy
birbiriyle **bedavaya** uyuşuyor, o alanları yazan tek oy **yalnız** kalıyordu.
Ölçüldü: **kazanan 1 oy → 7 kez**. Canlı bedeli `V13` (*«azalan sırada ilk 5»* →
11 satır) ve `V14` (*«yüzde kaçını»* → `pencere:pay` düştü).

⊙ Yani zengin cevap, **daha çok şey söylediği için** kaybediyordu.

## Sözleşme

| kural | neden |
|---|---|
| kapalıyken anahtar **tam `cq`** | `KURAL B` — davranış birebir bugünkü |
| açıkken anahtar **çekirdek** | zenginlik farkı oyu bölmez |
| kazanan **birleştirilmiş** zenginliği taşır | yoksa en fakir aday kazanır ve düzeltme tersine döner |
| zenginlik yalnız **oturuyorsa** taşınır | başka bir adayın ölçüsüne işaret eden `order`, kazanana **uymaz** |
"""

from __future__ import annotations

from app.routers.ask import (
    _canon_cekirdek,
    _canon_cq,
    _zenginlik_referansi_gecerli,
    _zenginligi_birlestir,
)

_FAKIR = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["makine"]}
_ZENGIN = {**_FAKIR, "order": {"measure": "toplam_fire_kg", "direction": "desc"},
           "limit": 5}


def test_ZENGINLIK_FARKI_OYU_BOLMEZ():
    """🔴 Kusurun kendisi: iki oy **aynı** soruyu cevaplıyor, biri daha çok söylüyor."""
    assert _canon_cekirdek(_FAKIR) == _canon_cekirdek(_ZENGIN)
    assert _canon_cq(_FAKIR) != _canon_cq(_ZENGIN), \
        "kapalı kipte ayrışmalı — yoksa `KURAL B` çiğnenir"


def test_KAZANAN_BIRLESTIRILMIS_ZENGINLIGI_TASIR():
    """🔴 Yoksa **en fakir** aday kazanır ve düzeltme tersine döner.

    *Zengin cevabın kaybetmesi bir oylama kazası değil, oylamanın yanlış şeyi
    saymasıydı.*
    """
    b = _zenginligi_birlestir([_FAKIR, _ZENGIN, _FAKIR])
    assert b.get("limit") == 5, b
    assert (b.get("order") or {}).get("measure") == "toplam_fire_kg", b


def test_OTURMAYAN_ZENGINLIK_TASINMAZ():
    """⚠ Başka bir adayın ölçüsüne işaret eden `order`, kazanana **uymaz**.

    Taşınsaydı, kazanan çekirdekte var olmayan bir ölçüye göre sıralanan bir sorgu
    üretilirdi — *doğru görünen, çalışmayan bir cevap.*
    """
    assert _zenginlik_referansi_gecerli(
        "order", {"measure": "toplam_fire_kg"}, _FAKIR) is True
    assert _zenginlik_referansi_gecerli(
        "order", {"measure": "baska_olcu"}, _FAKIR) is False


def test_SKALER_ZENGINLIK_HER_ZAMAN_TASINIR():
    """`limit` gibi skaler alanın referansı yoktur — sınanacak bir bağ da yoktur."""
    assert _zenginlik_referansi_gecerli("limit", 5, _FAKIR) is True


def test_BIRLESTIRME_CEKIRDEGI_BOZMAZ():
    """🔴 Birleştirme bir **zenginlik** işlemidir; ölçü/boyut/küp DEĞİŞMEZ."""
    b = _zenginligi_birlestir([_FAKIR, _ZENGIN])
    for alan in ("cube", "measures", "dimensions"):
        assert b[alan] == _FAKIR[alan], f"{alan} değişmiş: {b[alan]}"
