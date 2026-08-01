"""Deterministik görselleştirme önerisi — grafik/tablo/pivot KARARI sonuç ŞEKLİNDEN.

Karar backend semantik katmanda (ADR-0024): kolonları veri-tipine sınıflar (N/O/Q/T —
Stevens ölçekleri), kanal atar (Bertin/expressiveness), Mackinlay "Show Me" tablosuyla mark
seçer, Cleveland–McGill algısal sıralamasına uyar. LLM yok — saf kural, tekrarlanabilir.
Gerekçe + kaynaklar: docs/research/viz-oneri-standartlari-2026-07.md.

SUNUM (echarts option, renk, soluk sütun, responsive, kullanıcı override/toggle) FE'de KALIR;
burası yalnız TİP + ROL üretir (`VizSpec`). FE `data.viz` gelince yerel `analyze()` yerine bunu
kullanır; `view_hint` (açık NL niyeti) + kullanıcı toggle bu otomatik kararın ÜSTÜNE biner.

İki katman:
  • analyze()   — sonuç ŞEKLİNDEN taban karar (kpi/bar/line/heatmap/facet/table). FE chart.ts
                  analyze()'in birebir portu; mevcut davranışı KORUR (regresyonsuz geçiş).
  • recommend() — analyze üstüne STANDART katmanı: veri-tipi + BİRİM farkındalığı ile yeni mark'lar
                  (facet_measure / scatter / stacked / pivot) ve çok-birim politikası (§3).

KOPYA-MANTIK DURUMU (31 Temmuz 2026 — bağımsız araştırmayla denetlendi, `docs/research/
viz-chart-drift-2026-07-31.md` YERİNE burada özetlendi): chart.ts'in yerel `analyze()`'i BU
dosyanın `analyze()`'iyle hâlâ birebir eşdeğer (drift YOK) ama `recommend()`'in zenginleştirme
katmanını (scatter/facet_measure/stacked/pivot/partition) HİÇ taşımıyor — yani FE yereline
her düştüğünde kullanıcı GERÇEKTEN daha zayıf bir karar görüyor (varsayımsal değil, ölçüldü).
Kapatılan iki canlı tetikleyici: (1) `/ask`'in `_attach_viz`'i artık gerçek units/lower_set
kullanıyor + `recommend()` patlarsa None yerine çıplak `analyze()`'e düşüyor (ask.py), (2)
sohbet resume'i (`/conversations/{id}`) artık `viz`'i HER seferinde TAZE hesaplıyor (`result`
sabit kalır, yalnız sunum kararı yenilenir) — önceden donmuş/eski bir `viz` kalıcı olarak FE
yereline zorluyordu. KASITLI OLARAK AÇIK bırakılan TEK durum: `ResultView.tsx`'in facet
tek-panel drill-down'ı (kullanıcı bir facet panelini açtığında o ALT-KÜME satır için yerel
`analyze()` çağrılır) — backend bu ad-hoc alt-kümeyi hiç görmediğinden (yalnız tam sonuç
kümesi için `viz` hesaplanır) burada yerel bir yeniden-sınıflandırma mimari olarak gerekli;
bilinçli, dar kapsamlı bir istisna (genel bir "yedek" değil) — bkz. chart.ts'teki eşlenik not.
"""

from __future__ import annotations

import re
from typing import Any

# --- veri-tipi sinyalleri (Stevens ölçekleri) -------------------------------
# SÜREKLİ zaman (trend → çizgi). "gün/vardiya" gibi DÖNGÜSEL kategorikler kasıtlı YOK.
_TIME_NAMES = {
    "donem", "dönem", "tarih", "ay", "hafta", "period",
    "yil", "yıl", "year", "ceyrek", "çeyrek",
}
_DATEISH = re.compile(r"^\d{4}-\d{2}")
# Sıralı (ordinal) kategori kümeleri — çizgi/sıralama bunlarda anlamlı (N'de değil).
_WEEKDAY = {"pzt", "sal", "çar", "car", "per", "cum", "cmt", "paz"}
_SIZES = {"xs", "s", "m", "l", "xl", "xxl"}

