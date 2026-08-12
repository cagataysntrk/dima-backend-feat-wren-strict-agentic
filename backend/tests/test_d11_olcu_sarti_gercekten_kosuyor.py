"""🔴🔴 `§D11` — *«İKİ ÖLÇÜYÜ ŞABLON ANLATMASIN»* KURALI **GERÇEKTEN KOŞUYOR MU**.

## Ölçülen kusur (2026-08-12)

`anlatici.basit_mi`'nin son satırı şunu **yazıyordu**:

    # Tek ölçü şartı: iki ölçüyü tek cümlede anlatmak, aralarında bir İLİŞKİ ima eder
    olculer = {f.get("measure") for f in olgular if f.get("measure")}
    return len(olculer) <= 1

Ölçüm (iki ölçülü gerçek bir `interpret` çıktısıyla):

    olculer = {'toplam_ciro'}   →  len <= 1  →  **True** (kural GEÇTİ)

⊙ Çünkü `interpret` olguları yalnız `measures[0]` için üretir; ikinci ölçünün adı
hiçbir olguda geçmez. **Yazılı şart her zaman geçiyordu.**

## 🔴 Kuralı fiilen uygulayan İKİ KAZA — ve ikisi de bu kuralı bilmiyordu

| # | kaza | kırılganlığı |
|---|---|---|
| ① | `len(olgular) > _AZAMI_OLGU` | iki ölçüde olgu **5**, tavan **4** → tavan 5'e çıkarsa ölür |
| ② | `measures` tipi `TANINAN`da yok | kapsam kapısı onu *«bilinen istisna»* diye kaydetmiş — yani **eklenmeye davetiye** |

⚠ Ve `test_d1_anlatici_kapsami.py::test_COK_OLCULU_KIYAS_hala_LLM_e_gider` **yeşildi**
— yanlış sebeple. Bir kapı doğru sonucu ölçüyordu, doğru **sebebi** değil.

> *Bir kuralın yazılı sahibi onu uygulamıyorsa, kural yoktur; yalnız onu şu an
> tesadüfen karşılayan bir yan etki vardır.*

## Bu dosyanın yüklemi — kazaları KALDIRARAK ölçer

Asıl test (`test_KURAL_KAZALAR_KALKINCA_da_AYAKTA`) iki kazayı da geçici olarak
etkisizleştirir (tavanı yükseltir, `measures`i tanınanlara ekler) ve kuralın **hâlâ**
tuttuğunu ölçer. *Bir değişmezi, onu şu an ayakta tutan tesadüflerle birlikte ölçmek,
tesadüfü değişmez sanmaktır.*
"""

from __future__ import annotations

import pytest

from app import anlatici
from app.interpret import interpret

_ROWS = [{"ay": "2026-01", "toplam_ciro": 100.0, "toplam_fire_kg": 5.0},
         {"ay": "2026-02", "toplam_ciro": 130.0, "toplam_fire_kg": 4.0},
         {"ay": "2026-03", "toplam_ciro": 160.0, "toplam_fire_kg": 3.0}]


def _yorum(olculer: list[str]) -> dict:
    res = {"columns": ["ay", *olculer], "rows": _ROWS, "row_count": len(_ROWS)}
    cq = {"cube": "parti", "measures": olculer, "dimensions": [],
          "timeDimensions": [{"dimension": "ay", "granularity": "month"}]}
    y = interpret(res, cq)
    assert y, "⊘ ölçüm tabanı çöktü: interpret hiç yorum üretmedi"
    return y


def test_TEK_OLCU_SABLONDA_KALIR():
    """⊘ Ön koşul — kural fazla geniş olmamalı. Tek ölçü **şablonla** anlatılır (0 LLM)."""
    assert anlatici.basit_mi(_yorum(["toplam_ciro"])) is True


def test_IKI_OLCU_SABLONA_DUSMEZ():
    """Bugünkü davranış — ama bu satır tek başına kusuru **göremezdi**."""
    assert anlatici.basit_mi(_yorum(["toplam_ciro", "toplam_fire_kg"])) is False


def test_YAZILI_KURALIN_KAYNAGI_YORUMDA_TASINYOR():
    """🔴 Sayının **kaynağı** taşınmalı: olgulardan türetilen küme kuralı ölçemiyordu."""
    y = _yorum(["toplam_ciro", "toplam_fire_kg"])
    assert y.get("olcu_sayisi") == 2, (
        "🔴 `interpret` ölçü sayısını taşımıyor → `basit_mi` kuralı olgulardan türetmek "
        "zorunda kalır ve o küme İKİ ölçüde bile tek elemanlıdır (ölçüldü).")
    olculer = {f.get("measure") for f in y["facts"] if f.get("measure")}
    assert len(olculer) == 1, (
        "⊘ ölçüm tabanı değişti: artık ikinci ölçü de olgu üretiyor. O gün bu dosyanın "
        "gerekçesi yeniden okunmalı — ama kural yine `olcu_sayisi`den okunmalıdır.")


def test_KURAL_KAZALAR_KALKINCA_da_AYAKTA(monkeypatch):
    """🔴🔴 **ASIL KAPI.** İki kazayı da etkisizleştir, kural yine tutsun.

    ① olgu tavanı yükseltilir (`_AZAMI_OLGU` 4 → 9)
    ② `measures` tanınanlara eklenir (kapsam kapısının *«bilinen istisna»* notu tam da
       bunu davet ediyor)

    Bu ikisi olmadan **yazılı** kural çıplak kalır. Eskiden burada `basit_mi` **True**
    dönerdi ve iki ölçülü bir cevap şablona düşerdi — yorumun yasakladığı **bağlaç**
    cümlede belirirdi.
    """
    monkeypatch.setattr(anlatici, "_AZAMI_OLGU", 9)
    monkeypatch.setattr(anlatici, "TANINAN", (*anlatici.TANINAN, "measures"))
    y = _yorum(["toplam_ciro", "toplam_fire_kg"])
    assert len(y["facts"]) == 5, "⊘ olgu sayısı değişti — kaza ① artık başka bir sayıda"
    assert anlatici.basit_mi(y) is False, (
        "🔴 İKİ ÖLÇÜ ŞABLONA DÜŞTÜ. Kuralı ayakta tutan şey yazılı şart değil, iki "
        "**kaza**ymış: olgu tavanı ve `measures` tipinin tanınmayışı. İkisi de "
        "kaldırıldığında kural çöktü.\n"
        "*Bir kuralın yazılı sahibi onu uygulamıyorsa, kural yoktur.*")
    # Ve tek ölçü hâlâ geçmeli — kural genişleyip kapsamı yutmasın.
    assert anlatici.basit_mi(_yorum(["toplam_ciro"])) is True


@pytest.mark.parametrize("yorum", [
    None, {}, {"facts": []}, {"facts": [{"type": "trend", "measure": "a"}]},
])
def test_ESKI_SOZLUKLER_KIRILMAZ(yorum):
    """⚠ `olcu_sayisi` **ek** bir anahtardır: taşımayan çağrılar eski yolla ölçülür.

    (`KURAL B` disiplini: türetim öncesi/sonrası davranış aynı kalmalı.)"""
    beklenen = bool(yorum and yorum.get("facts"))
    assert anlatici.basit_mi(yorum) is beklenen
