"""🔴🔴 `§A14` — HAVA BOŞLUĞU **YAYINLANDI**; ve yayınlanmış bir sayı çürüyebilir.

## Raporun isteği

> *«Modelin rakamı üretememesi»* bizim **benzersiz** iddiamız… ⚠ **Ölçülüp
> yayınlanmadığı sürece sadece bir iddia.** Somut: *«N cevapta üretilen her sayının
> kaynağı fişte doğrulandı»*.

## Yayınlanan (2026-08-12, `belgeler/HAVA-BOSLUGU.md`)

    12 canlı cevap · 9'unda LLM anlatı basamağı HİÇ koşmadı (şablon)
    3'ünde koştu → 20 yer tutucu · 0 bozulan · 0 düşen iddia

## Bu kapı neden var — `§F8`'in birebir dersi

> *Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan kötüdür — çünkü ona
> güvenilir.*

Belge bir **iddia** taşıyor (*«model hiçbir sayıyı üretemez»*) ve o iddianın kod
karşılığı üç mekanizmadır. Biri sessizce kalkarsa belge **yalan söylemeye başlar**;
bu kapı onu duyurur.

⚠ Kapı belgenin **sayılarını** değil, sayıların **dayandığı mekanizmayı** ölçer:
canlı bir turu CI'da tekrar koşmak (ağ + kota) bu deponun reddettiği şeydir. *Bir
yayının kapısı, yayını üreten yolu korur; yayını yeniden üretmez.*
"""

from __future__ import annotations

import pathlib
import re

import pytest

_BELGE = pathlib.Path(__file__).parent.parent.parent / "belgeler" / "HAVA-BOSLUGU.md"

pytestmark = pytest.mark.skipif(
    not _BELGE.parent.is_dir(),
    reason="`belgeler/` bağlanmamış — `-v \"$PWD/belgeler:/belgeler:ro\"` ekleyin")


def test_BELGE_VAR():
    assert _BELGE.is_file(), (
        "🔴 `belgeler/HAVA-BOSLUGU.md` yok — `§A14` *«ölçülüp yayınlanmadığı sürece "
        "sadece bir iddia»* diyor.")


def test_OLCUM_SAYILARI_ve_PAYDASI_YAZILI():
    """🔴 Bir sayı, paydası söylenmeden bir iddia bile değildir."""
    m = _BELGE.read_text(encoding="utf-8")
    for parca in ("12 canlı cevap", "20 yer tutucu", "0 bozulan", "0 düşen iddia"):
        assert parca.split()[0] in m and parca.split()[-1] in m, (
            f"🔴 ölçüm kaydı eksik: «{parca}» belgede yok.")
    assert re.search(r"9/12|9'unda", m), "katman ① sayısı (9/12) yazılmamış"


def test_KORLUKLER_YAZILI():
    """⚠ `§F8` hijyeni: körlükler yazılmadan yayımlanan bir ölçüm bir reklamdır."""
    m = _BELGE.read_text(encoding="utf-8")
    for k in ("Payda küçük", "Discovery yolu ayrı", "bir tavan değil",
              "guard_muaf"):
        assert k in m, f"🔴 bilinen körlük yazılmamış: «{k}»"


def test_YENIDEN_URETME_KOMUTU_VAR():
    m = _BELGE.read_text(encoding="utf-8")
    assert "/auth/login" in m and "hava_boslugu" in m, (
        "🔴 yeniden üretme komutu yok — ölçülemeyen bir yayın bir anıdır.")
    assert "Çok **ölçülü** bir soru seçin" in m, (
        "⚠ tek ölçülü soruda `hava_boslugu` BOŞ döner; bunu yazmayan bir reçete, "
        "okuyucuya kusur gösterir.")


def test_UC_MEKANIZMA_da_KODDA_DURUYOR():
    """🔴🔴 **ASIL KAPI.** Belgenin iddiası üç mekanizmaya dayanıyor; biri kalkarsa
    belge yalan söylemeye başlar."""
    import app.answer as _a
    from app import iddia, narration_guard, yayilim

    assert hasattr(yayilim, "geri_koy"), (
        "🔴 yer tutucu mekanizması (`yayilim.geri_koy`) yok — sayılar modele AÇIK gider.")
    assert hasattr(iddia, "dogrula"), "🔴 iddia kapısı yok"
    assert hasattr(narration_guard, "dogrula"), "🔴 anlatı guard'ı yok"
    kaynak = pathlib.Path(_a.__file__).read_text(encoding="utf-8")
    assert "hava_boslugu" in kaynak and "geri_koy" in kaynak, (
        "🔴 `answer.py` makbuzu kurmuyor — belge ölçtüğü alanı bulamaz.")


def test_MAKBUZ_ALANLARI_BELGEDEKIYLE_AYNI():
    """⚠ Belge dört alanı **adıyla** açıklıyor; kod başka adlar kullanırsa okuyucu
    belgeyi doğrulayamaz. *Bir yayın, ölçtüğü alanın adını da yayımlar.*"""
    m = _BELGE.read_text(encoding="utf-8")
    kaynak = (pathlib.Path(__file__).parent.parent / "app"
              / "answer.py").read_text(encoding="utf-8")
    for alan in ("yer_tutucu", "bozulan", "iddia_dusen", "anlati_dogrulandi"):
        assert alan in m, f"belgede `{alan}` açıklanmamış"
        assert alan in kaynak, (
            f"🔴 `{alan}` artık kodda üretilmiyor — belge var olmayan bir alanı anlatıyor.")


def test_SABLON_YOLU_BIRINCIL_KALIYOR():
    """🔴 Belgenin en güçlü iddiası katman ①: *«şablonla anlatılabilen cevapta LLM hiç
    çağrılmaz»*. O yol kapanırsa hava boşluğu **zayıflar**, belge güçlü kalır."""
    from app import anlatici

    assert hasattr(anlatici, "basit_mi") and hasattr(anlatici, "anlat")
    kaynak = (pathlib.Path(__file__).parent.parent / "app"
              / "answer.py").read_text(encoding="utf-8")
    assert "basit_mi" in kaynak, (
        "🔴 `answer.py` şablon yolunu sormuyor → her cevap LLM'e gider ve katman ① çöker.")
