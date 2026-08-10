"""🔴🔴 `§NT` + `§ÇE` + `§DK-5` — **AYNI GÖZLEM, ÜÇ AYRI KANIT SINIFI.**

Üç kusur da tek bir turda ölçüldü ve üçü de aynı yanlıştan doğdu: *«bu değer listede
yok»* gözlemine **her yerde aynı kararı** vermek.

| # | ölçülen soru | garsonun ürettiği | eski davranış | doğru karar |
|---|---|---|---|---|
| `§NT` | *«en kötü bakım maliyeti hangi makinede»* | `makine neq "Bakım"` | ⊙ kullanıcıya **sordu** | ✅ **düşür** — var olmayanı dışlamak hiçbir satırı elemez |
| `§ÇE` | *«ram makinesinin fire oranı»* | `makine eq RAM-1` **AND** `eq RAM-2` … | 🔴 **0 satır**, suç döneme atıldı | ✅ **birleştir** (`in`) — çelişki kanıtlı |
| `§DK-5` | *«AKDENİZ ÖRME için ciro»* | `musteri eq "M1001"` | ⊙ 8 adı **chip** olarak sordu | ✅ **kurtar** — ad kullanıcının cümlesinde yazılı |

*Aynı gözlem üç ayrı şey kanıtlıyorsa, üçüne aynı kararı vermek kanıta değil kelimeye
bakmaktır.*
"""

from app import deger_capasi as dc

_SEMA = {"cubes": [{
    "name": "maliyet",
    "dimensions": ["makine", "musteri"],
    "dimension_values": {
        "makine": ["RAM-1", "RAM-2", "RAM-3", "KONTİNÜ KASAR", "KONTİNÜ YIKAMA"],
        "musteri": ["AKDENİZ ÖRME TEKSTİL A.Ş.", "EGE KNIT DIŞ TİCARET LTD. ŞTİ."],
    },
    "time_dimensions": ["donem_tarih"],
}]}


def _cq(*filtreler):
    return {"cube": "maliyet", "measures": ["ort_birim_maliyet"], "filters": list(filtreler)}


# --- `§NT` · YOK-İŞLEM DIŞLAMASI --------------------------------------------------

def test_OLMAYAN_DEGERI_DISLAMAK_SORU_DOGURMAZ():
    """🔴 **Kapının kalbi.** `neq` + karşılıksız değer → sorgu koşar, süzgeç düşer."""
    cq = _cq({"dimension": "makine", "operator": "neq", "value": "Bakım"})
    notu, netlestir = dc.huni_karari(cq, _SEMA)
    assert netlestir is None, "🔴 dışlamada sorulacak bir şey yok"
    assert cq["filters"] == []
    assert "Etkisiz bir dışlama" in (notu or "")


def test_DUSURME_SESSIZ_DEGIL():
    """⚠ Kanıtlı bir düşürme bile **söylenir** — `§TK-2`'nin aynı disiplini."""
    cq = _cq({"dimension": "makine", "operator": "neq", "value": "Bakım"})
    notu, _ = dc.huni_karari(cq, _SEMA)
    assert "**makine**" in (notu or "")


def test_LISTEDE_SADECE_KARSILIKSIZ_UYELER_ATILIR():
    """🔴 `nin` bir listedir: karşılığı **olan** üyeler gerçek birer dışlamadır ve
    düşürülmeleri kapsamı değiştirirdi. Yalnız karşılıksızlar atılır."""
    cq = _cq({"dimension": "makine", "operator": "nin", "value": ["RAM-1", "Bakım"]})
    dc.huni_karari(cq, _SEMA)
    assert cq["filters"] == [{"dimension": "makine", "operator": "nin", "value": ["RAM-1"]}]


