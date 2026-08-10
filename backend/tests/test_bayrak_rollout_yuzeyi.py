"""🔴 `D10`/`E-6` — **BİR BAYRAĞIN ROLLOUT YÜZEYİ YOKSA, O BAYRAK YOKTUR.**

Rapor `B-10` ölçtü: **5** yetenek `features.yml`'de değildi; dördü **çalışma zamanı
davranışıydı** ve *hiçbir kiracı onları açamıyordu*. Yani kodu inmiş, testi yazılmış,
belgesi tutulmuş yetenekler **ulaşılamaz** durumdaydı.

⊙ Bugün ölçüldü: **4'ünün yüzeyi artık var**, biri (`ayni_grain_gocu`) **bilerek**
dışarıda ve gerekçesi kayıtta. Yani borç kapandı — ama **kapısı yoktu**, ve kapısı
olmayan bir kapanış bir sonraki bayrakta sessizce geri gelir.

## Neden metin değil ALAN

Gerekçe `description` düzyazısında yazılıydı. Bir kapının onu **metin arayarak**
bulması gerekirdi — ve o, kapıyı bir cümlenin kelimelerine bağlardı.

*Bir gerekçeyi düzyazıda saklamak, onu bir gün silinebilir kılar; bir alana yazmak,
silinince kapının bağırmasını sağlar.*

⚠ Ve `MIMARI §9.11`'in dersi burada da geçerli: *"bir kill-switch yalnız kodda varsa
yarımdır"* — **açma anahtarı** için de aynısı.
"""

from __future__ import annotations

import pathlib

import yaml

from app.features import FLAG_REGISTRY

_YML = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs" / "features.yml"


def _yuzeydekiler() -> set[str]:
    d = yaml.safe_load(_YML.read_text(encoding="utf-8")) or {}
    return set(d.get("features") or {})


def test_HER_BAYRAK_YA_YUZEYDE_YA_BEYANLI():
    """🔴 Üçüncü seçenek yok: ya kiracı açabilir, ya **neden açamadığı** yazılıdır."""
    yuzey = _yuzeydekiler()
    sessiz = sorted(ad for ad, k in FLAG_REGISTRY.items()
                    if ad not in yuzey and not k.get("rollout_yuzeyi_yok"))
    assert not sessiz, (
        f"🔴 {len(sessiz)} bayrağın rollout yüzeyi YOK ve beyanı da yok: {sessiz}\n"
        "  İki seçenek: (1) `demo/packs/features.yml`'e ekle, "
        "(2) kayda `rollout_yuzeyi_yok: \"<gerekçe>\"` yaz.\n"
        "  ⚠ Boş bırakmak, ödenmiş ve testli bir yeteneği hiçbir kiracının "
        "açamayacağı bir yerde bırakmaktır — `E-1`'in tarifiyle **harcanmış bir emek**.")


def test_BEYAN_GEREKCE_TASIR():
    """*Gerekçesiz bir istisna, bir istisna değil bir unutulmuşluktur.*"""
    for ad, k in FLAG_REGISTRY.items():
        g = k.get("rollout_yuzeyi_yok")
        if g is not None:
            assert isinstance(g, str) and len(g.strip()) >= 40, \
                f"{ad}: `rollout_yuzeyi_yok` gerekçesi çok kısa/yok"


def test_BEYAN_BAYATLAMAZ():
    """⚠ Yüzeye giren bir bayrak beyanda kalmamalı — beyan **yalan** olur."""
    yuzey = _yuzeydekiler()
    hayalet = sorted(ad for ad, k in FLAG_REGISTRY.items()
                     if k.get("rollout_yuzeyi_yok") and ad in yuzey)
    assert not hayalet, (
        f"bu bayrak(lar) artık `features.yml`'de VAR, beyandan çıkarılmalı: {hayalet}")


def test_YUZEYDE_OLUP_KAYITTA_OLMAYAN_YOK():
    """🔴 Ters yön: `features.yml`'de olup kayıtta olmayan bir ad, **yazım hatasıdır**
    ve sessizce hiçbir şey yapmaz — açıldığı sanılan bir yetenek."""
    fazla = sorted(_yuzeydekiler() - set(FLAG_REGISTRY))
    assert not fazla, (
        f"`features.yml`'de kayıtsız bayrak: {fazla} — açıldığı SANILIR, hiçbir şey yapmaz")
