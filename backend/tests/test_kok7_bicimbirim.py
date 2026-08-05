"""🔴 KÖK-7 — **TEK BİÇİMBİRİM SAHİBİ.** (denetim raporu)

Rapor beş alt maddeyi tek çatı altında topluyor: *"bu kelime bilinen bir kökün biçimi
mi?"* sorusunun **birden çok sahibi var**. Ayrı ayrı düzeltmek, deponun **üç kez**
yaptığı ve her seferinde yeniden doğan şeydir.

## 7e · AY ÇEKİMİ — inen madde

⊙ Ölçüldü (2026-08-06): `_AY_ADI_RE` ay adından **sonra `\\b`** istiyordu.

```
ocak    ✅        ocakta    ❌
mart    ✅        martta    ❌   marttan ❌   marttaki ❌
```

**60 çekimin 11'i** geçiyordu (%18).

## 🔴 Ve asıl kusur kalıpta değil, İKİ SAHİPTE

Tarih **çözücüsü** (`_adlandirilan_aylar`) düzeltildikten sonra `ocakta`yı doğru
çözüyordu — `[2026-01-01, 2026-01-31]` — ama soru hâlâ **R10** ile reddediliyordu:
**kapsam kapısı** (`_period_hit_words`) kendi ay kalıbını taşıyordu ve onu görmüyordu.

> *Sistem tarihi biliyordu ama bildiğini bilmiyordu.*

İkisi de artık `_AY_ADI_RE` + `_ek_gecerli` kullanıyor — çekimin **tek sahibi**.

⚠ Yeni bir ek listesi **yazılmadı** (ADR-0008): kuyruğun geçerliliğine `_ek_gecerli`
karar veriyor ve o zaten `_covers` ile `_syn_hit`in de sahibi.
"""

from __future__ import annotations

import pytest

from app.cube_router import _AY_ADI_RE, _adlandirilan_aylar, _ek_gecerli, _norm, route

AYLAR = ["ocak", "subat", "mart", "nisan", "mayis", "haziran",
         "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik"]
#: Türkçenin en yaygın beş hâl eki. ⚠ Liste **ölçüt** değil **örneklem**: kapı
#: 60 çekimi sınar, `_ek_gecerli` bunlardan çok daha fazlasını kapsar.
CEKIMLER = ("{a}", "{a}ta", "{a}tan", "{a}taki", "{a}da")


def _soru(ay: str, kalip: str) -> str:
    # "aralık" tek başına belirsizdir ("tarih aralığı") → yalnız "aralık ayı" sayılır.
    return kalip.format(a=ay) + (" ayi" if ay == "aralik" else "") + " toplam ciro"


@pytest.mark.parametrize("ay", AYLAR)
def test_AY_CEKIMI_60_60(ay, schema):
    """🔴 **ASIL KAPI** — raporun ⊙ ölçütü: *"60 çekimde 60 HIT"*."""
    kacan = []
    for kalip in CEKIMLER:
        q = _soru(ay, kalip)
        cq = route(q, schema)
        f = ((cq or {}).get("cube_query") or {}).get("filters") or []
        if not any(str(x.get("value", "")).startswith("20") for x in f):
            kacan.append(kalip.format(a=ay))
    assert not kacan, f"🔴 ay çekimi eşleşmedi: {kacan}"


@pytest.mark.parametrize("q", [
    "mart ayakkabi fiyati",      # `mart` + ayrı kelime
    "kargo maliyeti bu yil",     # `kar` ⊄ `kargo` (mevcut koruma)
    "ekim ekipmani",             # `ekim` hem ay hem tarım terimi
])
def test_YANLIS_POZITIF_YOK(q, schema):
    """🔴 Raporun ⊙ ölçütünün **ikinci yarısı**: *"`mart ayakkabi` HIT VERMESİN"*.

    ⚠ Bir kalıbı genişletmek, yanlış-pozitif kapısını da genişletmeyi gerektirir —
    yoksa açılan kapsam sessiz-yanlış üretir (raporun A3 anti-çözümü)."""
    cq = route(q, schema)
    f = ((cq or {}).get("cube_query") or {}).get("filters") or []
    aylik = [x.get("value") for x in f
             if isinstance(x.get("value"), str) and x["value"].startswith("20")
             and x["value"][5:7] in ("03", "10")]
    assert not aylik, f"🔴 «{q}» yanlışlıkla ay filtresi üretti: {aylik}"


def test_CEKIM_TEK_SAHIPTEN():
    """🔴 Kuyruğun geçerliliğine `_ek_gecerli` karar verir — **yeni ek listesi yok**.

    *Bir kökün arkasındaki dizinin çekim olup olmadığı bir sözlük sorusu değil, bir
    biçimbilim sorusudur — ve bu depoda onun bir sahibi zaten vardı.*"""
    assert _ek_gecerli("ta") and _ek_gecerli("tan") and _ek_gecerli("")
    # Olumsuzluk eki ÇEKİM SAYILMAZ — anlamı tersine çevirir.
    assert not _ek_gecerli("siz")


def test_COZUCU_VE_KAPSAM_AYNI_KALIBI_KULLANIYOR():
    """🔴 **Ölçülen asimetrinin kapısı.** Tarih çözücüsü ile kapsam kapısı **aynı**
    ay kalıbını kullanmalı; ayrışırlarsa biri tarihi çözer, öteki soruyu reddeder."""
    import inspect

    from app import cube_router

    kaynak = inspect.getsource(cube_router._period_hit_words)
    assert "_AY_ADI_RE" in kaynak, \
        "🔴 kapsam kapısı kendi ay kalıbına dönmüş — asimetri geri geldi"


def test_COZUCU_CEKIMI_COZUYOR():
    """⊡ Birim: çözücü tek başına da doğru olmalı."""
    assert _adlandirilan_aylar(_norm("ocakta toplam ciro")) == \
        _adlandirilan_aylar(_norm("ocak toplam ciro"))


def test_KALIP_EK_GRUBU_TASIYOR():
    """⚠ Kalıp kuyruğu **yakalamalı** ki `_ek_gecerli` onu denetleyebilsin."""
    m = _AY_ADI_RE.search("martta")
    assert m and m.group("ek") == "ta"
