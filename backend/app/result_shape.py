"""Sonuç şekli — bir sonuç tablosundaki kolonların ROLÜ (ölçü / boyut / zaman ekseni).

## Neden tek kaynak

Bu karar iki yerde **bağımsız** veriliyordu ve ikisi de `source="cube"` rozetiyle,
"deterministik" iddiasıyla sunuluyordu:

- `app/viz.py::analyze` — grafik kararı. `cube_query`'den **otorite** alıyordu
  (`dim_cols`, `time_col_hint`), ad sözlüğü 11 isimdi.
- `app/interpret.py::_classify` — anlatım (ADR-0022). Otorite **almıyordu**, saf
  değer-tabanlıydı, ad sözlüğü 18 isimdi ve sayısal testi ad kontrolünden **önce**
  çalışıyordu.

**Ölçülen ayrışma (2 Ağustos 2026):**

| Vaka | `interpret` | `viz` |
|---|---|---|
| `ay` kolonu 1..12 (sayısal ay numarası) | **ÖLÇÜ**, zaman ekseni yok | boyut, zaman ekseni `ay` |
| `gun` kolonu "Pzt/Sal/Çar" (metin) | zaman ekseni `gun` | boyut, zaman ekseni **yok** |

Birinci satır ürünün tezine doğrudan zarar verir: grafik aylık bir seri çizerken altındaki
cümle **ay numaralarının ortalamasını** bir metrik gibi anlatır. İkincisinde grafik kategori
çubuğu gösterirken cümle bir "trend"den söz eder. İkisi de sessizdir ve ikisi de
"deterministik" rozetlidir — kullanıcının fark etmesi imkânsızdır.

## Kural sırası (tek yerde, gerekçesiyle)

1. **Otorite kazanır.** `cube_query` varsa `dimensions`/`timeDimensions` KESİNDİR: sayısal
   değerli bir boyut (vardiya no, yıl) ölçü sanılmaz; `_gecen`/`_degisim_yuzde` gibi
   cube_query'de olmayan türev sayısal kolonlar doğru şekilde ölçü sayılır.
2. **Otorite yoksa ad sözlüğü** — değer tipinden ÖNCE. LLM'in ürettiği SQL `EXTRACT(MONTH…)`
   ile ay'ı sayı döndürebilir; ad kontrolü olmadan bu ikinci bir "ölçü" olur ve zaman ekseni
   tamamen kaybolur.
3. **Son çare değer biçimi** (`_looks_date`, `_is_num`).

`gun`/`gün`/`day` ad sözlüğünde **BİLEREK YOK**: "Pzt/Sal/Çar" bir zaman ekseni değil
**döngüsel bir kategoridir**; onu timeline sanmak uydurma bir trend anlatımı doğurur.
Gerçek gün granülerliği (`tarih__day`) zaten 1. kuraldan, otoriteyle gelir. `date`/`month`/
`week`/`quarter` ise `tarih`/`ay`/`hafta`/`çeyrek`'in İngilizce karşılıklarıdır — güvenle
eklendi.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

# Ad sözlüğü — TEK. (Eskiden `viz._TIME_NAMES` 11, `interpret._DATE_NAMES` 18 isimdi.)
TIME_NAMES = {
    "tarih", "donem", "dönem", "ay", "hafta", "yil", "yıl", "ceyrek", "çeyrek",
    "date", "period", "month", "week", "year", "quarter",
}

_DATEISH = re.compile(r"^\d{4}-\d{2}")


def is_num(v: Any) -> bool:
    """Sayısal mı? Türkçe ondalık virgülü (`"1,5"`) KABUL EDİLİR.

    Yüklenen CSV/Excel'de (ADR-0021) Türkçe yerel biçim olağandır; katı bir test o
    kolonları kategorik sayıp grafiği tabloya düşürürdü.
    """
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        s = v.strip().replace(".", "").replace(",", ".") if "," in v else v.strip()
        try:
            float(s)
        except (TypeError, ValueError):
            return False
        return True
    return False


def looks_date(v: Any) -> bool:
    """Tarih mi? **Hem nesne hem metin.**

    `WrenService.query` Arrow `to_pylist()` döndürüyor → gerçek `date`/`datetime` NESNELERİ
    gelir. `viz` yalnız string bakıyordu, dolayısıyla nesneleri hiçbir zaman tarih saymıyordu;
    ad sözlüğü yaygın vakayı kurtarıyordu ama `fatura_tarihi`/`islem_gunu` gibi adlarda
    kurtarmıyordu.
    """
    if isinstance(v, (date, datetime)):
        return True
    return isinstance(v, str) and bool(_DATEISH.match(v))


def classify(columns: list[str], rows: list[dict], *,
             dim_cols: set[str] | None = None,
             measure_cols: set[str] | None = None,
             time_col_hint: str | None = None) -> tuple[list[str], list[str], str | None]:
    """`(measures, dims, time_col)` — bkz. modül docstring'indeki kural sırası.

    🔴🔴 `§VZ` — **OTORİTE YARIM VERİLMİŞTİ: BOYUTA EVET, ÖLÇÜYE HAYIR.**

    Kural 1 *«otorite kazanır»* diyordu ama yalnız `dimensions` için. Bir kolon otoriter
    boyut **değilse**, rolü yine **değerlerinden** çıkarılıyordu — ve çıkarımın koşulu
    `len(vals) > 0`'dı. Yani **değeri NULL olan bir ölçü** hiç değeri olmadığı için
    ölçü sayılamıyor, sessizce **boyuta** düşüyordu.

    ⊙ Canlıda ölçüldü (curl `T` turu, T6): *«geçen ay toplam fire kg»* → o ayda kayıt yok,
    tek satır `{"toplam_fire_kg": None}`:

        kind='table' · time_col='toplam_fire_kg' · dims=['toplam_fire_kg'] · measures=[]

    🔴 Bir **ölçü**, hem boyut hem de **zaman ekseni** ilan edildi. Aynı soru dolu bir ayda
    doğru (`kpi`) cevap veriyordu — yani kusur veriye göre **görünüp kayboluyordu**.

    ⚠ Otorite **kısıtlayıcı değil, kesinleştiricidir**: `cube_query.measures`'ta olan kolon
    kesin ölçüdür; **olmayan** sayısal kolonlar (`_gecen`, `_degisim_yuzde` gibi YoY türevleri)
    eskisi gibi çıkarımla ölçü sayılmaya devam eder — `_roles_from_cube_query`'nin kendi
    gerekçesi budur ve **korunmuştur**.

    *Bir rolü verinin kendisinden çıkarmak, verinin susduğu yerde rolü de susturur.*
    """
    measures: list[str] = []
    dims: list[str] = []
    for c in columns:
        if measure_cols and c in measure_cols:
            # 0) OTORİTE (ÖLÇÜ): fişin kendi ölçüsü — değeri NULL olsa da ölçüdür.
            olcu = True
        elif dim_cols is not None:
            # 1) OTORİTE: cube_query boyutları kesin. Boyut değilse ve sayısalsa ölçü.
            if c in dim_cols:
                olcu = False
            else:
                vals = [r.get(c) for r in rows if r.get(c) is not None]
                olcu = len(vals) > 0 and all(is_num(v) for v in vals)
        elif c.lower() in TIME_NAMES:
            # 2) AD SÖZLÜĞÜ — değer tipinden ÖNCE (bkz. docstring: EXTRACT(MONTH…) tuzağı).
            olcu = False
        else:
            # 3) DEĞER BİÇİMİ.
            vals = [r.get(c) for r in rows if r.get(c) is not None]
            olcu = len(vals) > 0 and all(is_num(v) for v in vals)
        (measures if olcu else dims).append(c)

    time_col: str | None = None
    if time_col_hint and time_col_hint in dims:
        time_col = time_col_hint
    if time_col is None:
        time_col = next((d for d in dims if d.lower() in TIME_NAMES), None)
    if time_col is None:
        time_col = next(
            (d for d in dims
             if rows and all(r.get(d) is None or looks_date(r.get(d)) for r in rows)),
            None,
        )
    return measures, dims, time_col


def measure_authority(cube_query: dict | None) -> set[str] | None:
    """`cube_query` → **KESİN ölçü** kolonları (`§VZ`). Yoksa `None` — çıkarıma düşülür.

    ⚠ Harman ölçüleri **dâhildir**: bir çapraz-küp harmanında ölçüler `cq["measures"]`'da
    değil `cq["blend"][*]["measures"]`'dadır. `§KB` tam olarak bu yüzeyi ıskaladığı için
    *«bu cevap onu içermiyor»* diye yanlış beyan yazmıştı; aynı hatayı burada tekrarlamak
    NULL değerli bir harman ölçüsünü yine boyuta düşürürdü.

    *Bir cevabın ölçüsünü, cevabın yalnız bir parçasına sorarsanız, öbür parçadakini
    kaybedersiniz.*
    """
    if not cube_query:
        return None
    olculer = {str(m) for m in (cube_query.get("measures") or [])}
    for parca in (cube_query.get("blend") or []):
        olculer.update(str(m) for m in ((parca or {}).get("measures") or []))
    return olculer or None


def authority_from_cube_query(cube_query: dict | None) -> tuple[set[str] | None, str | None]:
    """`cube_query` → `(dim_cols, time_col_hint)`. Yoksa `(None, None)` — çıkarıma düşülür.

    Zaman kovası kolonu `<boyut>__<granülerlik>` adıyla döner (ör. `tarih__month`); bu ad
    boyut listesinde YOKTUR, o yüzden ayrıca üretilir — `viz` bunu zaten yapıyordu,
    `interpret` hiç bilmiyordu.
    """
    if not cube_query:
        return None, None
    dims = set(cube_query.get("dimensions") or [])
    ipucu = None
    for td in cube_query.get("timeDimensions") or []:
        ad = td.get("dimension")
        gran = td.get("granularity")
        kova = f"{ad}__{gran}" if ad and gran else ad
        if kova:
            dims.add(kova)
            if ipucu is None:
                ipucu = kova
    return dims, ipucu
