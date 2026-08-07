"""🔴 **BAĞLAM ELDEYKEN «VERİ SİNYALİ YOK» DENEMEZ** — canlı curl bulgusu.

## Ölçülen

    peki bu neden düşük  →  "Görüşürüz! İstediğin zaman buradayım."   371 ms · 0 LLM

Kullanıcı bir **kök-neden** sorusu sordu; sistem **hoşça kal** dedi — ve bunu en ucuz,
en hızlı, kendinden emin biçimde yaptı.

## Kontrollü karşılaştırma tetikleyiciyi izole etti

| soru | eski davranış |
|---|---|
| `peki bu neden düşük` | 🔴 *"Görüşürüz!"* |
| `peki neden böyle` | 🔴 *"Görüşürüz!"* |
| `peki bu ay ciro` | ✅ rapor |
| `neden düşük` *(peki'siz)* | ✅ netleştirme |

⊙ Kusur `peki`'nin sözlükte olmasında **değil**, **veri sinyalinin tanımında**: bir takip
sorusu (`bu`·`neden`·`düşük`) katalog terimi **taşımaz** — onu önceki tur taşır, ve o tur
istekte **elde durur** (`cube_query`).

*Bir cümlenin veri sorusu olup olmadığı yalnız kendi kelimelerinden okunamaz; bağlamı
elde tutan bir sistem için bu bilgi zaten mevcuttur.*

## ⚠ İki kanat AYRI tutuldu

**Tam kaplama** bağlamdan **bağımsız** kazanmaya devam eder — bir thread'in ortasındaki
*"teşekkürler"* hâlâ sosyaldir. Bağlama bağlanan yalnız **zayıf** kanat (*"veri sinyali
bulamadım"*), çünkü yanılabildiği yer orasıydı.
"""

from __future__ import annotations

import pytest

from tests.conftest import ask


def _cq():
    return {"cube": "parti", "measures": ["toplam_ciro"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}


@pytest.mark.parametrize("soru", ["peki bu neden düşük", "peki neden böyle"])
def test_TAKIP_SORUSU_VEDA_SANILMIYOR(client, soru):
    """🔴 Kapının asıl iddiası: bağlam eldeyken sosyal sınıf **kazanamaz**."""
    d = ask(client, soru, cube_query=_cq(), history=["bu yıl ciro"])
    assert d.get("source") != "meta", (
        f"🔴 takip sorusu sosyal sınıfa düştü: {d.get('note')!r}")
    assert "Görüşürüz" not in (d.get("note") or ""), d.get("note")


def test_TESEKKURLER_THREAD_ICINDE_DE_SOSYAL(client):
    """⚠ Genişlemenin sınırı: **tam kaplama** bağlamdan bağımsız kazanır. *Bir kuralı
    düzeltmek, komşusunu bozma hakkı vermez.*"""
    d = ask(client, "teşekkürler", cube_query=_cq(), history=["bu yıl ciro"])
    assert d.get("source") == "meta", (
        f"🔴 saf sosyal ifade artık sosyal sayılmıyor: source={d.get('source')}")


def test_BAGLAMSIZ_DAVRANIS_DEGISMEDI(client):
    """`KURAL B` ruhu: bağlam **yokken** bugünkü davranış birebir korunur — orada soru
    gerçekten belirsizdir ve sistem bugünkü kararını verir."""
    d = ask(client, "teşekkürler")
    assert d.get("source") == "meta"


def test_KAPI_YAPISAL_YENI_SOZLUK_YOK():
    """🔴 `ADR-0008`. Düzeltme bir kelime listesi büyütmüyor; **istekte zaten duran**
    bir alana bakıyor."""
    import inspect

    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    i = src.index("_baglamli = bool(")
    blok = src[i:i + 400]
    assert "cube_query" in blok and "history" in blok, (
        "🔴 kapı istekteki bağlam alanlarına bakmıyor")
    # ⚠ Ölçüt *"tırnak var mı"* DEĞİL — `getattr(body, "cube_query")` meşru olarak tırnak
    # taşır ve ilk yazımda kapı **kendi düzeltmesini** reddetti. Ölçüt bir **liste**dir:
    # arka arkaya virgülle ayrılmış metin sabitleri. *Bir kapının ölçütü, koruduğu şeyin
    # biçimine değil ANLAMINA bakmalı.*
    import re as _re

    assert not _re.search(r'"[^"]+"\s*,\s*"[^"]+"\s*,', blok), (
        "🔴 satıra kelime listesi yazılmış — `ADR-0008`")
