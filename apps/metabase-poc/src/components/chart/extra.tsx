"use client";

// Extra chart forms (feature 3): trend number, meter, funnel, waterfall.
// Built to the dataviz skill's specs: thin marks, direct labels (the light-mode
// palette has sub-3:1 slots, so values are always printed), text in text
// tokens, series color only on marks, recessive grid, one axis.

import { useMemo } from "react";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, LabelList, Tooltip, XAxis, YAxis } from "recharts";
import type { QueryResult } from "@dima/contracts";
import { fmtAxis, fmtTemporal, fmtValue } from "@dima/domain";
import { ChartContainer } from "@/components/ui/chart";
import { cn } from "@/lib/utils";
import { LOWER_IS_BETTER, funnelSteps, meter, trendSummary, waterfallSteps } from "@/lib/viz";

const pct = (x: number) =>
  new Intl.NumberFormat("tr-TR", { style: "percent", maximumFractionDigits: x !== 0 && Math.abs(x) < 0.1 ? 1 : 0 }).format(x);

// ── Trend number (stat tile) ─────────────────────────────────────────────────

export function TrendNumber({ result, timeCol, measure }: { result: QueryResult; timeCol: string; measure: string }) {
  const t = useMemo(() => trendSummary(result, timeCol, measure), [result, timeCol, measure]);
  if (!t) return <p className="text-sm text-muted-foreground">Gösterilecek dönem yok.</p>;
  const lowerIsBetter = LOWER_IS_BETTER.test(measure);
  const good = t.change === null || t.change === 0 ? null : t.change > 0 !== lowerIsBetter;
  const Arrow = t.change === null || t.change === 0 ? Minus : t.change > 0 ? ArrowUpRight : ArrowDownRight;
  const period = fmtTemporal(t.period, timeCol) ?? t.period;

  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div className="space-y-1">
        <div className="text-3xl font-semibold tracking-tight tabular-nums">{fmtValue(t.value, measure)}</div>
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <Arrow
            className={cn(
              "size-4",
              good === true && "text-emerald-600 dark:text-emerald-400",
              good === false && "text-red-600 dark:text-red-400",
            )}
            aria-hidden
          />
          <span className="tabular-nums">
            {t.change === null ? "Karşılaştırma yok" : `${t.change > 0 ? "+" : ""}${pct(t.change)}`}
          </span>
          <span>
            · {period}
            {t.previous !== null && `, önceki dönem ${fmtValue(t.previous, measure)}`}
          </span>
        </div>
      </div>
      <Sparkline values={t.series} label={`${measure} son ${t.series.length} dönem`} />
    </div>
  );
}

/** 12-point sparkline: history in the de-emphasis ink, the latest point in the accent. */
function Sparkline({ values, label }: { values: number[]; label: string }) {
  if (values.length < 2) return null;
  const w = 120;
  const h = 36;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const pts = values.map((v, i) => [(i / (values.length - 1)) * (w - 4) + 2, h - 3 - ((v - min) / span) * (h - 6)] as const);
  const d = pts.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const [lx, ly] = pts[pts.length - 1];
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} role="img" aria-label={label} className="shrink-0 overflow-visible">
      <path d={d} fill="none" stroke="var(--muted-foreground)" strokeOpacity={0.55} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={lx} cy={ly} r={4} fill="var(--chart-1)" stroke="var(--card)" strokeWidth={2} />
    </svg>
  );
}

// ── Meter ────────────────────────────────────────────────────────────────────

export function Meter({ value, goal, measure }: { value: number; goal: number; measure: string }) {
  const { ratio, fill } = meter(value, goal);
  const done = ratio >= 1;
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="text-3xl font-semibold tracking-tight tabular-nums">{fmtValue(value, measure)}</span>
        <span className="text-sm text-muted-foreground tabular-nums">
          Hedef {fmtValue(goal, measure)} · %{new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 }).format(ratio * 100)}
        </span>
      </div>
      {/* Track = lighter step of the same hue, so state reads across the whole bar. */}
      <div
        role="meter"
        aria-valuemin={0}
        aria-valuemax={goal}
        aria-valuenow={value}
        aria-label="Hedefe göre ilerleme"
        className="h-3 overflow-hidden rounded-full bg-[color-mix(in_oklch,var(--chart-1)_18%,transparent)]"
      >
        <div
          className="h-full rounded-full bg-[var(--chart-1)] transition-[width] duration-500 ease-out motion-reduce:transition-none"
          style={{ width: `${fill * 100}%` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">
        {done ? "Hedefe ulaşıldı." : `Hedefe ${fmtValue(goal - value, measure)} kaldı.`}
      </p>
    </div>
  );
}

