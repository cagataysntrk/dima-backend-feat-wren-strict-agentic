// Sonuç tablosunun ŞEKLİNDEN otomatik grafik tipi çıkarımı + Recharts serisi üretimi.
// Desteklenen otomatik tipler: KPI (tek satır), bar, line (zaman), pie, heatmap, facet.
// `buildSeries` motordan bağımsız veri döndürür; çizim <Chart> façade'ında Recharts iledir.
// (heatmap/facet şimdilik tabloya düşer — bkz. components/chart/Chart.tsx.)
// Tüm sayılar birim-farkında biçimlendirilir (₺, kg, L, kWh, %, dk...) — bkz. format.ts.

import type { QueryResult, Row } from "@dima/contracts";
import { fmtTemporal, fmtValue } from "./format";

// Eksen ETİKETİ: zaman kovalarını okunur yap ("Oca 2026") — sıralama ham değerle kalır.
const axisLabel = (v: string, col: string | null) => (col ? fmtTemporal(v, col) ?? v : v);

// analyze() yalnız ÇIKARILAN tipleri döndürür (kpi/bar/line/pie/heatmap/facet/none).
// Gerisi kullanıcının elle seçebildiği varyantlardır — otomatik seçim asla üretmez,
// ama <Chart> hepsini çizebilir ve ResultView geçerli olanları menüde listeler.
export type ChartKind =
  | "kpi"
  | "bar"
  | "line"
  | "pie"
  | "heatmap"
  | "facet"
  | "none"
  | "area"
  | "bar-stacked"
  | "bar-h"
  | "scatter"
  | "radial"
  | "radar";

// SÜREKLI zaman (trend → çizgi). "gün/vardiya" gibi DÖNGÜSEL kategorikler kasıtlı olarak
// burada YOK — onlar ısı haritasına gitsin (ör. vardiya × haftanın günü). Gerçek tarih
// kolonları zaten değer biçiminden (looksDate) yakalanır.
const TIME_NAMES = new Set(["donem", "dönem", "tarih", "ay", "hafta", "period", "yil", "yıl", "year", "ceyrek", "çeyrek"]);

const isNum = (v: unknown) =>
  typeof v === "number" || (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v)));
const num = (v: unknown) => (typeof v === "number" ? v : Number(v));
const looksDate = (v: unknown) => typeof v === "string" && /^\d{4}-\d{2}/.test(v);
const distinct = (rows: Row[], c: string) => [...new Set(rows.map((r) => r[c]))];
const fmtCat = (v: unknown) => (looksDate(v) ? String(v).slice(0, 10) : String(v ?? "—"));

// Kanonik haftanın-günü sırası — kategori değerleri gün ise kronolojik sırala (Pzt→Paz),
// değilse alfabetik (tarih YYYY-MM zaten kronolojik). Kaynak cube ya da LLM olsun, her yerde.
const WEEKDAY_ORDER = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
export const orderCats = (vals: string[]): string[] =>
  vals.length && vals.every((v) => WEEKDAY_ORDER.includes(v))
    ? [...vals].sort((a, b) => WEEKDAY_ORDER.indexOf(a) - WEEKDAY_ORDER.indexOf(b))
    : [...vals].sort();

// Kategori sırası: zaman/haftanın günü → kanonik; aksi halde SQL sırası korunur
// ("en düşükleri göster" gibi kasıtlı sıralamalar bozulmasın).
function catOrder(rows: Row[], xCol: string, isTime: boolean): string[] {
  const raw = [...new Set(rows.map((r) => fmtCat(r[xCol])))];
  if (isTime) return orderCats(raw);
  const allWeekdays = raw.length > 0 && raw.every((c) => WEEKDAY_ORDER.includes(c));
  return allWeekdays ? orderCats(raw) : raw;
}

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
    if (timeCol) {
      const [a, b] = dims.filter((d) => d !== timeCol)
        .sort((x, y) => distinct(rows, x).length - distinct(rows, y).length);
      if (distinct(rows, a).length <= 6) facet = { dim: a, x: timeCol, series: b };
    } else {
      const sorted = [...dims].sort((a, b) => distinct(rows, a).length - distinct(rows, b).length);
      const [fd, sd, xd] = sorted;
      if (distinct(rows, fd).length <= 6) facet = { dim: fd, x: xd, series: sd };
    }
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

// Panelli görünümde gezinme (carousel): panel değerleri kanonik sırayla.
export const facetPanelValues = (result: QueryResult, dim: string): string[] =>
  orderCats(distinct(result.rows, dim).map(String));

