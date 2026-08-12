"""🔴🔴 AYNI ÖLÇÜ İKİ KEZ — kullanıcıya saçma, sisteme **bedava bir LLM çağrısı**.

## Canlı ölçüm (curl, 2026-08-12)

    soru : «hedefin neresindeyiz»
    cq   : {"cube": "butce", "measures": ["toplam_hedef", "toplam_hedef"]}
    özet : «hedef: ₺448.230.131,31. **2 ölçü: toplam_hedef, toplam_hedef**.»

Üç ayrı zarar, ve üçüncüsü **sessiz**:

| # | zarar | görünürlük |
|---|---|---|
| ① | anlamsız cümle — aynı ölçüyü iki kez sayan envanter satırı | kullanıcı görür |
| ② | `_ozet`/`viz` ikinci sütunu **ayrı bir ölçü** sanar | dolaylı |
| ③ | 🔴 `olcu_sayisi` **2** → `anlatici.basit_mi` **False** → deterministik şablon atlanır, tur **LLM'e** düşer | **hiç görünmez** |

⊙ Yani bir yinelenme, `§D11-b`'nin *«iki ölçüyü şablon anlatmasın»* kuralını *«iki farklı
ölçü var»* diye **yanıltıyor** ve bedava bir LLM çağrısı doğuruyor — tam da mimarinin
*«LLM'i gereksiz yere çağırma»* ilkesinin tersi.

> *Bir yinelenme, sayan her kuralı yanıltır — ve en pahalıya, sayıyı bir KARAR için
> kullanan kurala mal olur.*

## Yer: `parse_cube_query` — tek doğrulama boğazı

10+ çağıran (`/ask` · plan koşucusu · plan tüketicisi · panolar · zamanlamalar).
Çağıranlardan birine yazmak ötekilerde kusuru açık bırakırdı (`KAT-1`).

⚠ **Sıra korunur:** `interpret` olguları `measures[0]` üzerinden üretir; sıralamayı bozan
bir tekilleştirme, cevabın anlattığı ölçüyü sessizce değiştirirdi.
"""

from __future__ import annotations

import json

import pytest

from app import cube_router


@pytest.fixture(scope="module")
def indeks():
    # ⚠ `index` **cube adıyla anahtarlanmış** bir sözlüktür — `{"cubes": [...]}` DEĞİL.
    # (İlk yazımda şemayı varsaydım ve üç test `None` aldı; ders ⑤: *şekli ölç, varsayma.*)
    return {"butce": {"measures": ["toplam_hedef", "ort_hedef", "kalem_sayisi"],
                      "dimensions": ["kalem"], "time_dimensions": ["tarih"]}}


def _coz(cq: dict, indeks: dict) -> dict | None:
    return cube_router.parse_cube_query(json.dumps(cq, ensure_ascii=False), indeks)


def test_YINELENEN_OLCU_TEKILLESIR(indeks):
    """🔴 Kusurun ta kendisi — canlıda ölçülen `cube_query`."""
    out = _coz({"cube": "butce", "measures": ["toplam_hedef", "toplam_hedef"]}, indeks)
    assert out is not None, "⊘ ölçüm tabanı çöktü: geçerli sorgu reddedildi"
    assert out["measures"] == ["toplam_hedef"], (
        f"🔴 yinelenen ölçü kaldı: {out['measures']} — kullanıcı «2 ölçü: toplam_hedef, "
        "toplam_hedef» cümlesini görür ve tur şablon yerine LLM'e düşer.")


def test_SIRA_KORUNUR(indeks):
    """⚠ `interpret` olguları `measures[0]` üzerinden üretir — sıra bir sözleşmedir."""
    out = _coz({"cube": "butce",
                "measures": ["ort_hedef", "toplam_hedef", "ort_hedef"]}, indeks)
    assert out["measures"] == ["ort_hedef", "toplam_hedef"], (
        "🔴 tekilleştirme sırayı bozdu — cevabın anlattığı ölçü sessizce değişir.")


def test_KURAL_B_yinelenme_yoksa_LISTE_AYNI(indeks):
    """`KURAL B`: yinelenme yoksa çıktı **bayt bayt** aynı."""
    icin = ["toplam_hedef", "ort_hedef", "kalem_sayisi"]
    out = _coz({"cube": "butce", "measures": list(icin)}, indeks)
    assert out["measures"] == icin


def test_GECERSIZ_OLCU_HALA_REDDEDILIR(indeks):
    """⊘ Tekilleştirme bir **gevşetme değildir**: katalogda olmayan ölçü yine düşer.

    (Yinelenmeyi silip geçerlilik denetimini de yumuşatmak, kusuru kapatırken kapıyı
    açmak olurdu.)"""
    assert _coz({"cube": "butce", "measures": ["yok_boyle_bir_olcu"]}, indeks) is None
    assert _coz({"cube": "butce",
                 "measures": ["toplam_hedef", "yok_boyle_bir_olcu"]}, indeks) is None


def test_TEKILLESTIRME_OLCU_SAYISINI_de_DUZELTIR():
    """🔴🔴 **SESSİZ ZARARIN KAPISI** — ③ numaralı zarar.

    Yinelenen ölçü `olcu_sayisi`ni 2 yapıyor ve `basit_mi` deterministik şablonu
    atlıyordu. Bu test iki durumu **yan yana** ölçer: yinelenmiş liste (tekilleştirme
    sonrası) şablonda kalmalı, gerçekten iki farklı ölçü ise LLM'e gitmeli.
    """
    from app import anlatici
    from app.interpret import interpret

    rows = [{"ay": "2026-01", "toplam_hedef": 100.0, "ort_hedef": 5.0},
            {"ay": "2026-02", "toplam_hedef": 130.0, "ort_hedef": 4.0},
            {"ay": "2026-03", "toplam_hedef": 160.0, "ort_hedef": 3.0}]
    res = {"columns": ["ay", "toplam_hedef", "ort_hedef"], "rows": rows, "row_count": 3}

    def _yorum(olculer):
        return interpret(res, {"cube": "butce", "measures": olculer, "dimensions": [],
                               "timeDimensions": [{"dimension": "ay",
                                                   "granularity": "month"}]}) or {}

    # Tekilleştirilmiş hâl (kapıdan çıkan) → tek ölçü → ŞABLON (0 LLM)
    assert anlatici.basit_mi(_yorum(["toplam_hedef"])) is True, (
        "🔴 tekilleştirilmiş tek ölçü şablona düşmedi — tekilleştirmenin kazancı yok.")
    # Ham hâl (kapıdan geçmemiş) → sayı 2 → LLM. Kusurun bedeli tam olarak buydu.
    assert anlatici.basit_mi(_yorum(["toplam_hedef", "toplam_hedef"])) is False, (
        "⊘ ölçüm tabanı değişti: yinelenmiş liste artık şablonda kalıyor — bu testin "
        "gerekçesi (bedava LLM çağrısı) yeniden okunmalı.")
    # Ve gerçek iki ölçü hâlâ LLM'e gitmeli — düzeltme kuralı gevşetmedi.
    assert anlatici.basit_mi(_yorum(["toplam_hedef", "ort_hedef"])) is False
