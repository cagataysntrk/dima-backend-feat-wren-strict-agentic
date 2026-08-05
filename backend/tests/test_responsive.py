"""FAZ 7.6 kapısı — **üç kademe: masaüstü >1024 · tablet 768-1024 · mobil <768.**
[bayraksız: V-2]

> *"Responsive **GÜN-1** gereksinimidir."* — ve yol haritası bu kapının **FAZ 7'nin
> sonunda değil, her frontend maddesinde** koşmasını istiyor: *sonradan eklenen
> responsive, yeniden yazım demektir.*

## Ölçülen taban — teşhis DOĞRULANDI

| sinyal | ölçüm (7.6 öncesi) |
|---|---|
| `sm:` | 7 · `md:` **5** · `lg:` **2** · `xl:` 6 |
| `max-md:` / `max-lg:` | **0** — yani *"dar ekranda farklı davran"* hiç yazılmamıştı |
| sol bölme | `min-w-[320px]` **sabit** · sağ bölme `flex-1` · şerit `w-12` **sağda** |

🔴 375px'lik bir ekranda: `320px` (sol) + `48px` (şerit) = **368px**, sağ bölmeye
**7px** kalıyordu. Yani mobil düzen *"dar"* değil, **kullanılamazdı**.

## Üç karar

| # | Karar | Neden |
|---|---|---|
| 1 | `<1024` **sekmeli tek sütun** | tablet ve mobilin ikisi de yan yana iki bölmeyi taşıyamaz; `lg` (1024) yol haritasının kendi sınırı |
| 2 | `<768` **şerit → alt çubuk** | 3rem'lik dikey şerit 375px'in **%13'ü** ve başparmakla en zor ulaşılan köşede |
| 3 | Dar ekranda `min-w`/`max-w` **sıfırlanır** | sabit bir alt sınır, tek sütunda bile yatay taşma üretir |

## ⊘ ÖLÇÜLEMEDİ — V-2'nin **duman testi**

Gerçek 375/768/1024 render'ı bir **tarayıcı** ister. Bu kapı **statik kaynağı** okur:
*"kural yazılmış mı"*, *"taşma üretecek bir sabit kalmış mı"*. **Yatay taşmanın
gerçekten olmadığı burada kanıtlanmıyor** — ve bu bir sınırdır, bir geçiş değil.

## Kapsam dışı — dürüstçe

**SWOT 2×2 → tek sütun** kuralı v1'de **ölçülemez**: `grep -ril swot src/` → **0**.
SWOT bir **Bölüm II** yüzeyidir. *Var olmayan bir bileşen için kapı yazmak, kapının
kendisini bir temenniye çevirir.*
"""

from __future__ import annotations

import re

import pytest

from tests.kapi_ortak import fe_dosyalari, fe_kaynak

#: Yol haritasının üç kademesi ↔ Tailwind sınırları. `lg`=1024, `md`=768 — **tesadüf
#: değil**, seçim bu yüzden yapıldı: kademeler zaten çerçevenin sınırlarına oturuyor.
_KADEMELER = {"masaüstü >1024": "lg", "tablet 768-1024": "lg", "mobil <768": "md"}


def test_DAR_EKRAN_kurallari_YAZILMIS():
    """🔴 Ölçülen taban: `max-md:`/`max-lg:` **sıfır** kullanım. *Bir gereksinimi
    "gün-1" ilan edip kaynağa hiç yazmamak, onu gün-hiç yapar.*"""
    kaynak = fe_kaynak()
    for on in ("max-lg:", "max-md:"):
        assert on in kaynak, f"🔴 `{on}` hiç kullanılmamış — dar ekran kuralı yok"


def test_TEK_SUTUN_iki_bolmeyi_AYIRIYOR():
    """Kademe 1: `<1024` sekmeli tek sütun. İki bölme **aynı anda** görünürse tek sütun
    değildir — o yüzden kapı `max-lg:hidden`'ı **iki bölmede de** arar."""
    src = fe_dosyalari()["app/page.tsx"]
    assert src.count("max-lg:hidden") >= 2, (
        "🔴 Dar ekranda bölmelerden biri gizlenmiyor — iki sütun 375px'e sığmaz.")
    assert 'role="tablist"' in src, "🔴 Sekme çubuğu yok — kullanıcı diğer bölmeye GEÇEMEZ"


def test_SEKME_CUBUGU_masaustunde_YOK():
    """⚠ `lg:hidden` yeterli **değildir**: çubuk DOM'da kalırsa masaüstünde de yükseklik
    payı ayırır ve iki bölmenin üstünde boş bir şerit belirir."""
    src = fe_dosyalari()["app/page.tsx"]
    assert "hidden shrink-0 border-b border-hairline max-lg:flex" in src, (
        "🔴 Sekme çubuğu varsayılan olarak GİZLİ değil — masaüstünde de görünür.")


def test_SEKME_erisilebilir():
    """A11Y ile kesişim: sekme çubuğu `role`/`aria-selected` taşımazsa ekran okuyucu
    hangi görünümün etkin olduğunu **söyleyemez**."""
    src = fe_dosyalari()["app/page.tsx"]
    for beklenen in ('role="tablist"', 'role="tab"', "aria-selected", 'aria-label="Görünüm"'):
        assert beklenen in src, f"🔴 sekme çubuğu eksik: {beklenen}"


