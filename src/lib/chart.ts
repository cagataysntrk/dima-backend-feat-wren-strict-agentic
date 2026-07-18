// Sonuç tablosunun ŞEKLİNDEN otomatik grafik tipi çıkarımı + ECharts option üretimi.
// Desteklenen: KPI (tek satır), bar, line (zaman), pie, heatmap (2 boyut × ölçü matrisi).
// Tüm sayılar birim-farkında biçimlendirilir (₺, kg, L, kWh, %, dk...) — bkz. format.ts.

import type { EChartsOption } from "echarts";
import type { QueryResult, Row } from "./types";
import { fmtAxis, fmtValue, unitSuffix } from "./format";

export type ChartKind = "kpi" | "bar" | "line" | "pie" | "heatmap" | "none";

const TIME_NAMES = new Set(["donem", "dönem", "tarih", "ay", "hafta", "gun", "gün", "period"]);
const PALETTE = ["#4F8CFF", "#22C55E", "#F59E0B", "#EF4444", "#A855F7", "#06B6D4", "#EC4899", "#84CC16"];
const HEAT = ["#EF4444", "#F59E0B", "#FDE047", "#84CC16", "#22C55E"]; // düşük→yüksek (kırmızı→yeşil)
const AVG = "∑ Ort.";

const isNum = (v: unknown) =>
  typeof v === "number" || (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v)));
const num = (v: unknown) => (typeof v === "number" ? v : Number(v));
const looksDate = (v: unknown) => typeof v === "string" && /^\d{4}-\d{2}/.test(v);
const distinct = (rows: Row[], c: string) => [...new Set(rows.map((r) => r[c]))];
const fmtCat = (v: unknown) => (looksDate(v) ? String(v).slice(0, 10) : String(v ?? "—"));
const mean = (a: number[]) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);

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

  let heat: { row: string; col: string } | null = null;
  if (dims.length >= 2 && measures.length >= 1 && rows.length >= 4) {
    for (let i = 0; i < dims.length && !heat; i++) {
      for (let j = i + 1; j < dims.length && !heat; j++) {
        const ca = distinct(rows, dims[i]).length;
        const cb = distinct(rows, dims[j]).length;
        const prod = ca * cb;
        if (ca > 1 && cb > 1 && prod <= rows.length * 1.6 && prod >= rows.length * 0.5) {
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

  // -- HEATMAP: satır × sütun matrisi + kenar ortalamaları (marj) ---------
  if (o.kind === "heatmap" && a.heat) {
    const { row, col } = a.heat;
    const rowKeys = distinct(rows, row).map(String);
    // Sütun sırası SQL'den gelir (Pzt→Paz ya da kronolojik) — alfabetik sıralama YOK.
    const colKeys = distinct(rows, col).map(fmtCat);
    const val = new Map<string, number>();
    rows.forEach((r) => {
      const ri = rowKeys.indexOf(String(r[row]));
      const ci = colKeys.indexOf(fmtCat(r[col]));
      if (ri >= 0 && ci >= 0) val.set(`${ri}|${ci}`, num(r[measure]));
    });

    const rowLabels = [...rowKeys, AVG];
    const colLabels = [...colKeys, AVG];
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
        axisLabel: { color: axis, rotate: colLabels.length > 8 ? 40 : 0 },
      },
      yAxis: { type: "category", data: rowLabels, splitArea: { show: true }, axisLabel: { color: axis } },
      visualMap: {
        min: Math.min(...vals),
        max: Math.max(...vals),
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: 4,
        inRange: { color: HEAT },
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
    const xs = distinct(rows, xCol).map(fmtCat).sort();
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
      xAxis: { type: "category", data: xs, axisLabel: { color: axis }, axisLine: { lineStyle: { color: split } } },
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

  // -- BAR — zaman + kategori ise GRUPLU sütun (ör. ay × müşteri) --------
  const barSeries = a.timeCol ? a.dims.find((d) => d !== a.timeCol) ?? null : null;
  if (a.timeCol && barSeries) {
    const xs = distinct(rows, a.timeCol).map(fmtCat).sort();
    const groups = distinct(rows, barSeries).map(String);
    return {
      ...base,
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => fmtValue(v, measure) },
      legend: { type: "scroll", top: 0, textStyle: { color: axis } },
      xAxis: { type: "category", data: xs, axisLabel: { color: axis, rotate: xs.length > 8 ? 35 : 0 }, axisLine: { lineStyle: { color: split } } },
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
          const r = rows.find((rr) => fmtCat(rr[a.timeCol!]) === x && String(rr[barSeries]) === g);
          return r ? num(r[measure]) : null;
        }),
        itemStyle: { borderRadius: [3, 3, 0, 0] as [number, number, number, number] },
        barMaxWidth: 40,
      })),
    };
  }

  // -- BAR (tek boyut → tek seri) ----------------------------------------
  const dim = a.primaryDim!;
  const cats = rows.map((r) => fmtCat(r[dim]));
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
        data: rows.map((r) => num(r[measure])),
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
