r"""🔴🔴 `§F8`/`§A7` — YAYINLANAN DAVRANIŞ AYRIMI **PAYDAYA KAPANMALI**.

## Neden bu kapı — bir denetim ajanının ölçtüğü boşluk

`test_f8_dogruluk_yayini.py`'nin kendi sözü şuydu: *«bu dosya belgedeki **her** sayıyı
`lab/reports/nl_corpus.json`'dan yeniden hesaplar»*. Ölçüldü, **hesaplamıyordu**: `§A7`
yayını `DOGRULUK.md`'ye **on yeni sayı** koydu (`85`·`1`·`339`·`11.732`·`2.755`·…) ve
**hiçbir test dosyasına dokunmadı**.

Bedeli aynı turda görüldü — yayınlanan ayrım **kapanmıyordu**:

    11.732 + 339 + 2.755 + 85 + 1 = 14.912        payda = 14.957
                                    ADSIZ = 45  (%0,30)

⊙ Ve o 45'in kim olduğu önemliydi: `CUBE-SAPMA(None)` — soru küplerde karşılanamayıp
**Discovery'ye düşen** turlar. Yani ayrımdan düşen kategori, `CLAUDE.md`'nin *«her
Discovery ateşlenmesi bir MUTFAK EKSİKLİĞİ RAPORUDUR»* kuralının **tam ölçüsüydü**.

> *Bir ödünç alınan şema (EHRSQL: cevap ↔ red), kendi tanımadığı kategoriyi görünmez
> yapar — ve görünmeyen kategori çoğu zaman ölçmek istediğin şeyin ta kendisidir.*

## Yüklem — **kapanış**, tek tek sayılar değil

Bu kapı belgedeki her rakamı ayrıştırmaya çalışmıyor (kardeş dosya onu yapıyor). Onun
yerine **yapısal** olanı ölçüyor: ayrımın **toplamı paydaya eşit mi**. Bir kategori
eklenir, silinir ya da yeniden sınıflanırsa toplam kayar ve kapı konuşur — kimse
belgedeki bir sayıyı elle güncellemeyi unutsa bile.

⚠ Ve **tesadüf eşleşmesi elenmiştir** (ders ㉘): belgede aranan sayılar yalnız
**≥100** olanlardır; `1`, `45`, `85` gibi küçük sayılar bir metinde tesadüfen geçer ve
onları aramak, kapıyı bir rastlantı üstüne kurmak olurdu.
"""

from __future__ import annotations

import collections
import json
import pathlib

import pytest

_BACKEND = pathlib.Path(__file__).parent.parent
_ARTEFAKT = _BACKEND / "lab" / "reports" / "nl_corpus.json"
_BELGE = _BACKEND.parent / "belgeler" / "DOGRULUK.md"

pytestmark = pytest.mark.skipif(
    not _BELGE.parent.is_dir(),
    reason="`belgeler/` bağlanmamış — konteynere `-v \"$PWD/belgeler:/belgeler:ro\"` ekleyin")


def _olcum() -> tuple[collections.Counter, int]:
    """→ `({kategori: adet}, payda)` — **artefakttan**, belgeden değil."""
    if not _ARTEFAKT.is_file():
        pytest.skip(f"⊘ ölçüm artefaktı yok ({_ARTEFAKT.name}) — korpus hiç koşmamış")
    veri = json.loads(_ARTEFAKT.read_text(encoding="utf-8"))
    say: collections.Counter = collections.Counter()
    for sirket in veri:
        for anahtar, adet in (sirket.get("cats") or {}).items():
            # `tekil::OK` / `süreç::OK` → aynı davranış, iki koşum yolu
            say[anahtar.split("::")[-1]] += adet
    payda = sum(s.get("kesme_payda", 0) for s in veri)
    return say, payda


