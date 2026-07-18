// Sonuç tablosunun ŞEKLİNDEN otomatik grafik tipi çıkarımı + ECharts option üretimi.
// Desteklenen: KPI (tek satır), bar, line (zaman), pie, heatmap (2 boyut × ölçü matrisi).

import type { EChartsOption } from "echarts";
import type { QueryResult, Row } from "./types";

export type ChartKind = "kpi" | "bar" | "line" | "pie" | "heatmap" | "none";

const TIME_NAMES = new Set(["donem", "dönem", "tarih", "ay", "hafta", "gun", "gün", "period"]);
const PALETTE = ["#4F8CFF", "#22C55E", "#F59E0B", "#EF4444", "#A855F7", "#06B6D4", "#EC4899", "#84CC16"];
const HEAT = ["#EF4444", "#F59E0B", "#FDE047", "#84CC16", "#22C55E"]; // düşük→yüksek (kırmızı→yeşil)
const nf = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 2 });

const isNum = (v: unknown) =>
  typeof v === "number" || (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v)));
const num = (v: unknown) => (typeof v === "number" ? v : Number(v));
const looksDate = (v: unknown) => typeof v === "string" && /^\d{4}-\d{2}/.test(v);
const distinct = (rows: Row[], c: string) => [...new Set(rows.map((r) => r[c]))];
const fmtCat = (v: unknown) =>
  looksDate(v) ? String(v).slice(0, String(v).includes("T") ? 10 : 10) : String(v ?? "—");

export interface Analysis {
  kind: ChartKind;
  measures: string[];
  dims: string[];
  timeCol: string | null;
  primaryDim: string | null;
  heat: { row: string; col: string } | null;
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

  // Heatmap: iki GERÇEK boyut (kartezyen matris) + ≥1 ölçü.
  let heat: { row: string; col: string } | null = null;
  if (dims.length >= 2 && measures.length >= 1 && rows.length >= 4) {
    for (let i = 0; i < dims.length && !heat; i++) {
      for (let j = i + 1; j < dims.length && !heat; j++) {
        const ca = distinct(rows, dims[i]).length;
        const cb = distinct(rows, dims[j]).length;
        const prod = ca * cb;
        if (ca > 1 && cb > 1 && prod <= rows.length * 1.6 && prod >= rows.length * 0.5) {
          // satır = az kardinaliteli (ör. 3 vardiya), sütun = çok (ör. 7 gün)
          const [row, col] = ca <= cb ? [dims[i], dims[j]] : [dims[j], dims[i]];
          heat = { row, col };
        }
      }
    }
  }

  const primaryDim =
    timeCol ??
    (dims.length
      ? dims.slice().sort((a, b) => distinct(rows, b).length - distinct(rows, a).length)[0]
      : null);

  let kind: ChartKind = "none";
  if (rows.length === 1 && measures.length >= 1 && dims.length <= 1) kind = "kpi";
  else if (heat) kind = "heatmap";
  else if (timeCol && measures.length >= 1) kind = "line";
  else if (primaryDim && measures.length >= 1) kind = "bar";

  return { kind, measures, dims, timeCol, primaryDim, heat };
}

interface BuildOpts {
  kind: ChartKind;
  measure: string;
  dark: boolean;
}