// ── Funnel ───────────────────────────────────────────────────────────────────

export function Funnel({ result, dim, measure }: { result: QueryResult; dim: string; measure: string }) {
  const steps = useMemo(() => funnelSteps(result, dim, measure), [result, dim, measure]);
  if (steps.length === 0) return <p className="text-sm text-muted-foreground">Gösterilecek aşama yok.</p>;
  return (
    <ol className="space-y-1.5" aria-label="Huni">
      {steps.map((s, i) => (
        <li key={s.label} className="space-y-1">
          {i > 0 && (
            <p className="pl-1 text-xs text-muted-foreground tabular-nums">
              ↓ bir önceki aşamanın {pct(s.ofPrevious)}’i
            </p>
          )}
          <div className="grid grid-cols-[minmax(6rem,10rem)_1fr] items-center gap-3">
            <span className="truncate text-sm" title={s.label}>
              {s.label}
            </span>
            <div className="flex items-center gap-2">
              <div className="h-7 min-w-1 rounded-[4px] bg-[var(--chart-1)]" style={{ width: `${Math.max(s.ofFirst * 100, 1)}%` }} />
              <span className="shrink-0 text-sm tabular-nums">
                {fmtValue(s.value, measure)}
                <span className="ml-1.5 text-xs text-muted-foreground">{pct(s.ofFirst)}</span>
              </span>
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}

// ── Waterfall ────────────────────────────────────────────────────────────────

// Increase / decrease carry polarity (two distinct hues); the total is neutral ink.
const WATERFALL_FILL = { up: "var(--chart-1)", down: "var(--chart-2)", total: "var(--muted-foreground)" } as const;

export function Waterfall({
  result,
  dim,
  measure,
  box,
}: {
  result: QueryResult;
  dim: string;
  measure: string;
  box?: React.CSSProperties;
}) {
  const steps = useMemo(() => waterfallSteps(result, dim, measure), [result, dim, measure]);
  // Stacked bar: an invisible base up to `low`, then the visible span low→high.
  const data = steps.map((s) => ({ ...s, base: s.low, span: s.high - s.low }));
  return (
    <div className="space-y-2">
      <ChartContainer config={{ span: { label: measure } }} className="w-full" style={box}>
        <BarChart data={data} margin={{ left: 4, right: 12, top: 20, bottom: 0 }} barCategoryGap="20%">
          <CartesianGrid vertical={false} stroke="var(--border)" strokeOpacity={0.6} />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} interval={0} />
          <YAxis
            tick={{ fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={52}
            tickFormatter={(v: number) => fmtAxis(v, measure)}
          />
          <Tooltip
            cursor={{ fill: "var(--muted)", opacity: 0.4 }}
            content={({ active, payload }) => {
              const s = active ? (payload?.[0]?.payload as (typeof data)[number] | undefined) : undefined;
              if (!s) return null;
              return (
                <div className="rounded-lg border border-[var(--surface-edge)] bg-popover px-2.5 py-2 text-xs shadow-[var(--surface-shadow-raised)]">
                  <div className="font-medium">{s.label}</div>
                  <div className="tabular-nums text-muted-foreground">
                    {s.kind === "total" ? "Toplam" : s.value >= 0 ? "Artış" : "Azalış"}: {fmtValue(s.value, measure)}
                  </div>
                </div>
              );
            }}
          />
          <Bar dataKey="base" stackId="w" fill="transparent" isAnimationActive={false} />
          <Bar dataKey="span" stackId="w" radius={[4, 4, 4, 4]} isAnimationActive={false}>
            {data.map((s) => (
              <Cell key={s.label} fill={WATERFALL_FILL[s.kind]} />
            ))}
            <LabelList
              dataKey="value"
              position="top"
              className="fill-foreground text-[11px] tabular-nums"
              formatter={(v: unknown) => fmtAxis(Number(v), measure)}
            />
          </Bar>
        </BarChart>
      </ChartContainer>
      <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
        <LegendDot color={WATERFALL_FILL.up} label="Artış" />
        <LegendDot color={WATERFALL_FILL.down} label="Azalış" />
        <LegendDot color={WATERFALL_FILL.total} label="Toplam" />
      </div>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="size-2 rounded-[2px]" style={{ background: color }} aria-hidden />
      {label}
    </span>
  );
}
