/**
 * dima iş mantığı — platformdan bağımsız.
 *
 * Burada React, DOM ve Node YOK. Sebep pratik: mobil geldiğinde grafik seçimi,
 * birim biçimlendirme ve SQL okunurluğu birebir aynı olmalı — iki platformda
 * iki farklı `analyze()` tutmak, aynı soruya iki farklı grafik demektir.
 *
 * Kural `@dima/eslint-config/boundaries` ile lint'te zorlanır.
 */

// Sonuç şekli analizi + grafik seçimi
export {
  ALL_MEASURES,
  X_KEY,
  analyze,
  buildFacet,
  buildHeatGrid,
  buildSeries,
  chartDensity,
  facetPanelValues,
  kpiCards,
  orderCats,
  splitAxes,
} from "./chart";
export type {
  Analysis,
  ChartData,
  ChartKind,
  FacetData,
  FacetPanel,
  HeatGrid,
  SeriesSpec,
} from "./chart";

// Birim/değer biçimlendirme (₺, kg, %)
export {
  fmtAxis,
  fmtTemporal,
  fmtValue,
  setSchemaUnits,
  unitFor,
  unitSuffix,
} from "./format";
export type { Unit } from "./format";

// SQL okunurluğu (tokenizasyon + biçimlendirme)
export { formatSql, tokenizeSql } from "./sql-format";
export type { SqlToken, SqlTokenType } from "./sql-format";
