"""🔴🔴 `§DK` — **KATALOG ENUM'U, SORGUNUN KULLANACAĞI İFADEDEN OKUNUR.**

## Kapatılan kusur (canlı ölçüm, 2026-08-10)

`_enrich_cube_dim_values` bir küp boyutunun değerlerini **boyut ADIYLA** arıyordu ve
arama tablosu **80 modelin kolonlarını tek sözlükte** düzleştiriyordu. Bir küp boyutunun
adı başka bir modelin ham kolonuyla çakışınca o kolonun değerleri küpün **kendi
ifadesini gölgeliyor** ve `expression` satırına **hiç gelinmiyordu**.

| küp·boyut | küpün İFADESİ (verinin gerçeği) | enum (garsona söylenen) |
|---|---|---|
| `parti.musteri` | `musteri_ad` → *TOROS ÖRME TİC. LTD. ŞTİ.* | `M1001…` 🔴 |
| `kalite.tedarikci` | `tedarikci_ad` | `T-101…` 🔴 |
| `kalite.vardiya` | `CASE … '1. Vardiya (08-16)'` | `1 · 2 · 3` 🔴 |

**43 boyutun ifadesi adından farklıydı** — yalanın mümkün olduğu küme buydu.

## Bedeli bir kolaylık değil, bir SESSİZ YANLIŞ

    «bu yıl 1. vardiyada fire oranı» → 3 vardiya birden döndü, ilk satır
                                       «3. Vardiya (00-08)», süzgeç sessizce
                                       düştü, BEYAN YOK.

Kullanıcı 1. vardiyayı sordu, 3. vardiyanın sayısını okudu.

*Bir katalog, sorgunun kullanacağı ifadeden başka bir yerden okunuyorsa er ya da geç
ondan ayrışır — ve ayrıştığı gün kimse fark etmez, çünkü ikisi de geçerli birer cevap
üretir.*
"""

import pytest

from app.wren_service import WrenService


class _MotorsuzServis:
    """Yalnız `_enrich_cube_dim_values`'ın dokunduğu yüzey.

    ⚠ Motor **bilerek** yok: DISTINCT yolu düşerse enum'un **kaybolduğunu** (yani
    yalancı kısayola geri düşmediğini) görmek istiyoruz. *Eksik bir katalog dürüsttür;
    yanlış bir katalog değildir.*
    """

    _MAX_ENUM = 64

    def _engine(self):
        raise RuntimeError("bu kapıda motor yok — DISTINCT yolu bilerek düşürülüyor")

    def _fix_tr(self, s):                                   # pragma: no cover
        return s

    def _katalog_ozellikleri(self):                         # pragma: no cover
        return {}


#: `siparis` modelinde `musteri` KOD tutuyor; `partiler` modelinde `musteri_ad` AD tutuyor.
#: İkisinin de değeri örneklenmiş — canlıdaki durumun birebir küçüğü.
_MODELS = [
    {"name": "siparisler", "columns": [
        {"name": "musteri", "values": ["M1001", "M1002"]},
        # 🔴 İkinci çakışma: `tedarikci` adı burada KOD tutuyor — ve `parti` küpünün
        # `tedarikci` boyutunun ifadesi (`tedarikci_ad`) hiçbir yerde ÖRNEKLENMEMİŞ.
        {"name": "tedarikci", "values": ["T-101", "T-204"]},
    ]},
    {"name": "partiler", "columns": [
        {"name": "musteri_ad", "values": ["TOROS ÖRME TİC. LTD. ŞTİ.", "EGE KNIT A.Ş."]},
        {"name": "hat", "values": ["RAM 1", "RAM 2"]},
    ]},
]

_MDL = {"cubes": [{
    "name": "parti",
    "baseObject": "partiler",
    "dimensions": [
        # 🔴 Ad `musteri`, ifade `musteri_ad` — eski kısayolun yalan söylediği desen.
        #    ⊙ İfade **kendi base'inin** örneklenmiş kolonu olduğu için kanıta bağlı
        #    kısayol meşru biçimde ateşler: doğru değerler, motora **hiç gitmeden**.
        {"name": "musteri", "expression": "musteri_ad"},
        # 🔴 Ad `tedarikci`, ifade `tedarikci_ad` — ve o ifade örneklenmemiş.
        #    Tek çıkış motor DISTINCT'i; motor düşerse doğru davranış **susmaktır**.
        {"name": "tedarikci", "expression": "tedarikci_ad"},
        # ✅ Ad == ifade ve kolon KENDİ base'inde → kısayol meşru, DISTINCT'e gerek yok.
        {"name": "hat", "expression": "hat"},
        # ⚠ Türev ifade: kısayolu zaten alamazdı, motor DISTINCT'i ister.
        {"name": "hafta_gunu", "expression": "CASE isodow(tarih) WHEN 1 THEN 'Pzt' END"},
    ],
}]}


