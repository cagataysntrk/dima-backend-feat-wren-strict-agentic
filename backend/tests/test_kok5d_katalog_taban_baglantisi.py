"""🔴 KÖK-5d + KÖK-8e — **katalog büyürse taban da tazelenir.** (denetim raporu KN-2)

## Ölçülen kusur — tek commit, yedi kırmızı

`bf5a7eb` — *"ERP seed'i 47→80 tablo, katalog 13→23 cube"*:

| Ne değişti | Adet |
|---|---|
| Yeni tablo | 33 |
| 🔴 **Yeni cube** | **10** |
| 🔴 **Güncellenen taban dosyası** | **0** |
| 🔴 **Güncellenen kapı dosyası** | **0** |

Ve commit mesajının kendi ifadesi kritik: *"**test ortamı**"* — niyet **ölçüm ortamını
zenginleştirmekti**, ürünün yönlendirme uzayını değiştirmek değil. **Fakat cube eklemek
ikisini birden yapar.**

> ⚠ Kılavuzun kendi güvencesi bu sınıfı kapsamıyordu: `test_GENISLETME_yalniz_EKLER`
> **tablo** düzeyinde toplamsallığı sınıyor — **cube/sinonim** düzeyinde sınamıyor.
> *Tablo eklemek toplamsaldır; çakışan sinonimli cube eklemek **değildir**.*

## Bu kapı ne yapar

Katalogdaki cube sayısını **dondurulmuş bir beyanla** karşılaştırır. Cube eklendiğinde
kapı kırmızı verir ve **iki şeyi birden** ister: beyanı güncelle **ve** tabanların
tazelendiğini (ya da tazelenmediğini) **yaz**.

*Bir sayıyı değiştirmek serbesttir; onu sessizce değiştirmek değil.*
"""

from __future__ import annotations

import json
import pathlib

import yaml

KOK = pathlib.Path(__file__).resolve().parents[1]
PAKETLER = KOK / "demo" / "packs"

#: 🔴 DONDURULMUŞ BEYAN — boyahane kataloğunun cube sayısı.
#: ⚠ Bu sayı bir hedef değil bir **fotoğraf**tır. Değiştirmek serbesttir; değiştiren
#: aynı commit'te `_TABAN_DOSYALARI`nın da tazelendiğini (ya da neden tazelenmediğini)
#: yazmak zorundadır — kapının tek istediği budur.
BEYAN_CUBE_SAYISI = 19

#: Katalog değişiminden ETKİLENEN dondurulmuş tabanlar.
_TABAN_DOSYALARI = (
    KOK / "lab" / "nl_corpus_baseline.json",
    KOK / "lab" / "gercek_dunya_baseline.json",
    KOK / "eval" / "baseline.json",
)


def _boyahane_cubelari() -> list[str]:
    pack = yaml.safe_load((PAKETLER / "sektor/boyahane/pack.yml").read_text(encoding="utf-8"))
    yollar = []
    for m in (pack.get("moduller") or []):
        yollar += sorted((PAKETLER / "modul" / m).rglob("cubes/*/metadata.yml"))
    yollar += sorted((PAKETLER / "sektor/boyahane").rglob("cubes/*/metadata.yml"))
    return sorted({(yaml.safe_load(y.read_text(encoding="utf-8")) or {}).get("name")
                   or y.parent.name for y in yollar})


def test_KUP_SAYISI_BEYANLA_UYUSUYOR():
    """🔴 **ASIL KAPI.** Cube eklemek **toplamsal değildir**: yeni bir cube var olan
    terimlerin üstüne ikinci sahipler kondurur ve `route()`un çözdüğü uzayı değiştirir.

    Kırmızı verdiğinde YAPILACAK **iki** şey var:
      1. `BEYAN_CUBE_SAYISI`yi güncelle,
      2. `_TABAN_DOSYALARI`nı tazele **ya da tazelenmediğini YAZ**.
    """
    cubelar = _boyahane_cubelari()
    assert len(cubelar) == BEYAN_CUBE_SAYISI, (
        f"🔴 boyahane kataloğu {len(cubelar)} cube taşıyor, beyan {BEYAN_CUBE_SAYISI}.\n"
        f"   {cubelar}\n"
        "YAPILACAK: (1) beyanı güncelle · (2) dondurulmuş tabanları AYNI commit'te "
        "tazele ya da tazelenmediğini gerekçesiyle yaz.\n"
        "⚠ `bf5a7eb` bunu yapmadı ve tek commit YEDİ ayrı kırmızı üretti (süitin 4 "
        "hatası · 50 sessiz seçim · R1 99→126 · eval precision −%12,7).")


def test_TABANLAR_GEREKCE_TASIYOR():
    """🔴 KÖK-8e — bir taban değiştiyse **NEDEN** değiştiği yazılı olmalı.

    ⚠ Gerekçesiz bir taban değişikliği, bir ölçümü değil bir **kabulü** kaydeder; ve
    altı ay sonra kimse o sayının neden o olduğunu bilemez."""
    eksik = []
    for yol in _TABAN_DOSYALARI:
        if not yol.exists():
            continue
        d = json.loads(yol.read_text(encoding="utf-8"))
        # Gerekçe ya kök düzeyinde `_`-önekli bir alanda ya da `_turlar` kayıtlarında.
        gerekce = any(k.startswith("_") and isinstance(v, str) and len(v) > 40
                      for k, v in d.items() if isinstance(v, str))
        turlar = d.get("_turlar") or []
        if not gerekce and not turlar:
            eksik.append(yol.name)
    assert not eksik, (
        f"🔴 gerekçesiz dondurulmuş taban: {eksik}\n"
        "Bir taban değiştiğinde NEDEN değiştiği aynı dosyada yazılı olmalı.")


def test_KAPI_KIRMIZI_VEREBILIYOR():
    """⚠ *Kırmızı veremeyen bir kapı, olmayan bir kapıdır.* Beyan, ölçülen değere
    **eşit** olmalı — arada boşluk varsa kapı bir sonraki cube'u kaçırır."""
    assert len(_boyahane_cubelari()) == BEYAN_CUBE_SAYISI
