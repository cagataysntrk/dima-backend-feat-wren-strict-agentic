"""FAZ 5.13b kapısı — **kural SQL'i DEĞİŞTİRMİYOR.** [bayrak: `ui_knowledge_center`]

Yol haritasının tek şartı: *"kural **SQL'i değiştirmiyor** (kaynak taraması + davranış)."*

## 🔴 Neden bu maddenin en kolay yanlışı tam da budur

Kullanıcı *"fire %5'in üstü kötüdür"* yazar; sistem bunu bir **filtreye** çevirir; o
günden sonra sorular sessizce farklı sayılar döndürür. O an ürün, kullanıcının **hiç
sormadığı** bir soruya cevap vermeye başlar — ve **kimse fark etmez**.

Bu dosya iki yönden kilitler: **yapısal** (kural modülü sorgu üretemez) ve **davranışsal**
(bir kural yüklemek `cube_query`yi değiştirmez).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app import rules

_KAYNAK = Path(__file__).resolve().parents[1] / "app/rules.py"

_KURAL = {"id": "fire-esigi", "kapsam": {"cube": "parti", "olcu": "fire_orani_yuzde"},
          "metin": "Fire oranında %5 üstü, vardiya şefine bildirilmesi gereken bir eşiktir."}


# --- YAPISAL: kural modülü SORGU ÜRETEMEZ ------------------------------------------

def test_KURAL_MODULU_sorgu_uretmiyor():
    """🔴 `rules.py` bir `cube_query`/SQL üretemez, dokunamaz.

    ⚠ Belirteç **AST**: bu dosyanın ve `rules.py`'nin docstring'leri yasak alan adlarını
    **anlatmak için** sayıyor; alt-dize taraması kendi belgesini ölçerdi (bu deponun
    on ikinci kez ödediği ders).
    """
    agac = ast.parse(_KAYNAK.read_text(encoding="utf-8"))
    cagrilar = {getattr(c.func, "attr", getattr(c.func, "id", ""))
                for c in ast.walk(agac) if isinstance(c, ast.Call)}
    for yasak in ("cube_sql", "query", "deterministic_refine", "route",
                  "parse_cube_query", "date_filters"):
        assert yasak not in cagrilar, (
            f"🔴 `rules.py` `{yasak}` çağırıyor — kural SQL'e/ROTAYA sızmış. Bir kural "
            f"anlatıya girer, sorguya değil (ADR-0008 sınırı).")
    # Ve hiçbir fonksiyon `cube_query` DÖNDÜRMEZ: yalnız metin/liste.
    for fn in (n for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)):
        assert "cube_query" not in (
            ast.unparse(fn.returns) if fn.returns else ""), (
            f"🔴 `{fn.name}` bir `cube_query` döndürüyor.")


def test_YASAK_ALANLAR_listesi_SORGU_alanlarini_kapsiyor():
    for alan in ("filters", "sql", "cube_query", "measures", "dimensions", "limit"):
        assert alan in rules.YASAK_ALANLAR


# --- DAVRANIŞ: SQL alanı taşıyan kural REDDEDİLİR ----------------------------------

@pytest.mark.parametrize("yasak", ["filters", "sql", "measures", "limit", "cube_query"])
def test_SORGU_ALANI_tasiyan_kural_REDDEDILIR(yasak):
    """🔴 **Fail-closed** — sessizce yok sayılmaz.

    *Sessizce yok sayılan bir kural, yazan kişiye çalıştığını düşündürür — ve o kişi bir
    gün ona güvenerek karar verir.*
    """
    with pytest.raises(rules.KuralIhlali, match=yasak):
        rules.dogrula({**_KURAL, yasak: ["x"]})
    # Kapsam içinde de yasak.
    with pytest.raises(rules.KuralIhlali):
        rules.dogrula({**_KURAL, "kapsam": {"cube": "parti", yasak: "x"}})


def test_BIR_IHLAL_TUMUNU_durdurur():
    """⚠ *"Bozuk olanı atla, kalanı yükle"* daha nazik görünür ve **daha tehlikelidir**:
    yarım yüklenmiş bir bilgi kümesi, kullanıcının yazdığı kuralın çalıştığını
    sanmasına yol açar."""
    with pytest.raises(rules.KuralIhlali):
        rules.yukle([_KURAL, {**_KURAL, "id": "kotu", "sql": "SELECT 1"}])


def test_KIMLIKSIZ_ve_METINSIZ_kural_REDDEDILIR():
    with pytest.raises(rules.KuralIhlali, match="kimliksiz"):
        rules.dogrula({"metin": "x", "kapsam": {"cube": "a"}})
    with pytest.raises(rules.KuralIhlali, match="metinsiz"):
        rules.dogrula({"id": "a", "kapsam": {"cube": "a"}})


# --- EŞLEŞME: daraltıcı --------------------------------------------------------------

def test_KAPSAM_daraltici():
    ks = rules.yukle([_KURAL])
    assert rules.eslesen(ks, {"cube": "parti", "measures": ["fire_orani_yuzde"]})
    assert not rules.eslesen(ks, {"cube": "oee", "measures": ["fire_orani_yuzde"]})
    assert not rules.eslesen(ks, {"cube": "parti", "measures": ["toplam_fire_kg"]})


def test_BOS_KAPSAM_esdeslemez():
    """🔴 *Bir bilgi merkezi, her cevaba yapışan bir dipnot değildir.*"""
    ks = rules.yukle([{"id": "genel", "metin": "Her şeye yapışsın."}])
    assert rules.eslesen(ks, {"cube": "parti"}) == []


def test_AZAMI_UC_kural():
    """⚠ Üçten fazlası anlatıyı **boğar**: kullanıcı sayıya değil dipnotlara bakar."""
    ks = rules.yukle([{**_KURAL, "id": f"k{i}"} for i in range(6)])
    assert len(rules.eslesen(ks, {"cube": "parti",
                                  "measures": ["fire_orani_yuzde"]})) == rules.AZAMI_KURAL


def test_EK_BAGLAM_metin_doner_sorgu_DEGIL():
    m = rules.ek_baglam(rules.yukle([_KURAL]),
                        {"cube": "parti", "measures": ["fire_orani_yuzde"]})
    assert isinstance(m, str) and "eşiktir" in m
    assert rules.ek_baglam(rules.yukle([_KURAL]), {"cube": "oee"}) is None


def test_KURAL_cube_query_yi_DEGISTIRMEZ():
    """🔴 **Davranışsal kilit.** Kural yüklemek/eşleştirmek `cube_query`ye **dokunmaz**."""
    cq = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["makine"]}
    kopya = {k: (list(v) if isinstance(v, list) else v) for k, v in cq.items()}
    ks = rules.yukle([_KURAL])
    rules.eslesen(ks, cq)
    rules.ek_baglam(ks, cq)
    assert cq == kopya, f"🔴 `cube_query` DEĞİŞTİ: {cq} ≠ {kopya}"
