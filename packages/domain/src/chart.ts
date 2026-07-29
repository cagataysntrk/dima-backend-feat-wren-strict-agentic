// Sonuç tablosunun ŞEKLİNDEN otomatik grafik tipi çıkarımı + Recharts serisi üretimi.
// Desteklenen otomatik tipler: KPI (tek satır), bar/yatay bar, line (zaman), heatmap, facet.
// `buildSeries` motordan bağımsız veri döndürür; çizim <Chart> façade'ında Recharts iledir.
// (heatmap/facet şimdilik tabloya düşer — bkz. components/chart/Chart.tsx.)
// Tüm sayılar birim-farkında biçimlendirilir (₺, kg, L, kWh, %, dk...) — bkz. format.ts.

import type { QueryResult, Row } from "@dima/contracts";
import { fmtTemporal, fmtValue, unitSuffix } from "./format";

// Eksen ETİKETİ: zaman kovalarını okunur yap ("Oca 2026") — sıralama ham değerle kalır.
const axisLabel = (v: string, col: string | null) => (col ? fmtTemporal(v, col) ?? v : v);

// analyze() yalnız ÇIKARILAN tipleri döndürür (kpi/bar/bar-h/line/heatmap/facet/none).
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
  | "radar"
  // ÇAPRAZ KARŞILAŞTIRMA (kombo): miktarlar sütun (sol eksen) + farklı birimdeki
  // ölçüler çizgi (sağ eksen). Klasik BI kombosu; yalnız çok-ölçülü sonuçlarda.
  | "combo";

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
  else if (primaryDim && measures.length >= 1) {
    // Karşılaştırmalarda uzun adlar ve çok kategori dikey sütunda eğik/kırpılmış
    // etiket üretir. Yatay sütun hem sırayı hem adı doğrudan okunur tutar;
    // doğal zaman ve hafta-günü düzeni bundan istisnadır.
    const categories = distinct(rows, primaryDim).map(fmtCat);
    const longest = Math.max(0, ...categories.map((value) => value.length));
    kind = !timeCol && (categories.length >= 7 || longest > 12) ? "bar-h" : "bar";
  }

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
  /** KOMBO'da seri başına çizim biçimi. Diğer tiplerde tanımsız — `kind` belirler. */
  mark?: "bar" | "line";
  /** KOMBO'da seri başına y-ekseni. Diğer tiplerde tanımsız (tek eksen). */
  axis?: "left" | "right";
}

export interface ChartData {
  xKey: string;
  data: Record<string, string | number | null>[];
  series: SeriesSpec[];
  // seriler ÖLÇÜ ise (çok-ölçü "tümü" kombosu) her seri kendi birimiyle biçimlenir;
  // aksi halde tüm seriler tek `measure` biriminde (ör. kırılım grupları).
  multiMeasure: boolean;
  measure: string;
  /** KOMBO'da sağ eksenin birim referansı (o eksendeki ilk ölçü). Yoksa null. */
  rightMeasure?: string | null;
}

/**
 * ÇAPRAZ KARŞILAŞTIRMA için eksen ayrımı — BİRİME göre.
 *
 * fire_kg (~1000) ile agirlik (~50k) AYNI birimdedir; ölçek sezgisi onları yanlış
 * ayırıyordu. Bu yüzden önce birim: en büyük ölçüyle aynı birimdekiler SOL (sütun),
 * kalanlar SAĞ (çizgi). Birimler ayrışmazsa (hepsi birimsiz) ölçek sezgisine düşülür:
 * baskın ölçünün 1/50'sinden küçük olanlar sağ eksene gider — yoksa oranlar (%2)
 * miktarların (100.000 kg) yanında düz çizgi olarak ezilir.
 */
