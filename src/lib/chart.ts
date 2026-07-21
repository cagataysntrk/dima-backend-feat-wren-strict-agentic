// Sonuç tablosunun ŞEKLİNDEN otomatik grafik tipi çıkarımı + ECharts option üretimi.
// Desteklenen: KPI (tek satır), bar, line (zaman), pie, heatmap (2 boyut × ölçü matrisi).
// Tüm sayılar birim-farkında biçimlendirilir (₺, kg, L, kWh, %, dk...) — bkz. format.ts.

import type { EChartsOption } from "echarts";
import type { QueryResult, Row } from "./types";
import { fmtAxis, fmtTemporal, fmtValue, unitSuffix } from "./format";

// Eksen ETİKETİ: zaman kovalarını okunur yap ("Oca 2026") — sıralama ham değerle kalır.
const axisLabel = (v: string, col: string | null) => (col ? fmtTemporal(v, col) ?? v : v);

export type ChartKind = "kpi" | "bar" | "line" | "pie" | "heatmap" | "facet" | "none";

// SÜREKLI zaman (trend → çizgi). "gün/vardiya" gibi DÖNGÜSEL kategorikler kasıtlı olarak
// burada YOK — onlar ısı haritasına gitsin (ör. vardiya × haftanın günü). Gerçek tarih
// kolonları zaten değer biçiminden (looksDate) yakalanır.
const TIME_NAMES = new Set(["donem", "dönem", "tarih", "ay", "hafta", "period", "yil", "yıl", "year", "ceyrek", "çeyrek"]);
const PALETTE = ["#4F8CFF", "#22C55E", "#F59E0B", "#EF4444", "#A855F7", "#06B6D4", "#EC4899", "#84CC16"];
const HEAT = ["#EF4444", "#F59E0B", "#FDE047", "#84CC16", "#22C55E"]; // düşük→yüksek (kırmızı→yeşil)
// YÖN SEMANTİĞİ: bu metriklerde YÜKSEK KÖTÜDÜR (fire, duruş, sapma, maliyet, tüketim,
// yoğunluk) → ısı haritası paleti ters çevrilir (yüksek=kırmızı). Varsayılan: yüksek=iyi.
const LOWER_IS_BETTER = /fire|durus|sapma|maliyet|tuketim|yogunluk|su_|enerji/i;
const heatPalette = (measure: string): string[] =>
  LOWER_IS_BETTER.test(measure) ? [...HEAT].reverse() : HEAT;
const AVG = "∑ Ort.";

const isNum = (v: unknown) =>
  typeof v === "number" || (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v)));
const num = (v: unknown) => (typeof v === "number" ? v : Number(v));
const looksDate = (v: unknown) => typeof v === "string" && /^\d{4}-\d{2}/.test(v);
const distinct = (rows: Row[], c: string) => [...new Set(rows.map((r) => r[c]))];
const fmtCat = (v: unknown) => (looksDate(v) ? String(v).slice(0, 10) : String(v ?? "—"));
const mean = (a: number[]) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);

// Kanonik haftanın-günü sırası — kategori değerleri gün ise kronolojik sırala (Pzt→Paz),
// değilse alfabetik (tarih YYYY-MM zaten kronolojik). Kaynak cube ya da LLM olsun, her yerde.
const WEEKDAY_ORDER = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
const orderCats = (vals: string[]): string[] =>
  vals.length && vals.every((v) => WEEKDAY_ORDER.includes(v))
    ? [...vals].sort((a, b) => WEEKDAY_ORDER.indexOf(a) - WEEKDAY_ORDER.indexOf(b))
    : [...vals].sort();

export interface Analysis {
  kind: ChartKind;
  measures: string[];
  dims: string[];
  timeCol: string | null;
  primaryDim: string | null;
  heat: { row: string; col: string } | null;
  // Açık istek için serbest eşleme: "ısı haritası olarak ver" min-eksen≥3 otomatik
  // kuralına takılmamalı (kural yalnız OTOMATİK tip seçimi içindir; log 2026-07-20).
  heatAny: { row: string; col: string } | null;
  // 3 kırılım → small multiples (facet/trellis): en az-değerli boyut panellere bölünür,
  // her panel gruplu sütun (BI best practice; stack oran metriklerinde YANLIŞ olurdu).
  facet: { dim: string; x: string; series: string } | null;
}

