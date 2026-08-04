"""FAZ 5.3 kapısı — **her konuşma türü için ≥10 gerçek ifade varyantı.** (§C/9)

## Kök neden — 5.2'nin bulduğu şey

*"Müdüre 3 cümle yaz"* çalışan bir yeteneğe **bir kelime yüzünden** ulaşamıyordu. Kök
neden *"kelime eksik"* değildi: **kalıp sözlüğü tasarımcının kelimelerinden kuruldu**,
kullanıcının ifadelerinden değil.

## 🔴 Bu kapının ölçtüğü şey bir SÖZLÜK BÜYÜKLÜĞÜ DEĞİL

Ölçülen: *"gerçek kullanıcı ifadelerinin kaçı konuşma sınıfına giriyor"*. Sözlüğü
büyütmek bu sayıyı yükseltir **ama yanlış-pozitif riskini de yükseltir** — bu yüzden
`konusma_senaryolari`'nin `konu_degisimi` sınıfı **aynı turda** ölçülür ve gerilerse
sözlük genişlemesi **geri alınır**.
"""

from __future__ import annotations

import pytest

from lab.konusma_ifadeleri import ASGARI_VARYANT, CIKARILAN, IFADELER, olc


@pytest.fixture(scope="module")
def _olcum():
    return olc()


@pytest.mark.parametrize("tur", sorted(IFADELER))
def test_HER_TUR_icin_EN_AZ_ON_gercek_varyant(tur, _olcum):
    """🔴 §C/9'un kapısı. *"Bir kelime yüzünden kapalı yetenek"* sınıfı ölçülebilir olur."""
    d = _olcum[tur]
    assert d["konusma"] >= ASGARI_VARYANT, (
        f"🔴 `{tur}`: {d['toplam']} gerçek ifadeden yalnız **{d['konusma']}** konuşma "
        f"sınıfına girdi (< {ASGARI_VARYANT}).\n"
        f"Kaçanlar ve SEBEPLERİ:\n  "
        + "\n  ".join(f"{k['ifade']!r} → {k['sebep']} ({k['dustugu']})"
                      for k in d["kacan"])
        + "\n⚠ Körlemesine kelime EKLEME: yalnız `sozlukte-yok` sebebi bir sözlük "
          "işidir. `zamir-sarti` ve `yapisal-oncelik` DOKUNULMAZ — ikisi de "
          "`konu_degisimi` sınıfını koruyor.")


def test_KORPUS_her_turu_kapsiyor():
    """Bir tür doğarsa korpusu da doğmalı — aksi hâlde ölçülmeden sevk edilir."""
    from app import followup

    turler = {v for k, v in vars(followup).items()
              if k.startswith("TUR_") and isinstance(v, str)}
    eksik = sorted(turler - set(IFADELER))
    assert not eksik, (
        f"🔴 Korpusu OLMAYAN konuşma türü: {eksik}. Yeni bir tür, ölçüsü olmadan "
        f"inemez — 5.2'nin ölçtüğü kusur tam olarak buydu.")


def test_CIKARILAN_varyantlar_GEREKCELI():
    """*Sessizce silinen bir vaka, bir gün geri gelir.*"""
    assert CIKARILAN, "çıkarma kaydı boş olamaz — en az bir vaka ölçüldü ve çıkarıldı"
    for ifade, gerekce in CIKARILAN.items():
        assert len(gerekce) > 40, f"`{ifade}` gerekçesiz çıkarılmış"
        # Ve çıkarılan bir ifade korpusa GERİ SIZMAMALI.
        for varyantlar in IFADELER.values():
            assert ifade not in varyantlar, (
                f"🔴 `{ifade}` çıkarılmıştı ama korpusa geri girmiş — çıkarma gerekçesi "
                f"artık okunmuyor demektir.")


def test_KACMA_SEBEBI_siniflandiriliyor(_olcum):
    """🔴 *"Kök nedeni düzelt, örneği değil"* — sebep bilinmeden sözlük genişletilemez."""
    gecerli = {"sozlukte-yok", "zamir-sarti", "baska-tur-kazandi", "yapisal-oncelik"}
    for tur, d in _olcum.items():
        for k in d["kacan"]:
            assert k["sebep"] in gecerli, f"`{tur}`: bilinmeyen sebep {k['sebep']!r}"


def test_korpus_ILE_sozluk_AYNI_SEY_DEGIL():
    """⚠ Korpus bir **ölçü**dür, kalıp sözlüğü **ürün kodu**.

    Korpusun her ifadesini sözlüğe koymak, ölçüyü ölçtüğü şeye eşitlerdi — ve o an
    ölçüm **her zaman %100** verirdi. Bu kapı o çöküşü yakalar: en az bir ifade
    sözlükte **birebir** bulunmamalı.
    """
    from app import followup

    sozluk = set()
    for ad, v in vars(followup).items():
        if ad.startswith("_") and isinstance(v, tuple):
            sozluk |= {str(x) for x in v}
    tum = {x.lower() for v in IFADELER.values() for x in v}
    assert tum - sozluk, (
        "🔴 Korpusun TAMAMI kalıp sözlüğünde birebir var — ölçü, ölçtüğü şeye eşitlenmiş "
        "ve bundan sonra her zaman %100 verecek. *Kendi cevabını ölçen bir sınav, bir "
        "sınav değildir.*")
