"""🔴 `§0.6` KARNESİ **KENDİ SATIRLARINI SAYMALI** — manşet çürümez.

## Ölçülen kusur (2026-08-12)

Raporun tek sayfalık karnesi 30 satır taşıyor ve her satır bu oturumda **tek tek**
güncellendi. Ama altındaki özet satır güncellenmedi:

    yazılı  : 🟢 9 var · 🟡 5 yarım · 🔴 16 yok
    ölçülen : 🟢 18   · 🟡 5      · 🔴 7

⊙ Yani belgeyi açan biri *«9 var, 16 yok»* okuyup ürünü **yarısı yapılmış** sanırdı —
oysa 30 satırın 18'i yeşil. Bu, `§F8`'in kendi cümlesinin bu rapordaki hâlidir:

> *Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan kötüdür — çünkü ona
> güvenilir.*

## Neden bir KAPI

Karne **yürürlükteki planın** özetidir; bir sonraki turun neyi öncelikleyeceğini o
belirler. Bayat bir manşet yalnız yanlış bilgi değil, **yanlış öncelik** üretir.

⚠ Ve elle saymak çözüm değildir: satırlar her turda değişiyor. *Bir karneyi elle
saymak, bir gün yanlış saymaktır.* Kapı manşeti satırlardan **yeniden hesaplar**.

## Kapsam

Bu kapı yalnız **iç tutarlılık** ölçer — bir satırın 🟢 olup olmaması hâlâ bir
insan kararıdır ve öyle kalmalı. Ölçtüğü tek şey: *söylediğin sayı, saydığın satırlarla
aynı mı.*
"""

from __future__ import annotations

import pathlib
import re

_RAPOR = (pathlib.Path(__file__).parent.parent.parent / "belgeler" / "arastirma"
          / "2026-08-11_REKABET-VE-MIMARI-ANALIZI.md")

#: ⚠ İki AYRI eksiklik, iki AYRI sonuç (`§F8`'in hijyeni):
#:   · `belgeler/` **hiç bağlanmamış** → koşum ortamı eksiği → **SKIP**
#:   · dizin var ama rapor yok → plan gerçekten kayıp → **FAIL**
import pytest  # noqa: E402

pytestmark = pytest.mark.skipif(
    not _RAPOR.parent.is_dir(),
    reason="`belgeler/` bağlanmamış — konteynere `-v \"$PWD/belgeler:/belgeler:ro\"` ekleyin")

_ISARETLER = ("🟢", "🟡", "🔴")


def _karne() -> tuple[dict[str, int], str]:
    """→ `({işaret: adet}, özet satırı)`.

    ⚠ Ayrıştırıcı **gövdeye** kurulu: her tablo satırının **son hücresi** okunur.
    İlk sürümüm satır adının `**kalın**` olmasını şart koşuyordu ve 30 satırın
    **16'sını** yakaladı — bu turda aracın yirmi sekizinci yanılması. *Bir ayrıştırıcı,
    ölçtüğü şeyin biçimine değil YAPISINA bağlanmalıdır.*
    """
    s = _RAPOR.read_text(encoding="utf-8").splitlines()
    bas = next(i for i, l in enumerate(s) if l.startswith("### 0.6 "))
    son = next(i for i, l in enumerate(s[bas:], bas) if l.startswith("**Sayım:**"))
    say = dict.fromkeys(_ISARETLER, 0)
    for l in s[bas:son]:
        if not re.match(r"^\|\s*\d+\s*\|", l):
            continue
        son_hucre = l.split("|")[-2]
        for k in _ISARETLER:
            if k in son_hucre:
                say[k] += 1
                break
    return say, s[son]


def test_KARNE_BULUNUYOR_ve_SATIRLARI_var():
    """⊘ Ön koşul: ayrıştırıcı gerçekten satır buluyor mu. **Boş yeşil avı** — sıfır
    satır bulan bir sayaç, her manşeti doğrular."""
    say, _ = _karne()
    assert sum(say.values()) >= 25, (
        f"⊘ ölçüm tabanı çöktü: karnede yalnız {sum(say.values())} satır bulundu. "
        "Tablo biçimi değişmiş olabilir — ayrıştırıcı düzeltilsin, kapı susturulmasın.")


def test_MANSET_SATIRLARLA_AYNI():
    """🔴 Manşet, saydığı satırlarla **aynı** olmalı."""
    say, ozet = _karne()
    for isaret, beklenen in ((s, say[s]) for s in _ISARETLER):
        bulunan = re.search(rf"{isaret} \*\*(\d+)", ozet)
        assert bulunan, f"özet satırında `{isaret}` sayısı yok: {ozet[:120]}"
        assert int(bulunan.group(1)) == beklenen, (
            f"🔴 KARNE MANŞETİ BAYAT: `{isaret}` için özet **{bulunan.group(1)}** diyor, "
            f"satırlar **{beklenen}**.\n"
            "Karne yürürlükteki planın özetidir; bayat bir manşet yalnız yanlış bilgi "
            "değil, YANLIŞ ÖNCELİK üretir. Özeti satırlardan yeniden yaz.")


def test_TOPLAM_30_satir():
    """Satır sayısı düşerse bir yetenek **sessizce** karneden çıkmış demektir —
    payda oyununun karnedeki hâli (`§F8`'in `test_HER_SIRKET_belgede` dersi)."""
    say, _ = _karne()
    assert sum(say.values()) == 30, (
        f"karne satır sayısı {sum(say.values())} (önce 30). Bir yetenek eklendiyse özet "
        "de büyümeli; ÇIKARILDIYSA gerekçesi yazılmalı — sessizce düşen bir satır, "
        "ölçülmeyen bir eksikliktir.")
