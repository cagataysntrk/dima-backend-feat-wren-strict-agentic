"use client";

import { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { KpiCard } from "@dima/contracts";
import {
  ChartContainer,
  ChartLegendContent,
  type ChartConfig,
} from "@dima/ui/chart/chart-container";
import { Card } from "@dima/ui/primitives/card";

const GRAN_TR: Record<string, string> = {
  day: "günlük", week: "haftalık", month: "aylık", quarter: "çeyreklik", year: "yıllık",
};

// Cross-cube KPI kartı (CCC / likidite oranları): tek headline skaler + bileşenleri
// (DSO/DIO/DPO, dönen varlık/KV kaynak…) + formül + açıklama. Cube tablosu değil bileşke.
//
// NOT: trend grafiği ECharts'tan Recharts'a taşındı (tek motor — bkz. chart/Chart.tsx).
// Renkler artık --chart-* token'larından gelir, böylece koyu/açık tema otomatik doğru.

function fmt(v: number | null | undefined, unit?: string | null): string {
  if (v === null || v === undefined) return "—";
  const s = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 2 }).format(v);
  if (!unit) return s;
  if (unit === "%") return `%${s}`;
  if (unit === "₺") return `${s} ₺`;
  return `${s} ${unit}`;
}

// Etiketten kısa ad: "Alacak Tahsil Süresi (DSO)" → "DSO"; parantez yoksa etiketin kendisi.
function shortName(label: string): string {
  const m = label.match(/\(([^)]+)\)\s*$/);
  return m ? m[1] : label;
}

const seriesColor = (i: number) => `var(--chart-${(i % 5) + 1})`;

export function KpiCardView({ card }: { card: KpiCard }) {
  const series = (card.series ?? []).filter((s) => s.value !== null && s.value !== undefined);
  const gran = card.granularity ? (GRAN_TR[card.granularity] ?? card.granularity) : null;
  const unit = card.unit ?? "";

  // Bileşenler headline ile AYNI birimde mi? (öyleyse ayrı çizgi mantıklı — aynı eksen)
  // Farklı birim (likidite: ₺ vs oran) → skala bozulmasın diye yalnız headline.
  const { rows, lines, config } = useMemo(() => {
    const comps = series[0]?.components ?? [];
    const plotComps = comps.length > 0 && comps.every((c) => (c.unit ?? "") === unit);

    const defs = [
      { key: "__head__", label: shortName(card.label), head: true },
      ...(plotComps ? comps.map((c) => ({ key: c.key, label: shortName(c.label), head: false })) : []),
    ];

    const data = series.map((s) => {
      const row: Record<string, string | number | null> = { bucket: s.bucket, __head__: s.value };
      if (plotComps) {
        for (const c of comps) {
          row[c.key] = s.components?.find((x) => x.key === c.key)?.value ?? null;
        }
      }
      return row;
    });

    const cfg: ChartConfig = {};
    defs.forEach((d, i) => {
      cfg[d.key] = { label: d.label, color: d.head ? "var(--brand)" : seriesColor(i) };
    });

    return { rows: data, lines: defs, config: cfg };
  }, [series, card.label, unit]);

  const n = (v: number) => {
    const s = new Intl.NumberFormat("tr-TR", {
      notation: Math.abs(v) >= 10000 ? "compact" : "standard",
      maximumFractionDigits: 1,
    }).format(v);
    return unit === "%" ? `%${s}` : unit ? `${s} ${unit}` : s;
  };
  const axisTick = { fill: "var(--muted-foreground)", fontSize: 11 };

  return (
    <Card className="gap-0 p-5">
      <div className="flex items-center justify-between">
        <span className="text-[10px] tracking-wider text-muted-foreground uppercase">
          KPI{gran ? ` · ${gran} trend` : ""}
        </span>
        {card.lower_is_better && (
          <span
            className="text-[10px] tracking-wider text-muted-foreground"
            title="Düşük değer daha iyi"
          >
            ↓ düşük iyi
          </span>
        )}
      </div>

      <div className="mt-1 flex items-baseline gap-3">
        <span className="text-3xl font-semibold text-foreground tabular-nums">
          {fmt(card.value, card.unit)}
        </span>
        <span className="text-sm text-muted-foreground">
          {card.label}
          {gran && <span className="text-muted-foreground/70"> · son dönem</span>}
        </span>
      </div>

      {series.length > 1 && (
        <ChartContainer config={config} className="mt-4 aspect-[16/7] w-full">
          <LineChart data={rows} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--border)" strokeOpacity={0.6} />
            <XAxis
              dataKey="bucket"
              tick={axisTick}
              tickLine={false}
              axisLine={false}
              tickMargin={8}
            />
            <YAxis
              tick={axisTick}
              tickLine={false}
              axisLine={false}
              width={52}
              tickFormatter={n}
            />
            <Tooltip
              formatter={(v) => n(Number(v))}
              contentStyle={{
                background: "var(--popover)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-md)",
                fontSize: 12,
              }}
            />
            {lines.length > 1 && (
              <Legend
                verticalAlign="bottom"
                align="center"
                content={<ChartLegendContent />}
                wrapperStyle={{ fontSize: 12 }}
              />
            )}
            {lines.map((l, i) => (
              <Line
                key={l.key}
                type="monotone"
                dataKey={l.key}
                name={l.key}
                stroke={l.head ? "var(--brand)" : seriesColor(i)}
                strokeWidth={l.head ? 2.5 : 1.5}
                strokeDasharray={l.head ? undefined : "4 3"}
                dot={false}
                activeDot={{ r: 4 }}
                connectNulls
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ChartContainer>
      )}

      {card.components?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-3 border-t border-border pt-4">
          {card.components.map((c) => (
            <div key={c.key} className="flex flex-col">
              <span className="text-[11px] text-muted-foreground">{c.label}</span>
              <span className="font-mono text-sm text-foreground tabular-nums">
                {fmt(c.value, c.unit)}
              </span>
            </div>
          ))}
        </div>
      )}

      {card.formula && (
        <div className="mt-3 font-mono text-[11px] text-muted-foreground">= {card.formula}</div>
      )}
      {card.explain && (
        <p className="mt-3 max-w-prose text-xs leading-relaxed whitespace-pre-line text-muted-foreground">
          {card.explain}
        </p>
      )}
    </Card>
  );
}
