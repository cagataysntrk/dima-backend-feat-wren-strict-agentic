"""Türkçe sayı/tarih biçimlendirme — **tek kaynak** (Faz C2).

## Ölçülen sorun

Aynı sayı iki yüzeyde farklı görünüyordu:

| Değer | `interpret._fmt` (sohbet) | `schedules._fmt_deger` (e-posta) |
|---|---|---|
| `150.5` | **`150`** | **`150,50`** |
| `12.34` | `12,34` | `12,34` |
| `1234567.0` | `1.234.567` | `1.234.567` |

Kullanıcı aynı raporu ekranda ve e-postada farklı okuyor — bir BI ürününde bu, sayıya
duyulan güveni doğrudan aşındırır. Ayrıca ay kısaltmaları **üç** yerde ayrı ayrı tanımlıydı
(`interpret._MONTHS_TR`, `schedules._AY_KISA`, `kpi._MONTHS_TR`).

## Seçilen kural ve gerekçesi

`interpret`'in kuralı `abs(n) >= 100 or n == int(n)` → 0 ondalık idi; yani **150,5 → "150"**.
Bu, kullanıcıya gösterilen değeri **sessizce değiştirir** (%0,33 hata) ve ürünün "her sayı
kanıtlanabilir" tezine aykırıdır. Seçilen kural `schedules`'ınkidir:

- tam sayıysa → **0 ondalık** (`1.234.567`)
- değilse → **2 ondalık** (`150,50`)

Kesirli kısmı asla sessizce atmaz. Büyük tutarlarda iki hane biraz ayrıntılı görünür ama
"gösterilen sayı gerçek sayıdır" garantisi ondan önemlidir.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

AY_KISA = ("Oca", "Şub", "Mar", "Nis", "May", "Haz",
           "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara")

_PARA = ("₺", "$", "€")


def sayi(v: Any) -> str:
    """Türkçe biçimli sayı: binlik `.`, ondalık `,`. Bilimsel gösterim YOK.

    `15576000 → "15.576.000"` · `12.34 → "12,34"` · `150.5 → "150,50"`.
    """
    try:
        n = round(float(v), 2)
    except (TypeError, ValueError):
        return str(v)
    if n == int(n):
        return f"{int(n):,}".replace(",", ".")
    tam, kesir = f"{n:.2f}".split(".")
    return f"{int(tam):,}".replace(",", ".") + "," + kesir


def olcu(v: Any, unit: str | None = None) -> str:
    """Sayı + birim. Para birimi ÖNE, diğerleri arkaya (`₺1.500` · `12,5 kg`)."""
    if v is None:
        return "—"
    s = sayi(v)
    if not unit:
        return s
    return f"{unit}{s}" if unit in _PARA else f"{s} {unit}"


def kova(v: Any) -> str:
    """Zaman kovası etiketi: `2026-04-01` / `date(2026,4,1)` → `Nis 2026`.

    Ay-başı olmayan tarihler `gg.aa.yyyy` olur; tanınmayan değer olduğu gibi döner.
    """
    if isinstance(v, (date, datetime)):
        y, ay, gun = v.year, v.month, v.day
    else:
        s = str(v)
        parcalar = s[:10].split("-")
        if len(parcalar) < 2 or not parcalar[0].isdigit():
            return s
        try:
            y = int(parcalar[0])
            ay = int(parcalar[1])
            gun = int(parcalar[2]) if len(parcalar) > 2 and parcalar[2].isdigit() else 1
        except ValueError:
            return s
    if not 1 <= ay <= 12:
        return str(v)
    return f"{AY_KISA[ay - 1]} {y}" if gun == 1 else f"{gun:02d}.{ay:02d}.{y}"