# İNTENSİF (yoğunluk/oran) ölçüler additive DEĞİLDİR → yığma/pay grafiği YANLIŞ olur
# (ortalama %'leri toplamak anlamsız). Birim "%" ya da ad deseni oran/ortalama ise intensif.
_INTENSIVE_NAME = re.compile(r"(_yuzde|_orani?|_ort|_oran|oee|verimlilik|haslik|_de|yogunluk)$", re.I)
# Birim yedeği (schema()'nın "units" dict'i yoksa) — kaba eşleme; gerçek birim MDL'den gelir.
_UNIT_RX: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(_yuzde$|_orani?$|oee|haslik|verimlilik)", re.I), "%"),
    (re.compile(r"(tl$|_tl_|_tl$|ciro|maliyet|tutar|fiyat|gelir|gider|bakiye|kar$|karlilik)", re.I), "₺"),
    (re.compile(r"(_kg$|agirlik|tonaj|fire_kg)", re.I), "kg"),
    (re.compile(r"(kwh|elektrik)", re.I), "kWh"),
    (re.compile(r"(_l$|litre|_su_|water)", re.I), "L"),
    (re.compile(r"(_dk$|dakika|sure|durus)", re.I), "dk"),
    (re.compile(r"tep$", re.I), "tep"),
]


def _is_num(v: Any) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False
    return False


def _looks_date(v: Any) -> bool:
    return isinstance(v, str) and bool(_DATEISH.match(v))


def _card(rows: list[dict], c: str) -> int:
    """Bir kolonun ayrık (distinct) değer sayısı."""
    seen: set = set()
    for r in rows:
        try:
            seen.add(r.get(c))
        except TypeError:
            seen.add(str(r.get(c)))
    return len(seen)


def _unit_of(col: str, units: dict[str, str] | None) -> str:
    """Ölçünün birimi: MDL metadata (schema()'nın "units" dict'i) öncelik, yoksa regex yedeği,
    yoksa boş (birimsiz/sayım). Boş birim de AYRI birim sayılır (çok-birim kuralı için)."""
    if units and col in units and units[col]:
        return str(units[col])
    for rx, u in _UNIT_RX:
        if rx.search(col):
            return u
    return ""


def _additive(col: str, unit: str) -> bool:
    """Ölçü toplanabilir (extensive) mi? Yığma/pay grafiği yalnız additive'de geçerli."""
    if unit == "%":
        return False
    return not bool(_INTENSIVE_NAME.search(col))


# FE ChartKind ile hizalı. "table" = FE'nin "none"u (grafik değil → tablo).
VizKind = str


