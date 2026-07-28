"use client";

import { useMemo } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  RadialBar,
  RadialBarChart,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import type { QueryResult } from "@dima/contracts";
import {
  buildSeries,
  type Analysis,
  type ChartData,
  type ChartKind,
} from "@dima/domain";
import { fmtAxis, fmtValue } from "@dima/domain";
import { ChartContainer, ChartLegendContent, type ChartConfig } from "@/components/ui/chart";
import { cn } from "@/lib/utils";

const seriesColor = (i: number) => `var(--chart-${(i % 5) + 1})`;

/** Themed tooltip that formats each value with its measure unit (₺, kg, %…). */
function ChartTooltip({
  active,
  payload,
  label,
  data,
}: {
  active?: boolean;
  payload?: { name?: string; dataKey?: string; value?: number | null; color?: string }[];
  label?: string;
  data: ChartData;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="grid min-w-[9rem] gap-1.5 rounded-lg border border-border/60 bg-popover px-2.5 py-2 text-xs shadow-lg">
      {label != null && <div className="font-medium text-foreground">{label}</div>}
      <div className="grid gap-1">
        {payload
          .filter((p) => p.value != null)
          .map((p, i) => {
            const key = String(p.dataKey ?? p.name ?? "");
            const unitCol = data.multiMeasure ? key : data.measure;
            const label = data.series.find((s) => s.key === key)?.label ?? key;
            return (
              <div key={i} className="flex items-center justify-between gap-3">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <span
                    className="size-2 shrink-0 rounded-[2px]"
                    style={{ background: p.color }}
                  />
                  {label}
                </span>
                <span className="font-mono font-medium tabular-nums text-foreground">
                  {fmtValue(p.value, unitCol)}
                </span>
              </div>
            );
          })}
      </div>
    </div>
  );
}

const axisTick = { fontSize: 11 } as const;
const GRID = "var(--border)";

/**
 * Engine-agnostic chart façade. Callers pass a QueryResult + Analysis + kind;
 * the analysis logic lives in `@/lib/chart`. Renders bar/line/area/pie via
 * Recharts (themed by CSS-var chart tokens). heatmap/facet return a table hint.
 */