export function splitAxes(
  rows: Row[],
  measures: string[],
): { left: string[]; right: string[] } {
  const maxOf = (m: string) =>
    Math.max(0, ...rows.map((r) => num(r[m])).filter((v) => !Number.isNaN(v)));
  const gmax = Math.max(...measures.map(maxOf));
  const dominant = [...measures].sort((x, y) => maxOf(y) - maxOf(x))[0];
  let left = measures.filter((m) => unitSuffix(m) === unitSuffix(dominant));
  let right = measures.filter((m) => !left.includes(m));
  if (right.length === 0 && left.length > 1) {
    right = measures.filter((m) => maxOf(m) < gmax / 50);
    left = measures.filter((m) => !right.includes(m));
  }
  return { left, right };
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

  // heatmap/facet: kendi bileşenleri var (chart/Heatmap, chart/Facet) — seri üretmez.
  if (kind === "heatmap" || kind === "facet" || kind === "none" || kind === "kpi") return null;

  // -- BAR / LINE / AREA / COMBO ------------------------------------------
  const xCol = a.timeCol ?? a.primaryDim;
  if (!xCol) return null;
  const isTime = xCol === a.timeCol;
  const xs = catOrder(rows, xCol, isTime);
  const label = (x: string) => axisLabel(x, xCol);

  // -- KOMBO (çapraz karşılaştırma): sütun + çizgi, çift eksen ------------
  // Tek kategorik eksen gerekir: ikinci bir kırılım varsa seri kaynağı ikiye çıkar
  // (hem ölçü hem grup) ve lejant okunmaz olur — o durumda kombo kurulmaz.
  if (kind === "combo") {
    if (a.measures.length < 2) return null;
    if (a.dims.some((d) => d !== xCol)) return null;
    const { left, right } = splitAxes(rows, a.measures);
    const byCat = new Map(xs.map((x) => [x, rows.find((r) => fmtCat(r[xCol]) === x)]));
    const data = xs.map((x) => {
      const r = byCat.get(x);
      const row: Record<string, string | number | null> = { [X_KEY]: label(x) };
      for (const m of a.measures) row[m] = r ? num(r[m]) : null;
      return row;
    });
    return {
      xKey: X_KEY,
      data,
      series: [
        ...left.map((m): SeriesSpec => ({ key: m, label: m, mark: "bar", axis: "left" })),
        ...right.map((m): SeriesSpec => ({ key: m, label: m, mark: "line", axis: "right" })),
      ],
      multiMeasure: true,
      measure: left[0] ?? measure,
      rightMeasure: right[0] ?? null,
    };
  }

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

// --- FACET (small multiples) ------------------------------------------------
// 3 kırılımlı sonuç → panel başına gruplu sütun. Paneller ORTAK y-skalayı paylaşır,
// yoksa yan yana duran paneller karşılaştırılamaz (BI best practice). Seri adları
// paneller arası aynıdır → tek lejant hepsini yönetir.

export interface FacetPanel {
  /** Panel başlığı — facet boyutunun bu paneldeki değeri. */
  value: string;
  data: Record<string, string | number | null>[];
}

export interface FacetData {
  xKey: string;
  panels: FacetPanel[];
  /** Paneller arası PAYLAŞILAN seriler (ortak renk + tek lejant). */
  series: SeriesSpec[];
  measure: string;
  /** ORTAK y tavanı — paneller karşılaştırılabilir olsun. */
  yMax: number | null;
}

export function buildFacet(
  result: QueryResult,
  a: Analysis,
  measureSel: string,
): FacetData | null {
  if (!a.facet) return null;
  const { rows } = result;
  const measure = !measureSel || measureSel === ALL_MEASURES ? a.measures[0] : measureSel;
  if (!measure) return null;

  const { dim: fDim, x: xDim, series: sDim } = a.facet;
  const panelValues = orderCats(distinct(rows, fDim).map(String));
  const xs = orderCats(distinct(rows, xDim).map(fmtCat));
  // seri sırası KANONİK + zaman değerleri BİÇİMLİ (ham ISO lejantı olmasın)
  const groups = orderCats(distinct(rows, sDim).map(fmtCat));

  // (panel, x, seri) → değer: satır başına tek geçiş; her hücrede find() O(n²) olurdu.
  const at = new Map<string, number>();
  for (const r of rows) {
    at.set(`${String(r[fDim])} ${fmtCat(r[xDim])} ${fmtCat(r[sDim])}`, num(r[measure]));
  }

  const allVals = rows.map((r) => num(r[measure])).filter((v) => !Number.isNaN(v));
  const yMax = allVals.length ? Math.max(...allVals) * 1.08 : null;

  return {
    xKey: X_KEY,
    panels: panelValues.map((p) => ({
      value: p,
      data: xs.map((x) => {
        const row: Record<string, string | number | null> = { [X_KEY]: axisLabel(x, xDim) };
        for (const g of groups) {
          const v = at.get(`${p} ${x} ${g}`);
          row[g] = v === undefined || Number.isNaN(v) ? null : v;
        }
        return row;
      }),
    })),
    series: groups.map((g) => ({ key: g, label: axisLabel(g, sDim) })),
    measure,
    yMax,
  };
}

// --- HEATMAP ızgarası --------------------------------------------------------
// Satır × sütun matrisi + KENAR ORTALAMALARI (marj): son sütun satır ortalaması,
// son satır sütun ortalaması, köşe genel ortalama. Marj hücreleri renk rampasını
// sıkıştırmasın diye min/max YALNIZ veri hücrelerinden hesaplanır.

const mean = (a: number[]) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);

