r"""🔴 `§B.4` — **ROUTE ÇEKİLİYORDU AMA SEBEBİ SAYILMIYORDU.**

`§B.1`'de ölçüldü: çok sahipli bir terimde `route()` **`None`** dönüyor — kural
**uygulanıyor** ve çürütülebilir. Ama `None` **sebepsizdi**: *«`adet` altı küpe işaret
ediyor»* ile *«bu kelimeyi hiç tanımıyorum»* **aynı boşluğa** düşüyordu.

⊙ Sonuç: garsonun yükünün **ne kadarının** belirsizlikten geldiği bilinemiyordu — ve
`§A.2`'nin **73 çok-sahipli terimlik** borcunun **ürün maliyeti** ölçülemiyordu.

✅ `Niyet.cekilme_sebebi` — **türev**, alan değil (`referans`'ın gerekçesiyle aynı:
*bir değeri iki yerden yazılabilir yapmak, iki değeri garanti etmektir*). Yalnız nesnenin
**zaten taşıdığı** alanlardan okunur; yeni ölçüm/liste/eşik **yok**.

> 🆓 *Bir boşluğu saymak için önce ona bir ad vermek gerekir; adsız bir boşluk, her
> seferinde başka bir şeyle karıştırılır.*
"""

from __future__ import annotations

from app.niyet import Niyet


def _n(**kw) -> Niyet:
    return Niyet(soru=kw.pop("soru", "x"), **kw)


def test_COK_SAHIPLI_TERIM_AYRI_SINIFLANIYOR():
    """🔴 **ASIL KAPI.** `adet` → 6 küp: bu bir **bilgisizlik değil çokluk**."""
    n = _n(olcu_adaylari=[("bakim", "ariza_sayisi"), ("cari", "hareket_sayisi"),
                          ("kalite", "rework_sayisi")])
    assert n.cekilme_sebebi == Niyet.SEBEP_COK_SAHIP


def test_TEK_SAHIP_CEKILME_SEBEBI_URETMIYOR():
    """⚠ `§101.1` — tek sahipli bir terimde sebep **üretilmemeli**; yoksa her cevap bir
    belirsizlik vakası gibi sayılır ve oran anlamsızlaşır."""
    n = _n(olcu_adaylari=[("parti", "toplam_ciro")])
    assert n.cekilme_sebebi is None


def test_AYNI_KUPTE_IKI_OLCU_COKLUK_SAYILMIYOR():
    """🔴 **İNCE AYRIM.** İki aday **aynı küpte**yse bu bir sahiplik çatışması değil;
    ölçüt **küp** kümesidir, aday sayısı değil.

    *Bir çokluğu aday sayısıyla ölçmek, aynı evin iki odasını iki ev sanmaktır.*
    """
    n = _n(olcu_adaylari=[("parti", "toplam_ciro"), ("parti", "toplam_fire_kg")])
    assert n.cekilme_sebebi is None


def test_BILINMEYEN_TOKEN_AYRI_SINIF():
    n = _n(bilinmeyenler=["kablosuz"])
    assert n.cekilme_sebebi == Niyet.SEBEP_BILINMEYEN


def test_OLCU_YOKSA_UCUNCU_SINIF():
    assert _n().cekilme_sebebi == Niyet.SEBEP_OLCU_YOK


def test_COKLUK_BILINMEYENDEN_ONCE_GELIR():
    """⚠ Sıra **anlamlıdır**: bir soru hem çok sahipli bir terim hem tanınmayan bir
    kelime taşıyorsa, ürün açısından ağır olan **çokluktur** (cevap üretilebilir ama
    hangi tanımla belirsiz). *Bir sınıflandırmanın sırası, onun ne için sayıldığını
    belli eder.*"""
    n = _n(olcu_adaylari=[("cari", "bakiye"), ("mizan", "bakiye")],
           bilinmeyenler=["zebra"])
    assert n.cekilme_sebebi == Niyet.SEBEP_COK_SAHIP


def test_SEBEP_KUMESI_KAPALI():
    """⚠ `ADR-0008` — sebep kümesi **kapalı** olmalı; açık uçlu bir dize alanı bir gün
    serbest metin taşır ve sayılamaz hâle gelir."""
    kapali = {Niyet.SEBEP_COK_SAHIP, Niyet.SEBEP_BILINMEYEN, Niyet.SEBEP_OLCU_YOK}
    assert len(kapali) == 3
    for s in kapali:
        assert isinstance(s, str) and s and " " not in s
