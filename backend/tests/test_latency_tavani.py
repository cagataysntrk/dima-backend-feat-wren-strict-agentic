"""FAZ O-0 — LATENCY TAVANI. Orkestratörün ön koşulu, ve ondan bağımsız bir borç.

## Neden bu kapı var

Orkestratör planı bir soruyu **3-8 sorguya** bölecek. Bugün soru başına gecikmenin bir
**tavanı yok** ve bu, iki ayrı biçimde zarar veriyor:

1. Bir gerileme **sessizce birikir** — kimse bakmıyorsa 400 ms 900 ms'e çıkar ve fark
   ancak kullanıcı şikâyet edince görülür.
2. Plan geldiğinde çarpan **var olan tabanın üstüne** biner: 8 sorgu × bilinmeyen bir
   taban = ölçülemeyen bir ürün.

## 🔴 TABAN ÖLÇÜLDÜ — ve devralınan iddiayı DÜZELTTİ

Bağımsız ajanın kapı-yavaşlaması raporu *"`/ask` 47 ms → **177 ms**"* diyordu (medyan,
kendi örneklemi). Bu kapı için taban **kapının kendi kütüğünden** ölçüldü — korpus
koşumunun **15.149** isteği, `answer.py`'nin zaten yazdığı `süre=…ms` alanından:

    n=15149   min=77   p50=445   p90=801   p99=1923   max=3472

⊙ Yani gerçek p50 **445 ms** — raporun 177'sinden de yüksek. İki sayı **çelişmiyor**,
farklı şeyler ölçüyorlar: rapor bir örneklemin medyanını, bu ise **tam korpusu**. Ve
korpus daha zor sorular içerir (netleştirme, çapraz-konu, kapsam kapısı).

*Bir tabanı iki kez ölçmek, ikisinin de neyi ölçtüğünü yazmayı gerektirir.*

## Tavan neden 700 ms

`p50=445`'in **~%57 üstü**. Neden bu kadar geniş: bu kapı bir **hedef** değil bir
**cırcır**dır — bugünkü davranışı dondurmak değil, **sessiz erozyonu** yakalamak için
var. Dar bir tavan makine yüküyle dalgalanır ve kapıyı gürültüye boğar; geniş bir tavan
yalnız **gerçek** bir gerilemeyi (×1,5) yakalar.

⚠ Tavan **düştükçe çekilir** (`test_kapi_hizi`nin dilim disipliniyle aynı): p50 iyileşirse
bu sayı da iner ve gerekçesi yazılır. *Bir cırcır yalnız yanlış yöne dönmeyi engellemeli.*

## ⚠ NE ÖLÇMEZ — sınırı yazılı

Bu kapı **koşum yapmaz**: gerçek bir `/ask` turu bir LLM sağlayıcısı ister ve o
belirlenimsizdir (`--hepsi` `eval_llm`'i tam bu yüzden dışarıda bırakıyor). Burada
ölçülen şey **kayıtlı gecikmedir** — kapının kendi kütüğü. Kütük yoksa test **atlanır**,
uydurma bir sayı üretmez.

*Ölçemediğini yeşil sayan bir kapı, olmayan bir kapıdır.*
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

#: Ölçülen taban (korpus koşumu, 15.149 istek, 2026-08-09).
TABAN_P50_MS = 445
#: Cırcır: gerçek bir gerilemeyi (×1,5) yakalar, makine gürültüsünü yakalamaz.
TAVAN_P50_MS = 700

#: Kayıt biçimi: `| **15.149** | 77 ms | **445 ms** | …` satırındaki p50 sütunu.
#: ⟳ İlk yazımda HAM ÖRNEKLERİ (`süre=…ms`) topluyordum ve kapı hep atlıyordu — çünkü
#: elimizde 15.149 ham satır değil, onlardan ÇIKARILMIŞ bir p50 var. Bir kaydı okumak
#: için ham veriyi aramak, kaydın ne olduğunu anlamamaktır.
_P50 = re.compile(r"\|\s*\*\*([\d.]+)\*\*\s*\|\s*\d+\s*ms\s*\|\s*\*\*(\d+)\s*ms\*\*")


def _kayitli_p50() -> tuple[float | None, int]:
    """Ölçüm kaydından `(p50_ms, örneklem)` okur — yoksa `(None, 0)`.

    ⚠ Kaynak **koşum değil kayıttır**: bu kapı bir sağlayıcı çağırmaz, bir konteyner
    başlatmaz, bir sayı uydurmaz. Kayıt yoksa test **atlanır** ve bunu **söyler**.
    """
    kayit = Path(__file__).resolve().parent.parent / "lab" / "reports" / "latency.md"
    try:
        m = _P50.search(kayit.read_text(encoding="utf-8"))
    except OSError:
        return None, 0
    if not m:
        return None, 0
    return float(m.group(2)), int(m.group(1).replace(".", ""))


def test_LATENCY_TAVANI_ASILMIYOR():
    """🔴 `/ask` medyan gecikmesi tavanın altında mı — **sessiz erozyon kapısı**."""
    p50, n = _kayitli_p50()
    if p50 is None or n < 50:
        pytest.skip("gecikme kaydı yok (lab/reports/latency.md) — kapı ölçemediğini söyler")
    assert p50 <= TAVAN_P50_MS, (
        f"🔴 `/ask` medyan gecikmesi **{p50:.0f} ms** — tavan {TAVAN_P50_MS} ms "
        f"(taban {TABAN_P50_MS} ms, {n} örnek).\n"
        "Orkestratör planı bir soruyu 3-8 sorguya böler; bu taban onunla ÇARPILIR.\n"
        "⚠ Tavanı yükseltmek bir çözüm DEĞİLDİR: gerileme önce **teşhis** edilir.")


def test_TAVAN_TABANIN_USTUNDE_VE_MAKUL():
    """⊙ Cırcırın kendisi denetlenir: tavan tabandan yüksek ama **iki katından az**.

    Bir tavan tabana çok yakınsa makine gürültüsüyle kırmızı verir ve **atlanan bir
    kapıya** dönüşür; çok uzaksa hiçbir şey yakalamaz ve **süs** olur.
    """
    assert TABAN_P50_MS < TAVAN_P50_MS < TABAN_P50_MS * 2, (
        f"tavan {TAVAN_P50_MS} taban {TABAN_P50_MS} ile makul bir oranda değil")