def analyze(
    columns: list[str],
    rows: list[dict],
    dim_cols: set[str] | None = None,
    time_col_hint: str | None = None,
) -> dict[str, Any]:
    """chart.ts analyze()'in portu — sonuç şeklinden TABAN viz kararı.

    Döndürür: {kind, measures, dims, time_col, primary_dim, heat, heat_any, facet}.
    recommend() bunun üstüne standart katmanını uygular.

    Rol OTORİTESİ (opsiyonel): `dim_cols`/`time_col_hint` cube_query'den geldiğinde BOYUT
    kolonları kesindir → (a) sayısal-değerli boyutlar (vardiya no, yıl) yanlışlıkla ölçü sanılmaz,
    (b) türetilmiş ölçüler (YoY `_gecen`/`_degisim_yuzde` gibi cube_query.measures'ta OLMAYAN ama
    sayısal kolonlar) doğru şekilde ÖLÇÜ sayılır, (c) zaman kovaları (tarih__month) kaçmaz. Boyut
    olmayan sayısal kolon = ölçü; boyut olmayan sayısal-olmayan kolon = boyut (güvenli). Verilmezse
    (yüklenen serbest veri) değer biçiminden çıkarıma düşülür (FE analyze() paritesi)."""
    measures: list[str] = []
    dims: list[str] = []
    for c in columns:
        if dim_cols is not None:
            # Otoriter boyut → boyut; değilse sayısalsa ölçü (türetilmiş YoY ölçüleri dahil).
            if c in dim_cols:
                is_measure = False
            else:
                vals = [r.get(c) for r in rows if r.get(c) is not None]
                is_measure = len(vals) > 0 and all(_is_num(v) for v in vals)
        elif c.lower() in _TIME_NAMES:
            # Otoriter dim_cols YOK (LLM/Discovery yolu, cube_query=None) — ama kolon adı
            # bilinen bir zaman/dönem adıysa (ay/yıl/çeyrek/...) DEĞER TİPİNDEN BAĞIMSIZ
            # boyut say. Küp yolunda bu kolonlar HER ZAMAN metin/tarih string'idir; LLM'in
            # ürettiği SQL aynı anlamı SAYISAL döndürebilir (ör. EXTRACT(MONTH FROM ...) →
            # 1..12) — isim eşleşmesi olmadan bu, "tüm değerler sayısal" testiyle yanlışlıkla
            # İKİNCİL bir ölçü sayılır, zaman ekseni tamamen kaybolur (kind "table"a düşer).
            is_measure = False
        else:
            vals = [r.get(c) for r in rows if r.get(c) is not None]
            is_measure = len(vals) > 0 and all(_is_num(v) for v in vals)
        (measures if is_measure else dims).append(c)

    time_col: str | None = None
    if time_col_hint and time_col_hint in dims:
        time_col = time_col_hint
    if time_col is None:
        for d in dims:
            if d.lower() in _TIME_NAMES:
                time_col = d
                break
    if time_col is None:
        for d in dims:
            if len(rows) > 0 and all(
                (r.get(d) is None or _looks_date(r.get(d))) for r in rows
            ):
                time_col = d
                break

    heat: dict[str, str] | None = None
    if len(dims) >= 2 and len(measures) >= 1 and len(rows) >= 4:
        for i in range(len(dims)):
            if heat:
                break
            for j in range(i + 1, len(dims)):
                if heat:
                    break
                ca = _card(rows, dims[i])
                cb = _card(rows, dims[j])
                prod = ca * cb
                if (
                    ca > 1 and cb > 1 and min(ca, cb) >= 3
                    and prod <= len(rows) * 1.6 and prod >= len(rows) * 0.5
                ):
                    heat = (
                        {"row": dims[i], "col": dims[j]} if ca <= cb
                        else {"row": dims[j], "col": dims[i]}
                    )

    heat_any: dict[str, str] | None = heat
    if not heat_any and len(dims) >= 2 and len(measures) >= 1:
        multi = sorted(
            [d for d in dims if _card(rows, d) > 1], key=lambda d: _card(rows, d)
        )
        if len(multi) >= 2:
            heat_any = {"row": multi[0], "col": multi[-1]}

    if time_col is not None:
        primary_dim: str | None = time_col
    elif dims:
        primary_dim = sorted(dims, key=lambda d: _card(rows, d), reverse=True)[0]
    else:
        primary_dim = None

    facet: dict[str, str] | None = None
    if len(dims) == 3 and len(measures) >= 1:
        if time_col:
            rest = sorted(
                [d for d in dims if d != time_col], key=lambda d: _card(rows, d)
            )
            a, b = rest[0], rest[1]
            if _card(rows, a) <= 6:
                facet = {"dim": a, "x": time_col, "series": b}
        else:
            srt = sorted(dims, key=lambda d: _card(rows, d))
            fd, sd, xd = srt[0], srt[1], srt[2]
            if _card(rows, fd) <= 6:
                facet = {"dim": fd, "x": xd, "series": sd}

    kind: VizKind = "table"
    if len(rows) == 1 and len(measures) >= 1 and len(dims) <= 1:
        kind = "kpi"
    elif len(measures) == 0:
        kind = "table"
    elif len(dims) == 3 and facet:
        kind = "facet"
    elif len(dims) > 2:
        kind = "table"
    elif time_col and len(measures) >= 1:
        kind = "line"
    elif heat:
        kind = "heatmap"
    elif primary_dim and len(measures) >= 1:
        kind = "bar"

    return {
        "kind": kind,
        "measures": measures,
        "dims": dims,
        "time_col": time_col,
        "primary_dim": primary_dim,
        "heat": heat,
        "heat_any": heat_any,
        "facet": facet,
    }


