"""🔴 `§45` — **ÖNGÖRÜ TIKLAMASI HAZIR SORGUYU KOŞAR** (`0 LLM`).

## Ölçülen kusur (2026-08-13)

Şerit katalogdan **deterministik** cümleler üretiyordu ve her cümle kendi `cube_query`'sini
taşıyordu. Ama tıklama onu **atıyordu**:

    onSec: (etiket: string) => void   // ← yalnız METİN
    onSec(a.metin)                    // cube_query · tur · cube ATILIYOR
    onSec={onDeger}                   // → composer → /ask → route «şüpheli» → GARSON

Yani **kendi ürettiğimiz** cevabı sistem bir LLM'e **yeniden tahmin ettiriyordu** 🆤.
Planın `§6 Thread 1`'i tersini yazıyor: *«Enter → `cube_query` koşar · 34 ms · 0 token»*.

## Bu kapının savunduğu üç şey

| # | savunulan | neden kapı gerekiyor |
|---|---|---|
| 1 | `onSorgu` dalı **var** | dal silinirse davranış sessizce eski hâline döner |
| 2 | dal **sırası**: makro → hazır sorgu → metin | makro satırının `cube_query`'si **yoktur**; sıra bozulursa `/ask`'a düşer |
| 3 | zincir **uçtan uca bağlı** (`page.tsx` → `onSorguKos`) | prop bağlanmazsa dal hiç çalışmaz ve kapı yine yeşil kalırdı 🆆 |

⚠ Üçüncü satır bu kapının **asıl işi**: bir davranışın *«yazıldığını»* ölçmek kolaydır,
*«çalıştığını»* ölçmek zincirin **her halkasını** sormayı gerektirir ㉕.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_FE = Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"
_SERIT = _FE / "components" / "OneriSeridi.tsx"
_SAYFA = _FE / "app" / "page.tsx"

pytestmark = pytest.mark.skipif(
    not _SERIT.exists(),
    reason="frontend mount edilmedi — kapı kapsamı dışında (kayıp `lab/kapi.py`'de bildirilir)")


def _kod(yol: Path) -> str:
    return yol.read_text(encoding="utf-8")


def test_HAZIR_SORGU_DALI_VAR():
    """`cube_query` taşıyan öngörü **koşulur**; metin olarak yeniden sorulmaz."""
    s = _kod(_SERIT)
    assert "onSorgu" in s, "🔴 `onSorgu` dalı yok — tıklama sorguyu yine atıyor"
    assert re.search(r"if \(a\.cq && onSorgu\)", s), (
        "🔴 dal `a.cq` üzerinden kurulmuyor — satır sorguyu taşımıyor olabilir")


def test_DAL_SIRASI_MAKRO_ONCE_METIN_SONRA():
    """🔴 Sıra bir üslup değil bir **şart**.

    Makro satırının `cube_query`'si **yoktur** (`tur="neden"`, reçete adı); hazır sorgu
    dalı ondan önce koşarsa makro hiç çalışmaz. Ve `onSec` (metin) **en sonda** olmalı:
    öne alınırsa iki üstteki dal da erişilemez olur.
    """
    s = _kod(_SERIT)
    i_makro = s.find("MAKRO_ADLARI.has(a.tur)")
    i_sorgu = s.find("if (a.cq && onSorgu)")
    i_metin = s.find("onSec(a.metin)")
    assert -1 not in (i_makro, i_sorgu, i_metin), "🔴 üç daldan biri yok"
    assert i_makro < i_sorgu < i_metin, (
        f"🔴 dal sırası bozuk: makro={i_makro} sorgu={i_sorgu} metin={i_metin}")


def test_ZINCIR_SAYFAYA_KADAR_BAGLI():
    """🆆 Dal yazılmış olabilir ama **beslenmiyorsa** hiç çalışmaz.

    `page.tsx` → `ReportPanel.onSorguKos` → `Besteci.onSorgu` → `OneriSeridi.onSorgu`.
    Kapı en uçtaki halkayı sorar: sayfa prop'u **geçiyor mu**.
    """
    p = _kod(_SAYFA)
    assert "onSorguKos=" in p, "🔴 `page.tsx` `onSorguKos` geçmiyor — dal beslenmiyor 🆘"
    assert "cubeMutation.mutate" in p, (
        "🔴 koşum `cubeMutation` üzerinden değil — ikinci bir koşum yolu `KAT-1`'i bozar")


def test_METIN_YOLU_KALDIRILMADI():
    """⚠ Zıt ölçüt 🆃: sorgusuz öneri (eski `adaylar` dalı) hâlâ **metni** tamamlamalı.

    Yeni dal bir **ekleme**dir, bir değiştirme değil: `cube_query`'si olmayan bir satır
    tıklandığında davranış bugünküyle birebir kalır (`KURAL B`).
    """
    assert "onSec(a.metin)" in _kod(_SERIT), "🔴 metin yolu düştü — `KURAL B` ihlali"