export function buildOption(result: QueryResult, a: Analysis, o: BuildOpts): EChartsOption {
  const { rows } = result;
  const axis = o.dark ? "#9ca3af" : "#6b7280";
  const split = o.dark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.07)";
  const measure = o.measure || a.measures[0];
  const base = {
    color: PALETTE,
    textStyle: { fontFamily: "inherit" },
    grid: { left: 8, right: 18, top: 30, bottom: 8, containLabel: true },
  } as const;

  // -- HEATMAP: satır × sütun matrisi, hücreler ölçüye göre renkli --------
  if (o.kind === "heatmap" && a.heat) {
    const { row, col } = a.heat;
    const rowVals = distinct(rows, row).map(String);
    const colVals = distinct(rows, col).map((v) => fmtCat(v)).sort();
    const idx = (arr: string[], v: string) => arr.indexOf(v);
    const data = rows
      .map((r) => [idx(colVals, fmtCat(r[col])), idx(rowVals, String(r[row])), num(r[measure])])
      .filter((d) => d[0] >= 0 && d[1] >= 0);
    const vals = data.map((d) => d[2] as number);
    return {
      ...base,
      tooltip: {
        position: "top",
        formatter: (p: unknown) => {
          const d = (p as { data: [number, number, number] }).data;
          return `${rowVals[d[1]]} · ${colVals[d[0]]}<br/><b>${nf.format(d[2])}</b>`;
        },
      },
      grid: { left: 8, right: 18, top: 12, bottom: 60, containLabel: true },
      xAxis: {
        type: "category",
        data: colVals,
        splitArea: { show: true },
        axisLabel: { color: axis, rotate: colVals.length > 8 ? 40 : 0 },
      },
      yAxis: { type: "category", data: rowVals, splitArea: { show: true }, axisLabel: { color: axis } },
      visualMap: {
        min: Math.min(...vals),
        max: Math.max(...vals),
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: 0,
        inRange: { color: HEAT },
        textStyle: { color: axis },
      },
      series: [
        {
          type: "heatmap",
          data,
          label: { show: true, formatter: (p: unknown) => nf.format((p as { data: number[] }).data[2]) },
          emphasis: { itemStyle: { shadowBlur: 8, shadowColor: "rgba(0,0,0,0.3)" } },
        },
      ],
    };
  }

  // -- PIE: parça-bütün --------------------------------------------------
  if (o.kind === "pie" && a.primaryDim) {
    const dim = a.primaryDim;
    return {
      ...base,
      tooltip: { trigger: "item", formatter: (p: unknown) => {
        const d = p as { name: string; value: number; percent: number };
        return `${d.name}<br/><b>${nf.format(d.value)}</b> (%${d.percent})`;
      } },
      legend: { type: "scroll", bottom: 0, textStyle: { color: axis } },
      series: [
        {
          type: "pie",
          radius: ["42%", "70%"],
          itemStyle: { borderRadius: 6, borderColor: o.dark ? "#0a0a0a" : "#fff", borderWidth: 2 },
          data: rows.map((r) => ({ name: fmtCat(r[dim]), value: num(r[measure]) })),
          label: { color: axis },
        },
      ],
    };
  }

  // -- LINE: zaman ekseni (varsa ikinci boyuta göre çoklu seri) ----------
  if (o.kind === "line") {
    const xCol = a.timeCol ?? a.primaryDim!;
    const seriesDim = a.dims.find((d) => d !== xCol) ?? null;
    const xs = distinct(rows, xCol).map((v) => fmtCat(v)).sort();
    let series;
    if (seriesDim) {
      const groups = distinct(rows, seriesDim).map(String);
      series = groups.map((g) => ({
        name: g,
        type: "line" as const,
        smooth: true,
        showSymbol: false,
        data: xs.map((x) => {
          const row = rows.find((r) => fmtCat(r[xCol]) === x && String(r[seriesDim]) === g);
          return row ? num(row[measure]) : null;
        }),
      }));
    } else {
      series = [
        {
          name: measure,
          type: "line" as const,
          smooth: true,
          areaStyle: { opacity: 0.12 },
          showSymbol: true,
          data: xs.map((x) => {
            const row = rows.find((r) => fmtCat(r[xCol]) === x);
            return row ? num(row[measure]) : null;
          }),
        },
      ];
    }
    return {
      ...base,
      tooltip: { trigger: "axis", valueFormatter: (v: unknown) => nf.format(v as number) },
      legend: seriesDim ? { type: "scroll", top: 0, textStyle: { color: axis } } : undefined,
      xAxis: { type: "category", data: xs, axisLabel: { color: axis }, axisLine: { lineStyle: { color: split } } },
      yAxis: { type: "value", axisLabel: { color: axis, formatter: (v: number) => nf.format(v) }, splitLine: { lineStyle: { color: split } } },
      series,
    };
  }

  // -- BAR (varsayılan) --------------------------------------------------
  const dim = a.primaryDim!;
  const cats = rows.map((r) => fmtCat(r[dim]));
  return {
    ...base,
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => nf.format(v as number) },
    xAxis: {
      type: "category",
      data: cats,
      axisLabel: { color: axis, rotate: cats.length > 8 ? 35 : 0, interval: 0 },
      axisLine: { lineStyle: { color: split } },
    },
    yAxis: { type: "value", axisLabel: { color: axis, formatter: (v: number) => nf.format(v) }, splitLine: { lineStyle: { color: split } } },
    series: [
      {
        type: "bar",
        name: measure,
        data: rows.map((r) => num(r[measure])),
        itemStyle: { borderRadius: [5, 5, 0, 0], color: PALETTE[0] },
        barMaxWidth: 46,
      },
    ],
  };
}

// KPI kartlarında gösterilecek değerler (tek satırlık sonuç).
export function kpiCards(result: QueryResult, a: Analysis): { label: string; value: string; ctx?: string }[] {
  const row = result.rows[0] ?? {};
  const ctx = a.dims.length ? String(row[a.dims[0]] ?? "") : undefined;
  return a.measures.map((m) => ({ label: m, value: nf.format(num(row[m])), ctx }));
}
