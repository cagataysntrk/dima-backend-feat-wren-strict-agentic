"""🔴🔴 `§UY/K` — **ÖBEK EŞLEŞMEZ AMA KELİME KAPSANIR: doğru bir cevap «eksik» diye
etiketleniyordu.**

## Ölçülen kusur (curl turu, 2026-08-10)

    «en çok duruşa yol açan 3 nedeni bul»
      → makine_duruslari.toplam_sure_dk · «Malzeme/Parti Bekleme · 427.140 dk»  ✅ DOĞRU
      → not: «⚠ Sayı doğru ama EKSİK: «durus» bu küpte tanımlı değil.»          🔴 YANLIŞ

🔴 Oysa kelime **bol bol** kapsanıyordu: küp sinonimleri `durus nedeni` · `durus
sebebi`; ölçü sinonimleri `toplam durus` · `toplam durus dakikasi`. Sebep: hepsi **çok
kelimeli öbek** ve `_match_measure` **tam öbeği** arıyor — soruda öbek geçmiyor,
**kelime** geçiyor.

⊙ Doğru yüklem depoda **zaten vardı**: `partial_unknowns` kapsamayı `_syn_hit_words`
ile **kelime düzeyinde** hesaplıyor. İkinci bir kapsama kavramı yazmak `KAT-1` olurdu.

*Bir doğru cevaba «eksik» demek, tüm beyanların güvenini aşındırır* (`§101.1`): kusur
bazen olur, yanlış-pozitif **her seferinde** yanlıştır.
"""

from app.uyum import _kup_sozlugunde_kelime as kapsiyor

_DURUS = {
    "name": "makine_duruslari",
    "display": "duruş nedenleri",
    "synonyms": ["durus nedeni", "durus kaydi", "stoppage reason"],
    "measure_synonyms": {"toplam_sure_dk": ["toplam durus dakikasi", "toplam durus"],
                         "durus_sayisi": ["durus sayisi", "kac durus"]},
    "dimension_synonyms": {"neden": ["neden", "sebep"]},
    "measures": ["toplam_sure_dk", "durus_sayisi"],
    "dimensions": ["neden", "makine"],
}
_KALITE = {
    "name": "kalite",
    "display": "kalite",
    "synonyms": ["kalite", "tamir rework"],
    "measure_synonyms": {"rework_sayisi": ["rework", "tamir sayisi"]},
    "dimension_synonyms": {"musteri": ["musteri"]},
    "measures": ["rework_sayisi"],
    "dimensions": ["musteri"],
}


def test_COK_KELIMELI_SINONIMIN_ICINDEKI_KELIME_KAPSANIR():
    """🔴 **Kusurun kendisi.** `durus` hiçbir sinonime **tek başına** eşit değil ama
    dördünün de **içinde** — ve cevap o kavramı ölçüyor."""
    assert kapsiyor("durus", _DURUS) is True


def test_GERCEK_IKAME_HALA_BEYAN_EDILIR():
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    `§Cİ`'nin ölçtüğü gerçek vaka — kullanıcı **fire** sordu, cevap **rework** verdi —
    bu düzeltmeden **etkilenmemeli**: `kalite`nin sözlüğünde `fire` diye bir kelime yok,
    beyan aynen yazılır. *Bir yanlış-pozitifi kapatırken gerçek pozitifi kapatmak,
    kapıyı dekora çevirir.*
    """
    assert kapsiyor("fire", _KALITE) is False


def test_KENDI_OLCUSU_KAPSANIR():
    """Cevabın kendi ölçüsünün adı elbette kapsanır — kapının tabanı."""
    assert kapsiyor("rework", _KALITE) is True


def test_ALAKASIZ_TERIM_KAPSANMAZ():
    """`ciro` duruş küpünün sözlüğünde geçmez — yüklem **gevşek değil**."""
    assert kapsiyor("ciro", _DURUS) is False


def test_COK_KELIMELI_TERIM_TAMAMI_ARANIR():
    """⚠ Terim kendisi çok kelimeliyse **hepsi** kapsanmalı: bir kelimesi geçiyor diye
    kapsanmış sayılmak, yüklemi gevşetip gerçek ikameyi gizlerdi."""
    assert kapsiyor("toplam durus", _DURUS) is True
    assert kapsiyor("toplam ciro", _DURUS) is False


def test_KISA_KELIMELER_SAYILMAZ():
    """⚠ İki harfli parçalar tesadüfen her yerde bulunur; `partial_unknowns`'ın aynı
    disiplini burada da geçerli."""
    assert kapsiyor("da", _DURUS) is False


def test_BOS_TERIM_KAPSANMIS_SAYILMAZ():
    """*Bir ölçümün susması, ölçtüğü şeyin yokluğu değildir* — boş terim `True`
    dönseydi bütün beyanlar susardı."""
    assert kapsiyor("", _DURUS) is False