export function analyze(result: QueryResult): Analysis {
  const { columns, rows } = result;
  const measures: string[] = [];
  const dims: string[] = [];
  for (const c of columns) {
    const vals = rows.map((r) => r[c]).filter((v) => v != null);
    (vals.length > 0 && vals.every(isNum) ? measures : dims).push(c);
  }
  const timeCol =
    dims.find((d) => TIME_NAMES.has(d.toLowerCase())) ??
    dims.find((d) => rows.length > 0 && rows.every((r) => r[d] == null || looksDate(r[d]))) ??
    null;

  let heat: { row: string; col: string } | null = null;
  if (dims.length >= 2 && measures.length >= 1 && rows.length >= 4) {
    for (let i = 0; i < dims.length && !heat; i++) {
      for (let j = i + 1; j < dims.length && !heat; j++) {
        const ca = distinct(rows, dims[i]).length;
        const cb = distinct(rows, dims[j]).length;
        const prod = ca * cb;
        // min eksen 3+: 2 kategorili boyut (ör. cinsiyet) ısı haritası değil GRUPLU
        // sütun olarak daha okunur (farklı renk + lejant).
        if (ca > 1 && cb > 1 && Math.min(ca, cb) >= 3 && prod <= rows.length * 1.6 && prod >= rows.length * 0.5) {
          const [row, col] = ca <= cb ? [dims[i], dims[j]] : [dims[j], dims[i]];
          heat = { row, col };
        }
      }
    }
  }

  // Açık "ısı haritası" isteği için: 2+ boyutta her zaman kurulabilir bir eşleme
  // (küçük kardinalite → satır). Otomatik seçim yine `heat` kuralını kullanır.
  let heatAny: Analysis["heatAny"] = heat;
  if (!heatAny && dims.length >= 2 && measures.length >= 1) {
    const multi = [...dims].filter((d) => distinct(rows, d).length > 1)
      .sort((a, b) => distinct(rows, a).length - distinct(rows, b).length);
    if (multi.length >= 2) heatAny = { row: multi[0], col: multi[multi.length - 1] };
  }

  const primaryDim =
    timeCol ??
    (dims.length
      ? dims.slice().sort((a, b) => distinct(rows, b).length - distinct(rows, a).length)[0]
      : null);

  // 3 kırılım → facet adayı: en düşük kardinaliteli boyut panel olur (≤6 panel),
  // kalan ikisinden büyüğü x-ekseni, küçüğü renk serisi.
  let facet: Analysis["facet"] = null;
  if (dims.length === 3 && measures.length >= 1) {
    const sorted = [...dims].sort((a, b) => distinct(rows, a).length - distinct(rows, b).length);
    const [fd, sd, xd] = sorted;
    if (distinct(rows, fd).length <= 6) facet = { dim: fd, x: xd, series: sd };
  }

  let kind: ChartKind = "none";
  if (rows.length === 1 && measures.length >= 1 && dims.length <= 1) kind = "kpi";
  else if (measures.length === 0) kind = "none";
  else if (dims.length === 3 && facet) kind = "facet";
  // Geniş detay/liste (3+ kırılım facet'lenemedi ya da 4+) → grafik değil, TABLO.
  else if (dims.length > 2) kind = "none";
  // Zaman ekseni varsa TREND önce gelir (çizgi), ısı haritasından önce.
  else if (timeCol && measures.length >= 1) kind = "line";
  else if (heat) kind = "heatmap";
  else if (primaryDim && measures.length >= 1) kind = "bar";

  return { kind, measures, dims, timeCol, primaryDim, heat, heatAny, facet };
}

interface BuildOpts {
  kind: ChartKind;
  measure: string;
  dark: boolean;
}

// Ölçü seçicide "tümü" nöbetçisi — çok-ölçülü kombo görünüm (ADR/log 2026-07-21).
export const ALL_MEASURES = "__tumu__";