export interface HeatGrid {
  /** Görüntü etiketleri (zaman kovaları biçimli). Marj etiketi dahil DEĞİL. */
  rowLabels: string[];
  colLabels: string[];
  /** (R+1) × (C+1) matris — son satır/sütun marj (ortalama), köşe genel ortalama. */
  cells: (number | null)[][];
  /** Veri hücrelerinin (marjsız) uç değerleri — renk rampası bunlarla ölçeklenir. */
  min: number;
  max: number;
  grand: number | null;
  measure: string;
}

export function buildHeatGrid(
  result: QueryResult,
  a: Analysis,
  measureSel: string,
): HeatGrid | null {
  const heat = a.heatAny ?? a.heat;
  if (!heat) return null;
  const measure = !measureSel || measureSel === ALL_MEASURES ? a.measures[0] : measureSel;
  if (!measure) return null;

  const { rows } = result;
  const { row, col } = heat;
  // Kanonik sıra: haftanın günü → Pzt→Paz, aksi halde alfabetik/kronolojik.
  const rowKeys = orderCats(distinct(rows, row).map(String));
  const colKeys = orderCats(distinct(rows, col).map(fmtCat));

  const R = rowKeys.length;
  const C = colKeys.length;
  const rowIndex = new Map(rowKeys.map((k, i) => [k, i]));
  const colIndex = new Map(colKeys.map((k, i) => [k, i]));

  const cells: (number | null)[][] = Array.from({ length: R + 1 }, () =>
    Array.from({ length: C + 1 }, () => null),
  );
  const data: number[] = [];
  for (const r of rows) {
    const ri = rowIndex.get(String(r[row]));
    const ci = colIndex.get(fmtCat(r[col]));
    if (ri === undefined || ci === undefined) continue;
    const v = num(r[measure]);
    if (Number.isNaN(v)) continue;
    cells[ri][ci] = v;
    data.push(v);
  }
  if (data.length === 0) return null;

  // satır ortalamaları (sağ kenar sütunu)
  for (let ri = 0; ri < R; ri++) {
    cells[ri][C] = mean(cells[ri].slice(0, C).filter((v): v is number => v != null));
  }
  // sütun ortalamaları (alt kenar satırı)
  for (let ci = 0; ci < C; ci++) {
    cells[R][ci] = mean(
      Array.from({ length: R }, (_, ri) => cells[ri][ci]).filter((v): v is number => v != null),
    );
  }
  const grand = mean(data);
  cells[R][C] = grand;

  return {
    rowLabels: rowKeys.map((k) => axisLabel(k, row)),
    colLabels: colKeys.map((k) => axisLabel(k, col)),
    cells,
    min: Math.min(...data),
    max: Math.max(...data),
    grand,
    measure,
  };
}

// --- Yoğunluk -----------------------------------------------------------------
// "Bu sonuç dar bir sütuna sığar mı?" Sığmıyorsa kart AÇILARAK başlar; kullanıcı
// her seferinde genişlet'e basmak zorunda kalmasın. Ölçüt eksen/panel/seri SAYISI:
// bunlar yatay yer kaplayan şeyler. Satır sayısı ölçüt DEĞİL — 500 satırlık bir
// tablo uzundur, geniş değil (onun çözümü sayfalama).
export function chartDensity(result: QueryResult, a?: Analysis): "normal" | "dense" {
  const an = a ?? analyze(result);
  const { rows } = result;

  // panelli: 2'den fazla panel yan yana daralır
  if (an.facet && distinct(rows, an.facet.dim).length > 2) return "dense";

  const xCol = an.timeCol ?? an.primaryDim;
  // uzun kategori ekseni → etiketler eğilir/kırpılır
  if (xCol && distinct(rows, xCol).length > 10) return "dense";

  // çok seri → lejant sarar, sütunlar incelir
  const seriesDim = xCol ? an.dims.find((d) => d !== xCol) : null;
  const seriesCount = seriesDim ? distinct(rows, seriesDim).length : an.measures.length;
  if (seriesCount > 4) return "dense";

  // ısı haritası: sütun sayısı matrisin genişliğidir
  const heat = an.heatAny ?? an.heat;
  if (heat && distinct(rows, heat.col).length > 6) return "dense";

  // grafik yoksa tablo genişliği belirler
  if (an.kind === "none" && result.columns.length > 7) return "dense";

  return "normal";
}

// KPI kartları (tek satırlık sonuç) — birim-farkında.
export function kpiCards(result: QueryResult, a: Analysis): { label: string; value: string; ctx?: string }[] {
  const row = result.rows[0] ?? {};
  const ctx = a.dims.length ? String(row[a.dims[0]] ?? "") : undefined;
  return a.measures.map((m) => ({ label: m, value: fmtValue(row[m], m), ctx }));
}
