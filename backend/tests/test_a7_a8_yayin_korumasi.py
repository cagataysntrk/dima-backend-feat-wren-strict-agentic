r"""🔴🔴 `§A7` + `§A8` — YAYINLANDI **AMA KORUMASIZDI**.

## Ölçülen boşluk

`§A8` (*«Inspect AI'ın `stderr`'i»* — Wilson %95 güven aralıkları) ve `§A7` (EHRSQL
güvenilirlik ayrımı) `belgeler/DOGRULUK.md`'ye **on yeni sayı** koydu. Bir denetim
ajanı sordu, ölçüm doğruladı:

    grep -c "Wilson\|ci95\|%95"  tests/test_f8_dogruluk_yayini.py           → 0
    grep -c "Wilson\|ci95\|%95"  tests/test_f8_dogruluk_ayrimi_kapaniyor.py → 0

Yani dört güven aralığı ve EHRSQL tablosu bugün **silinebilir, değiştirilebilir,
bayatlayabilir** ve süit yeşil kalır. Oysa aynı belgenin kendi cümlesi:

> *«Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan kötüdür — çünkü
> ona güvenilir.»*

## Yüklem — **yeniden hesap**, dizge eşleme değil

Kapı yayınlanan aralığı okuyup *«yazılı mı»* diye sormaz; **oran ve paydadan yeniden
hesaplar** ve tutmasını ister. Böylece üç sayıdan biri kayarsa (oran · aralık · payda)
kapı konuşur.

🔴 **Ve hesap YENİDEN YAZILMADI** (`KAT-1`): `eval/run.py:209`'daki `wilson()` **zaten
var** ve üretimde `coverage_ci95`/`precision_ci95`'i o üretiyor. İkinci bir Wilson
uygulaması yazmak, aynı istatistiğin iki sahibi olması demekti — ve ikisi bir gün
ayrışırdı. *Bir yayını korumak için yazdığın kod, koruduğu şeyin ikizi olmamalıdır.*

⊙ Ölçüldü: mevcut `wilson()` yayınlanan **dört aralığın dördünü de** birebir üretiyor
(`[95,2–96,0]` · `[92,3–96,0]` · `[19,1–20,3]` · `[0,15–0,63]`).
"""

from __future__ import annotations

import pathlib
import re

import pytest

_BELGE = pathlib.Path(__file__).parent.parent.parent / "belgeler" / "DOGRULUK.md"

pytestmark = pytest.mark.skipif(
    not _BELGE.parent.is_dir(),
    reason="`belgeler/` bağlanmamış — konteynere `-v \"$PWD/belgeler:/belgeler:ro\"` ekleyin")

#: `%95,6` → `95.6` · `11.237` → `11237` (Türkçe binlik `.`, ondalık `,`)
def _sayi(m: str) -> float:
    return float(m.replace(".", "").replace(",", "."))


