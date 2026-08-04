"""FAZ 5.7 kapısı — **segment A↔B farkı.** [bayraksız]

## Ölçülen boşluk

`in` filtresi **vardı** (*"RAM-2 ve RAM-3"* → `{"operator": "in", "value": [...]}`) ve
iki segment **yan yana çiziliyordu** — ama *"aradaki fark ne?"* sorusunun **sayısı**
hiçbir yerde yazılı değildi. Kullanıcı iki çubuğa bakıp farkı **kafadan çıkarıyordu**.

## ⚠ Şekil düzeltmesi — kolon DEĞİL, fact

Yol haritası *"Δ kolonu"* diyordu; ölçüldü ve şekil yanlış çıktı: `A − B` satır başına
bir değer **değil**, iki satırın arasındaki **tek bir skalerdir**. Kolon olarak basmak,
her satıra aynı sayıyı yazmak demekti. *Bir sayının şekli, onu nereye koyacağını
belirler.*
"""

from __future__ import annotations

import pytest

from app.interpret import _segment_delta, interpret


def _r(*ciftler):
    return [{"makine": a, "fire": v} for a, v in ciftler]


def test_IKI_segmentte_fark_URETILIR():
    f = _segment_delta(_r(("RAM-2", 120), ("RAM-3", 80)), "makine", "fire", None)
    assert len(f) == 1
    assert f[0]["type"] == "segment_delta"
    assert f[0]["mutlak"] == 40
    assert f[0]["pct"] == 50.0
    assert f[0]["a"] == "RAM-2" and f[0]["b"] == "RAM-3"


def test_UC_segmentte_URETILMEZ():
    """🔴 *"A−B"* üçlüde **hangi ikisi** olduğunu söylemez.

    Üç ayrı fark yazmak, kullanıcının sormadığı bir tabloyu doğururdu.
    *Belirsiz bir fark, farkın kendisinden kötüdür.*
    """
    assert _segment_delta(_r(("A", 1), ("B", 2), ("C", 3)), "makine", "fire", None) == []


def test_TEK_segmentte_URETILMEZ():
    """Kıyaslanacak bir şey yok."""
    assert _segment_delta(_r(("A", 1)), "makine", "fire", None) == []


def test_SAYISAL_OLMAYAN_satir_ELENIR():
    """Ölçüsü olmayan bir satır bir segment değildir — ve onu saymak 'iki segment'
    şartını **sahte** olarak sağlardı."""
    rows = [{"makine": "A", "fire": 10}, {"makine": "B", "fire": None},
            {"makine": "C", "fire": 4}]
    f = _segment_delta(rows, "makine", "fire", None)
    assert f and f[0]["a"] == "A" and f[0]["b"] == "C"


def test_SIFIR_paydada_YUZDE_URETILMEZ():
    """`B = 0` iken yüzde **tanımsızdır** — 'sonsuz artış' yazmak uydurma olurdu."""
    f = _segment_delta(_r(("A", 10), ("B", 0)), "makine", "fire", None)
    assert f and f[0]["pct"] is None and f[0]["mutlak"] == 10
    assert "%" not in f[0]["text"]


def test_FAVORABLE_yalniz_BEYAN_varsa_yazilir():
    """⚠ *"A daha yüksek"*in **iyi mi kötü mü** olduğunu beyan olmadan söylemek uydurmadır."""
    yok = _segment_delta(_r(("A", 10), ("B", 4)), "makine", "fire", None)[0]
    assert yok["favorable"] is None
    var = _segment_delta(_r(("A", 10), ("B", 4)), "makine", "fire", None, lib=True)[0]
    assert var["favorable"] is False        # fire yüksek → kötü


def test_UCTAN_UCA_interpret_ciktisinda_gorunur():
    """Fact üretiliyor ama `interpret()` onu düşürüyorsa **kullanıcı görmez**."""
    out = interpret({"columns": ["makine", "fire"],
                     "rows": _r(("RAM-2", 120), ("RAM-3", 80)), "row_count": 2},
                    {"cube": "parti", "measures": ["fire"], "dimensions": ["makine"]})
    turler = [f["type"] for f in out["facts"]]
    assert "segment_delta" in turler, f"fact zincirden düştü: {turler}"
    assert "RAM-2 − RAM-3" in out["summary"]


@pytest.mark.parametrize("n", [0, 1, 3, 4])
def test_SADECE_IKI_segment(n):
    rows = [{"makine": f"M{i}", "fire": i + 1} for i in range(n)]
    assert _segment_delta(rows, "makine", "fire", None) == []
