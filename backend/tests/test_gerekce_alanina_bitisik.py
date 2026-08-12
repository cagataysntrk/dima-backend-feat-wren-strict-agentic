"""🔴 ① — *«`vqr_acik=False` GEREKÇESİZ»* — ÖLÇÜLDÜ, BORÇ **YARI YANLIŞTI**.

## Ölçüm (2026-08-12)

Gerekçe **vardı ve güçlüydü** — kullanıcı kararı + canlı ölçüm + mimari ilke:

> 🔴 **VQR KAPALI (kullanıcı kararı, 2026-08-07): *«o bambaşka bir ar-ge konusu.»***
> Doğrulanmış soru deposu merdivenin **İLK** basamağıdır… *«şubatta ciro ocağa göre nasıl
> değişti»* `source=vqr` ile 434 ms'de dönüyordu ve cevabı **beyanlı kısmiydı** — aynı
> soruyu `Ö10` ile düzelttiğimiz hâlde kullanıcı **eski cevabı** görecekti.
> ⚠ Mekanizma **silinmedi, kapatıldı** (`MIMARI §10`).

⊙ Yani borç *«gerekçesiz»* demekle **yanılıyordu**. Ama yarısı doğruydu:

🔴 **GEREKÇE ALANINDAN KOPMUŞTU.** Blok `config.py:131-144`'teydi, `vqr_acik` ise
**167**'de — aradaki 22 satırda üç ilgisiz alan (`intent_azami_saniye` ·
`discovery_azami_saniye` · `anlati_azami_saniye`) ve iki ilgisiz yorum bloğu vardı.
Blok görsel olarak `consistency_k`'ya yapışıktı. Aynı kopukluk **anlatı bütçesinde** de
vardı (blok 145-152, alan 165).

> *Bulunamayan bir beyan, yazılmamış bir beyandır.* Bu deponun kendi kültürü
> (`beyan kültürü`, `§38.4`) bir kararın **yazılı** olmasını ister; okunabilir olması
> onun ayrılmaz parçasıdır.

✅ **Yapılan:** iki blok **kendi alanının hemen üstüne** taşındı. Metin **bir karakter**
değişmedi — yalnız yeri. `KURAL B`: davranış birebir aynı (yorum taşındı, kod değil).

## Bu kapı neyi tutuyor

Bir gerekçe bloğu ile alanı arasına **yeni bir alan** girerse kapı konuşur. *Bir yorumu
yazmak onu bulunabilir kılmaz; onu bulunabilir kılan, aralarına başka bir şey
girmemesidir.*
"""

from __future__ import annotations

import pathlib
import re

_CONFIG = pathlib.Path(__file__).parent.parent / "app" / "config.py"

#: `(gerekçenin ilk satırındaki iz, hemen altında beklenen alan)`
#: ⚠ Liste **kapalı ve ölçülmüş**: bu turda gerçekten kopuk bulunan iki blok. Yeni bir
#: kalem ancak **kopukluğu ölçülünce** eklenir — kapı bir dilek listesi değildir.
BITISIK_OLMALI = [
    ("VQR KAPALI", "vqr_acik"),
    ("ANLATININ ZAMAN BÜTÇESİ", "anlati_azami_saniye"),
    ("INTENT'İN BÜTÇESİ", "intent_azami_saniye"),
]


def _satirlar() -> list[str]:
    return _CONFIG.read_text(encoding="utf-8").splitlines()


def test_GEREKCE_kendi_alanina_BITISIK():
    """🔴 Bulunamayan bir beyan, yazılmamış bir beyandır."""
    satir = _satirlar()
    for iz, alan in BITISIK_OLMALI:
        bas = next((i for i, s in enumerate(satir) if iz in s), None)
        assert bas is not None, f"«{iz}» gerekçesi kayboldu"
        # Bloğun bitişi: yorum olmayan ilk satır
        son = bas
        while son + 1 < len(satir) and satir[son + 1].lstrip().startswith("#"):
            son += 1
        gelen = satir[son + 1] if son + 1 < len(satir) else ""
        assert re.match(rf"\s*{re.escape(alan)}\s*[:=]", gelen), (
            f"🔴 «{iz}» gerekçesi `{alan}`'dan KOPMUŞ — hemen altında gelen satır:\n"
            f"    {gelen.strip()[:90]}\n"
            "Aralarına bir alan girerse okuyan, gerekçeyi YANLIŞ alana bağlar.")


def test_VQR_GEREKCESI_uc_dayanagi_da_TASIYOR():
    """Gerekçenin **içeriği** de çürümemeli: kullanıcı kararı · canlı ölçüm · geri alma."""
    m = _CONFIG.read_text(encoding="utf-8")
    assert "kullanıcı kararı, 2026-08-07" in m, "kararın sahibi ve tarihi kayboldu"
    assert "eksik_niyet" in m, "canlı ölçüm kanıtı kayboldu"
    assert "DIMA_VQR_ACIK=1" in m, "GERİ ALMA yolu yazılı değil"


def test_MEKANIZMA_SILINMEDI_kapatildi():
    """`MIMARI §10` — *kapananlar işaretlenir, silinmez.* VQR yüzeyi yerinde durmalı."""
    app = _CONFIG.parent
    assert (app / "vqr.py").is_file(), "VQR modülü silinmiş — kapatma bir silme değildir"
    m = _CONFIG.read_text(encoding="utf-8")
    assert "vqr_path" in m and "vqr_embedder" in m