// Ölçü seçicide "tümü" nöbetçisi — çok-ölçülü kombo görünüm (ADR/log 2026-07-21).
export const ALL_MEASURES = "__tumu__";

// Recharts satır anahtarı: x kategori değeri (biçimli etiket) bu alanda tutulur.
export const X_KEY = "__x";

export interface SeriesSpec {
  key: string;
  label: string;
}

export interface ChartData {
  xKey: string;
  data: Record<string, string | number | null>[];
  series: SeriesSpec[];
  // seriler ÖLÇÜ ise (çok-ölçü "tümü" kombosu) her seri kendi birimiyle biçimlenir;
  // aksi halde tüm seriler tek `measure` biriminde (ör. kırılım grupları).
  multiMeasure: boolean;
  measure: string;
}

// Motordan bağımsız Recharts verisi. bar/line/area/pie destekler; heatmap/facet null
// döner (façade tabloya düşer). Birim biçimlendirme <Chart>'ta format.ts ile yapılır.
export function buildSeries(
  result: QueryResult,
  a: Analysis,
  kind: ChartKind,
  measureSel: string,
): ChartData | null {
  const { rows } = result;
  if (rows.length === 0 || a.measures.length === 0) return null;

  const measure = !measureSel || measureSel === ALL_MEASURES ? a.measures[0] : measureSel;

  // -- PIE / RADIAL: tek boyut × tek ölçü (aynı ad/değer şekli) -----------
  if (kind === "pie" || kind === "radial" || kind === "radar") {
    const dim = a.primaryDim;
    if (!dim) return null;
    return {
      xKey: "name",
      data: rows.map((r) => ({ name: fmtCat(r[dim]), value: num(r[measure]) })),
      series: [{ key: "value", label: measure }],
      multiMeasure: false,
      measure,
    };
  }

  // heatmap/facet: Recharts primitifi yok → tabloya düş (visx ileride).
  if (kind === "heatmap" || kind === "facet" || kind === "none" || kind === "kpi") return null;

  // -- BAR / LINE / AREA --------------------------------------------------
  const xCol = a.timeCol ?? a.primaryDim;
  if (!xCol) return null;
  const isTime = xCol === a.timeCol;
  const xs = catOrder(rows, xCol, isTime);
  const label = (x: string) => axisLabel(x, xCol);

  const multi = measureSel === ALL_MEASURES && a.measures.length > 1;

  // çok-ölçü kombo: her ölçü ayrı seri (tek kategorik eksen gerekir).
  if (multi) {
    const data = xs.map((x) => {
      const r = rows.find((rr) => fmtCat(rr[xCol]) === x);
      const row: Record<string, string | number | null> = { [X_KEY]: label(x) };
      for (const m of a.measures) row[m] = r ? num(r[m]) : null;
      return row;
    });
    return { xKey: X_KEY, data, series: a.measures.map((m) => ({ key: m, label: m })), multiMeasure: true, measure };
  }

  // ikinci boyut → gruplu seri (ay × müşteri, hafta günü × cinsiyet)
  const seriesDim = a.dims.find((d) => d !== xCol) ?? null;
  if (seriesDim) {
    const groups = orderCats(distinct(rows, seriesDim).map(String));
    const data = xs.map((x) => {
      const row: Record<string, string | number | null> = { [X_KEY]: label(x) };
      for (const g of groups) {
        const r = rows.find((rr) => fmtCat(rr[xCol]) === x && String(rr[seriesDim]) === g);
        row[g] = r ? num(r[measure]) : null;
      }
      return row;
    });
    return { xKey: X_KEY, data, series: groups.map((g) => ({ key: g, label: g })), multiMeasure: false, measure };
  }

  // tek boyut → tek seri
  const valByCat = new Map(rows.map((r) => [fmtCat(r[xCol]), num(r[measure])]));
  const data = xs.map((x) => ({ [X_KEY]: label(x), [measure]: valByCat.get(x) ?? null }));
  return { xKey: X_KEY, data, series: [{ key: measure, label: measure }], multiMeasure: false, measure };
}

// KPI kartları (tek satırlık sonuç) — birim-farkında.
export function kpiCards(result: QueryResult, a: Analysis): { label: string; value: string; ctx?: string }[] {
  const row = result.rows[0] ?? {};
  const ctx = a.dims.length ? String(row[a.dims[0]] ?? "") : undefined;
  return a.measures.map((m) => ({ label: m, value: fmtValue(row[m], m), ctx }));
}
