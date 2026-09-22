"use client";

import { useMemo, useState } from "react";
import type { EChartsOption } from "echarts";
import { EChart } from "@/components/EChart";
import { ResultTable } from "@/components/ResultTable";
import type { QueryResult } from "@/lib/types";

type ViewMode = "chart" | "table";

function isIdentifier(column: string): boolean {
  return /(?:^|_)(id|kod|kodu|no|ref)(?:$|_)/i.test(column);
}

function numeric(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return null;
}

function inferChart(result: QueryResult): {
  option: EChartsOption;
  x: string;
  y: string;
} | null {
  if (result.row_count < 2 || result.rows.length < 2 || result.rows.length > 100) return null;

  const numericColumns = result.columns.filter((column) => {
    if (isIdentifier(column)) return false;
    const values = result.rows.map((row) => numeric(row[column])).filter((value) => value !== null);
    return values.length >= Math.max(2, Math.ceil(result.rows.length * 0.8));
  });

  const y = numericColumns[0];
  if (!y) return null;

  const dimensionColumns = result.columns.filter((column) => column !== y && !numericColumns.includes(column));
  const x =
    dimensionColumns.find((column) => /(date|time|tarih|gun|ay|hafta|year|month)/i.test(column)) ??
    dimensionColumns[0];

  if (!x) return null;

  const points = result.rows
    .map((row) => ({ label: row[x], value: numeric(row[y]) }))
    .filter((point) => point.label !== null && point.label !== undefined && point.value !== null);

  if (points.length < 2) return null;

  const temporal = /(date|time|tarih|gun|ay|hafta|year|month)/i.test(x);

  return {
    x,
    y,
    option: {
      animation: false,
      tooltip: { trigger: "axis" },
      grid: { left: 52, right: 20, top: 24, bottom: 48 },
      xAxis: {
        type: "category",
        data: points.map((point) => String(point.label)),
        axisLabel: { hideOverlap: true },
      },
      yAxis: { type: "value" },
      series: [
        {
          type: temporal ? "line" : "bar",
          data: points.map((point) => point.value),
          smooth: temporal,
          symbolSize: 6,
        },
      ],
    },
  };
}

export function FastResultCard({
  result,
}: {
  result: QueryResult;
}) {
  const chart = useMemo(() => inferChart(result), [result]);
  const [view, setView] = useState<ViewMode>(chart ? "chart" : "table");

  return (
    <section
      aria-labelledby="fast-result-heading"
      className="border border-hairline bg-background p-4 shadow-[var(--shadow-1)] sm:p-5"
    >
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
            rendering proof · real Metabase fixture
          </p>
          <h2 id="fast-result-heading" className="mt-1 text-base font-medium">
            Analitik sonuç
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-neutral-500">
            Bu kart yalnız sonuç sunumunu kanıtlar; AI bulgusu veya kök neden iddiası üretmez.
          </p>
        </div>

        <div className="flex border border-hairline p-0.5" aria-label="Sonuç görünümü">
          <button
            type="button"
            disabled={!chart}
            aria-pressed={view === "chart"}
            onClick={() => chart && setView("chart")}
            className="px-3 py-1.5 font-mono text-[11px] disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)] data-[active=true]:bg-foreground data-[active=true]:text-background"
            data-active={view === "chart"}
          >
            Grafik
          </button>
          <button
            type="button"
            aria-pressed={view === "table"}
            onClick={() => setView("table")}
            className="px-3 py-1.5 font-mono text-[11px] data-[active=true]:bg-foreground data-[active=true]:text-background"
            data-active={view === "table"}
          >
            Tablo
          </button>
        </div>
      </div>

      {view === "chart" && chart ? (
        <div data-fast-chart>
          <div className="mb-2 flex gap-4 font-mono text-[10px] text-neutral-500">
            <span>x: {chart.x}</span>
            <span>y: {chart.y}</span>
          </div>
          <EChart option={chart.option} aspect={0.42} minHeight={240} maxHeight={360} />
        </div>
      ) : (
        <div data-fast-table>
          <ResultTable result={result} />
        </div>
      )}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-hairline pt-3 font-mono text-[10px] text-neutral-500">
        <span>{result.row_count} satırlık sentetik örnek</span>
        <span>chart-safe değilse tabloya düşer</span>
      </div>
    </section>
  );
}
