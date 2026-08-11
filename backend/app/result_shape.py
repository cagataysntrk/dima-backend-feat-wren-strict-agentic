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

import numbers
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
    # 🔴🔴 **`Decimal` BİR SAYIDIR — ve bunu tanımamak sessiz bir rol kaymasıydı.**
    #
    # ⊙ Canlıda ölçüldü (`§KN`, `egitim` küpü): motor `toplam_egitim_saati`'ni
    # `Decimal('122')` olarak döndürüyor. `isinstance(v, (int, float))` **False**;
    # `isinstance(v, str)` de **False** → sayı sayılmıyordu. Sonuç: o kolon her yerde
    # bir **boyut** gibi davranıyordu (`classify` bu yüklemi kullanır) ve `§KN`
    # ayrıştırabileceği bir ölçüde **sessizce** susuyordu.
    #
    # ⚠ Ve kusur **ölçüm yüzeyi yüzünden gizlenmişti**: HTTP `/cube` üzerinden bakınca
    # `Decimal` JSON'a `"122"` diye serileşiyor ve **string dalı** onu kurtarıyordu.
    # Yani prob çalışıyor, üretim susuyordu. *Bir kusuru ölçtüğünüz yüzey, üretimin
    # çalıştığı yüzey değilse, ölçtüğünüz şey kusur değil onun gölgesidir.*
    #
    # ⚠ `numbers.Number` **eksi** `complex`. İlk yazımda `numbers.Real` kullandım ve
    # ölçüm çürüttü: `Decimal` `Real`e **kayıtlı değildir** (Python'un bilinçli kararı —
    # ikili kayan noktayla aynı semantiği taşımadığı için). `Number` onu kapsar; tek
    # dışlanması gereken `complex`tir. *Bir soyutlamanın adı, neyi kapsadığını
    # söylemez — kaydı söyler.*
    if isinstance(v, numbers.Number) and not isinstance(v, complex):
        return True
    if isinstance(v, str):
        s = v.strip().replace(".", "").replace(",", ".") if "," in v else v.strip()
        try:
            float(s)
        except (TypeError, ValueError):
            return False
        return True
    return False


def sayi(v: Any) -> float | None:
    """`is_num`'ın **ikizi**: sayıysa değeri, değilse `None`.

    🔴 Bu fonksiyon bir ölçümden doğdu: motor bazı ölçüleri **metin** olarak döndürüyor
    (`toplam_egitim_saati: "316"` — canlıda ölçüldü) ve `isinstance(v, (int, float))`
    süzgeci onları sessizce **eliyordu**. `§KN` bu yüzden ayrıştırabileceği bir ölçüde
    susuyordu: bileşen bulunuyor, değeri okunamıyor, bileşen sayısı ikinin altına
    düşüyor, hiçbir şey söylenmiyordu.

    ⚠ Yeni bir kural yazılmadı: `is_num`'ın **aynı** Türkçe-ondalık disiplini. Depoda
    zaten üç ayrı `_num` var (`interpret` · `statements` · `viz_email`) ve dördüncüsünü
    yazmak `KAT-1`'i büyütmek olurdu; bu, yükleminin **yanına** konmuş hâlidir.

    *Bir veriyi tanıyan yüklem varken, onu okuyanı başka yerde aramak dördüncü bir
    gerçek üretir.*
    """
    if not is_num(v):
        return None
    if isinstance(v, numbers.Number) and not isinstance(v, complex):
        return float(v)
    s = str(v).strip()
    return float(s.replace(".", "").replace(",", ".") if "," in s else s)


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


def belirlenimli_sirala(resp) -> bool:
    """🔴🔴 `§SB` — **SIRASIZ BİR KIRILIM, HER KOŞUMDA BAŞKA BİR RAPORDUR.**

    ⊙ Ölçüldü (curl `CC` turu, CC-5…CC-8): **aynı** `cube_query` dört kez koşuldu, dört
    farklı ilk satır geldi — `RAM-1` · `DİJİTAL BASKI` · `RAM-1` · `FERRARO SANFOR-1`.
    `GROUP BY` sırası motorun iç işidir ve `ORDER BY` yoksa **söz vermez**. Kullanıcı
    açısından bu, aynı soruyu iki kez sorduğunda çubukları yer değiştirmiş bir grafik
    demektir — ve *«en yüksek hangisi»*in cevabı her bakışta başka bir yerdedir.

    ## 🔴 Ve **İLK ÇÖZÜMÜM BİR GERİLEME SATIN ALDI** — kapı yakaladı

    Önce bunu SQL'de yapmıştım (`cube_sql`'e varsayılan bir dış `ORDER BY`). Korpus
    **taban ile birebir** geçti, ama tam süit iki testi kırdı: `dry_plan` **JOIN
    budamayı** kaybediyordu (`parti`de 0 → **3** JOIN, `mizan`da 0 → 2). Yani bir
    sunum kararı, planlayıcının maliyet varsayımını bozuyordu — ve o varsayım
    *«manifesti ilişki-türevi kolonlarla zenginleştirmek, o kolonlar istenmedikçe
    maliyet doğurmaz»* cümlesinin tamamıdır.

    ⚠ Doğru yer **sonuç katmanıdır**: `limit` yokken satırlar zaten **tamamı** çekilmiş
    olur, dolayısıyla burada sıralamak SQL'de sıralamakla **denktir** — ama derleyiciye,
    planlayıcıya ve makbuza hiç dokunmaz.

    *Bir belirlenimsizliği düzeltmek için doğru katmanı seçmek, düzeltmenin kendisinden
    önemlidir: yanlış katman, çözdüğünden pahalı bir şey bozar.*

    Yüklem — **hiçbir şey seçmez, yalnız sıralar**:
      • `limit` **yok** → hangi satırların döndüğü değişemez
      • kullanıcının kendi `order`ı **yok** → onu ezmeyiz
      • `timeDimensions` **yok** → zaman serisi kronolojik kalır
      • `dimensions` **var** ve sayısal bir ölçü kolonu **var** → sıralanacak şey var

    Döner: sıralandı mı (çağıran ize yazabilir).
    """
    cq = getattr(resp, "cube_query", None) or {}
    res = getattr(resp, "result", None)
    if not isinstance(cq, dict) or res is None:
        return False
    if cq.get("limit") or cq.get("order") or cq.get("timeDimensions"):
        return False
    if not cq.get("dimensions") or not (cq.get("measures") or []):
        return False
    rows = getattr(res, "rows", None)
    if not isinstance(rows, list) or len(rows) < 2:
        return False
    olcu = str(cq["measures"][0])
    # ⚠ `is not None` — `sayi()` sıfır için `0.0` döner ve bir doğruluk sınavında
    # **yanlış** okunur. Sıfırlı bir kırılım (ölçülen sıradan bir hâl) sıralanmadan
    # kalırdı ve kusur tam da o raporlarda sürerdi.
    if not all(isinstance(r, dict) and sayi(r.get(olcu)) is not None for r in rows):
        return False
    try:
        rows.sort(key=lambda r: sayi(r[olcu]) or 0.0, reverse=True)
    except Exception:                    # noqa: BLE001 — sıra bir süs, cevap değil
        return False
    return True
