"""🔴🔴 `E1` — **DESEN BİR KEZ DERLENİR** ve davranış birebir aynı kalır.

## Ölçüm (cProfile, 10 istek — hepsi *«teşekkürler»*, yani ürün ~hiçbir iş yapmıyor)

| | önce | sonra |
|---|---|---|
| `ask()` | **903 ms**/istek | **316 ms**/istek |
| `re._compile` | **60.720** çağrı → 5,66 s | — |
| `_syn_hit` | 50.940 çağrı (istek başına **5.094**) | aynı, ama derlemesiz |

⊙ Bir **selamlaşma** için istek başına altı bin regex derleniyordu. Python `re`
derlenmiş desenleri önbelleğe alır ama önbellek **512 kalemdir** ve bu depoda yüzlerce
sinonim var — önbellek her turda **çöpe dönüyordu**.

⚠ Rapor `E-1` bunu adıyla yazmıştı (*"`cube_router`'da SIFIR memoizasyon"*); teşhis
doğruydu, **ölçüsü yoktu**. `A10` kapısı ölçüyü verdi, profil kökü gösterdi.

*Bir kuralı her sorduğunda yeniden yazmak, kuralı değiştirmez — yalnız sormayı pahalı
yapar.*
"""

from __future__ import annotations

from app.cube_router import _norm, _syn_desen, _syn_hit


def test_DAVRANIS_BIREBIR_AYNI():
    """🔴 Memoizasyon bir **hızlandırmadır**, bir kural değişikliği değil."""
    ornekler = [
        ("bu yil toplam ciro", "ciro", True),
        ("renkler bazinda fire", "renk", True),
        ("bu ayrica onemli", "bu ay", False),      # `in q` tuzağı — hâlâ kapalı
        ("trendyol satislari", "trend", False),    # aynı sınıf
        ("uygun fiyat", "gun", False),
        ("nasil degisti", "de!", False),           # tam-kelime işareti korunur
    ]
    for q, syn, beklenen in ornekler:
        assert _syn_hit(_norm(q), syn) is beklenen, (q, syn)


def test_AYNI_SINONIM_AYNI_NESNEYI_DONER():
    """⊙ Memoizasyonun kanıtı: ikinci çağrı **yeni bir nesne üretmez**."""
    a = _syn_desen("ciro", False)
    b = _syn_desen("ciro", False)
    assert a is b, "desen önbelleğe alınmıyor — `lru_cache` çalışmıyor"


def test_TAM_KELIME_VE_EKLI_DESEN_AYRI_ONBELLEKLENIR():
    """🔴 İkisi **farklı** desenlerdir; aynı anahtara düşerlerse biri ötekini ezer
    ve `!` işaretinin koruması **sessizce** kaybolurdu."""
    assert _syn_desen("de", True) is not _syn_desen("de", False)


def test_ONBELLEK_SINIRSIZ_DEGIL():
    """⚠ Sınırsız bir önbellek, sinonim sayısıyla büyüyen bir sızıntıdır."""
    assert _syn_desen.cache_info().maxsize is not None
