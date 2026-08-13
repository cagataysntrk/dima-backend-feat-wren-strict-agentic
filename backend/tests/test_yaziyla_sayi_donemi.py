"""🔴 `§74` (`K5`) — **YAZIYLA YAZILMIŞ SAYI**: *«son üç ay»* ≡ *«son 3 ay»*.

## Ölçülen kusur (canlı `s35`, curl)

```
«son 3 ayda fire ne kadar»   → source=cube      · dönem 2026-05-13 →            ✅
«son üç ayda fire ne kadar»  → source=cube+llm  · dönem 2025-06-01 → 2026-06-30 🔴 13 AY
```

İki zarar birden: route **düşüyor** (gereksiz bir LLM turu) **ve** dönem 13 aya açılıyor —
kullanıcı yanlış sayıyı doğru sanıyor. *Bir sistemin yanlış cevabı, cevapsızlığından
pahalıdır.*

## Neden bu bir *«route'a dil kuralı eklemek»* DEĞİL

`_REL_DATE` **zaten** bir Türkçe birim listesi taşıyor (`ay|gun|hafta|yil`). Sayı
sözcükleri aynı cinsten: **kapalı ve sonlu** (`bir…on iki`). Yasak olan **açık uçlu**
sözcük listeleridir ㊱ — bu küme sayılabilir ve bitmiştir.

## ⚠ `«bir ay»` belirsizliği ⑯ — yapısal olarak çözüldü

Sözcük ancak `son <SAYI> <birim>` **üçlüsünün ortasında** eşleşir. Tek başına duran
*«bir ay»* (*«herhangi bir ay»*) bu kalıba **hiç girmez** — bir eşik ya da sezgiyle değil,
**kalıbın şekliyle**.

## Bu kapının altı yüklemi

| # | savunulan |
|---|---|
| 1 | *«son üç ay»* ≡ *«son 3 ay»* — **aynı tarih** |
| 2 | `on bir`/`on iki` **iki sözcüklü** ve doğru çözülür (uzun-önce sırası) |
| 3 | 🆃 tek başına *«bir ay»* **eşleşmez** — belirsizlik korunur |
| 4 | 🆃 sıra sayısı (*«üçüncü ay»*) **eşleşmez** |
| 5 | komşu kalıp: *«son üç aya göre»* bir **dönem**dir, kırılım değil ⑯ |
| 6 | çözümün **tek sahibi** `donem_capasi.sayi_coz` ㊲ |
"""

from __future__ import annotations

import pytest

from app import donem_capasi
from app.cube_router import _norm, _relative_date_filter


def _gte(q: str) -> str | None:
    f = _relative_date_filter(_norm(q), "tarih")
    return (f or {}).get("value")


def test_YAZIYLA_VE_RAKAMLA_AYNI_TARIH():
    """🔴 **ASIL DEĞİŞMEZ.** İki yazım aynı dönemi verir."""
    assert _gte("son uc ay") == _gte("son 3 ay") is not None
    assert _gte("son bes ay") == _gte("son 5 ay") is not None


def test_IKI_SOZCUKLU_SAYILAR():
    """`on iki` `on`dan **önce** denenmeli; yoksa artık `iki ay` kalır ve kalıp tutmaz."""
    assert _gte("son on iki ay") == _gte("son 12 ay") is not None
    assert _gte("son on bir ay") == _gte("son 11 ay") is not None
    assert _gte("son on ay") == _gte("son 10 ay") is not None


def test_ZIT_OLCUT_TEK_BASINA_BIR_AY_ESLESMEZ():
    """🆃⑯ *«bir ay»* iki anlamlıdır; kalıp onu **kapsamaz** — ve kapsamamalı."""
    assert _gte("bir ay") is None, "🔴 «bir ay» dönem sanıldı — belirsizlik yutuldu"
    assert _gte("bir ayda fire ne kadar") is None


def test_ZIT_OLCUT_SIRA_SAYISI_ESLESMEZ():
    """🆃 *«üçüncü ay»* bir süre değil bir **sıradır**."""
    assert _gte("son ucuncu ay") is None, "🔴 sıra sayısı süre sanıldı"


def test_KOMSU_KALIP_GORE_TUZAGINA_DUSMEZ():
    """⑯ *«son üç aya göre»* bir **dönem** ifadesidir; `«göre»` burada kırılım istemez —
    bu tuzak bu depoyu **üç kez** ısırdı."""
    from app.cube_router import _PERIOD_RANGE_REF

    assert _PERIOD_RANGE_REF.search(_norm("son üç aya göre")), (
        "🔴 komşu kalıp genişletilmemiş — «son üç aya göre» kırılım sanılır")
    assert _PERIOD_RANGE_REF.search(_norm("son 3 aya göre")), "🔴 rakamlı biçim bozuldu"


@pytest.mark.parametrize("soz,beklenen", [("uc", 3), ("on iki", 12), ("7", 7),
                                          ("", None), (None, None), ("yarim", None)])
def test_COZUMUN_TEK_SAHIBI(soz, beklenen):
    """㊲ Sayı **bir** yerde çözülür; iki yerde çözülen bir sayı iki tarihe dönüşür.
    ⊘ `yarim` **yok**: *«son yarım ay»* bir dönem değil bir yuvarlamadır 🆂."""
    assert donem_capasi.sayi_coz(soz) == beklenen
