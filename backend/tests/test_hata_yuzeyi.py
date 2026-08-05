"""**HER MUTASYON BİR HATA YÜZEYİ TAŞIR.** [bayraksız: kapı] *(denetim F3)*

## 🔴 Ölçülen kusur

`DashboardsPanel` (3 mutasyon) · `TercihlerPanel` (3) · `HistoryPanel` (1) —
**`onError: 0`, `isError: 0`**. 403 dönen bir *"Panoyu sil"* ekranda **hiçbir iz
bırakmıyordu**: düğmeye basılır, hiçbir şey olmaz, kullanıcı tekrar basar.

> 🔴 *Sessizce başarısız olan bir eylem, kullanıcıya ürünün bozuk olduğunu değil,
> **kendisinin yanlış yaptığını** düşündürür.*

Ve bu, denetimin adlandırdığı zincirin ortasıydı:
**onay yok (F1) → başarısızlık bildirimi yok (F3) → geri alma yok (F2).**
F1 kapandı (`932b7a2`), F3 burada kapanıyor, **F2 açık**.

## Neden tek yerde

On mutasyona on ayrı `onError` yazmak **on sahip** demekti; dokuzu bir gün 403 ile 500'ü
aynı cümleyle anlatırdı. Eşleme `lib/mutasyonHatasi.ts`'te **bir kez** yapılır.
"""

from __future__ import annotations

import re

import pytest

from tests.kapi_ortak import fe_dosyalari

#: Yazma yapan paneller — her `useMutation` bir `onError` taşımalı.
_PANELLER = ("components/DashboardsPanel.tsx", "components/HistoryPanel.tsx",
             "components/TercihlerPanel.tsx")


@pytest.mark.parametrize("dosya", _PANELLER)
def test_HER_MUTASYON_onError_TASIYOR(dosya):
    """🔴 Sayı **eşit** olmalı: bir mutasyonun hata yolu eksikse, o yol **sessizdir**."""
    src = fe_dosyalari()[dosya]
    mutasyon = len(re.findall(r"=\s*useMutation\(\{", src))
    hata = src.count("onError:")
    assert mutasyon > 0, f"⊘ {dosya} mutasyon içermiyor — kapı bir şey korumuyor"
    assert hata == mutasyon, (
        f"🔴 {dosya}: {mutasyon} mutasyon, {hata} `onError` — aradaki fark "
        f"**sessizce başarısız olan** eylem sayısıdır.")


@pytest.mark.parametrize("dosya", _PANELLER)
def test_HATA_EKRANA_ciziliyor(dosya):
    """⚠ Durumu tutmak yetmez: `onError` yazıp şeridi render etmemek, hatayı bir
    **değişkene** hapsetmektir."""
    assert "<HataSeridi" in fe_dosyalari()[dosya], f"🔴 {dosya} hatayı ÇİZMİYOR"


def test_ESLEME_TEK_YERDE():
    """🔴 On mutasyona on ayrı metin, dokuz farklı yanlış demektir."""
    for dosya in _PANELLER:
        assert "hataMetni(" in fe_dosyalari()[dosya]
    src = fe_dosyalari()["lib/mutasyonHatasi.ts"]
    assert "export function hataMetni" in src


def test_403_ile_500_AYRI_anlatiliyor():
    """🔴 **En önemli ayrım**: birinde tekrar denemek işe yaramaz, diğerinde yarar.
    *"Bir şeyler ters gitti"* bir bilgi değil bir **süstür**."""
    src = fe_dosyalari()["lib/mutasyonHatasi.ts"]
    assert "case 403:" in src and "yetkiniz yok" in src
    assert "sunucu hatası" in src
    i = src.index("case 403:")
    blok = src[i:i + 300]
    assert "Tekrar deneyin" not in blok, (
        "🔴 403'te *tekrar deneyin* deniyor — yetki eksikse tekrar denemek işe yaramaz "
        "ve kullanıcıyı aynı duvara ikinci kez çarptırır.")


def test_SUNUCUNUN_KENDI_CUMLESI_onceLIKLI():
    """⚠ `detail` zaten kullanıcıya yazılmış bir gerekçedir (ör. *"Onay süresi doldu
    (30 dk)"*); onu genel bir metinle ezmek, **sunucunun bildiğini kullanıcıdan
    saklamaktır**."""
    src = fe_dosyalari()["lib/mutasyonHatasi.ts"]
    assert "if (detay && durum && durum < 500) return detay;" in src


def test_AG_HATASI_ile_SUNUCU_HATASI_ayri():
    """⚠ Birinde bağlantı, diğerinde ürün suçlu — ve kullanıcının yapacağı şey farklı."""
    src = fe_dosyalari()["lib/mutasyonHatasi.ts"]
    assert "bağlantı kurulamadı" in src


def test_BILINMEYEN_DURUM_gizlenmiyor():
    """*Anlaşılmayan bir hatayı "bilinmeyen hata" diye yutmak, destek isteyen
    kullanıcıdan tek ipucunu alır.*"""
    src = fe_dosyalari()["lib/mutasyonHatasi.ts"]
    assert "${durum}" in src


def test_SERIT_ROLE_ALERT():
    """🔴 `role="status"` bir **ilerleme** bildirimi içindir ve başarısızlığı sıraya alır —
    *bir hatayı sıraya almak, onu ıskalatmaktır.*"""
    src = fe_dosyalari()["components/HataSeridi.tsx"]
    assert 'role="alert"' in src


def test_SERIT_KENDILIGINDEN_KAYBOLMUYOR():
    """⚠ *Bir hatayı zaman aşımına uğratmak, onu kullanıcının dikkatine değil takvimine
    bağlamaktır.*"""
    src = fe_dosyalari()["components/HataSeridi.tsx"]
    assert "setTimeout" not in src, "🔴 hata şeridi kendiliğinden soluyor"


def test_SERIT_KAPATILABILIR_ve_ETIKETLI():
    src = fe_dosyalari()["components/HataSeridi.tsx"]
    assert 'aria-label="Hatayı kapat"' in src


def test_SERIT_yeni_PANEL_acmadi():
    """K5 13/13."""
    from tests.test_panel_sayisi import DESEN

    assert not DESEN.findall(fe_dosyalari()["components/HataSeridi.tsx"])


def test_ZINCIRIN_ACIK_HALKASI_yazili():
    """⊘ F2 (geri alma yüzeyi) **hâlâ açık** ve bu gizlenmiyor: *bir zinciri yarısına
    kadar onarıp tamam demek, onarılmamış olmaktan kötüdür.*"""
    assert "**F2 açık**" in (__doc__ or "")
