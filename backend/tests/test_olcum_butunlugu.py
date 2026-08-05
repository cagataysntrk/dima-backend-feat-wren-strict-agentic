"""🔴 KÖK-8 — **ölçüm aracı kendi boşluğunu bildirsin.** (denetim raporu §2.8/1)

## Ölçülen kusur — raporun `[DOĞRULANMADI]` bıraktığı madde

Korpus dilimleri `compose kilidi 60 sn'de alınamadı` ile düşebiliyordu. O şirket
rapordan çıkıyor, **TOPLAM kalan şirketler üstünden** hesaplanıp dondurulmuş tabanla
kıyaslanıyordu. Aynı kod **üç farklı toplam** verdi:

| koşum | düşen şirket | TOPLAM | kapının dediği |
|---|---|---|---|
| A | `boyahane` | **%93,4** | ✅ *(tabanın ÜSTÜNDE — «iyileşme»)* |
| B | — | **%93,0** | ✅ |
| C | `boyahane` + `atiksan` | **%91,8** | ❌ *«GERİLEME»* |

🔴 **En tehlikelisi A**: eksik bir ölçüm **iyileşme** gibi okundu. Kapı, ölçemediği
şeyi hem başarı hem başarısızlık diye raporlayabiliyordu.

*Bir kapı, ölçemediği şeyi "başarılı" ya da "başarısız" diye raporlarsa, ölçüm
aracının kendisi bir kusur kaynağıdır.*

## İki düzeltme

1. **Sebep**: kilit çekişmesi değil **CPU açlığı** — her dilim kendi aynasında compose
   ediyor, yani aynı kilide girmiyorlar; 20 çekirdekte 16 eşzamanlı compose tek bir
   compose'u 60 sn'in üstüne çıkarıyor. Zaman aşımı **makinenin yüküne** bağlandı.
2. **Belirti**: ölçülemeyen şirket artık `⊘ ÖLÇÜLEMEDİ` — ne yeşil ne kırmızı; ve
   toplam kıyası **geçersiz** işaretlenir.
"""

from __future__ import annotations

import os

from app.compose import KILIT_ZAMAN_ASIMI_SN
from lab.nl_corpus import kapi_degerlendir


def test_KILIT_ZAMAN_ASIMI_MAKINE_YUKUNE_BAGLI():
    """⚠ Sabit 60 sn bir **tahmindi**; ölçüldü ki yetmiyor. *Bir zaman aşımı, işin
    süresine değil makinenin yüküne göre ölçülmelidir.*"""
    assert KILIT_ZAMAN_ASIMI_SN >= 60.0
    if (os.cpu_count() or 4) >= 8:
        assert KILIT_ZAMAN_ASIMI_SN > 60.0, \
            "🔴 çok çekirdekli makinede zaman aşımı hâlâ sabit 60 sn"


def test_OLCULEMEYEN_SIRKET_GERILEME_SAYILMIYOR():
    """🔴 **ASIL KAPI.** Bir şirket ölçülemediyse verdikt *"gerileme"* olamaz."""
    reports = [
        {"company": "boyahane", "error": "RuntimeError: compose kilidi …"},
        {"company": "atiksan", "cats": {"tekil::OK": 900, "tekil::NOTE": 100},
         "dogru_cube": {"dogru": 931, "toplam": 949}},
    ]
    gecti, satirlar = kapi_degerlendir(reports)
    metin = "\n".join(satirlar)
    assert "⊘ ÖLÇÜLEMEDİ" in metin, "🔴 ölçüm boşluğu bildirilmiyor"
    assert "GERİLEME DEĞİL" in metin, "🔴 boşluk gerileme diye okunuyor"
    assert not gecti, "⚠ ölçülemeyen bir kapı GEÇİLMİŞ de sayılmaz"


def test_EKSIK_PAYDAYLA_KIYAS_GECERSIZ_ISARETLENIYOR():
    """🔴 Raporun A koşumu: eksik ölçüm **tabanın üstünde** çıkıp ✅ görünmüştü.
    Toplam satırı artık kıyasın geçersizliğini **kendi üstünde** taşır."""
    reports = [
        {"company": "boyahane", "error": "compose kilidi"},
        {"company": "gitas", "cats": {"tekil::OK": 1793, "tekil::NOTE": 686},
         "dogru_cube": {"dogru": 1517, "toplam": 1696}},
    ]
    _, satirlar = kapi_degerlendir(reports)
    toplam = next((s for s in satirlar if "TOPLAM doğru-cube" in s), "")
    assert "KIYAS GEÇERSİZ" in toplam, f"🔴 eksik payda işaretlenmiyor: {toplam}"


def test_TAM_OLCUMDE_UYARI_YOK():
    """⚠ Ters yön: hepsi ölçüldüyse uyarı **çıkmamalı** — yoksa kapı her koşumda
    kendi gürültüsünü üretir ve okunmaz olur."""
    reports = [
        {"company": "gulteks", "cats": {"tekil::OK": 1112, "tekil::NOTE": 506},
         "dogru_cube": {"dogru": 995, "toplam": 1040}},
    ]
    _, satirlar = kapi_degerlendir(reports)
    metin = "\n".join(satirlar)
    assert "⊘ ÖLÇÜLEMEDİ" not in metin and "KIYAS GEÇERSİZ" not in metin