def test_KAPSAYAN_OPERATORDE_HALA_SORULUR():
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    `eq`'te karşılıksız bir değer hâlâ bir **belirsizliktir** — kullanıcı onu gerçekten
    kastetmiş olabilir. `§DK-2` aynen çalışmalı; yoksa bu düzeltme sessiz bir kapsam
    değişikliğine dönerdi."""
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "Bakım"})
    _, netlestir = dc.huni_karari(cq, _SEMA)
    assert netlestir is not None
    assert "listesinde yok" in netlestir["note"]


# --- `§ÇE` · ÇOKLU EŞİTLİK ---------------------------------------------------------

def test_AYNI_BOYUTA_IKI_ESITLIK_BIRLESIR():
    """🔴 Ölçülen kusur: üç `eq` **AND**'lenince hiçbir satır kalmıyordu."""
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "RAM-1"},
             {"dimension": "makine", "operator": "eq", "value": "RAM-2"},
             {"dimension": "makine", "operator": "eq", "value": "RAM-3"})
    notu, netlestir = dc.huni_karari(cq, _SEMA)
    assert netlestir is None
    assert cq["filters"] == [{"dimension": "makine", "operator": "in",
                              "value": ["RAM-1", "RAM-2", "RAM-3"]}]
    assert "çoklu seçim" in (notu or "")


def test_TEK_ESITLIK_DOKUNULMAZ():
    """`KURAL B`: çelişki yoksa süzgeç birebir kalır."""
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "RAM-1"})
    notu, _ = dc.huni_karari(cq, _SEMA)
    assert cq["filters"] == [{"dimension": "makine", "operator": "eq", "value": "RAM-1"}]
    assert notu is None


def test_AYNI_DEGERIN_TEKRARI_SESSIZCE_TEKILLESIR():
    """⚠ `A eq X AND A eq X` bir çelişki değil bir tekrardır: anlam değişmez, o yüzden
    **beyan da yazılmaz**. *Bir beyan, ölçebildiğinden fazlasını söylemez.*"""
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "RAM-1"},
             {"dimension": "makine", "operator": "eq", "value": "RAM-1"})
    notu, _ = dc.huni_karari(cq, _SEMA)
    assert cq["filters"] == [{"dimension": "makine", "operator": "eq", "value": "RAM-1"}]
    assert notu is None


def test_FARKLI_BOYUTLARDAKI_ESITLIKLER_BIRLESMEZ():
    """🔴 İki **ayrı** boyuta eşitlik bir çelişki değil, normal bir `AND`'dir — birleşmesi
    cevabı bozardı."""
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "RAM-1"},
             {"dimension": "musteri", "operator": "eq", "value": "EGE KNIT DIŞ TİCARET LTD. ŞTİ."})
    notu, _ = dc.huni_karari(cq, _SEMA)
    assert len(cq["filters"]) == 2
    assert notu is None


def test_BIRLESEN_LISTE_KIMLIK_KAPISINDAN_GECER():
    """⚠ Sıra bir tasarım kararıdır: `§ÇE` **önce** koşar, `§DK-2` birleşmiş listeyi
    denetler. İki kural birbirini görmezse uydurma bir üye listenin içine saklanırdı."""
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "RAM-1"},
             {"dimension": "makine", "operator": "eq", "value": "YOK BÖYLE"})
    _, netlestir = dc.huni_karari(cq, _SEMA)
    assert netlestir is not None and "YOK BÖYLE" in netlestir["note"]


# --- `§DK-5` · SORUDAN KURTARMA ----------------------------------------------------

def test_KULLANICININ_YAZDIGI_AD_SORULMAZ():
    """🔴 Ölçülen kusurun kendisi: kullanıcı gerçek adın **tam önekini** yazmıştı."""
    cq = _cq({"dimension": "musteri", "operator": "eq", "value": "M1001"})
    notu, netlestir = dc.huni_karari(cq, _SEMA, "AKDENİZ ÖRME için bu yıl ciro")
    assert netlestir is None, "🔴 cevap kullanıcının cümlesinde yazılıydı"
    assert cq["filters"][0]["value"] == "AKDENİZ ÖRME TEKSTİL A.Ş."
    assert "eşleştirildi" in (notu or "")


def test_SORU_VERILMEZSE_ESKI_DAVRANIS():
    """`KURAL B`: soru geçilmezse yol birebir bugünküdür."""
    cq = _cq({"dimension": "musteri", "operator": "eq", "value": "M1001"})
    _, netlestir = dc.huni_karari(cq, _SEMA)
    assert netlestir is not None