# --- STANDART KATMAN: veri-tipi + birim farkındalığı ------------------------

def _roles_from_cube_query(
    cube_query: dict | None, columns: list[str]
) -> tuple[set[str] | None, str | None]:
    """cube_query'den OTORİTER BOYUT kolonları + zaman kolonu. Boyutları (measures'ı DEĞİL)
    otoriter alırız: boyut olmayan sayısal kolon = ölçü. Böylece (a) sayısal boyutlar (vardiya no)
    boyut kalır, (b) türetilmiş ölçüler (YoY `_gecen`/`_degisim_yuzde` — cube_query.measures'ta
    YOK ama sayısal) doğru şekilde ölçü sayılır → YoY grafiği yanlışlıkla panel/facet'e düşmez.
    timeDimensions kovası `{dimension}__{granularity}` kolon adına çözülür (boyut + zaman ipucu)."""
    if not cube_query:
        return None, None
    colset = set(columns)
    dim_cols = {d for d in (cube_query.get("dimensions") or []) if d in colset}
    time_hint: str | None = None
    for td in (cube_query.get("timeDimensions") or []):
        dim = td.get("dimension")
        gran = td.get("granularity")
        for cand in (f"{dim}__{gran}" if gran else None, dim):
            if cand and cand in colset:
                time_hint = cand
                dim_cols.add(cand)
                break
        if time_hint:
            break
    return dim_cols, time_hint


