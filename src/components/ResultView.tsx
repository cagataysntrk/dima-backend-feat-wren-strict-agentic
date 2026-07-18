"use client";

import { useEffect, useMemo, useState } from "react";
import type { QueryResult } from "@/lib/types";
import { analyze, buildOption, kpiCards, type ChartKind } from "@/lib/chart";
import { EChart } from "./EChart";
import { ResultTable } from "./ResultTable";

const TYPE_LABEL: Record<ChartKind, string> = {
  bar: "Sütun",
  line: "Çizgi",
  pie: "Pasta",
  heatmap: "Isı haritası",
  kpi: "KPI",
  none: "—",
};

export function ResultView({ result }: { result: QueryResult }) {
  const a = useMemo(() => analyze(result), [result]);
  const chartable = a.kind !== "none" && a.kind !== "kpi";

  const [view, setView] = useState<"chart" | "table">(a.kind === "none" ? "table" : "chart");
  const [type, setType] = useState<ChartKind>(a.kind);
  const [measure, setMeasure] = useState<string>(a.measures[0] ?? "");
  const [dark, setDark] = useState(false);

  // yeni sonuç geldiğinde otomatik seçime dön
  useEffect(() => {
    setView(a.kind === "none" ? "table" : "chart");
    setType(a.kind);
    setMeasure(a.measures[0] ?? "");
  }, [a]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    setDark(mq.matches);
    const h = (e: MediaQueryListEvent) => setDark(e.matches);
    mq.addEventListener("change", h);
    return () => mq.removeEventListener("change", h);
  }, []);

  const availableTypes = useMemo<ChartKind[]>(() => {
    const t: ChartKind[] = [];
    if (a.timeCol) t.push("line");
    t.push("bar");
    if (a.heat) t.push("heatmap");
    if (!a.timeCol && a.primaryDim && a.measures.length >= 1 && result.rows.length <= 12) t.push("pie");
    // analiz edilen tip başta, tekrarsız (kpi/none hariç)
    return [...new Set([a.kind, ...t])].filter((k) => k !== "kpi" && k !== "none");
  }, [a, result.rows.length]);

  const option = useMemo(
    () => buildOption(result, a, { kind: type, measure, dark }),
    [result, a, type, measure, dark],
  );

  const cards = a.kind === "kpi" ? kpiCards(result, a) : [];

  const seg =
    "px-3 py-1 text-xs font-medium rounded-md transition-colors";
  const segOn = "bg-neutral-900 dark:bg-white text-white dark:text-black";
  const segOff = "text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200";

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Sonuç ({result.row_count} satır)
        </h3>
        <div className="flex items-center gap-2">
          {view === "chart" && chartable && (
            <>
              {availableTypes.length > 1 && (
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value as ChartKind)}
                  className="rounded-md border border-neutral-200 dark:border-neutral-800 bg-transparent px-2 py-1 text-xs"
                >
                  {availableTypes.map((t) => (
                    <option key={t} value={t}>
                      {TYPE_LABEL[t]}
                    </option>
                  ))}
                </select>
              )}
              {a.measures.length > 1 && (
                <select
                  value={measure}
                  onChange={(e) => setMeasure(e.target.value)}
                  className="rounded-md border border-neutral-200 dark:border-neutral-800 bg-transparent px-2 py-1 text-xs"
                >
                  {a.measures.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              )}
            </>
          )}
          {a.kind !== "none" && (
            <div className="flex rounded-lg border border-neutral-200 dark:border-neutral-800 p-0.5">
              <button className={`${seg} ${view === "chart" ? segOn : segOff}`} onClick={() => setView("chart")}>
                Grafik
              </button>
              <button className={`${seg} ${view === "table" ? segOn : segOff}`} onClick={() => setView("table")}>
                Tablo
              </button>
            </div>
          )}
        </div>
      </div>

      {view === "table" || a.kind === "none" ? (
        <ResultTable result={result} />
      ) : a.kind === "kpi" ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {cards.map((c) => (
            <div
              key={c.label}
              className="rounded-xl border border-neutral-200 dark:border-neutral-800 p-4 bg-neutral-50/50 dark:bg-neutral-900/40"
            >
              <div className="text-2xl font-bold tabular-nums">{c.value}</div>
              <div className="mt-1 text-xs text-neutral-500">{c.label}</div>
              {c.ctx && <div className="text-xs text-neutral-400">{c.ctx}</div>}
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 p-2">
          <EChart option={option} />
        </div>
      )}
    </div>
  );
}
