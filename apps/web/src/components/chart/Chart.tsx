"use client";

import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
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
  type SeriesSpec,
} from "@dima/domain";
import { fmtAxis, fmtValue } from "@dima/domain";
import { ChartContainer, type ChartConfig } from "@/components/ui/chart";
import { cn } from "@/lib/utils";

const seriesColor = (i: number) => `var(--chart-${(i % 5) + 1})`;

/**
 * TIKLANIR LEJANT — bir seriyi gizler/gösterir.
 *
 * Kendi seri listesini çizer, Recharts'ın `payload`'ını KULLANMAZ: gizlenen seri
 * payload'dan düşerse geri açılamaz olurdu. Gizli seri soluk ve üstü çizili durur,
 * yani "buradaydı, kapattın" bilgisi kaybolmuyor.
 */
function InteractiveLegend({
  series,
  hidden,
  onToggle,
  colorOf,
}: {
  series: SeriesSpec[];
  hidden: ReadonlySet<string>;
  onToggle: (key: string) => void;
  colorOf: (key: string) => string;
}) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 pt-2 text-xs">
      {series.map((s) => {
        const off = hidden.has(s.key);
        return (
          <button
            key={s.key}
            type="button"
            onClick={() => onToggle(s.key)}
            aria-pressed={!off}
            title={off ? `${s.label} — göster` : `${s.label} — gizle`}
            className={cn(
              "flex cursor-pointer items-center gap-1.5 rounded-sm px-1 py-0.5 transition-colors",
              "hover:bg-accent focus-visible:ring-ring/50 focus-visible:ring-2 focus-visible:outline-none",
              off ? "text-muted-foreground/60 line-through" : "text-muted-foreground",
            )}
          >
            <span
              className="size-2 shrink-0 rounded-[2px] transition-opacity"
              style={{ background: colorOf(s.key), opacity: off ? 0.3 : 1 }}
            />
            {s.label}
            {/* kombo: bu seri hangi eksende çiziliyor */}
            {s.axis === "right" && (
              <span className="font-mono text-[9px] text-muted-foreground/70">sağ</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

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
 * the analysis logic lives in `@dima/domain`. Renders supported comparison,
 * trend, composition and relationship views through Recharts and CSS tokens.
 */
export function Chart({
  result,
  analysis,
  kind,
  measure,
  className,
  box: boxStyle,
}: {
  result: QueryResult;
  analysis: Analysis;
  kind: ChartKind;
  measure: string;
  className?: string;
  /** Kutu ölçüsü — SATIR İÇİ stil (bkz. ResultView.SIZE_BOX). Dinamik oran/yükseklik
   *  utility sınıfıyla verilince üretilen CSS'e girmiyor ve kutu 0 yükseklikte
   *  çöküyordu; bu yüzden ölçü sınıf değil stil olarak geçiyor. */
  box?: React.CSSProperties;
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

  // Lejanttan kapatılan seriler. Veri/tip değişince sıfırlanır — yoksa yeni bir
  // sonuçta eski seri adına takılı kalan gizleme sessizce seri yutar.
  const [hidden, setHidden] = useState<ReadonlySet<string>>(() => new Set());
  const signature = data?.series.map((s) => s.key).join("|") ?? "";
  const [lastSignature, setLastSignature] = useState(signature);
  if (signature !== lastSignature) {
    setLastSignature(signature);
    setHidden(new Set());
  }

  if (!data) return null;

  const colorIndex = new Map(data.series.map((s, i) => [s.key, i]));
  const colorOf = (key: string) => seriesColor(colorIndex.get(key) ?? 0);
  const toggle = (key: string) =>
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  const isOff = (key: string) => hidden.has(key);

  const yTick = (v: number) => fmtAxis(v, data.measure);
  const tip = <Tooltip content={<ChartTooltip data={data} />} cursor={{ fill: "var(--muted)", opacity: 0.4 }} />;
  const showLegend = data.series.length > 1;
  // Altta ortalanmış lejyon; etiketler uzunsa alt satıra sarar (ChartLegendContent
  // flex-wrap). Üstte-solda dururken y-ekseni etiketiyle çakışıyordu.
  const legend = showLegend ? (
    <Legend
      verticalAlign="bottom"
      align="center"
      content={
        <InteractiveLegend
          series={data.series}
          hidden={hidden}
          onToggle={toggle}
          colorOf={colorOf}
        />
      }
    />
  ) : null;

  // Varsayılan oran sınıf olarak kalır (statik, her zaman üretilir); çağıran bir
  // ölçü verdiyse satır içi stil onu ezer.
  const box = cn("aspect-[16/10] w-full", className);
  const boxProps = { className: box, style: boxStyle };

  // -- KOMBO (çapraz karşılaştırma) ---------------------------------------
  // Miktarlar SOL eksende sütun, farklı birimdeki ölçüler (%, oran) SAĞ eksende
  // çizgi. Tek eksende çizilseler oranlar miktarların yanında düz çizgi olurdu.
  if (kind === "combo") {
    const hasRight = data.series.some((s) => s.axis === "right" && !isOff(s.key));
    return (
      <ChartContainer config={config} {...boxProps}>
        <ComposedChart data={data.data} margin={{ left: 4, right: hasRight ? 4 : 12, top: 8, bottom: 0 }}>
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
          <YAxis
            yAxisId="left"
            domain={[(min: number) => Math.min(0, min), "auto"]}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={(v: number) => fmtAxis(v, data.measure)}
          />
          {/* Sağ eksen yalnız o eksende GÖRÜNÜR seri varsa çizilir. */}
          <YAxis
            yAxisId="right"
            orientation="right"
            hide={!hasRight}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={(v: number) => fmtAxis(v, data.rightMeasure ?? data.measure)}
          />
          {tip}
          {legend}
          {data.series
            .filter((s) => s.mark === "bar")
            .map((s) => (
              <Bar
                key={s.key}
                yAxisId="left"
                dataKey={s.key}
                hide={isOff(s.key)}
                fill={colorOf(s.key)}
                radius={[3, 3, 0, 0]}
                maxBarSize={34}
                isAnimationActive={false}
              />
            ))}
          {data.series
            .filter((s) => s.mark === "line")
            .map((s) => (
              <Line
                key={s.key}
                yAxisId="right"
                type="monotone"
                dataKey={s.key}
                hide={isOff(s.key)}
                stroke={colorOf(s.key)}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
                connectNulls
                isAnimationActive={false}
              />
            ))}
        </ComposedChart>
      </ChartContainer>
    );
  }

  // Pasta/radyal seri DEĞİL kategori taşır (tek dataKey, satır başına dilim), bu
  // yüzden lejant seriler yerine KATEGORİLER üzerinden kurulur ve gizleme veriyi
  // filtreler (`hide` prop'u dilim bazında yok). Kapatılan dilim toplamdan da
  // düşer — pastada beklenen davranış budur: kalanların payı yeniden hesaplanır.
  if (kind === "pie" || kind === "radial") {
    // buildSeries pasta/radyal için her satıra `name` yazar — anahtar odur.
    const cats = data.data.map((d, i) => ({ key: String(d.name), label: String(d.name), index: i }));
    const catColor = new Map(cats.map((c) => [c.key, seriesColor(c.index)]));
    const shown = data.data.filter((d) => !isOff(String(d.name)));
    const catLegend = (
      <Legend
        verticalAlign="bottom"
        align="center"
        content={
          <InteractiveLegend
            series={cats.map(({ key, label }) => ({ key, label }))}
            hidden={hidden}
            onToggle={toggle}
            colorOf={(k) => catColor.get(k) ?? seriesColor(0)}
          />
        }
      />
    );

    if (kind === "radial") {
      const rows = shown.map((d) => ({ ...d, fill: catColor.get(String(d.name)) }));
      return (
        <ChartContainer config={config} {...boxProps}>
          <RadialBarChart data={rows} innerRadius="28%" outerRadius="95%" startAngle={90} endAngle={-270}>
            <PolarAngleAxis type="number" domain={[0, "dataMax"]} tick={false} />
            <Tooltip content={<ChartTooltip data={data} />} />
            {catLegend}
            <RadialBar dataKey="value" background cornerRadius={6} isAnimationActive={false} />
          </RadialBarChart>
        </ChartContainer>
      );
    }

    return (
      <ChartContainer config={config} {...boxProps}>
        <PieChart>
          <Tooltip content={<ChartTooltip data={data} />} />
          {catLegend}
          <Pie
            data={shown}
            dataKey="value"
            nameKey="name"
            innerRadius="45%"
            outerRadius="72%"
            paddingAngle={2}
            stroke="var(--background)"
            strokeWidth={2}
            isAnimationActive={false}
          >
            {shown.map((d, i) => (
              <Cell key={i} fill={catColor.get(String(d.name))} />
            ))}
          </Pie>
        </PieChart>
      </ChartContainer>
    );
  }

  // Radar — az sayıda kategoride tek ölçünün profili (ör. makine bazında OEE).
  if (kind === "radar") {
    return (
      <ChartContainer config={config} {...boxProps}>
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
      <ChartContainer config={config} {...boxProps}>
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
            tickFormatter={(value: number) => fmtAxis(value, data.series[0]?.key ?? data.measure)}
          />
          <YAxis
            type="number"
            dataKey={yk}
            name={data.series[1]?.label ?? data.series[0]?.label}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={(value: number) => fmtAxis(value, data.series[1]?.key ?? data.measure)}
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
      <ChartContainer config={config} {...boxProps}>
        <BarChart data={data.data} layout="vertical" margin={{ left: 8, right: 16, top: 8, bottom: 0 }}>
          <CartesianGrid horizontal={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis
            type="number"
            domain={[(min: number) => Math.min(0, min), "auto"]}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            tickFormatter={yTick}
          />
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
          {data.series.map((s) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              hide={isOff(s.key)}
              fill={colorOf(s.key)}
              radius={[0, 4, 4, 0]}
              maxBarSize={26}
              isAnimationActive={false}
            />
          ))}
        </BarChart>
      </ChartContainer>
    );
  }

  // Yığılmış sütun — parça/bütün. (Oran metriklerinde yanıltıcıdır; otomatik seçilmez.)
  if (kind === "bar-stacked") {
    return (
      <ChartContainer config={config} {...boxProps}>
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
          <YAxis
            domain={[(min: number) => Math.min(0, min), "auto"]}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={yTick}
          />
          {tip}
          {legend}
          {data.series.map((s, i) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              stackId="a"
              hide={isOff(s.key)}
              fill={colorOf(s.key)}
              radius={
                i === data.series.findLastIndex((x) => !isOff(x.key))
                  ? [4, 4, 0, 0]
                  : [0, 0, 0, 0]
              }
              maxBarSize={44}
              isAnimationActive={false}
            />
          ))}
        </BarChart>
      </ChartContainer>
    );
  }

  if (kind === "line") {
    return (
      <ChartContainer config={config} {...boxProps}>
        <LineChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} />
          <YAxis
            domain={[(min: number) => Math.min(0, min), "auto"]}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={yTick}
          />
          {tip}
          {legend}
          {data.series.map((s) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              hide={isOff(s.key)}
              stroke={colorOf(s.key)}
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
      <ChartContainer config={config} {...boxProps}>
        <BarChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} interval={0} angle={data.data.length > 8 ? -30 : 0} textAnchor={data.data.length > 8 ? "end" : "middle"} height={data.data.length > 8 ? 52 : 30} />
          <YAxis
            domain={[(min: number) => Math.min(0, min), "auto"]}
            tick={axisTick}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={yTick}
          />
          {tip}
          <Bar dataKey={data.series[0].key} fill={colorOf(data.series[0].key)} radius={[5, 5, 0, 0]} maxBarSize={48} isAnimationActive={false} />
        </BarChart>
      </ChartContainer>
    );
  }

  if (kind === "bar") {
    // grouped bars (second dimension or multi-measure)
    return (
      <ChartContainer config={config} {...boxProps}>
        <BarChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
          <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} interval={0} angle={data.data.length > 8 ? -30 : 0} textAnchor={data.data.length > 8 ? "end" : "middle"} height={data.data.length > 8 ? 52 : 30} />
          <YAxis tick={axisTick} tickLine={false} axisLine={false} width={48} tickFormatter={yTick} />
          {tip}
          {legend}
          {data.series.map((s) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              hide={isOff(s.key)}
              fill={colorOf(s.key)}
              radius={[3, 3, 0, 0]}
              maxBarSize={34}
              isAnimationActive={false}
            />
          ))}
        </BarChart>
      </ChartContainer>
    );
  }

  // fallback: area (only reached if a caller passes an unexpected kind we can chart)
  return (
    <ChartContainer config={config} {...boxProps}>
      <AreaChart data={data.data} margin={{ left: 4, right: 12, top: 8, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke={GRID} strokeOpacity={0.6} />
        <XAxis dataKey={data.xKey} tick={axisTick} tickLine={false} axisLine={false} tickMargin={8} />
        <YAxis
          tick={axisTick}
          tickLine={false}
          axisLine={false}
          width={48}
          tickFormatter={yTick}
        />
        {tip}
        {legend}
        {data.series.map((s) => (
          <Area
            key={s.key}
            type="monotone"
            dataKey={s.key}
            hide={isOff(s.key)}
            stroke={colorOf(s.key)}
            fill={colorOf(s.key)}
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
