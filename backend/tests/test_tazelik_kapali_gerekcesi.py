"""🔴 `D5`/`F5` — **`tazelik` NEDEN KAPALI: gerekçe artık YAZILI ve ÖLÇÜLÜ.**

Rapor `F5`: *"8 test · 7 kod dosyası — ve hâlâ `off`. Neden kapalı olduğu **hiçbir
yerde yazılı değil**. İlk iş gerekçeyi bulmak; gerekçe yoksa bugün açılabilir."*

## Bulunan gerekçe (ölçüm, 2026-08-10)

`DbConnection` **0 satır** · `SyncState` **0 satır**. Tazelik `SyncState.
last_synced_at`'ten okunur; kayıt yoksa kademe **`bilinmiyor`** olur ve o kademede
tasarım gereği **sayı gösterilmez**.

🔴 Yani bayrak bugün açılsaydı ürün **hiçbir sayı göstermezdi** — bir gerileme değil
bir **karartma**.

## Ve asıl kusur: iki farklı şey aynı kademede

Bayrak *«senkron bilinmiyor»* ile *«veri bayat»*ı aynı kovaya koyuyor. Dosya-tabanlı
(DuckDB) bir kiracıda **senkron diye bir kavram yoktur**; bilinmemesi bir bayatlık
işareti değil, **sorunun geçersizliğidir**.

⚠ `B4` (*"bilinmeyen tazelik taze DEĞİLDİR"*) doğru bir kuraldır — ama **bağlanabilir**
kiracılar için yazılmıştır. Dosya kiracısına uygulanınca *ölçülemeyeni kötü varsaymaya*
dönüşüyor, ki o da bir uydurmadır — yalnız ters yönde.

*Bir yeteneğin kapalı olması bazen bir unutulmuşluk, bazen tek yazılmamış bir
gerekçedir; ikisini ayırmanın tek yolu **aramaktır**.*
"""

from __future__ import annotations

import pathlib

import yaml

_YML = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs" / "features.yml"


def test_TAZELIK_KAPALI_VE_GEREKCESI_YAZILI():
    """🔴 Kapalı bir bayrak, **neden** kapalı olduğu yazılmadan kapalı kalamaz.

    ⚠ Bu kapı bayrağın kapalı olmasını değil, **gerekçesizliğini** yasaklar: açılırsa
    da bu test güncellenir ve o zaman `on` şartının karşılandığı yazılır.
    """
    ham = _YML.read_text(encoding="utf-8")
    d = yaml.safe_load(ham) or {}
    assert d["features"]["tazelik"] == "off", (
        "bayrak açılmış — `on` şartı karşılandı mı? (1) kiracının gerçek bağlantısı "
        "var mı, (2) `bilinmiyor` kademesi «tazelik kavramı yok»tan ayrıldı mı?")
    # Gerekçe, bayrak satırının **hemen üstündeki** yorum bloğunda olmalı.
    satirlar = ham.split("\n")
    i = next(n for n, s in enumerate(satirlar) if s.startswith("  tazelik:"))
    blok = "\n".join(satirlar[max(0, i - 30):i])
    assert "SyncState" in blok and "D5" in blok, (
        "🔴 `tazelik` kapalı ama gerekçesi yazılı DEĞİL. Rapor `F5`'in ilk işi buydu: "
        "gerekçe bulunmadan bir bayrak süresiz `off` kalamaz — o bir karar değil bir "
        "ertelemedir ve ertelemenin de sahibi olmalıdır (`E-1`).")


def test_ON_SARTI_YAZILI():
    """`E-4` — `on` şartı olmayan bir bayrak `beta`/`off`'ta **süresiz** yaşar."""
    ham = _YML.read_text(encoding="utf-8")
    i = ham.index("  tazelik:")
    assert "`on` ŞARTI" in ham[max(0, i - 2000):i], \
        "`tazelik` için yazılı bir `on` şartı yok (`E-4`)"