def _satirlar() -> list[tuple[str, float, float, float, int]]:
    """`DOGRULUK.md`'nin aralık tablosundan `(ad, oran, alt, ust, payda)`.

    ⚠ Ayrıştırıcı **yapıya** bağlı (tablo hücreleri), bir dize dilimine değil — bu
    deponun ⑭ numaralı dersi.
    """
    out = []
    for satir in _BELGE.read_text(encoding="utf-8").splitlines():
        if not satir.startswith("|"):
            continue
        h = [x.strip() for x in satir.split("|")[1:-1]]
        if len(h) < 4:
            continue
        oran = re.search(r"%([\d.,]+)", h[1])
        aralik = re.search(r"%([\d.,]+)\s*[–-]\s*%([\d.,]+)", h[2])
        payda = re.search(r"^\**([\d.]+)\**$", h[3])
        if oran and aralik and payda:
            out.append((re.sub(r"\*", "", h[0]), _sayi(oran.group(1)),
                        _sayi(aralik.group(1)), _sayi(aralik.group(2)),
                        int(payda.group(1).replace(".", ""))))
    return out


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı** — sıfır satır ayrıştıran bir kapı her yayını doğrular."""
    s = _satirlar()
    assert len(s) >= 4, (
        f"⊘ ölçüm tabanı çöktü: aralık tablosundan yalnız {len(s)} satır okundu "
        f"({[x[0] for x in s]}). Tablo biçimi değiştiyse ayrıştırıcı düzeltilsin — "
        "kapı susturulmasın.")


def test_WILSON_ARALIKLARI_YENIDEN_HESAPLANINCA_TUTUYOR():
    """🔴🔴 **ASIL KAPI.** Her yayınlanan aralık, kendi oranı ve paydasından
    **yeniden hesaplanınca** aynı çıkmalı.

    Kırmızı verirse üç sayıdan biri kaymıştır: oran · aralık · payda. Hangisi olursa
    olsun yayın **kendi içinde tutmuyor** demektir ve okuyucu bunu ayırt edemez.
    """
    from eval.run import wilson

    sapan = []
    for ad, oran, alt, ust, payda in _satirlar():
        k = round(oran / 100 * payda)
        _p, lo, hi = wilson(k, payda)
        # yayında bir ondalık (bazı satırlarda iki) — tolerans o yuvarlamadır
        if abs(lo * 100 - alt) > 0.06 or abs(hi * 100 - ust) > 0.06:
            sapan.append(f"{ad}: yayın [{alt}–{ust}] ↔ hesap "
                         f"[{lo * 100:.2f}–{hi * 100:.2f}] (k={k}, n={payda})")
    assert not sapan, (
        "🔴 YAYINLANAN GÜVEN ARALIĞI TUTMUYOR:\n  " + "\n  ".join(sapan) +
        "\n*Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan kötüdür — "
        "çünkü ona güvenilir.*")


def test_ARALIK_HESABININ_TEK_SAHIBI_VAR():
    """⚠ `KAT-1`: Wilson hesabı **bir** yerde yaşamalı.

    Bu kapı `eval/run.py`'nin `wilson`'ını **çağırıyor**, kendi kopyasını yazmıyor.
    İkinci bir uygulama doğarsa ikisi bir gün ayrışır ve hangisinin yayını ürettiği
    bilinemez.
    """
    import ast

    kok = pathlib.Path(__file__).parent.parent
    sahipler = []
    for f in list((kok / "app").rglob("*.py")) + list((kok / "lab").rglob("*.py")) \
            + list((kok / "eval").rglob("*.py")):
        try:
            agac = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):            # noqa: PERF203
            continue
        for n in ast.walk(agac):
            if isinstance(n, ast.FunctionDef) and "wilson" in n.name.lower():
                sahipler.append(f"{f.relative_to(kok)}:{n.lineno}")
    assert len(sahipler) == 1, (
        f"🔴 Wilson hesabının {len(sahipler)} sahibi var: {sahipler}. "
        "*Bir yayını korumak için yazdığın kod, koruduğu şeyin ikizi olmamalıdır.*")


def test_EHRSQL_AYRIMI_YAYINDA_PAYDAYA_KAPANIYOR():
    """🔴 `§A7`'nin beş satırı **yayında** paydaya kapanmalı.

    ⊙ Kardeş kapı (`test_f8_dogruluk_ayrimi_kapaniyor`) bunu **artefakttan** ölçüyor;
    bu kapı **belgeden** ölçüyor. İkisi ayrı şeydir: artefakt kapanıp belge kapanmazsa
    (bu turda tam olarak bu oldu — **45 satır adsızdı**) yalnız bu kapı konuşur.
    """
    m = _BELGE.read_text(encoding="utf-8")
    # `§A7` bloğu: davranış tablosu + netleştirme satırı
    bulunan = {}
    for etiket, desen in (
            ("kapsam-dışı red", r"kapsam-\*\*dışı\*\* soruya \*\*red\*\*[^|]*\|[^|]*\|\s*\*\*([\d.]+)\*\*"),
            ("kapsam-dışı cevap", r"kapsam-\*\*dışı\*\* soruya \*\*CEVAP\*\*[^|]*\|[^|]*\|\s*\*\*([\d.]+)\*\*"),
            ("kapsam-içi red", r"kapsam-\*\*içi\*\* soruya \*\*red\*\*[^|]*\|[^|]*\|\s*\*\*([\d.]+)\*\*"),
            ("kapsam-içi cevap", r"kapsam-\*\*içi\*\* soruya cevap[^|]*\|[^|]*\|\s*\*\*([\d.]+)\*\*"),
            ("Discovery sapması", r"Discovery'ye düştü[^|]*\|[^|]*\|\s*\*\*([\d.]+)\*\*"),
            ("netleştirme", r"netleştirme[^\n]*?([\d.]+)\s+\(%"),
    ):
        g = re.search(desen, m)
        if g:
            bulunan[etiket] = int(g.group(1).replace(".", ""))
    assert len(bulunan) >= 5, (
        f"⊘ ölçüm tabanı çöktü: `§A7` tablosundan yalnız {len(bulunan)} satır okundu: "
        f"{bulunan}")
    payda = next((n for ad, _o, _a, _u, n in _satirlar() if "esme" in ad or "kesme" in ad),
                 None)
    assert payda, "⊘ `Cevapsız kesme` paydası okunamadı"
    toplam = sum(bulunan.values())
    assert toplam == payda, (
        f"🔴 `§A7` AYRIMI YAYINDA KAPANMIYOR: satırlar {toplam}, payda {payda}, "
        f"fark **{payda - toplam}**.\n  {bulunan}\n"
        "*Bir ayrım paydasına kapanmıyorsa «tam ayrım» değil bir SEÇKİDİR* — ve "
        "seçilmeyenin adı, çoğu zaman ölçmek istediğin şeydir.")