def test_SORUDA_IKI_ADAY_VARSA_YINE_SORULUR():
    """🔴🔴 **Sınır tekillik.** Soruda iki geçerli değer birden anılıyorsa hangisi
    olduğunu bilmiyoruz — *belirsizlikte tahmin etmemek bu deponun tek kuralıdır ve bir
    kurtarma yolu onun istisnası olamaz.*"""
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "M1001"})
    _, netlestir = dc.huni_karari(cq, _SEMA, "RAM-1 ve RAM-2 için maliyet")
    assert netlestir is not None


def test_SORUDA_DEGER_YOKSA_YINE_SORULUR():
    """Kurtarma bir tahmin üretmez: soruda karşılık yoksa netleştirme aynen çalışır."""
    cq = _cq({"dimension": "musteri", "operator": "eq", "value": "M1001"})
    _, netlestir = dc.huni_karari(cq, _SEMA, "bu yıl toplam maliyet")
    assert netlestir is not None


def test_YAZIM_YAKINLIGI_KURTARMADAN_ONCE_GELIR():
    """⚠ Sıra bilinçli: yakın yazım bir **düzeltmedir**, sorudan kurtarma bir **kanıt** —
    ama yakın yazım zaten doğruysa ikincisini koşmak israftır.

    ⊙ Örneği **iki kez** yanlış seçtim ve ikisini de ölçüm gösterdi:
    1. `«RAM 1»` — `_ratio("ram 1","ram-1") ≈ 0,80` eşiğin (`0,82`) altında; yakın yazım
       zaten pes ediyordu, yani test iki yolun hangisinin **kazandığını** değil, ikisinin
       de kaybettiğini ölçüyordu.
    2. `«KONTİNU KASAR»` — `_norm` `Ü`↔`U` farkını **yutuyor**, yani değer zaten
       *geçerli* sayılıyor ve ortada bir bulgu bile doğmuyordu.

    *Bir sınavı geçen kod değil, sınavın ölçtüğü şey önemlidir* — ve bir sınavın neyi
    ölçmediği ancak ölçülerek görülür.
    """
    # Garsonun değeri `KONTİNÜ KASAR`'a **yakın** (fazladan bir harf, normalizasyonun
    # yutmadığı bir fark); soruda ise **başka bir makinenin** iki kelimelik öneki geçiyor.
    # Yakın yazım kazanmalı — yoksa sorudaki alakasız ad cevabı çalardı.
    cq = _cq({"dimension": "makine", "operator": "eq", "value": "KONTİNÜ KASARR"})
    dc.huni_karari(cq, _SEMA, "KONTİNÜ YIKAMA hattının maliyeti")
    assert cq["filters"][0]["value"] == "KONTİNÜ KASAR"


def test_TEK_KELIMELIK_ONEK_YETMEZ():
    """🔴🔴 **Önek yolunun sınırı.** Tek kelimelik bir önek (*«akdeniz»*) cümlenin
    ortasında tesadüfen bulunabilir; **iki** kelimelik bitişik bir dizi bir tesadüf
    değil bir **atıftır**. *Bir bağ, tesadüfen kurulabiliyorsa bağ değildir.*"""
    cq = _cq({"dimension": "musteri", "operator": "eq", "value": "M1001"})
    _, netlestir = dc.huni_karari(cq, _SEMA, "AKDENİZ için bu yıl ciro")
    assert netlestir is not None


def test_AYNI_ONEKI_PAYLASAN_IKI_DEGER_SORULUR():
    """⚠ Tekillik önek yolunda da şart: iki değerin aynı iki-kelimelik öneki varsa
    hangisi olduğunu bilmiyoruz."""
    sema = {"cubes": [{"name": "maliyet", "dimensions": ["musteri"],
                       "dimension_values": {"musteri": ["AKDENİZ ÖRME TEKSTİL A.Ş.",
                                                        "AKDENİZ ÖRME KONFEKSİYON LTD."]},
                       "time_dimensions": []}]}
    cq = _cq({"dimension": "musteri", "operator": "eq", "value": "M1001"})
    _, netlestir = dc.huni_karari(cq, sema, "AKDENİZ ÖRME için bu yıl ciro")
    assert netlestir is not None
