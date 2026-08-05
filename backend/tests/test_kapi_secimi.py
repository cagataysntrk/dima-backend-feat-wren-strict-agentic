"""**HIZLI KAPININ KENDİSİ ÖLÇÜLÜYOR** — *bir kapının kapsamı, onu tetikleyen sinyalden
büyük olamaz.* [bayraksız: ölçüm aracı kapısı]

## 🔴 Ölçülmüş kör nokta (2026-08-05)

`lab/kapi.py --hizli --degisen` değişen **Python modüllerine** göre test seçiyordu:
`_desenler()` `.py` olmayan her dosyayı **atlıyordu**. Yani bir `.tsx` değişikliği
**hiçbir** kapı seçmiyor, yalnız çekirdek duman testi koşuyordu.

**Bedeli ölçüldü:** FAZ 7.8'de `kanit_sinifi` `ReportCard.tsx`'ten `Makbuz.tsx`'e taşındı;
`test_ai_act_uyumu` kırmızıya döndü ve **dört demet boyunca görünmedi** — hızlı kapı her
seferinde yeşil dedi. Kırmızı ancak tam süit koşulunca çıktı.

> 🔴 *Ölçüm aracının kendisi de bir bağımlılıktır* — ve bu operasyonda **sekizinci** kez
> kusur araçtaydı, kodda değil.

## Neden modül-bağımlılığıyla seçilemezler

Frontend'i okuyan kapılar bir Python modülünü **import etmez**; bir **dosya ağacını
okur**. Bu yüzden ayrı ve adı olan bir kural gerekti.

⚠ Ve desen **`kapi_ortak`'ın yardımcı adlarına** bağlandı, `"frontend"` gibi bir kelimeye
değil: `--hizli`'nin kendi belgelenmiş tuzağı tam olarak buydu — sade ad araması
`app/routers/ask.py` için **67/137 dosya** seçmişti, çünkü sinyal bağımlılık değil **ad
çakışmasıydı**.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]
if str(_KOK) not in sys.path:
    sys.path.insert(0, str(_KOK))

from lab.kapi import _FE_OKUYAN, _frontend_degisti, _secim  # noqa: E402

_TSX = "dima-frontend-demo-master/src/components/ReportCard.tsx"


def test_TSX_degisikligi_KAPI_SECIYOR():
    """🔴 Kör noktanın kendisi: önce **0**, şimdi onlarca."""
    secili, toplam = _secim([_TSX])
    assert len(secili) > 5, (
        f"🔴 `.tsx` değişikliği yalnız {len(secili)}/{toplam} kapı seçiyor — frontend "
        f"gerilemesi hızlı kapıda GÖRÜNMEZ.")


@pytest.mark.parametrize("kapi", ["test_ai_act_uyumu.py", "test_kanit_gorunurlugu.py",
                                  "test_a11y.py", "test_responsive.py",
                                  "test_panel_sayisi.py", "test_tasarim_sistemi.py",
                                  "test_cevap_alani_yetim_degil.py"])
def test_FRONTEND_KAPILARI_secilenler_arasinda(kapi):
    """Adı verilen her kapı frontend'i okur; biri kaçarsa o sınıf yine kör kalır."""
    secili, _ = _secim([_TSX])
    assert kapi in secili, f"🔴 `{kapi}` `.tsx` değişikliğinde SEÇİLMİYOR"


def test_CSS_de_sayiliyor():
    """⚠ FAZ 7.2'nin tasarım sistemi kapısı `globals.css`'i okuyor: bir token silinmesi
    **yalnız oradan** görünür. `.css` dışlansaydı o kapı da kör kalırdı."""
    assert _frontend_degisti(["dima-frontend-demo-master/src/app/globals.css"])
    secili, _ = _secim(["dima-frontend-demo-master/src/app/globals.css"])
    assert "test_tasarim_sistemi.py" in secili


def test_PY_degisikligi_FRONTEND_kapilarini_SURUKLEMIYOR():
    """⚠ Kural **tek yönlü** olmalı: sıradan bir backend değişikliği 42 frontend kapısını
    da koşturursa `--hizli` yavaşlar ve *"hızlı"* olmaktan çıkar — ve yavaşlayan bir
    sinyal, koşulmayan bir sinyale dönüşür."""
    assert not _frontend_degisti(["backend/app/yoy.py"])


def test_DESEN_SADE_AD_tuzagina_dusmuyor():
    """🔴 `--hizli`'nin kendi belgelenmiş tuzağı: sade ad araması `ask` için **67/137**
    dosya seçmişti çünkü sinyal **ad çakışmasıydı**. Bu desen `kapi_ortak`'ın yardımcı
    **adlarına** bağlı."""
    assert not _FE_OKUYAN.search("bu bir frontend yorumudur")
    assert _FE_OKUYAN.search("from tests.kapi_ortak import fe_dosyalari")


def test_SECIM_hicbir_zaman_BOS_donmuyor():
    """⚠ Tanınmayan bir dosya değiştiğinde bile çekirdek duman testi koşmalı: *boş bir
    seçim, koşmayan bir kapıdır ve yeşil görünür.*"""
    secili, _ = _secim(["README.md"])
    assert secili, "🔴 seçim boş — hızlı kapı hiçbir şey koşmadan yeşil der"
