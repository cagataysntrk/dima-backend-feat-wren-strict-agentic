"""🔴 `§F8` — YAYINLANMIŞ DOĞRULUK SAYISI **ÇÜRÜMEZ**.

## Neden bu kapı var

`belgeler/DOGRULUK.md` bir pazarlama sayfası değil bir **ölçüm kaydıdır** ve dışarıya
verilir. Bir ölçüm kaydının tek gerçek riski **bayatlamaktır**: kod ilerler, sayı yerinde
kalır, ve belge bir güvence gibi okunmaya devam eder.

> *Yayınlanmış ve çürümüş bir sayı, hiç yayınlanmamış bir sayıdan kötüdür — çünkü ona
> güvenilir.*

Bu dosya belgedeki **her** sayıyı `lab/reports/nl_corpus.json`'dan yeniden hesaplar ve
karşılaştırır. Ölçüm değişip belge güncellenmezse kapı **kırmızı** olur.

## Neden JSON'dan, `.md`'den değil

`nl_corpus.md` insan içindir ve biçimi değişebilir; `nl_corpus.json` koşumun **verisidir**
(`company` · `dogru_cube` · `vaka_dogru` · `vaka_toplam` · `kesme_sayi` · `kesme_payda`).
*Bir kapıyı biçime bağlamak, onu bir gün biçim değiştiği için susturur.*

⚠ Ve `§F6`'nın dersi burada da geçerli: kapı **gerçek artefaktı** okur, elle yazılmış bir
fikstürü değil.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

_KOK = pathlib.Path(__file__).parent.parent
_JSON = _KOK / "lab" / "reports" / "nl_corpus.json"
_BELGE = _KOK.parent / "belgeler" / "DOGRULUK.md"

pytestmark = pytest.mark.skipif(
    not _JSON.is_file(),
    reason="korpus artefaktı yok — `python lab/kapi.py --tam` koşulmamış")


def _dc(k: dict) -> tuple[int, int]:
    """⚠ Şekil **ölçüldü, tahmin edilmedi** — ve iki kez düzeltildi: `dogru_cube` bir çift
    değil bir **sözlük** (`{"dogru": n, "yanlis": n, "discovery": n}`), ve `discovery`
    **sıfırsa anahtar hiç yazılmıyor**. Payda üçünün toplamıdır.

    *Bir artefaktın şeklini varsaymak, bu turda üçüncü kez sahte bir kırmızı üretti.*"""
    x = k["dogru_cube"]
    dogru = int(x.get("dogru", 0))
    return dogru, dogru + int(x.get("yanlis", 0)) + int(x.get("discovery", 0))


def _olcum() -> dict:
    kayit = json.loads(_JSON.read_text(encoding="utf-8"))
    ciftler = [_dc(k) for k in kayit]
    return {
        "kayit": {k["company"]: k for k in kayit},
        "dogru_cube": (sum(a for a, _ in ciftler), sum(b for _, b in ciftler)),
        "vaka": (sum(int(k["vaka_dogru"]) for k in kayit),
                 sum(int(k["vaka_toplam"]) for k in kayit)),
        "kesme": (sum(int(k["kesme_sayi"]) for k in kayit),
                  sum(int(k["kesme_payda"]) for k in kayit)),
    }


def _metin() -> str:
    return _BELGE.read_text(encoding="utf-8")


def test_BELGE_VAR():
    assert _BELGE.is_file(), "`belgeler/DOGRULUK.md` yok — F8 yayını kayıp"


def test_DOGRU_KUP_orani_ve_PAYDASI_belgede_DOGRU():
    """🔴 Sayı **ve** payda birlikte doğrulanır: payda oyunu tam da paydayı sessizce
    değiştirmektir."""
    o = _olcum()
    oran = 100.0 * o["dogru_cube"][0] / o["dogru_cube"][1]
    m = _metin()
    assert f"%{oran:.1f}".replace(".", ",") in m, f"doğru-küp oranı bayat (ölçülen %{oran:.1f})"
    assert f"{o['dogru_cube'][1]:,}".replace(",", ".") in m, "payda bayat"


def test_SEMANTIK_VAKA_ve_CEVAPSIZ_belgede_DOGRU():
    o = _olcum()
    m = _metin()
    vaka = 100.0 * o["vaka"][0] / o["vaka"][1]
    kesme = 100.0 * o["kesme"][0] / o["kesme"][1]
    assert f"%{vaka:.1f}".replace(".", ",") in m, f"semantik vaka bayat (%{vaka:.1f})"
    assert str(o["vaka"][1]) in m, "semantik vaka paydası bayat"
    assert f"%{kesme:.1f}".replace(".", ",") in m, f"cevapsız bayat (%{kesme:.1f})"


def test_HER_SIRKET_belgede_ADIYLA_ve_SAYISIYLA():
    """🔴 En düşük şirket **gizlenemez**: payda oyununun en sık biçimi, kötü performans
    gösteren dilimi tablodan düşürmektir."""
    o = _olcum()
    m = _metin()
    for ad, k in o["kayit"].items():
        assert ad in m, f"{ad} yayından DÜŞMÜŞ — payda oyunu"
        d, dp = _dc(k)
        assert f"{d:,}".replace(",", ".") in m and f"{dp:,}".replace(",", ".") in m, (
            f"{ad} sayıları bayat ({d}/{dp})")


def test_KORLUKLER_yazili():
    """Bir güvence, sınırı yazılmadan güvence değildir. Korpusun **kendi yazılı körlüğü**
    (`CLAUDE.md`) belgede geçmeli."""
    m = _metin()
    for iz in ("Yazım hatası", "route()", "körlük"):
        assert iz.lower() in m.lower(), f"«{iz}» körlüğü yayında yok"


def test_YENIDEN_URETME_komutu_ve_SURUM_yazili():
    """Sınanamayan bir sayı bir iddiadır. Komut + sha + tarih olmadan kimse doğrulayamaz."""
    m = _metin()
    assert "lab/kapi.py --tam" in m, "yeniden üretme komutu yok"
    assert re.search(r"`[0-9a-f]{7,40}`", m), "kod sürümü (sha) yok"
    assert re.search(r"20\d\d-\d\d-\d\d", m), "ölçüm tarihi yok"
