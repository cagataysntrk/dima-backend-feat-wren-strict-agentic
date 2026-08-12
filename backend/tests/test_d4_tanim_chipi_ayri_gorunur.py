r"""🔴 `§38 D4` — **TANIM CHİP'İ İKİ RENDERER'DAN BİRİNDE JENERİKTİ.**

## Denetim ajanının iddiası ve ÖLÇÜM

> Ajan: *«Ön uç `kind`'ı **hiç okumuyor** (`ReportPanel.tsx:357-362`, `grep tanim` → 0)
> → tanım chip'i «tedarikçi kırılımı» ile **aynı görünümde**.»*

⚠ **İDDİA KISMEN YANLIŞTI — ve doğrusu daha dar.** Ölçüldü (2026-08-12):

| renderer | üç edim ayrı mı |
|---|---|
| `ReportCard.tsx` *(ana cevap yolu)* | ✅ **evet** — `!s.kind` (`:1130`) · `"turetme"` (`:1165`) · `"tanim"` (`:1188`) |
| `ReportPanel.tsx` *(saf-not dalı)* | 🔴 **hayır** — `it.suggestions.map(...)` hepsini **tek tip** butona basıyordu |

Yani sözleşme **ana yolda tam onurlandırılmış**; boşluk yalnız `result`/`kpi` taşımayan
(netleştirme · yükleme bildirimi · kapsam dışı) dalındaydı. Ajanın grep'i tek dosyaya
baktığı için tabloyu tersine okumuştu — *bir kapının yokluğunu iddia etmek, aradığın
YERİN kapsamıyla sınırlıdır.*

⊙ Kusur yine de gerçekti ve kapatıldı: backend sözleşmesi
(`app/belirsizlik_chipi.py:51`) *«Frontend bunu AYRI bir grupta ve KENDİ açıklamasıyla
basar»* diyor ve **bileşen ayrımı yapmıyor** — o cümle bu dalı da kapsıyordu.

> *Bir chip'in yanındaki açıklama, chip'in kendisi kadar bir vaattir.*
"""

from __future__ import annotations

import pathlib

import pytest

_FE = (pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master"
       / "src" / "components")


def _oku(ad: str) -> str:
    f = _FE / ad
    if not f.is_file():
        pytest.skip('⊘ ön uç bağlanmadı — `-v "$PWD/dima-frontend-demo-master:'
                    '/dima-frontend-demo-master:ro"`')
    return f.read_text(encoding="utf-8")


def test_SOZLESME_CUMLESI_HALA_YAZILI():
    """🔴 **ZİNCİR YÜKLEMİ.** Bu kapının bütün gerekçesi backend'in yazılı sözleşmesidir.
    O cümle silinirse kapı bir *«çünkü»*siz kalır ve bir sonraki tur onu keyfî sanar.

    ⊘ İki meşru yol vardı: sözleşmeyi **uygula** ya da cümleyi **sil**. Uygulandı — ama
    o zaman cümle de **durmalı**, yoksa yerine getirilen bir vaat kayıtsız kalır.
    """
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app" / "belirsizlik_chipi.py").read_text(encoding="utf-8")
    assert "AYRI bir grupta" in kaynak, (
        "🔴 `belirsizlik_chipi`'nin FE sözleşmesi cümlesi kaldırılmış — bu kapının "
        "dayanağı yok. Ya cümleyi geri koy ya bu kapıyı gerekçesiyle kaldır.")


def test_RAPOR_KARTI_UC_EDIMI_AYIRIYOR():
    """⚠ Gerileme koruması: ana cevap yolu bu ayrımı **zaten** taşıyordu (`KÖK-9`).
    Buradaki iş onu korumak — *bir eksiği kapatırken çalışanı bozmamak.*"""
    m = _oku("ReportCard.tsx")
    for desen, ne in ((') => !s.kind)', "devam sorusu (kind'sız)"),
                      ('s.kind === "turetme"', "türetme"),
                      ('s.kind === "tanim"', "tanım")):
        assert desen in m, f"🔴 `ReportCard` artık **{ne}** edimini ayırmıyor: {desen!r}"


def test_SAF_NOT_DALI_DA_AYIRIYOR():
    """🔴🔴 **ASIL KAPI.** `result`/`kpi` taşımayan cevaplarda da üç edim ayrı olmalı."""
    m = _oku("ReportPanel.tsx")
    assert '.filter((s) => !s.kind)' in m, (
        "🔴 saf-not dalı `kind`'lı chip'leri devam-sorusu kutusuna KOYUYOR — o kutunun "
        "vaadi *«bu cevabın üstünde konuşur»*, oysa tanım chip'i **yeni bir sorgu "
        "yazar** ve **yeni bir sayı** getirir.")
    assert 's.kind === "tanim"' in m, (
        "🔴 saf-not dalında **tanım** chip'i için ayrı bir şerit yok — "
        "`belirsizlik_chipi.py`'nin *«AYRI bir grupta ve KENDİ açıklamasıyla»* "
        "sözleşmesi bu dalda yerine getirilmiyor.")
    assert "başka tanım" in m, (
        "🔴 şerit var ama **kendi açıklaması** yok — sözleşmenin ikinci yarısı eksik.")


def test_ACIKLAMA_YENI_SAYI_UYARISINI_TASIYOR():
    """🔴 Ayrımın **anlamı** metindedir. Renk tek başına *«bu başka bir hesap»* demez;
    kullanıcı tıklamadan önce **yeni bir sayı geleceğini** bilmeli.

    ⚠ Ve metin **tek sahipten**: iki renderer aynı cümleyi taşımalı, yoksa bir gün
    ikisi iki farklı vaat verir (`KAT-1` disiplininin arayüzdeki hâli).
    """
    cumle = "Aynı soruyu bu tanımla yeniden sorar"
    for ad in ("ReportCard.tsx", "ReportPanel.tsx"):
        assert cumle in _oku(ad), (
            f"🔴 `{ad}` tanım chip'inin açıklamasını taşımıyor — chip görünüyor ama "
            "**ne yapacağını söylemiyor**.")


def test_YANLIS_UYARI_YOK_kindsiz_chipler_seride_kalmiyor():
    """⚠ `§101.1` — ayrım bir **daraltma** değil bir **gruplama**dır: `kind`'sız chip'ler
    eskisi gibi basılmaya devam etmeli. *Bir eksiği kapatırken başka bir yeteneği
    sessizce kaldırmak, kusuru yer değiştirmektir.*"""
    m = _oku("ReportPanel.tsx")
    assert m.count(".filter((s) => !s.kind)") >= 1
    assert "onReply?.(thread.id, i, s.query)" in m, (
        "🔴 saf-not dalında chip tıklama bağlantısı kaybolmuş — chip'ler artık "
        "**tıklanamaz** olabilir.")