def recommend(
    result: dict | None,
    units: dict[str, str] | None = None,
    lower_set: list[str] | set[str] | None = None,
    cube_query: dict | None = None,
) -> dict[str, Any] | None:
    """QueryResult ({columns, rows}) → VizSpec. Sonuç yok/boşsa None.

    analyze() taban kararını alır, üstüne Show Me + çok-birim politikasını (§3) uygular:
      • ≥3 farklı birim ölçü + ortak eksen → facet_measure (ölçüye-göre small multiples)
      • 2 birim → dual_axis (FE combo zaten böler)
      • 2 ölçü + kimlik-boyutu (kard=satır, ≥8) + zamansız → scatter (korelasyon)
      • zaman/kategori + orta-kard additive seri → stacked
      • 2+ kategorik boyut grafiklenemiyor → pivot
      • tek boyut + additive ölçü → partition (pie≤6 / treemap) FE toggle olarak sunulur
      • tek boyut (kard≥4) + tek ölçü → reference_line (ortalama, aynı bar grafiğinde)
    """
    if not result:
        return None
    columns = result.get("columns") or []
    rows = result.get("rows") or []
    if not columns:
        return None

    dim_cols, time_hint = _roles_from_cube_query(cube_query, columns)
    spec = analyze(columns, rows, dim_cols=dim_cols, time_col_hint=time_hint)
    measures: list[str] = spec["measures"]
    dims: list[str] = spec["dims"]
    time_col: str | None = spec["time_col"]
    primary_dim: str | None = spec["primary_dim"]

    umap = {m: _unit_of(m, units) for m in measures}
    unit_count = len({u for u in umap.values()})
    cat_dims = [d for d in dims if d != time_col]
    # bar/line'da renk-serisi: ikinci (zaman-dışı) boyut
    shared_x = time_col or (primary_dim if len(dims) == 1 else None)
    series_dim = next((d for d in dims if d != shared_x), None) if shared_x else None
    # DÖNEMSEL KIYAS (YoY/MoM): türetilmiş ölçüler (baz + `_gecen` + `_degisim_yuzde`) bir
    # KIYAS AİLESİDİR — birbirinden bağımsız ölçü değil. Enhancement katmanı (scatter/facet_measure/
    # pivot/partition) bunları YANLIŞ yorumlar (ciro vs ciro_gecen serpme, YoY bar'a pie önerisi).
    # Kıyas varsa taban kararı (bar/line combo) KORUNUR; FE combo `_gecen` soluk sütun +
    # `_degisim_yuzde` ikincil çizgi olarak render eder.
    has_compare = bool(cube_query and cube_query.get("compare")) or any(
        m.endswith(("_gecen", "_degisim_yuzde")) for m in measures
    )

    spec.update({
        "units": umap,
        "unit_count": unit_count,
        "series_dim": series_dim,
        "facet_measure": None,
        "scatter": None,
        "pivot": None,
        "stackable": False,
        "partition": False,
        "dual_axis": False,
        "reference_line": None,
        "alternatives": [],
        "table_mode": "table",
    })

    kind = spec["kind"]

    # (A) SCATTER (korelasyon): 2+ ölçü, zaman yok, TEK kimlik-boyutu (kard=satır) yüksek kard.
    #     Az kategoride (≤~12) gruplu bar daha okunur; çok varlıkta (≥8) 2-ölçü serpme daha iyi.
    #     Çok-birim (B) küçük-multiple'dan ÖNCE bakılır: kimlik-boyutu paylaşılan-eksen DEĞİL,
    #     nokta kimliğidir → korelasyon serpmesi doğru mark (small multiples değil).
    if (
        kind in ("bar", "table")
        and not has_compare
        and time_col is None
        and len(measures) >= 2
        and len(cat_dims) == 1
        and _card(rows, cat_dims[0]) == len(rows)
        and len(rows) >= 8
    ):
        spec["kind"] = kind = "scatter"
        sc = {"x": measures[0], "y": measures[1], "color": cat_dims[0]}
        if len(measures) >= 3:
            sc["size"] = measures[2]
        spec["scatter"] = sc

    # (B) ÇOK-BİRİM (§3): tek/çift eksende yalnız 1-2 birim; ≥3 → ölçüye-göre small multiples.
    #     Yalnız TEK kategorik/zaman eksende çok-ölçü senaryosunda (seri boyutu YOKKEN) geçerli —
    #     seri boyutu varsa ölçü zaten teke düşer (iki seri kaynağı bir arada olmaz).
    multi_measure_x = kind in ("bar", "line") and shared_x is not None and series_dim is None
    if multi_measure_x and len(measures) >= 2:
        if unit_count >= 3 and not has_compare:
            spec["kind"] = kind = "facet_measure"
            spec["facet_measure"] = {"measures": measures, "x": shared_x, "series": None}
        elif unit_count == 2:
            # BİLİNÇLİ KARAR (Madde 10 değerlendirmesi, 1 Ağustos 2026): bu bayrak FE'de
            # OKUNMUYOR (chart.ts yalnız parse eder, hiçbir yerde tüketmez) — FE kendi
            # `comboSeriesDim` sezgisiyle (series_dim YOKKEN) AYNI durumu BAĞIMSIZ tespit
            # edip birincil-bar+ikincil-çizgi kombosunu ZATEN doğru üretiyor (chart.ts'teki
            # "KOMBO" bloğu). Bilgi doğru/zararsız — kaldırmak public viz sözleşmesini
            # (AskResponse.viz) gereksiz kırar; entegre etmek FE'de zaten çalışan combo
            # mantığını YENİDEN İCAT etmek olurdu. Bilerek dokunulmuyor.
            spec["dual_axis"] = True
    elif (
        kind in ("bar", "line") and shared_x is not None and series_dim is not None
        and len(measures) >= 2 and unit_count >= 2 and not has_compare
    ):
        # Madde 10 (1 Ağustos 2026): kırılım boyutu (series_dim) VARKEN çok-birim ölçüler
        # ÖNCEDEN HİÇBİR ayırma mekanizmasından geçmiyordu — combo (chart.ts) VE dual_axis
        # (yukarıdaki dal) İKİSİ de `series_dim is None` şartıyla sınırlıydı; kırılımlı
        # 2+-birim durumu (ör. "ay VE makine bazında oee ve duruş dakikası") iki farklı
        # birimi TEK eksende eziyordu. Var olan facet_measure (ölçüye-göre panel) diline
        # `series` alanını doldurarak GENİŞLETİLİYOR — yeni bir görsel dil İCAT edilmiyor.
        spec["kind"] = kind = "facet_measure"
        spec["facet_measure"] = {"measures": measures, "x": shared_x, "series": series_dim}

    # (C) STACKED (kompozisyon): x (zaman/kategori) + renk-serisi + TEK additive ölçü.
    #     Az seri (≤4) → gruplu (doğrudan kıyas okunur); orta seri (5..8) additive → yığılı.
    if kind in ("bar", "line") and series_dim is not None and len(measures) == 1:
        m0 = measures[0]
        if _additive(m0, umap.get(m0, "")):
            spec["stackable"] = True
            sc_card = _card(rows, series_dim)
            if 4 < sc_card <= 8:
                spec["kind"] = kind = "stacked"

    # (D) PIVOT: 2+ kategorik boyut grafiklenemiyor (heatmap değil / çok-ölçü), ya da 3+ boyut
    #     facet'lenemedi. Eski "table"yı okunur satır×sütun×hücre yapısına yükseltir.
    if not has_compare and (
        (kind == "table" and len(cat_dims) >= 2 and len(measures) >= 1)
        or (kind == "heatmap" and len(measures) >= 2)
    ):
        srt = sorted(cat_dims, key=lambda d: _card(rows, d))
        rows_dim = [srt[0]] if len(srt) >= 1 else []
        cols_dim = [srt[1]] if len(srt) >= 2 else []
        spec["kind"] = kind = "pivot"
        spec["table_mode"] = "pivot"
        spec["pivot"] = {"rows": rows_dim, "cols": cols_dim, "measures": measures}

    # (E) PARTITION (pay): TEK kategorik boyut + TEK additive ölçü → pie(≤6)/treemap FE toggle olarak.
    #     Cleveland–McGill: pay grafiği bar'dan zayıf → OTOMATİK bar KALIR, pay yalnız öneri/hint.
    #     Tek ölçü şartı: çok-ölçü/YoY bar'da pay grafiği anlamsız (birden çok ölçünün payı olmaz).
    if kind == "bar" and len(cat_dims) == 1 and len(measures) == 1 and series_dim is None:
        m0 = measures[0]
        if _additive(m0, umap.get(m0, "")):
            card = _card(rows, cat_dims[0])
            spec["partition"] = True
            spec["alternatives"] = ["pie"] if card <= 6 else ["treemap"]

    # (F) REFERANS ÇİZGİSİ (Madde 11 kalan kısım, §E, 1 Ağustos 2026): TEK kategorik boyut +
    #     TEK ölçü + orta-yüksek kardinalite (kişi/varlık bazlı karşılaştırma — "personelin
    #     OEE üzerindeki etkisi" gibi) → ölçünün ORTALAMASI yatay referans çizgisi olarak AYNI
    #     bar grafiğinde. Kim ortalamanın üstünde/altında ANINDA görülür — Cleveland-McGill'i
    #     bozmaz (bar KALIR), yalnız bir ANNOTASYON ekler. `_additive` şartı YOK (yüzde/oran
    #     ölçülerin de ortalaması anlamlıdır — additive yalnız TOPLAMA/yığma için gerekli, sade
    #     ORTALAMA için değil). 2+ ölçü durumu (İKİNCİL ölçü referans) mevcut combo (chart.ts)
    #     mekanizmasınca ZATEN karşılanıyor — bu yalnız TEK-ölçü boşluğunu kapatır.
    if kind == "bar" and len(cat_dims) == 1 and len(measures) == 1 and series_dim is None:
        m0 = measures[0]
        card = _card(rows, cat_dims[0])
        if card >= 4:
            vals = [r.get(m0) for r in rows if _is_num(r.get(m0))]
            if vals:
                spec["reference_line"] = {
                    "kind": "average", "measure": m0,
                    "value": round(sum(float(v) for v in vals) / len(vals), 4),
                }

    # normalize: lower_set'i (FE ısı paleti yönü) taşı
    if lower_set:
        spec["lower_set"] = sorted(lower_set)
    return spec