export function Chart({
  result,
  analysis,
  kind,
  measure,
  className,
}: {
  result: QueryResult;
  analysis: Analysis;
  kind: ChartKind;
  measure: string;
  className?: string;
}) {
  const data = useMemo(
    () => buildSeries(result, analysis, kind, measure),
    [result, analysis, kind, measure],
  );

  const config = useMemo<ChartConfig>(() => {
    const c: ChartConfig = {};
    data?.series.forEach((s, i) => {
      c[s.key] = { label: s.label, color: seriesColor(i) };
    });
    return c;
  }, [data]);

  if (!data) return null;

  const yTick = (v: number) => fmtAxis(v, data.measure);
  const tip = <Tooltip content={<ChartTooltip data={data} />} cursor={{ fill: "var(--muted)", opacity: 0.4 }} />;
  const showLegend = data.series.length > 1;
  // Altta ortalanmış lejyon; etiketler uzunsa alt satıra sarar (ChartLegendContent
  // flex-wrap). Üstte-solda dururken y-ekseni etiketiyle çakışıyordu.
  const legend = showLegend ? (
    <Legend
      verticalAlign="bottom"
      align="center"
      content={<ChartLegendContent />}
      wrapperStyle={{ fontSize: 12 }}
    />
  ) : null;

  const box = cn("aspect-[16/10] w-full", className);

  if (kind === "pie") {
    return (
      <ChartContainer config={config} className={box}>
        <PieChart>
          <Tooltip content={<ChartTooltip data={data} />} />
          <Legend
            verticalAlign="bottom"
            align="center"
            content={<ChartLegendContent nameKey="name" />}
            wrapperStyle={{ fontSize: 12 }}
          />
          <Pie
            data={data.data}
            dataKey="value"
            nameKey="name"
            innerRadius="45%"
            outerRadius="72%"
            paddingAngle={2}
            stroke="var(--background)"
            strokeWidth={2}
          >
            {data.data.map((_, i) => (
              <Cell key={i} fill={seriesColor(i)} />
            ))}
          </Pie>
        </PieChart>
      </ChartContainer>
    );
  }

  // Radyal — tek seri, az kategori. Kategori başına bir halka.
  if (kind === "radial") {
    // buildSeries pasta ile aynı ad/değer şeklini döndürür → nameKey "name".
    const rows = data.data.map((d, i) => ({ ...d, fill: seriesColor(i) }));
    return (
      <ChartContainer config={config} className={box}>
        <RadialBarChart data={rows} innerRadius="28%" outerRadius="95%" startAngle={90} endAngle={-270}>
          <PolarAngleAxis type="number" domain={[0, "dataMax"]} tick={false} />
          <Tooltip content={<ChartTooltip data={data} />} />
          <Legend
            verticalAlign="bottom"
            align="center"
            content={<ChartLegendContent nameKey="name" />}
            wrapperStyle={{ fontSize: 12 }}
          />
          <RadialBar dataKey="value" background cornerRadius={6} isAnimationActive={false} />
        </RadialBarChart>
      </ChartContainer>
    );
  }

  // Radar — az sayıda kategoride tek ölçünün profili (ör. makine bazında OEE).
  if (kind === "radar") {
    return (
      <ChartContainer config={config} className={box}>
        <RadarChart data={data.data} outerRadius="72%">
          <PolarGrid stroke={GRID} strokeOpacity={0.7} />
          <PolarAngleAxis dataKey="name" tick={axisTick} />
          <PolarRadiusAxis tick={false} axisLine={false} tickFormatter={yTick} />
          <Tooltip content={<ChartTooltip data={data} />} />
          <Radar
            dataKey="value"
            stroke="var(--chart-1)"
            fill="var(--chart-1)"
            fillOpacity={0.22}
            strokeWidth={2}
            isAnimationActive={false}
          />
        </RadarChart>
      </ChartContainer>
    );
  }

  // Dağılım — ilk iki ölçüyü x/y olarak karşılaştırır (korelasyon bakışı).
  if (kind === "scatter") {
    const xk = data.series[0]?.key;
    const yk = data.series[1]?.key ?? xk;
    return (
      <ChartContainer config={config} className={box}>
        <ScatterChart margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid stroke={GRID} strokeOpacity={0.6} />
          <XAxis
            type="number"
            dataKey={xk}
            name={data.series[0]?.label}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            tickFormatter={yTick}
          />
          <YAxis
            type="number"
            dataKey={yk}
            name={data.series[1]?.label ?? data.series[0]?.label}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={yTick}
          />
          <ZAxis range={[60, 60]} />
          {tip}
          <Scatter data={data.data} fill={seriesColor(0)} isAnimationActive={false} />
        </ScatterChart>
      </ChartContainer>
    );
  }

  // Yatay sütun — uzun kategori etiketleri için (etiketler kırpılmadan okunur).
  if (kind === "bar-h") {
    const longest = data.data.reduce(
      (n, d) => Math.max(n, String(d[data.xKey] ?? "").length),
      0,
    );
    const catWidth = Math.min(160, Math.max(44, longest * 7 + 12));
    return (
      <ChartContainer config={config} className={box}>
        <BarChart data={data.data} layout="vertical" margin={{ left: 8, right: 16, top: 8, bottom: 0 }}>
          <CartesianGrid horizontal={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis type="number" tick={axisTick} tickLine={false} axisLine={false} tickFormatter={yTick} />
          <YAxis
            type="category"
            dataKey={data.xKey}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={catWidth}
          />
          {tip}
          {legend}
          {data.series.map((s, i) => (
            <Bar key={s.key} dataKey={s.key} fill={seriesColor(i)} radius={[0, 4, 4, 0]} maxBarSize={26} />
          ))}
        </BarChart>
      </ChartContainer>
    );
  }

  // Yığılmış sütun — parça/bütün. (Oran metriklerinde yanıltıcıdır; otomatik seçilmez.)
  if (kind === "bar-stacked") {
    return (
      <ChartContainer config={config} className={box}>
        <BarChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis
            dataKey={data.xKey}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            interval={0}
            angle={data.data.length > 8 ? -30 : 0}
            textAnchor={data.data.length > 8 ? "end" : "middle"}
            height={data.data.length > 8 ? 52 : 30}
          />
          <YAxis tick={axisTick} tickLine={false} axisLine={false} width={48} tickFormatter={yTick} />
          {tip}
          {legend}
          {data.series.map((s, i) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              stackId="a"
              fill={seriesColor(i)}
              radius={i === data.series.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]}
              maxBarSize={44}
            />
          ))}
        </BarChart>
      </ChartContainer>
    );
  }

  if (kind === "line") {
    return (
      <ChartContainer config={config} className={box}>
        <LineChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} />
          <YAxis tick={axisTick} tickLine={false} axisLine={false} width={48} tickFormatter={yTick} />
          {tip}
          {legend}
          {data.series.map((s, i) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              stroke={seriesColor(i)}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              connectNulls
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ChartContainer>
    );
  }

  if (kind === "bar" && data.series.length === 1) {
    // single series → subtle area fill reads more editorial than a lone bar row? keep bar.
    return (
      <ChartContainer config={config} className={box}>
        <BarChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} interval={0} angle={data.data.length > 8 ? -30 : 0} textAnchor={data.data.length > 8 ? "end" : "middle"} height={data.data.length > 8 ? 52 : 30} />
          <YAxis tick={axisTick} tickLine={false} axisLine={false} width={48} tickFormatter={yTick} />
          {tip}
          <Bar dataKey={data.series[0].key} fill={seriesColor(0)} radius={[5, 5, 0, 0]} maxBarSize={48} />
        </BarChart>
      </ChartContainer>
    );
  }

  if (kind === "bar") {
    // grouped bars (second dimension or multi-measure)
    return (
      <ChartContainer config={config} className={box}>
        <BarChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} interval={0} angle={data.data.length > 8 ? -30 : 0} textAnchor={data.data.length > 8 ? "end" : "middle"} height={data.data.length > 8 ? 52 : 30} />
          <YAxis tick={axisTick} tickLine={false} axisLine={false} width={48} tickFormatter={yTick} />
          {tip}
          {legend}
          {data.series.map((s, i) => (
            <Bar key={s.key} dataKey={s.key} fill={seriesColor(i)} radius={[3, 3, 0, 0]} maxBarSize={34} />
          ))}
        </BarChart>
      </ChartContainer>
    );
  }

  // fallback: area (only reached if a caller passes an unexpected kind we can chart)
  return (
    <ChartContainer config={config} className={box}>
      <AreaChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
        <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} />
        <YAxis tick={axisTick} tickLine={false} axisLine={false} width={48} tickFormatter={yTick} />
        {tip}
        {legend}
        {data.series.map((s, i) => (
          <Area
            key={s.key}
            type="monotone"
            dataKey={s.key}
            stroke={seriesColor(i)}
            fill={seriesColor(i)}
            fillOpacity={0.15}
            strokeWidth={2}
            connectNulls
            isAnimationActive={false}
          />
        ))}
      </AreaChart>
    </ChartContainer>
  );
}
