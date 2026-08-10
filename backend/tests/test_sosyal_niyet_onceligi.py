"""🔴🔴 `R2` — **TANINMIŞ BİR NİYET, SOSYAL SINIFI ÇÜRÜTÜR.**

## Ölçülen kusur

```
«peki ne yapmalıyız»  →  «Görüşürüz! İstediğin zaman buradayım.»
trace: sosyal sınıf (kapanis) → deterministik yanıt
```

⊙ Sebep `peki`'nin kapanış kalıplarında olması **tek başına değil**: sosyal sınıfın
*tam kaplama* yüklemi yalnız **katalog** kelimesi arıyordu ve *«ne yapmalıyız»*
katalogda hiçbir terim taşımıyor — ifade "tamamen sosyal" sayıldı. Oysa `followup`
o kalıbı **zaten tanıyor** (`TUR_NE_YAPMALI`).

*Bir sistemin kendi tanıdığı niyeti bir selamlaşma sanması, bilgi eksikliği değil
sıralama hatasıdır.*
"""

from __future__ import annotations

import pytest

from app.cube_router import sosyal_edim
from app.followup import niyet_kalibi_var


@pytest.mark.parametrize("soru", [
    "peki ne yapmalıyız",       # kusurun kendisi
    "peki neden düşük",         # aynı sınıf, kök-neden takibi
    "tamam! peki bunu nasıl yorumlarsın",
])
def test_NIYET_TASIYAN_IFADE_SOSYAL_CEVAP_ALMAZ(soru):
    """🔴 Sosyal kalıp eşleşebilir — ama **tam kaplama** iddia edemez."""
    sonuc = sosyal_edim(soru)
    assert sonuc is None or sonuc[1] is False, (
        f"«{soru}» sosyal cevapla kapatılıyor — oysa tanınmış bir niyet taşıyor "
        f"({niyet_kalibi_var(soru)})")


@pytest.mark.parametrize("soru", ["görüşürüz", "teşekkürler", "merhaba",
                                  "iyi çalışmalar", "kolay gelsin", "tamamdır"])
def test_SAF_SOSYAL_IFADE_HALA_SOSYALDIR(soru):
    """⚠ Kapsam daralmamalı: düzeltme, sosyal yolu **kapatmak** değildir.

    *Bir yanlış-pozitifi kaparken doğru-pozitifi de kapatmak, kusuru yer değiştirmektir.*
    """
    sonuc = sosyal_edim(soru)
    assert sonuc is not None and sonuc[1] is True, soru


def test_VERI_SORUSU_ZATEN_SOSYAL_DEGILDI():
    """Var olan koruma bozulmadı: sosyal kelime + veri sinyali → veri sorusu."""
    sonuc = sosyal_edim("teşekkürler bu yıl ciro")
    assert sonuc is None or sonuc[1] is False


def test_NIYET_KALIBI_TEK_SAHIPTEN_OKUNUR():
    """🔴 İkinci bir sözlük yazılmadı — `sinifla` ile **aynı** tablo."""
    assert niyet_kalibi_var("ne yapmalıyız") == "ne_yapmali"
    assert niyet_kalibi_var("neden böyle") == "neden"
    assert niyet_kalibi_var("merhaba") is None


# ── ZAYIF KANAT — asıl kusur buradaydı ────────────────────────────────────────
#
# `ask.py`'nin sosyal kapısı İKİ kanatlıdır:
#   (a) güçlü: `tam_kaplama` — bağlamdan bağımsız kazanır
#   (b) zayıf: *«veri sinyali bulamadım»* — yalnız bağlam YOKKEN kazanır
# İlk düzeltmem (a)'yı onardı; canlı curl (b)'nin hâlâ kazandığını gösterdi, çünkü
# `veri_niyeti_var` de yalnız **katalog terimi** arıyordu.
#
# *Bir kapının iki kanadı varsa, birini onarmak onu kapatmaz.*


@pytest.mark.parametrize("soru", ["peki ne yapmalıyız", "ne yapmalıyız",
                                  "bunu nasıl yorumlarsın", "neden böyle"])
def test_TANINMIS_NIYET_BIR_VERI_SINYALIDIR(soru, schema):
    """🔴 «anlamadım yok» kuralının doğrudan gereği: bir reçete ya da kök-neden
    sorusuna *hoşça kal* demek, en ucuz ve en hızlı **yanlış** cevaptır."""
    from app.cube_router import veri_niyeti_var

    assert veri_niyeti_var(soru, schema) is True, soru


@pytest.mark.parametrize("soru", ["görüşürüz", "teşekkürler", "merhaba",
                                  "iyi çalışmalar", "kolay gelsin"])
def test_SAF_SOSYAL_IFADE_VERI_SINYALI_TASIMAZ(soru, schema):
    """⚠ Kapsam daralmamalı — sosyal yol **kapatılmadı**, önceliği düzeltildi."""
    from app.cube_router import veri_niyeti_var

    assert veri_niyeti_var(soru, schema) is False, soru
