"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import type { QueryResult } from "@/lib/types";
import { analyze, buildOption, kpiCards, type ChartKind } from "@/lib/chart";
import { EChart } from "./EChart";
import { ResultTable } from "./ResultTable";
import { Select } from "./Select";

const TYPE_LABEL: Record<ChartKind, string> = {
  bar: "Sütun",
  line: "Çizgi",
  pie: "Pasta",
  heatmap: "Isı haritası",
  kpi: "KPI",
  none: "—",
};

// Sistem koyu-tema tercihini dışsal store olarak izler (effect'te setState yok).
function usePrefersDark(): boolean {
  return useSyncExternalStore(
    (cb) => {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      mq.addEventListener("change", cb);
      return () => mq.removeEventListener("change", cb);
    },
    () => window.matchMedia("(prefers-color-scheme: dark)").matches,
    () => false,
  );
}

// Not: yeni sonuçta seçimlerin sıfırlanması için ana bileşen bunu `key={...}` ile remount eder.
export function ResultView({ result }: { result: QueryResult }) {
  const a = useMemo(() => analyze(result), [result]);
  const chartable = a.kind !== "none" && a.kind !== "kpi";

  const [view, setView] = useState<"chart" | "table">(a.kind === "none" ? "table" : "chart");
  const [type, setType] = useState<ChartKind>(a.kind);
  const [measure, setMeasure] = useState<string>(a.measures[0] ?? "");
  const dark = usePrefersDark();

  const availableTypes = useMemo<ChartKind[]>(() => {
    const t: ChartKind[] = [];
    if (a.timeCol) t.push("line");
    t.push("bar");
    if (a.heat) t.push("heatmap");
    if (!a.timeCol && a.primaryDim && a.measures.length >= 1 && result.rows.length <= 12) t.push("pie");
    // analiz edilen tip başta, tekrarsız (kpi/none hariç)
    return [...new Set([a.kind, ...t])].filter((k) => k !== "kpi" && k !== "none");
  }, [a, result.rows.length]);

  // Grafik yalnız çizilebilir + ölçü varsa hesaplanır (0 satır / ölçüsüz → tablo, çökme yok).
  const option = useMemo(
    () => (chartable && measure ? buildOption(result, a, { kind: type, measure, dark }) : null),
    [chartable, result, a, type, measure, dark],
  );

  const cards = a.kind === "kpi" ? kpiCards(result, a) : [];

  const seg = "px-3 py-1 font-mono text-[11px] tracking-wide transition-colors";
  const segOn = "bg-foreground text-background";
  const segOff = "text-neutral-500 hover:text-foreground";

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-mono text-[11px] uppercase tracking-wider text-neutral-400">
          sonuç · {result.row_count} satır
        </h3>
        <div className="flex items-center gap-1.5">
          {view === "chart" && chartable && (
            <>
              {availableTypes.length > 1 && (
                <Select
                  ariaLabel="Grafik tipi"
                  value={type}
                  onChange={(v) => setType(v as ChartKind)}
                  options={availableTypes.map((t) => ({ value: t, label: TYPE_LABEL[t] }))}
                />
              )}
              {a.measures.length > 1 && (
                <Select
                  ariaLabel="Ölçü"
                  value={measure}
                  onChange={setMeasure}
                  options={a.measures.map((m) => ({ value: m, label: m }))}
                />
              )}
            </>
          )}
          {a.kind !== "none" && (
            <div className="inline-flex border border-hairline">
              <button className={`${seg} ${view === "chart" ? segOn : segOff}`} onClick={() => setView("chart")}>
                grafik
              </button>
              <button
                className={`border-l border-hairline ${seg} ${view === "table" ? segOn : segOff}`}
                onClick={() => setView("table")}
              >
                tablo
              </button>
            </div>
          )}
        </div>
      </div>

      {view === "table" || a.kind === "none" ? (
        <ResultTable result={result} />
      ) : a.kind === "kpi" ? (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {cards.map((c) => (
            <div key={c.label} className="border border-hairline p-4">
              <div className="font-mono text-[1.6rem] leading-none tabular-nums text-foreground">
                {c.value}
              </div>
              <div className="mt-2 font-mono text-[11px] uppercase tracking-wide text-neutral-400">
                {c.label}
              </div>
              {c.ctx && <div className="font-mono text-[11px] text-neutral-400">{c.ctx}</div>}
            </div>
          ))}
        </div>
      ) : (
        option ? (
          <div className="border border-hairline p-2">
            <EChart option={option} />
          </div>
        ) : (
          <ResultTable result={result} />
        )
      )}
    </div>
  );
}
