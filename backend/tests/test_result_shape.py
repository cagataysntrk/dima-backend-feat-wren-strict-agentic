"""FAZ C1 — kolon rolü TEK kaynaktan: `app/result_shape.py`.

Aynı sonuç tablosu üzerinde "hangi kolon ölçü, hangisi boyut, hangisi zaman ekseni"
sorusuna **iki bağımsız motor** cevap veriyordu ve ikisi de `source="cube"` rozetiyle,
"deterministik" iddiasıyla sunuluyordu:

- `viz.analyze` — `cube_query`'den **otorite** alıyor, ad sözlüğü 11 isim.
- `interpret._classify` — otorite **almıyor** (oysa `interpret()` `cube_query`'yi zaten
  alıyordu!), saf değer-tabanlı, ad sözlüğü 18 isim, sayısal testi ad kontrolünden ÖNCE.

**Ölçülen ayrışma (uygulama öncesi, bu dosyanın var olma sebebi):**

| Vaka | `interpret` | `viz` |
|---|---|---|
| `ay` = 1..12 | **ÖLÇÜ**, zaman ekseni yok | boyut, zaman ekseni `ay` |
| `gun` = "Pzt/Sal/Çar" | zaman ekseni `gun` | boyut, zaman ekseni yok |

Birincisi ürünün tezine doğrudan zarar verir: grafik aylık seri çizerken cümle **ay
numaralarının ortalamasını** bir metrik gibi anlatır. Kullanıcının fark etmesi imkânsız —
her iki çıktı da "deterministik" rozetli.
"""

from __future__ import annotations

import datetime as dt

import pytest

from app import viz
from app.interpret import _classify
from app.result_shape import authority_from_cube_query, classify, is_num, looks_date

