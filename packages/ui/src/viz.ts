// Pure helpers for the extra chart types (trend number, meter, funnel,
// waterfall, pivot totals). Unit-tested; the components only draw.

import type { QueryResult } from "@dima/contracts";

const num = (v: unknown): number | null => {
  const n = typeof v === "number" ? v : Number(v);
  return v == null || v === "" || Number.isNaN(n) ? null : n;
};

// ── Trend number ─────────────────────────────────────────────────────────────

export interface TrendSummary {
  /** Latest period's value. */
  value: number;
  /** Label of the latest period (raw bucket value). */
  period: string;
  /** Previous period's value, if any. */
  previous: number | null;
  /** Relative change vs previous (0.12 = +12%), null when not computable. */
  change: number | null;
  /** Up to the last 12 values, oldest first (sparkline). */
  series: number[];
}

export function trendSummary(result: QueryResult, timeCol: string, measure: string): TrendSummary | null {
  const points = result.rows
    .map((r) => ({ t: String(r[timeCol] ?? ""), v: num(r[measure]) }))
    .filter((p): p is { t: string; v: number } => p.t !== "" && p.v !== null)
    .sort((a, b) => (a.t < b.t ? -1 : a.t > b.t ? 1 : 0));
  if (points.length === 0) return null;
  const last = points[points.length - 1];
  const prev = points.length > 1 ? points[points.length - 2].v : null;
  return {
    value: last.v,
    period: last.t,
    previous: prev,
    change: prev === null || prev === 0 ? null : (last.v - prev) / Math.abs(prev),
    series: points.slice(-12).map((p) => p.v),
  };
}

/** Measures where a decrease is the good direction (costs, downtime, defects). */
export const LOWER_IS_BETTER = /fire|durus|duruş|sapma|maliyet|tuketim|tüketim|hata|iade|gecikme|rework|tamir|borc/i;

// ── Meter ────────────────────────────────────────────────────────────────────

/** Share of goal reached, clamped to [0, 1] for the bar; `ratio` keeps the real value. */
export function meter(value: number, goal: number): { ratio: number; fill: number } {
  if (!(goal > 0)) return { ratio: 0, fill: 0 };
  const ratio = value / goal;
  return { ratio, fill: Math.max(0, Math.min(1, ratio)) };
}

// ── Funnel ───────────────────────────────────────────────────────────────────

export interface FunnelStep {
  label: string;
  value: number;
  /** value / first step's value. */
  ofFirst: number;
  /** value / previous step's value (1 for the first step). */
  ofPrevious: number;
}

/** Stages in query order (the query defines the stage order, as in the engine). */
export function funnelSteps(result: QueryResult, dim: string, measure: string): FunnelStep[] {
  const rows = result.rows
    .map((r) => ({ label: String(r[dim] ?? "—"), value: num(r[measure]) ?? 0 }))
    .filter((r) => r.value >= 0);
  const first = rows[0]?.value ?? 0;
  return rows.map((r, i) => ({
    ...r,
    ofFirst: first > 0 ? r.value / first : 0,
    ofPrevious: i === 0 ? 1 : rows[i - 1].value > 0 ? r.value / rows[i - 1].value : 0,
  }));
}

// ── Waterfall ────────────────────────────────────────────────────────────────

export interface WaterfallStep {
  label: string;
  value: number;
  /** Bar spans [low, high] on the value axis. */
  low: number;
  high: number;
  kind: "up" | "down" | "total";
}

/** Running total of signed contributions, with a final "Toplam" bar. */
export function waterfallSteps(result: QueryResult, dim: string, measure: string, totalLabel = "Toplam"): WaterfallStep[] {
  let running = 0;
  const steps: WaterfallStep[] = [];
  for (const r of result.rows) {
    const v = num(r[measure]);
    if (v === null) continue;
    const start = running;
    running += v;
    steps.push({
      label: String(r[dim] ?? "—"),
      value: v,
      low: Math.min(start, running),
      high: Math.max(start, running),
      kind: v >= 0 ? "up" : "down",
    });
  }
  if (steps.length) {
    steps.push({ label: totalLabel, value: running, low: Math.min(0, running), high: Math.max(0, running), kind: "total" });
  }
  return steps;
}

// ── Pivot totals ─────────────────────────────────────────────────────────────

/** Can values of this measure be summed? Ratios, percentages and averages can't. */
export function isAdditive(measure: string): boolean {
  return !/(yuzde|oran|oee|ortalama|avg|mean|_pct|percent|kullanilabilirlik|performans|kalite)/i.test(measure);
}
