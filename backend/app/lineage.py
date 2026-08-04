"""FAZ 1.6 — **KOLON KÖKENİ.** *"Bu sayı nereden geldi?"* — LLM'siz, deterministik.

## Neden bu modül var — ve neden `answer.koken()`'in yerine geçmiyor

`answer.koken()` **ilişki** düzeyinde çalışıyor: *hangi kırılım hangi join'den geldi*.
Cevaplayamadığı soru **kolon** düzeyinde: *"bu sayı hangi tablonun hangi kolonundan ve
hangi dönüşümle üretildi?"* İkisi farklı sorular; birini ötekinin yerine koymak, bir
kanıtı **başka bir kanıtın adıyla** sunmak olurdu.

## Neden yeni bir BEYAN yazılmıyor

Dönüşüm tipi **manifestten türetilir** — ölçü `expression`'ı zaten orada:

| ifade | `donusum_tipi` |
|---|---|
| `SUM(x)` · `COUNT(*)` | `toplam` |
| `AVG(x)` · `a / b` · `… * 100` | `oran` |
| `CASE WHEN …` · `FILTER (WHERE …)` | `filtre` |
| düz kolon adı | `dogrudan` |
| ilişkiden gelen boyut (`dimension_origin`) | `birlestirme` |
| yukarıdakilerin hiçbiri | `turetilmis` |

Yeni bir `lineage:` alanı beyan ettirmek, bu deponun **defalarca ölçtüğü** hatayı
tekrarlardı: *ikinci bir kaynak açmak*. Katalog zaten cevabı taşıyor; sorulmuyordu.

## 🔴 Discovery ham SQL'i → `bilinmiyor`

Ham SQL'de `cube_query` **yoktur**; köken türetilemez. `"bilinmiyor"` yazmak bir eksiklik
değil bir **beyandır** — ve `None` ile aynı şey **değildir**: `None` *"hiç sorulmadı"*,
`"bilinmiyor"` *"soruldu, cevap yok"*. Bu deponun `⊘ ÖLÇÜLEMEDİ` üçüncü hâliyle aynı
disiplin.

## ⚠ ÜÇÜNCÜ ŞABLON CÜMLE BU TURDA GELMEDİ

Yol haritası üç cümle istiyor:
1. *"Bu sayı `<tablo>.<kolon>`'dan geldi."* ✅
2. *"`<boyut>` = `<değer>` filtresiyle daraltıldı."* ✅
3. *"Bir üst-akış tablo `<N>` gün önce değişti."* ⏳ **FAZ 1.7**

Üçüncüsü **tazelik** verisi ister (`SyncState.last_synced_at`) ve o veri bugün `/ask`'e
**hiç ulaşmıyor** — ölçüldü: `grep -rl freshness backend/app/` → **0**. Uydurma bir gün
sayısı yazmak, `pvm:`/`target:` eşleştirmesinde **reddedilen** şeyin aynısı olurdu:
**güvenle yanlış** bir sayı, ve kimse onu sorgulamaz. Cümle `1.7` ile gelir.
"""

from __future__ import annotations

import re
from typing import Any

#: Altı dönüşüm tipi — OpenLineage'ın **iç temsili benimsendi** (kütüphane değil).
DONUSUM_TIPLERI = ("dogrudan", "toplam", "oran", "filtre", "birlestirme", "turetilmis")

#: Köken sorulamayan yol için beyan. `None` ile **aynı şey değildir**.
BILINMIYOR = "bilinmiyor"

_TOPLAM = re.compile(r"\b(sum|count|min|max)\s*\(", re.I)
_ORAN = re.compile(r"\b(avg|median|stddev)\s*\(|/|\*\s*100\b", re.I)
_FILTRE = re.compile(r"\bcase\s+when\b|\bfilter\s*\(\s*where\b|\bwhere\b", re.I)
_DUZ = re.compile(r"^[a-z_][a-z0-9_]*$", re.I)


def donusum_tipi(ifade: str | None, *, iliskiden: bool = False) -> str:
    """Ölçü/boyut ifadesinden dönüşüm tipi — **saf fonksiyon**.

    Sıra **önemlidir ve ölçüldü**: `ROUND(AVG(durus_dakika),1)` hem `AVG` hem parantez
    taşır; `filtre` en dışta sorulur çünkü `CASE WHEN SUM(...)` bir **filtreli toplamdır**
    ve kullanıcıya söylenmesi gereken şey **daraltma**dır — toplam olduğu zaten görünür.
    """
    if iliskiden:
        return "birlestirme"
    s = (ifade or "").strip()
    if not s:
        return "turetilmis"
    if _FILTRE.search(s):
        return "filtre"
    if _ORAN.search(s):
        return "oran"
    if _TOPLAM.search(s):
        return "toplam"
    if _DUZ.match(s):
        return "dogrudan"
    return "turetilmis"