export function buildOption(result: QueryResult, a: Analysis, o: BuildOpts): EChartsOption {
  const { rows } = result;
  const axis = o.dark ? "#9ca3af" : "#6b7280";
  const split = o.dark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.07)";
  const multi = o.measure === ALL_MEASURES && a.measures.length > 1;
  const measure = (!o.measure || o.measure === ALL_MEASURES) ? a.measures[0] : o.measure;
  const base = {
    color: PALETTE,
    textStyle: { fontFamily: "inherit" },
    grid: { left: 8, right: 18, top: 30, bottom: 8, containLabel: true },
  } as const;

  // -- KOMBO (çok ölçü, "tümü"): miktarlar yan yana SÜTUN; ölçek olarak ezilen
  //    ölçüler (oranlar: %2 vs 100.000 kg) SAĞ EKSENDE ÇİZGİ — klasik BI kombosu.
  //    Yalnız tek kategorik eksen (ya da zaman ekseni, seri boyutu yokken) desteklenir;
  //    boyut-serili görünümlerde ölçü teke düşer (iki seri kaynağı aynı anda olmaz).
  const comboX = a.timeCol ?? a.primaryDim;
  const comboSeriesDim = comboX ? a.dims.find((d) => d !== comboX) ?? null : null;
  if (multi && (o.kind === "bar" || o.kind === "line") && comboX && !comboSeriesDim) {
    const xs = orderCats(distinct(rows, comboX).map(fmtCat));
    const maxOf = (m: string) =>
      Math.max(0, ...rows.map((r) => num(r[m])).filter((v) => !Number.isNaN(v)));
    const gmax = Math.max(...a.measures.map(maxOf));
    // Eksen ayrımı BİRİME göre: kg ölçüleri birlikte SOL (sütun), farklı birimdekiler
    // (%) SAĞ (çizgi). fire_kg ~1000 vs agirlik ~50k aynı birimdir — ölçek sezgisi
    // onları yanlış ayırıyordu (ekran görüntüsü 2026-07-21). Birimler ayrışmazsa
    // ölçek sezgisine düşülür.
    const dominant = [...a.measures].sort((x, y) => maxOf(y) - maxOf(x))[0];
    let primary = a.measures.filter((m) => unitSuffix(m) === unitSuffix(dominant));
    let secondary = a.measures.filter((m) => !primary.includes(m));
    if (secondary.length === 0 && primary.length > 1) {
      secondary = a.measures.filter((m) => maxOf(m) < gmax / 50);
      primary = a.measures.filter((m) => !secondary.includes(m));
    }
    const val = (m: string, x: string) => {
      const r = rows.find((rr) => fmtCat(rr[comboX]) === x);
      return r ? num(r[m]) : null;
    };
    return {
      ...base,
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        // her seri KENDİ birimiyle biçimlenir (819.4000000000001 ham değeri değil)
        formatter: (ps: unknown) => {
          const arr = ps as { marker: string; seriesName: string; value: number | null }[];
          const head = arr.length ? `${(arr[0] as unknown as { name: string }).name}<br/>` : "";
          return head + arr
            .map((p) => `${p.marker}${p.seriesName}: <b>${fmtValue(p.value, p.seriesName)}</b>`)
            .join("<br/>");
        },
      },
      legend: { type: "scroll", top: 0, textStyle: { color: axis } },
      grid: { left: 8, right: secondary.length ? 8 : 18, top: 30, bottom: 8, containLabel: true },
      xAxis: {
        type: "category",
        data: xs.map((x) => axisLabel(x, comboX)),
        axisLabel: { color: axis, interval: 0, rotate: xs.length > 8 ? 35 : 0 },
        axisLine: { lineStyle: { color: split } },
      },
      yAxis: [
        {
          type: "value",
          axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, primary[0] ?? measure) },
          splitLine: { lineStyle: { color: split } },
        },
        ...(secondary.length
          ? [{
              type: "value" as const,
              axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, secondary[0]) },
              splitLine: { show: false },
            }]
          : []),
      ],
      series: [
        ...primary.map((m) => ({
          name: m,
          type: (o.kind === "line" ? "line" : "bar") as "line" | "bar",
          data: xs.map((x) => val(m, x)),
          ...(o.kind === "bar"
            ? { itemStyle: { borderRadius: [3, 3, 0, 0] as [number, number, number, number] }, barMaxWidth: 34 }
            : { smooth: true, showSymbol: false }),
        })),
        ...secondary.map((m) => ({
          name: m,
          type: "line" as const,
          yAxisIndex: 1,
          smooth: true,
          data: xs.map((x) => val(m, x)),
        })),
      ],
    };
  }

  // -- HEATMAP: satır × sütun matrisi + kenar ortalamaları (marj) ---------
  // Açık istek otomatik min-eksen kuralını ezer: a.heat yoksa a.heatAny kullanılır.
  if (o.kind === "heatmap" && (a.heat || a.heatAny)) {
    const { row, col } = (a.heat ?? a.heatAny)!;
    const rowKeys = orderCats(distinct(rows, row).map(String));
    // Sütun sırası: haftanın günü ise kanonik (Pzt→Paz), değilse alfabetik/kronolojik.
    const colKeys = orderCats(distinct(rows, col).map(fmtCat));
    const val = new Map<string, number>();
    rows.forEach((r) => {
      const ri = rowKeys.indexOf(String(r[row]));
      const ci = colKeys.indexOf(fmtCat(r[col]));
      if (ri >= 0 && ci >= 0) val.set(`${ri}|${ci}`, num(r[measure]));
    });

    const rowLabels = [...rowKeys.map((k) => axisLabel(k, row)), AVG];
    const colLabels = [...colKeys.map((k) => axisLabel(k, col)), AVG];
    const R = rowKeys.length;
    const C = colKeys.length;
    const marginStyle = { borderColor: axis, borderWidth: 1, borderType: "dashed" as const };
    type Cell = { value: [number, number, number]; itemStyle?: object };
    const data: Cell[] = [];

    for (let ri = 0; ri < R; ri++)
      for (let ci = 0; ci < C; ci++) {
        const v = val.get(`${ri}|${ci}`);
        if (v != null) data.push({ value: [ci, ri, v] });
      }
    // satır ortalamaları (sağ kenar sütunu)
    for (let ri = 0; ri < R; ri++) {
      const m = mean([...Array(C).keys()].map((ci) => val.get(`${ri}|${ci}`)).filter((x): x is number => x != null));
      if (m != null) data.push({ value: [C, ri, m], itemStyle: marginStyle });
    }
    // sütun ortalamaları (alt kenar satırı)
    for (let ci = 0; ci < C; ci++) {
      const m = mean([...Array(R).keys()].map((ri) => val.get(`${ri}|${ci}`)).filter((x): x is number => x != null));
      if (m != null) data.push({ value: [ci, R, m], itemStyle: marginStyle });
    }
    // genel ortalama (köşe)
    const all = [...val.values()];
    const grand = mean(all);
    if (grand != null) data.push({ value: [C, R, grand], itemStyle: { ...marginStyle, borderWidth: 1.5 } });

    const vals = data.map((d) => d.value[2]);
    return {
      ...base,
      title: {
        text: `Ortalama ${fmtValue(grand, measure)}`,
        subtext: `en düşük ${fmtValue(Math.min(...all), measure)} · en yüksek ${fmtValue(Math.max(...all), measure)}`,
        left: 8,
        top: 4,
        textStyle: { fontSize: 13, color: o.dark ? "#e5e7eb" : "#374151" },
        subtextStyle: { fontSize: 11, color: axis },
      },
      tooltip: {
        position: "top",
        formatter: (p: unknown) => {
          const d = (p as { data: Cell }).data.value;
          const rl = d[1] === R ? "Ortalama" : rowLabels[d[1]];
          const cl = d[0] === C ? "Ortalama" : colLabels[d[0]];
          return `${rl} · ${cl}<br/><b>${fmtValue(d[2], measure)}</b>`;
        },
      },
      grid: { left: 8, right: 18, top: 54, bottom: 64, containLabel: true },
      xAxis: {
        type: "category",
        data: colLabels,
        splitArea: { show: true },
        // kategorik eksende etiket ATLANMAZ (kumaş adları gibi her değer anlamlı)
        axisLabel: { color: axis, interval: 0, rotate: colLabels.length > 5 ? 30 : 0 },
      },
      yAxis: { type: "category", data: rowLabels, splitArea: { show: true }, axisLabel: { color: axis, interval: 0 } },
      visualMap: {
        min: Math.min(...vals),
        max: Math.max(...vals),
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: 4,
        inRange: { color: heatPalette(measure) },
        textStyle: { color: axis },
        formatter: (v: number | string | Date | null | undefined) => fmtValue(v, measure),
      },
      series: [
        {
          type: "heatmap",
          data,
          label: {
            show: true,
            formatter: (p: unknown) => {
              const d = (p as { data: Cell }).data.value;
              return fmtValue(d[2], measure);
            },
          },
          emphasis: { itemStyle: { shadowBlur: 8, shadowColor: "rgba(0,0,0,0.3)" } },
        },
      ],
    };
  }

  // -- FACET (small multiples): 3 kırılım → panel başına gruplu sütun ------
  if (o.kind === "facet" && a.facet) {
    const { dim: fDim, x: xDim, series: sDim } = a.facet;
    const panels = orderCats(distinct(rows, fDim).map(String));
    const xs = orderCats(distinct(rows, xDim).map(fmtCat));
    const groups = distinct(rows, sDim).map(String);
    const N = panels.length;
    const w = 100 / N;
    // ORTAK y-skala — paneller karşılaştırılabilir olsun (best practice).
    const allVals = rows.map((r) => num(r[measure])).filter((v) => !Number.isNaN(v));
    const yMax = allVals.length ? Math.max(...allVals) * 1.08 : undefined;

    return {
      ...base,
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => fmtValue(v, measure) },
      legend: { type: "scroll", top: 0, textStyle: { color: axis } },
      title: panels.map((p, i) => ({
        text: p,
        left: `${i * w + w / 2}%`,
        textAlign: "center" as const,
        top: 22,
        textStyle: { fontSize: 11, color: axis, fontWeight: "normal" as const },
      })),
      grid: panels.map((_, i) => ({
        left: `${i * w + 5}%`,
        width: `${w - 8}%`,
        top: 46,
        bottom: 28,
      })),
      xAxis: panels.map((_, i) => ({
        type: "category" as const,
        gridIndex: i,
        data: xs.map((x) => axisLabel(x, xDim)),
        axisLabel: { color: axis, fontSize: 10, interval: 0, rotate: xs.length > 5 ? 45 : 0 },
        axisLine: { lineStyle: { color: split } },
      })),
      yAxis: panels.map((_, i) => ({
        type: "value" as const,
        gridIndex: i,
        max: yMax,
        axisLabel: i === 0 ? { color: axis, formatter: (v: number) => fmtAxis(v, measure) } : { show: false },
        splitLine: { lineStyle: { color: split } },
        name: i === 0 ? unitSuffix(measure) : undefined,
        nameTextStyle: { color: axis },
      })),
      series: panels.flatMap((p, i) =>
        groups.map((g) => ({
          name: g, // aynı ad → lejant panolar arası paylaşılır
          type: "bar" as const,
          xAxisIndex: i,
          yAxisIndex: i,
          data: xs.map((x) => {
            const r = rows.find(
              (rr) => String(rr[fDim]) === p && fmtCat(rr[xDim]) === x && String(rr[sDim]) === g,
            );
            return r ? num(r[measure]) : null;
          }),
          itemStyle: { borderRadius: [2, 2, 0, 0] as [number, number, number, number] },
          barMaxWidth: 18,
        })),
      ),
    };
  }

  // -- PIE ---------------------------------------------------------------
  if (o.kind === "pie" && a.primaryDim) {
    const dim = a.primaryDim;
    return {
      ...base,
      tooltip: {
        trigger: "item",
        formatter: (p: unknown) => {
          const d = p as { name: string; value: number; percent: number };
          return `${d.name}<br/><b>${fmtValue(d.value, measure)}</b> (%${d.percent})`;
        },
      },
      legend: { type: "scroll", bottom: 0, textStyle: { color: axis } },
      series: [
        {
          type: "pie",
          radius: ["42%", "70%"],
          itemStyle: { borderRadius: 6, borderColor: o.dark ? "#0a0a0a" : "#fff", borderWidth: 2 },
          data: rows.map((r) => ({ name: fmtCat(r[dim]), value: num(r[measure]) })),
          label: { color: axis, formatter: (p: unknown) => (p as { name: string }).name },
        },
      ],
    };
  }

  // -- LINE (zaman, ops. çoklu seri) -------------------------------------
  if (o.kind === "line") {
    const xCol = a.timeCol ?? a.primaryDim!;
    const seriesDim = a.dims.find((d) => d !== xCol) ?? null;
    const xs = orderCats(distinct(rows, xCol).map(fmtCat));
    const series = seriesDim
      ? distinct(rows, seriesDim).map(String).map((g) => ({
          name: g,
          type: "line" as const,
          smooth: true,
          showSymbol: false,
          data: xs.map((x) => {
            const r = rows.find((rr) => fmtCat(rr[xCol]) === x && String(rr[seriesDim]) === g);
            return r ? num(r[measure]) : null;
          }),
        }))
      : [
          {
            name: measure,
            type: "line" as const,
            smooth: true,
            areaStyle: { opacity: 0.12 },
            data: xs.map((x) => {
              const r = rows.find((rr) => fmtCat(rr[xCol]) === x);
              return r ? num(r[measure]) : null;
            }),
          },
        ];
    return {
      ...base,
      tooltip: { trigger: "axis", valueFormatter: (v: unknown) => fmtValue(v, measure) },
      legend: seriesDim ? { type: "scroll", top: 0, textStyle: { color: axis } } : undefined,
      xAxis: { type: "category", data: xs.map((x) => axisLabel(x, xCol)), axisLabel: { color: axis }, axisLine: { lineStyle: { color: split } } },
      yAxis: {
        type: "value",
        name: unitSuffix(measure),
        nameTextStyle: { color: axis },
        axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, measure) },
        splitLine: { lineStyle: { color: split } },
      },
      series,
    };
  }

  // -- BAR — İKİNCİ boyut varsa GRUPLU sütun (ay × müşteri, hafta günü × cinsiyet):
  //    her grup ayrı renk + lejant; 14 tek-renk sütun yerine 7 gün × 2 seri.
  const barX = a.timeCol ?? (a.dims.length >= 2 ? a.primaryDim : null);
  const barSeries = barX ? a.dims.find((d) => d !== barX) ?? null : null;
  if (barX && barSeries) {
    const xs = orderCats(distinct(rows, barX).map(fmtCat));
    const groups = distinct(rows, barSeries).map(String);
    return {
      ...base,
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => fmtValue(v, measure) },
      legend: { type: "scroll", top: 0, textStyle: { color: axis } },
      xAxis: { type: "category", data: xs.map((x) => axisLabel(x, barX)), axisLabel: { color: axis, interval: 0, rotate: xs.length > 8 ? 35 : 0 }, axisLine: { lineStyle: { color: split } } },
      yAxis: {
        type: "value",
        name: unitSuffix(measure),
        nameTextStyle: { color: axis },
        axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, measure) },
        splitLine: { lineStyle: { color: split } },
      },
      series: groups.map((g) => ({
        name: g,
        type: "bar" as const,
        data: xs.map((x) => {
          const r = rows.find((rr) => fmtCat(rr[barX]) === x && String(rr[barSeries]) === g);
          return r ? num(r[measure]) : null;
        }),
        itemStyle: { borderRadius: [3, 3, 0, 0] as [number, number, number, number] },
        barMaxWidth: 40,
      })),
    };
  }

  // -- BAR (tek boyut → tek seri) ----------------------------------------
  // Kategoriler hafta günüyse KANONİK sıra (Pzt→Paz); değilse SQL sırası korunur
  // ("en düşükleri göster" gibi kasıtlı sıralamalar bozulmasın).
  const dim = a.primaryDim!;
  const rawCats = rows.map((r) => fmtCat(r[dim]));
  const isWeekdays = rawCats.length > 0 && rawCats.every((c) => WEEKDAY_ORDER.includes(c));
  const cats = isWeekdays ? orderCats(rawCats) : rawCats;
  const valByCat = new Map(rows.map((r) => [fmtCat(r[dim]), num(r[measure])]));
  return {
    ...base,
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => fmtValue(v, measure) },
    xAxis: {
      type: "category",
      data: cats,
      axisLabel: { color: axis, rotate: cats.length > 8 ? 35 : 0, interval: 0 },
      axisLine: { lineStyle: { color: split } },
    },
    yAxis: {
      type: "value",
      name: unitSuffix(measure),
      nameTextStyle: { color: axis },
      axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, measure) },
      splitLine: { lineStyle: { color: split } },
    },
    series: [
      {
        type: "bar",
        name: measure,
        data: cats.map((c) => valByCat.get(c) ?? null),
        itemStyle: { borderRadius: [5, 5, 0, 0], color: PALETTE[0] },
        barMaxWidth: 46,
      },
    ],
  };
}

// KPI kartları (tek satırlık sonuç) — birim-farkında.
export function kpiCards(result: QueryResult, a: Analysis): { label: string; value: string; ctx?: string }[] {
  const row = result.rows[0] ?? {};
  const ctx = a.dims.length ? String(row[a.dims[0]] ?? "") : undefined;
  return a.measures.map((m) => ({ label: m, value: fmtValue(row[m], m), ctx }));
}