def _tr(n: int) -> str:
    """`14957` → `14.957` — belgenin (ve Türkçe'nin) binlik ayırıcısı."""
    return f"{n:,}".replace(",", ".")


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı** — sıfır kategori okuyan bir sayaç her ayrımı doğrular."""
    say, payda = _olcum()
    assert len(say) >= 5, f"⊘ yalnız {len(say)} kategori okundu: {dict(say)}"
    assert payda > 1000, f"⊘ payda anlamsız: {payda}"


def test_AYRIM_PAYDAYA_KAPANIYOR():
    """🔴🔴 **ASIL KAPI.** Davranış ayrımının toplamı paydaya **eşit** olmalı.

    Eşit değilse yayın *«tam ayrım»* demeye devam ederken bir kategoriyi **adsız**
    bırakıyor demektir — ve bu turda adsız kalan, tam da mutfak eksiğini ölçen
    kategoriydi.
    """
    say, payda = _olcum()
    toplam = sum(say.values())
    assert toplam == payda, (
        f"🔴 AYRIM KAPANMIYOR: kategoriler {toplam}, payda {payda}, fark "
        f"**{payda - toplam}**.\nKategoriler: {dict(say.most_common())}\n"
        "*Bir ayrım paydasına kapanmıyorsa, «tam ayrım» değil bir SEÇKİDİR* — ve "
        "seçilmeyenin adı, çoğu zaman ölçmek istediğin şeydir.")


def test_MUTFAK_EKSIGI_KATEGORISI_YAYINDA_ADIYLA_VAR():
    """🔴 `CUBE-SAPMA(None)` yayında **adıyla** durmalı.

    ⊙ `CLAUDE.md`'nin en üst kuralı: *«Discovery'nin her ateşlenmesi bir MUTFAK
    EKSİKLİĞİ RAPORUDUR… hedef oranını sıfıra yaklaştırmak»*. Bu sayı yayından
    düşerse, hedefin ölçüsü de düşer.
    """
    say, _ = _olcum()
    if "CUBE-SAPMA(None)" not in say:
        pytest.skip("⊘ bu koşumda hiç Discovery sapması yok — kategori doğmamış (iyi haber)")
    metin = _BELGE.read_text(encoding="utf-8")
    assert "CUBE-SAPMA" in metin, (
        "🔴 `DOGRULUK.md` Discovery'ye düşen turları **adsız** bırakıyor. Yayın "
        "*«davranışın tam ayrımı»* diyorsa, karşılanamayan soruyu da saymalıdır.")


def test_BUYUK_SAYILAR_YAYINDA_TAZE():
    """⚠ Yeniden hesaplanan **≥100** kategorilerin her biri belgede geçmeli.

    Korpus yeniden koşup bir sayı kayarsa, belge onu **elle** güncellemeyi unutabilir —
    `§A7` yayınında birebir bu oldu (on yeni sayı, sıfır kapı).

    ⚠ Eşik `100`: küçük sayılar (`1`·`45`·`85`) bir metinde tesadüfen geçer ve onları
    aramak kapıyı bir **rastlantının** üstüne kurmak olurdu (ders ㉘).
    """
    say, payda = _olcum()
    metin = _BELGE.read_text(encoding="utf-8")
    eksik = {k: v for k, v in say.items() if v >= 100 and _tr(v) not in metin}
    # ⊙ `CLARIFY:*` üçlüsü belgede **toplanarak** yayımlanıyor (`netleştirme 2.755`) —
    #   bu bilinçli bir sunum kararı, bir eksiklik değil; toplamları aranır.
    netlestirme = sum(v for k, v in say.items() if k.startswith("CLARIFY"))
    for k in list(eksik):
        if k.startswith("CLARIFY") and _tr(netlestirme) in metin:
            del eksik[k]
    assert not eksik, (
        f"🔴 yayınlanan ayrım BAYAT — bu kategoriler belgede geçmiyor: {eksik}. "
        f"(payda {_tr(payda)})\n*Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış "
        "bir sayıdan kötüdür — çünkü ona güvenilir.*")


def test_PAYDA_YAYINDA_ve_KESME_ORANI_TUTUYOR():
    """⚠ Manşet oran (`%19,7 cevapsız kesme`) paydasıyla birlikte doğrulanır.

    ⊙ Yüklem oranı **yeniden hesaplıyor**: belgedeki yüzdeyi okuyup kendine
    doğrulatmak, bir sayıyı kendi kopyasıyla ölçmek olurdu.
    """
    _, payda = _olcum()
    veri = json.loads(_ARTEFAKT.read_text(encoding="utf-8"))
    kesme = sum(s.get("kesme_sayi", 0) for s in veri)
    metin = _BELGE.read_text(encoding="utf-8")
    assert _tr(payda) in metin, f"🔴 payda ({_tr(payda)}) yayında geçmiyor"
    oran = f"%{100 * kesme / payda:.1f}".replace(".", ",")
    assert oran in metin, (
        f"🔴 cevapsız-kesme oranı BAYAT: artefakt **{oran}** diyor ({kesme}/{payda}), "
        f"belgede yok. Bir oranı paydası değişince güncellememek, payda oyununun "
        "kendisidir.")
