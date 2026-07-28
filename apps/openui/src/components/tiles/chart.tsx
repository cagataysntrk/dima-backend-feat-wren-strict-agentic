"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AskResponse } from "@dima/contracts";
import { analyze, buildSeries, fmtAxis, fmtValue, type ChartKind } from "@dima/domain";

import { TileTitle } from "./shared";

/**
 * Grafik karosu.
 *
 * KRİTİK: grafik türü VARSAYILAN OLARAK `analyze()`'dan gelir — yani veri
 * şeklinden deterministik olarak. Model yalnız kullanıcı açıkça istediğinde
 * türü geçersiz kılar. Böylece en kötü senaryoda model kötü bir YERLEŞİM
 * üretir, ama her karo tek tek doğru kalır.
 */

// dataviz referans paleti (dima globals.css ile aynı sıra — CVD güvenliği
// slot SIRASINDAN gelir, tek tek renklerden değil).
const PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"];

const ALLOWED_KINDS = new Set<ChartKind>([
  "bar",
  "line",
  "area",
  "pie",
  "bar-stacked",
  "bar-h",
  "scatter",
  "radial",
  "radar",
]);

/**
 * Modelin verdiği grafik türünü DOĞRULAR.
 *
 * NEDEN GEREKLİ: OpenUI parser'ı enum üyeliğini denetlemiyor. Üretilen spec
 * yalnız imza METNİ taşıyor ("kind?: \"bar\" | \"line\" | …"), yapısal tip
 * değil — yani `ChartTile("q1", "sankey")` ayrıştırmadan sorunsuz geçiyor.
 * Enum, modele yalnız TAVSİYE; zorlama burada olmak zorunda.
 *
 * Tanınmayan tür sessizce sütuna düşürülmez; `analyze()`'ın deterministik
 * seçimine geri dönülür — o seçim zaten veri şekline en uygun olandır.
 * Modelin hatası, doğru davranışa düşmeli.
 */
export function resolveKind(requested: string | undefined, fallback: ChartKind): ChartKind {
  if (!requested) return fallback;
  return ALLOWED_KINDS.has(requested as ChartKind) ? (requested as ChartKind) : fallback;
}

export function Chart({
  response,
  kind,
  measure,
}: {
  response: AskResponse;
  kind?: string;
  measure?: string;
}) {
  if (!response.result?.rows.length) return <p className="muted">Veri yok.</p>;

  const a = analyze(response.result);
  const resolved = resolveKind(kind, a.kind);
  const data = buildSeries(response.result, a, resolved, measure ?? "");

  // heatmap/facet için Recharts primitifi yok; dima'da bunlar tabloya düşer.
  // Yanlış çizmektense çizmemek doğru — bozuk grafik, grafik yokluğundan kötüdür.
  if (!data) {
    return (
      <>
        <TileTitle>{response.question}</TileTitle>
        <p className="muted">Bu veri şekli ({resolved}) grafik olarak çizilemiyor — tablo kullan.</p>
      </>
    );
  }

  const axisFmt = (v: unknown) => fmtAxis(v, data.measure);
  const tipFmt = (v: unknown) => fmtValue(v, data.measure);

  return (
    <>
      <TileTitle>{response.question}</TileTitle>
      <div className="dima-chart">
        <ResponsiveContainer width="100%" height={220}>
          {renderChart(resolved, data, axisFmt, tipFmt)}
        </ResponsiveContainer>
      </div>
    </>
  );
}

type Data = NonNullable<ReturnType<typeof buildSeries>>;

function renderChart(
  kind: ChartKind,
  data: Data,
  axisFmt: (v: unknown) => string,
  tipFmt: (v: unknown) => string,
) {
  const grid = <CartesianGrid strokeDasharray="3 3" opacity={0.25} />;
  const x = <XAxis dataKey={data.xKey} tick={{ fontSize: 11 }} />;
  const y = <YAxis tickFormatter={axisFmt} tick={{ fontSize: 11 }} width={64} />;
  const tip = <Tooltip formatter={(v: unknown) => tipFmt(v)} />;

  if (kind === "pie" || kind === "radial") {
    return (
      <PieChart>
        <Tooltip formatter={(v: unknown) => tipFmt(v)} />
        <Pie data={data.data} dataKey="value" nameKey="name" outerRadius={80} label>
          {data.data.map((_, i) => (
            <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
          ))}
        </Pie>
      </PieChart>
    );
  }

  if (kind === "line") {
    return (
      <LineChart data={data.data}>
        {grid}
        {x}
        {y}
        {tip}
        {data.series.map((s, i) => (
          <Line
            key={s.key}
            dataKey={s.key}
            name={s.label}
            stroke={PALETTE[i % PALETTE.length]}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    );
  }

  if (kind === "area") {
    return (
      <AreaChart data={data.data}>
        {grid}
        {x}
        {y}
        {tip}
        {data.series.map((s, i) => (
          <Area
            key={s.key}
            dataKey={s.key}
            name={s.label}
            stroke={PALETTE[i % PALETTE.length]}
            fill={PALETTE[i % PALETTE.length]}
            fillOpacity={0.2}
          />
        ))}
      </AreaChart>
    );
  }

  // bar · bar-stacked · bar-h · diğer her şey sütuna düşer
  return (
    <BarChart data={data.data} layout={kind === "bar-h" ? "vertical" : "horizontal"}>
      {grid}
      {x}
      {y}
      {tip}
      {data.series.map((s, i) => (
        <Bar
          key={s.key}
          dataKey={s.key}
          name={s.label}
          fill={PALETTE[i % PALETTE.length]}
          stackId={kind === "bar-stacked" ? "a" : undefined}
          radius={[4, 4, 0, 0]}
        />
      ))}
    </BarChart>
  );
}