def _cube(schema: dict, ad: str | None) -> dict | None:
    return next((c for c in (schema.get("cubes") or []) if c.get("name") == ad), None)


def kolon_kokeni(schema: dict, cube_query: dict | None) -> dict[str, Any] | None:
    """Cevabın **kolon düzeyi** köken kaydı — ya da `None`/`bilinmiyor`.

    Döner:
    ```
    {"olculer": [{"ad", "ifade", "donusum_tipi", "kaynak", "maskelendi"}],
     "boyutlar": [{"ad", "donusum_tipi", "kaynak"}],
     "filtreler": [{"boyut", "deger"}]}
    ```

    🔴 **`maskelendi` `sensitivity.classify`'dan gelir — TEK SAHİP.** İkinci bir hassasiyet
    kuralı yazmak, `pii.py` · CLS (`1.2a`) · köken üçlüsünün **ayrışması** demekti: aynı
    kolon bir yerde maskeli, ötekinde *"maskelenmedi"* diye raporlanırdı.
    """
    if not cube_query:
        return None
    cube = _cube(schema, cube_query.get("cube"))
    if cube is None:
        return None
    from app.sensitivity import classify

    base = str(cube.get("base_object") or cube.get("baseObject") or "")
    olcu_ifade = {m.get("name"): m.get("expression")
                  for m in (cube.get("measures") or []) if isinstance(m, dict)}
    kokenler = cube.get("dimension_origin") or {}

    olculer = []
    for ad in cube_query.get("measures") or []:
        ifade = olcu_ifade.get(ad)
        olculer.append({
            "ad": ad,
            "ifade": ifade,
            "donusum_tipi": donusum_tipi(ifade),
            "kaynak": base,
            "maskelendi": classify(None, column_name=ad) != "normal",
        })

    boyutlar = []
    for ad in cube_query.get("dimensions") or []:
        k = kokenler.get(ad) or {}
        boyutlar.append({
            "ad": ad,
            "donusum_tipi": donusum_tipi(ad, iliskiden=bool(k)),
            "kaynak": str(k.get("model") or k.get("via") or base),
        })

    filtreler = [
        {"boyut": f.get("dimension"), "deger": f.get("value")}
        for f in (cube_query.get("filters") or [])
        if isinstance(f, dict) and f.get("dimension") and f.get("value") is not None
    ]
    if not (olculer or boyutlar or filtreler):
        return None
    return {"olculer": olculer, "boyutlar": boyutlar, "filtreler": filtreler}


def cumleler(koken: dict[str, Any] | str | None) -> list[str]:
    """Köken kaydı → **LLM'siz şablon cümleler** (KD-13: teknik graf gösterilmez).

    🔴 **Teknik graf kullanıcıya gösterilmez.** `KD-13`'ün kuralı: bir köken grafiği
    geliştirici artefaktıdır; kullanıcının sorduğu soru *"bu sayı nereden geldi"*dir ve
    cevabı **bir cümledir**. Grafiği basmak, `ReportCard`'ın `D3`'te düzeltilen
    *"geliştirici katmanı son kullanıcıda"* kusurunu tekrarlardı.

    ⚠ Üçüncü cümle (*"bir üst-akış tablo N gün önce değişti"*) **FAZ 1.7**'de gelir:
    tazelik verisi bugün `/ask`'e ulaşmıyor ve uydurma bir gün sayısı **güvenle yanlış**
    olurdu.
    """
    if koken == BILINMIYOR:
        return ["Bu cevap ham SQL ile üretildi; kolon kökeni **bilinmiyor**."]
    if not isinstance(koken, dict):
        return []
    out: list[str] = []
    for m in koken.get("olculer") or []:
        kaynak = m.get("kaynak") or "?"
        tip = m.get("donusum_tipi")
        ek = {"toplam": " (toplanarak)", "oran": " (oranlanarak)",
              "filtre": " (daraltılarak)", "birlestirme": " (birleştirilerek)",
              "turetilmis": " (türetilerek)"}.get(tip, "")
        cumle = f"Bu sayı `{kaynak}.{m.get('ad')}`'dan geldi{ek}."
        if m.get("maskelendi"):
            cumle += " Değerler **maskeli** gösteriliyor."
        out.append(cumle)
    for f in koken.get("filtreler") or []:
        out.append(f"`{f.get('boyut')}` = `{f.get('deger')}` filtresiyle daraltıldı.")
    return out
