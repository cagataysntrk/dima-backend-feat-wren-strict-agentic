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

#: ⚠ İki AYRI eksiklik, iki AYRI sonuç — ve bunu ayırmak bir kapı hijyenidir:
#:   · `belgeler/` **hiç bağlanmamış** (konteynerde `-v …/belgeler:/belgeler:ro` yok)
#:     → bu bir **koşum ortamı** eksiğidir, bir ürün kusuru değil → **SKIP**
#:   · dizin **var** ama `DOGRULUK.md` yok → yayın gerçekten kayıp → **FAIL**
#: Ölçüldü: mount unutulunca kapı dört sahte kırmızı verdi (bu turda aracın yirmi
#: birinci yanılması). *Bir kapı, kendi ortamının eksiğini ürünün kusuru gibi
#: göstermemelidir.*
pytestmark = [
    pytest.mark.skipif(
        not _JSON.is_file(),
        reason="korpus artefaktı yok — `python lab/kapi.py --tam` koşulmamış"),
    pytest.mark.skipif(
        not _BELGE.parent.is_dir(),
        reason="`belgeler/` bağlanmamış — konteynere `-v \"$PWD/belgeler:/belgeler:ro\"` ekleyin"),
]


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

# --- 🔴 SESSİZ-YANLIŞ: yayının EN AĞIR satırı, ve korumasızdı --------------------

_GD = _KOK / "lab" / "reports" / "gercek_dunya.json"


def _gercek_dunya() -> dict:
    import json as _j

    return _j.loads(_GD.read_text(encoding="utf-8"))


@pytest.mark.skipif(not _GD.is_file(),
                    reason="`gercek_dunya.json` yok — `python lab/kapi.py --tam` koşulmamış")
def test_SESSIZ_YANLIS_ve_PAYDASI_belgede_DOGRU():
    """🔴🔴 **YAYININ EN AĞIR SATIRI KORUMASIZDI.**

    ## Ölçülen boşluk (2026-08-12, denetim ajanı buldu)

    `belgeler/DOGRULUK.md` *«Sessiz yanlış **7** / **2.286**»* yayımlıyor ve bu dosya
    belgedeki her sayıyı korpustan yeniden hesaplıyor — **bunu hariç**
    (`grep sessiz` → **0**). Yani en pahalı kusur sınıfının yayınlanmış sayısı
    çürüyebilirdi.

    ⚠ **Sebep yapısaldı, ihmal değil:** bu dosyanın kendi ilkesi *«JSON'dan, `.md`'den
    değil»* ve o ölçümün JSON'u **diske hiç yazılmıyordu** (yalnız `--json` ile
    stdout'a). `lab/gercek_dunya.py` artık `lab/reports/gercek_dunya.json` yazıyor.

    ## ⊙ Ve bir «çelişki» ihbarı ölçümle ÇÖZÜLDÜ

    Ajan *«DOGRULUK.md 7 ↔ taban 8 ↔ rapor §39.4 8»* diye üç yerde iki sayı bildirdi.
    Ölçüm ayrımı gösterdi:

        gercek_dunya.md (2026-08-12, GÜNCEL) → K1 0 · K2 2 · K3 3 · K4 0 · K5 2 = **7**
        gercek_dunya_baseline.json (08-10)   → **8**  ← bir RATCHET TAVANI, ölçüm değil

    ⊙ Yani yayın **doğruydu**; taban bir üst sınır ve `7 < 8` bir **iyileşme**. Bayat
    olan yalnız raporun §39.4 satırıydı. *Bir tavanı bir ölçüm sanmak, iyileşmeyi
    çelişki gibi okur.*

    ## Payda da denetlenir

    `toplam_vaka − katalog sızıntısı` = 2351 − 65 = **2286**. Payda oyununun en sık
    biçimi paydayı sessizce değiştirmektir; sayı ile payda **birlikte** doğrulanır.
    """
    d = _gercek_dunya()
    sayac = d.get("sayac") or {}
    assert sayac, "⊘ ölçüm tabanı çöktü: `sayac` boş — kapı hiçbir şey ölçmüyor"

    sessiz = sum(int((v or {}).get("sessiz_yanlis", 0) or 0) for v in sayac.values())
    payda = int(d.get("toplam_vaka") or 0) - len(d.get("sizinti") or [])
    m = _metin()

    assert f"**{sessiz}**" in m or f"| {sessiz} |" in m, (
        f"🔴 sessiz-yanlış yayını BAYAT: ölçülen **{sessiz}**, belgede yok.\n"
        "Bu, yayının en ağır satırıdır — *yayınlanmış ve çürümüş bir sayı, hiç "
        "yayınlanmamış bir sayıdan kötüdür.*")
    assert f"{payda:,}".replace(",", ".") in m, (
        f"🔴 sessiz-yanlış PAYDASI bayat (ölçülen {payda:,}). Paydayı sessizce "
        "değiştirmek, payda oyununun en sık biçimidir.")


@pytest.mark.skipif(not _GD.is_file(), reason="`gercek_dunya.json` yok")
def test_TABAN_bir_TAVANDIR_olcum_ONU_ASMAZ():
    """`gercek_dunya_baseline.json` bir **ratchet**: ölçüm onu aşarsa gerileme vardır.

    ⚠ Ve taban **ölçüm değildir** — yayın tabandan değil **ölçümden** yazılır. İkisini
    karıştırmak bu turda bir «çelişki» ihbarı üretti.
    """
    import json as _j

    taban_yolu = _KOK / "lab" / "gercek_dunya_baseline.json"
    if not taban_yolu.is_file():
        pytest.skip("taban yok")
    taban = int(_j.loads(taban_yolu.read_text(encoding="utf-8")).get("sessiz_yanlis", 0))
    olcum = sum(int((v or {}).get("sessiz_yanlis", 0) or 0)
                for v in (_gercek_dunya().get("sayac") or {}).values())
    assert olcum <= taban, (
        f"🔴 GERİLEME: sessiz-yanlış {olcum} > taban {taban}. Bu, rozetli ve uyarısız "
        "yanlış sayı demektir — bu deponun en pahalı kusur sınıfı.")