def _kos():
    cubes = [{"name": "parti"}]
    WrenService._enrich_cube_dim_values(_MotorsuzServis(), cubes, _MDL, _MODELS)
    return cubes[0]["dimension_values"]


def test_IFADESI_ADINDAN_FARKLI_BOYUT_BASKA_MODELIN_KOLONUNU_ALMAZ():
    """🔴 **Kapının kalbi.** `parti.musteri`'nin ifadesi `musteri_ad`; `siparisler`
    modelindeki aynı adlı KOD kolonu onu **gölgeleyemez**."""
    dv = _kos()
    assert "M1001" not in (dv.get("musteri") or []), (
        "🔴 GERİLEME: küp boyutu, ifadesi başka bir kolonu gösterirken başka bir "
        "modelin aynı ADLI kolonundan değer aldı — `§DK` kusurunun ta kendisi."
    )


def test_IFADESI_KENDI_BASEINDE_ORNEKLENMISSE_DOGRU_DEGERI_MOTORSUZ_ALIR():
    """⊙ Düzeltme yalnız yalanı kesmiyor, **doğruyu bedavaya** veriyor: ifade küpün
    kendi `baseObject`'inin örneklenmiş kolonuysa DISTINCT ile birebir aynı sonucu
    verir → motora hiç gidilmez.

    *Bir kısayolu kaldırmak değil, onu kanıta bağlamak gerekiyordu.*
    """
    assert _kos().get("musteri") == ["TOROS ÖRME TİC. LTD. ŞTİ.", "EGE KNIT A.Ş."]


def test_MOTOR_DUSERSE_ENUM_KAYBOLUR_YALANA_DUSMEZ():
    """Motor DISTINCT'i koşamadıysa doğru davranış **susmaktır**.

    `parti.tedarikci`'nin ifadesi (`tedarikci_ad`) örneklenmemiş → tek çıkış motordur.
    Motor düşünce enum **kaybolur**; `siparisler.tedarikci`'nin `T-101…` kodlarına
    düşmez.

    ⚠ Bir yedek olarak ad-kısayoluna düşmek, kapıyı kâğıt üstünde yeşil tutup kusuru
    geri getirirdi. *Eksik bir katalog «bilmiyorum» der; yanlış bir katalog «biliyorum»
    der ve yanılır.*
    """
    dv = _kos()
    assert not dv.get("tedarikci")
    assert "T-101" not in str(dv), "🔴 yalancı kısayola geri düşüldü"


def test_ADI_IFADESIYLE_AYNI_VE_KENDI_BASEINDE_OLAN_BOYUT_KISAYOLU_KORUR():
    """⚠ Düzeltme bir **kırpma** değil: kanıtlanabilir durumda ucuz yol korunur.

    `hat` ifadesi `hat` ve kolon `partiler`in (küpün kendi `baseObject`'i) → DISTINCT
    ile birebir aynı sonucu verirdi; motora gitmek boşuna maliyettir. Bu satır kapının
    **fazla ileri gitmediğini** kilitler.
    """
    assert _kos().get("hat") == ["RAM 1", "RAM 2"]


def test_TUREV_IFADE_KISAYOL_ALMAZ():
    """`CASE …` bir kolon değildir; ona ad üzerinden değer atamak kategorik hatadır."""
    assert not _kos().get("hafta_gunu")


@pytest.mark.parametrize("boyut", ["tedarikci", "hafta_gunu"])
def test_ENUM_YOKLUGU_BOS_LISTE_DEGIL_HIC_KAYIT_OLMAMASIDIR(boyut):
    """🔴 Ayrım tüketici için kritik: `deger_capasi` *«kaydı yoksa yargı verme»* diyor.
    Boş bir liste *«hiçbir değer yok»* diye okunursa kapı her sorguyu reddederdi."""
    assert boyut not in _kos()
