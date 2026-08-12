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

#: 🔴 Türkçe sayı sözcükleri — **kapalı bir gramer sınıfı** (`ADR-0008` bunu açıkça
#: ayırıyor: açık uçlu kelime listesi yasak, kapalı gramatik sınıf serbest).
_SAYI_SOZCUGU = {
    "bir": 1, "iki": 2, "üç": 3, "dört": 4, "beş": 5, "altı": 6, "yedi": 7,
    "sekiz": 8, "dokuz": 9, "on": 10, "on bir": 11, "on iki": 12, "on üç": 13,
    "on dört": 14, "on beş": 15, "on altı": 16, "on yedi": 17, "on sekiz": 18,
    "on dokuz": 19, "yirmi": 20,
}
_RENK = {"yeşil": "🟢", "sarı": "🟡", "kırmızı": "🔴"}


def _iddia_govdesi() -> str:
    """🔴 Karne bölümünün **İDDİA** metni — alıntılar çıkarılmış hâli.

    ## Neden gerekli — kapı kendi düzeltme notunu suçladı

    İlk sürüm tüm bölümü tarıyordu ve **kendi ⟳ düzeltme notumdaki alıntıyı** yakaladı:
    not, eski bayat metni *«dokuz yeşil / on altı kırmızı / beş sarı»* diye **aktarıyor**
    ve kapı bunu bir iddia sandı.

    ⊙ Bu, bu deponun `grep`-docstring dersinin aynısı: *bir tarayıcı, alıntıyı iddiadan
    ayırmıyorsa kendi kaydını suçlar.* Ve düzeltme notunu yazmayı **cezalandıran** bir
    kapı, kayıt tutmayı caydırır.

    ## Ayrım YAPISAL — iki kapalı işaretle

    | çıkarılan | neden |
    |---|---|
    | `>` ile başlayan satırlar | markdown **blok alıntısı**; bu belgede ⟳ düzeltme notlarının evi |
    | `*«…»*` arasındaki metin | bu deponun **aktarma** işareti (kendi metnini değil, birinin sözünü taşır) |

    İkisi de biçim değil **yapı**dır: bir kelime listesi değil, iki markdown/tipografi
    kuralı.
    """
    import re as _re

    s = _RAPOR.read_text(encoding="utf-8").splitlines()
    bas = next(i for i, l in enumerate(s) if l.startswith("### 0.6 "))
    son = next((i for i, l in enumerate(s[bas + 1:], bas + 1)
                if l.startswith("## ")), len(s))
    satirlar = [l for l in s[bas:son] if not l.lstrip().startswith(">")]
    govde = "\n".join(satirlar)
    govde = _re.sub(r"«[^»]*»", " ", govde)          # aktarma işareti içi
    return govde.lower()


def test_KARNE_PROSASI_da_MANSETLE_TUTUYOR():
    """🔴🔴 **BİR KAPIYI TEK CÜMLEYE BAĞLAMAK, KOMŞUSUNA YALAN SÖYLEME İZNİDİR.**

    ## Ölçülen kusur (2026-08-12) — ve bu kapının KENDİ eksiğiydi

    İki tur önce karne **manşeti** düzeltildi ve bu dosya onu kilitledi. Ama hemen
    altındaki üç cümle bayat kaldı ve kapı onları **görmedi**:

        «Kalan 🔴 **yedi**»                              (ölçülen: 6)
        «Gerçekten açık **üç** ürün kalemi»              (ölçülen: 1 + 1 bayraklı)
        «**dokuz** yeşilin … **on altı** kırmızının … **beş** sarının»  (18/6/6)

    ⊙ Yani manşet doğruydu, **paragraf yalan söylüyordu** — ve bir okuyucu için ikisi
    aynı belgedir. Bir denetim ajanı bunu bağımsız olarak buldu; kapı bulamadı, çünkü
    kapı **tek bir satırı** ölçüyordu.

    ## Yüklem — kapalı gramer sınıfı, açık uçlu liste DEĞİL

    `ADR-0008` açık uçlu **kelime listelerini** yasaklar; Türkçe sayı sözcükleri ise
    **kapalı bir gramer sınıfıdır** (`bir`…`yirmi`) — depoda `_TREND` fiil kümesiyle
    aynı meşruiyet. Yüklem: karne bölümünde `<sayı sözcüğü> <renk>` kalıbı geçiyorsa,
    o sayı **satırlardan hesaplanan** sayıya eşit olmalı.

    ⚠ Yalnız karne bölümünü tarar (`### 0.6` → bir sonraki `##`); belgenin geri kalanı
    bir anlatıdır ve orada *«dokuz yeşil»* demek bir sayım iddiası değildir.
    """
    import re

    say, _ = _karne()
    govde = _iddia_govdesi()
    # Uzun sözcükler önce (on altı, on sekiz…) — kısa olan uzunu parçalamasın.
    for sozcuk in sorted(_SAYI_SOZCUGU, key=len, reverse=True):
        for renk_ad, isaret in _RENK.items():
            # ⚠ `(?<!on )` — «on sekiz yeşil» içindeki «sekiz»i yakalamamak için.
            # İlk sürümüm bunu yakaladı: bileşik sayı sözcüğünün ikinci parçası kendi
            # başına bir sayı gibi okunuyordu. *Kapalı bir sınıfı taramak, sınıfın
            # BİLEŞİK üyelerini de tanımayı gerektirir.*
            for kalip in (rf"(?<!on )\b{sozcuk}\s+{renk_ad}",
                          rf"(?<!on )\b{sozcuk}\s+\*\*{renk_ad}"):
                if re.search(kalip, govde):
                    assert _SAYI_SOZCUGU[sozcuk] == say[isaret], (
                        f"🔴 KARNE PROSASI BAYAT: «{sozcuk} {renk_ad}» yazıyor ama "
                        f"satırlar {say[isaret]} diyor.\n"
                        "Manşeti düzeltip paragrafı bırakmak, kapıyı tek cümleye "
                        "bağlamaktır — komşusu yalan söylemeye devam eder.")


def test_KALAN_KIRMIZI_SAYISI_da_TUTUYOR():
    """*«Kalan 🔴 altı»* gibi doğrudan işaretli sayımlar da satırlarla tutmalı."""
    import re

    say, _ = _karne()
    govde = _iddia_govdesi()
    for isaret in _ISARETLER:
        for m in re.finditer(rf"kalan\s+\**{isaret}\**\s+\**(\w+)", govde):
            sz = m.group(1)
            if sz in _SAYI_SOZCUGU:
                assert _SAYI_SOZCUGU[sz] == say[isaret], (
                    f"🔴 «kalan {isaret} {sz}» yazıyor, satırlar {say[isaret]} diyor")