def test_SABIT_ALT_SINIR_dar_ekranda_SIFIRLANIYOR():
    """🔴 **Ölçülen asıl kusur.** `min-w-[320px]` + şerit `w-12` = 368px; 375px'lik bir
    ekranda sağ bölmeye **7px** kalır. Tek sütuna geçmek yetmez — **alt sınır da
    kalkmalı**, yoksa tek sütun bile taşar."""
    src = fe_dosyalari()["app/page.tsx"]
    assert "max-lg:min-w-0" in src and "max-lg:max-w-none" in src, (
        "🔴 Dar ekranda `min-w`/`max-w` sıfırlanmıyor — yatay taşma sürer.")


def test_SERIT_mobilde_ALT_CUBUGA_donuyor():
    """Kademe 2 (`<768`). Yol haritasının kendi cümlesi: *"rail alt çubuğa dönüşür."*"""
    src = fe_dosyalari()["components/FloatingControls.tsx"]
    for beklenen in ("max-md:bottom-0", "max-md:w-full", "max-md:flex-row"):
        assert beklenen in src, f"🔴 şerit alt çubuğa dönmüyor: {beklenen}"
    assert "max-md:pt-0" in src, (
        "🔴 `pt-[4.5rem]` mobilde sıfırlanmıyor — alt çubukta üstten boşluk ikonları "
        "ekranın DIŞINA iter.")


def test_SAYFA_PAYI_seritle_BIRLIKTE_donuyor():
    """🔴 *Bir kuralın iki yarısı vardır ve biri unutulur.* Şerit alta indiğinde sayfanın
    `pr-12`'si **olmayan bir kolona** yer ayırmaya devam ederdi; ve alt çubuk içeriğin
    **üstüne binerdi**."""
    src = fe_dosyalari()["app/page.tsx"]
    assert "max-md:pb-12" in src and "max-md:pr-0" in src, (
        "🔴 Sayfa payı şeritle birlikte dönmüyor — sağda boş 3rem, altta örtülen içerik.")


def test_CEKMECE_de_serit_kararini_IZLIYOR():
    """⚠ Üçüncü yarı: `SettingsDrawer` `right-12`'de duruyordu — o pay **şeridin**
    payıydı. Şerit alta inince çekmece sağda 3rem boşluk bırakmaya devam ederdi."""
    src = fe_dosyalari()["components/SettingsDrawer.tsx"]
    assert "max-md:right-0" in src and "max-md:bottom-12" in src, (
        "🔴 Çekmece dar ekranda şeridin eski yerini koruyor.")


@pytest.mark.parametrize("kademe", sorted(_KADEMELER))
def test_UC_KADEME_de_bir_kurala_BAGLI(kademe):
    """Üç kademenin **her biri** en az bir yazılı kurala dayanmalı — biri yalnız
    *"varsayılan"* olarak kalırsa, o kademe tasarlanmamış demektir."""
    on = _KADEMELER[kademe]
    kaynak = fe_kaynak()
    assert f"max-{on}:" in kaynak or f"{on}:" in kaynak


def test_YATAY_TASMA_riski_TARANDI():
    """Statik olarak ölçülebilen tek taşma sinyali: mobil sınırını (375px) **aşan**
    sabit genişlikler. ⚠ Bu bir **duman testi değildir** — yalnız en kaba sınıfı yakalar.
    """
    # 🔴 `(?<!max-)(?<!min-)` ZORUNLU: ilk sürüm `\bw-\[…\]` yazdı ve `max-w-[440px]`'in
    # İÇİNDEKİ `w-[440px]`'i yakaladı — yani bir **üst sınırı** bir taşma sanıyordu.
    # *Bir taramanın kendi deseni de bir bağımlılıktır.*
    kotu = []
    for yol, kaynak in fe_dosyalari().items():
        for m in re.finditer(r"(?<!max-)(?<!min-)\bw-\[(\d+)px\]", kaynak):
            if int(m.group(1)) > 375:
                kotu.append(f"{yol}: {m.group(0)}")
    assert not kotu, (
        "🔴 375px'i aşan ve bir üst sınırla eşleşmeyen sabit genişlik(ler): " + str(kotu))


def test_SINIRLAR_ve_KAPSAM_DISI_yazili():
    """⊘ *Ölçülemeyeni ölçülmüş göstermek, ölçmemekten kötüdür* — ve **var olmayan bir
    bileşen için kapı yazmak**, kapıyı bir temenniye çevirir (SWOT: `grep -ril swot` → 0).
    """
    from pathlib import Path
    doc = Path(__file__).read_text(encoding="utf-8")
    assert "⊘ ÖLÇÜLEMEDİ" in doc and "SWOT" in doc
    assert "swot" not in fe_kaynak().lower(), (
        "🔴 SWOT artık VAR — kapsam-dışı notu geçersiz; 2×2 → tek sütun kuralı yazılmalı.")