# (ad, kolonlar, satırlar, cube_query)
VAKALAR = [
    ("sayısal ay numarası", ["ay", "ciro"],
     [{"ay": i, "ciro": 100 * i} for i in range(1, 6)], None),
    ("metin hafta günü", ["gun", "ciro"],
     [{"gun": g, "ciro": 10} for g in ("Pzt", "Sal", "Çar")], None),
    ("date NESNESİ", ["tarih", "ciro"],
     [{"tarih": dt.date(2026, i, 1), "ciro": 10} for i in (1, 2, 3)], None),
    ("dönem metni", ["donem", "ciro"],
     [{"donem": f"2026-0{i}", "ciro": 10} for i in (1, 2, 3)], None),
    ("otorite: sayısal BOYUT", ["vardiya", "ciro"],
     [{"vardiya": i, "ciro": 10} for i in (1, 2, 3)],
     {"cube": "oee", "measures": ["ciro"], "dimensions": ["vardiya"]}),
    ("otorite: zaman kovası", ["tarih__month", "ciro"],
     [{"tarih__month": f"2026-0{i}-01", "ciro": 10} for i in (1, 2, 3)],
     {"cube": "parti", "measures": ["ciro"],
      "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}),
]


@pytest.mark.parametrize("ad,cols,rows,cq", VAKALAR, ids=[v[0] for v in VAKALAR])
def test_interpret_ve_viz_AYNI_karari_verir(ad, cols, rows, cq):
    """ASIL KAPI. İki "deterministik" motor aynı tabloya bakıp farklı şey söyleyemez."""
    dim_cols, ipucu = authority_from_cube_query(cq)
    a = viz.analyze(cols, rows, dim_cols=dim_cols, time_col_hint=ipucu)
    m, _d, t = _classify(cols, rows, cq)
    assert m == a["measures"], f"{ad}: ölçü kararı ayrıştı ({m} ≠ {a['measures']})"
    assert t == a["time_col"], f"{ad}: zaman ekseni ayrıştı ({t} ≠ {a['time_col']})"


def test_sayisal_ay_OLCU_SANILMAZ():
    """Ölçülen sessiz-yanlış: `ay` 1..12 ise `interpret` onu ÖLÇÜ sayıp "ortalama 3"
    gibi anlamsız bir cümle kurabiliyordu. Ad sözlüğü değer tipinden ÖNCE bakmalı."""
    m, _d, t = classify(["ay", "ciro"], [{"ay": i, "ciro": 10} for i in range(1, 6)])
    assert m == ["ciro"] and t == "ay"


def test_hafta_gunu_ZAMAN_EKSENI_SAYILMAZ():
    """"Pzt/Sal/Çar" bir timeline değil **döngüsel kategoridir**; zaman ekseni saymak
    uydurma bir trend anlatımı doğurur. Gerçek gün granülerliği (`tarih__day`) otoriteyle
    gelir, ad tahminiyle değil."""
    _m, _d, t = classify(["gun", "ciro"], [{"gun": g, "ciro": 1} for g in ("Pzt", "Sal")])
    assert t is None


def test_OTORITE_sayisal_boyutu_korur():
    """`cube_query.dimensions` KESİNDİR: vardiya no / yıl sayısaldır ama ölçü değildir."""
    rows = [{"vardiya": i, "yil": 2026, "ciro": 10} for i in (1, 2, 3)]
    m, d, _t = classify(["vardiya", "yil", "ciro"], rows,
                        dim_cols={"vardiya", "yil"})
    assert m == ["ciro"] and set(d) == {"vardiya", "yil"}


def test_OTORITE_turev_olculeri_kaybetmez():
    """YoY `_gecen`/`_degisim_yuzde` kolonları `cube_query.measures`'ta YOKTUR ama
    ölçüdürler — otorite "boyut değilse ve sayısalsa ölçü" der."""
    rows = [{"makine": "A", "ciro": 10, "ciro_gecen": 8, "ciro_degisim_yuzde": 25.0}]
    m, _d, _t = classify(["makine", "ciro", "ciro_gecen", "ciro_degisim_yuzde"], rows,
                         dim_cols={"makine"})
    assert m == ["ciro", "ciro_gecen", "ciro_degisim_yuzde"]


def test_zaman_kovasi_otoriteden_TURETILIR():
    """Kova kolonu `<boyut>__<granülerlik>` adıyla döner ve `dimensions` listesinde YOKTUR;
    `interpret` bunu hiç bilmiyordu."""
    dims, ipucu = authority_from_cube_query(
        {"timeDimensions": [{"dimension": "tarih", "granularity": "month"}]})
    assert ipucu == "tarih__month" and "tarih__month" in dims


def test_looks_date_NESNEYI_de_tanir():
    """`WrenService.query` Arrow `to_pylist()` döndürür → gerçek `date` nesneleri gelir.
    `viz` yalnız string bakıyordu, nesneleri hiçbir zaman tarih saymıyordu."""
    assert looks_date(dt.date(2026, 1, 1)) and looks_date(dt.datetime(2026, 1, 1))
    assert looks_date("2026-01") and not looks_date("Pzt") and not looks_date(42)


def test_is_num_TURKCE_ondaligi_kabul_eder():
    """Yüklenen CSV/Excel'de (ADR-0021) `"1,5"` olağandır; katı test o kolonu kategorik
    sayıp grafiği tabloya düşürürdü."""
    assert is_num(1) and is_num(1.5) and is_num("1,5") and is_num("2")
    assert not is_num(True) and not is_num("abc") and not is_num(None)


def test_TEK_uygulama_kaldi():
    """İkinci bir rol-atama motoru geri doğmasın: her iki tüketici de `result_shape`'i
    çağırmalı, kendi döngüsünü kurmamalı."""
    import inspect

    for mod, fn in ((viz, "analyze"), ):
        kaynak = inspect.getsource(getattr(mod, fn))
        assert "result_shape" in kaynak, f"{mod.__name__}.{fn} tek kaynağı kullanmıyor"
    from app import interpret

    assert "result_shape" in inspect.getsource(interpret._classify)
