"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import type { QueryResult } from "@/lib/types";
import { ALL_MEASURES, analyze, buildOption, facetPanelValues, kpiCards, type ChartKind } from "@/lib/chart";
import { EChart } from "./EChart";
import { ResultTable } from "./ResultTable";
import { Select } from "./Select";

const TYPE_LABEL: Record<ChartKind, string> = {
  bar: "Sütun",
  line: "Çizgi",
  pie: "Pasta",
  heatmap: "Isı haritası",
  facet: "Panelli",
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

// Not: yeni sonuçta/görünüm ipucunda seçimlerin sıfırlanması için ana bileşen bunu
// `key={...}` ile remount eder; viewHint ("grafik ver") başlangıç görünümünü belirler.
export function ResultView({ result, viewHint }: { result: QueryResult; viewHint?: string }) {
  // "facet:kumas_cinsi" — panel boyutu KULLANICININ istediği boyut olur ("her kumaş
  // türü için ayrı grafik"); analiz sezgisi (en düşük kardinalite) ezilir.
  const hintBase = viewHint?.split(":")[0];
  const facetDim = viewHint?.startsWith("facet:") ? viewHint.slice(6) : null;
  const a = useMemo(() => {
    const b = analyze(result);
    if (facetDim && b.dims.length === 3 && b.dims.includes(facetDim)) {
      const others = b.dims.filter((d) => d !== facetDim);
      const x = b.timeCol && b.timeCol !== facetDim ? b.timeCol : others[0];
      const series = others.find((d) => d !== x) ?? others[0];
      return { ...b, kind: "facet" as ChartKind, facet: { dim: facetDim, x, series } };
    }
    return b;
  }, [result, facetDim]);
  const chartable = a.kind !== "none" && a.kind !== "kpi";

  const hintKind = (["line", "bar", "pie", "heatmap", "facet"] as ChartKind[]).find((k) => k === hintBase);
  const wantsChart = viewHint != null && hintBase !== "table";
  const [view, setView] = useState<"chart" | "table">(() => {
    if (hintBase === "table") return "table";
    if (wantsChart) return "chart";
    return a.kind === "none" ? "table" : "chart";
  });
  const [type, setType] = useState<ChartKind>(hintKind ?? a.kind);
  // çok ölçü → varsayılan "tümü" (kombo); tek ölçü → kendisi
  const [measure, setMeasure] = useState<string>(
    a.measures.length > 1 ? ALL_MEASURES : (a.measures[0] ?? ""),
  );
  const dark = usePrefersDark();

  const availableTypes = useMemo<ChartKind[]>(() => {
    const t: ChartKind[] = [];
    if (a.facet) t.push("facet");
    if (a.timeCol) t.push("line");
    if (!a.facet) t.push("bar");
    if (a.heat || a.heatAny) t.push("heatmap");  // açık seçim min-eksen kuralına takılmaz
    if (!a.timeCol && a.primaryDim && a.measures.length >= 1 && result.rows.length <= 12) t.push("pie");
    // analiz edilen tip başta, tekrarsız (kpi/none hariç)
    return [...new Set([a.kind, ...t])].filter((k) => k !== "kpi" && k !== "none");
  }, [a, result.rows.length]);

  // PANEL GEZİNME (carousel, "instagram" tarzı): panelli görünümde ◀ ▶ ile
  // "tüm paneller" ↔ tek panel arasında geçilir; tek panelde o dilim TAM BOY çizilir.
  const facetInfo = type === "facet" && a.facet ? a.facet : null;
  const panels = useMemo(
    () => (facetInfo ? facetPanelValues(result, facetInfo.dim) : []),
    [result, facetInfo],
  );
  const [panelIdx, setPanelIdx] = useState(-1); // -1 = tüm paneller (grid)
  const single = facetInfo && panelIdx >= 0 && panelIdx < panels.length;
  const effResult = useMemo(() => {
    if (!single || !facetInfo) return result;
    const val = panels[panelIdx];
    const rows = result.rows
      .filter((r) => String(r[facetInfo.dim]) === val)
      .map((r) => {
        const { [facetInfo.dim]: _omit, ...rest } = r;
        return rest;
      });
    return { ...result, columns: result.columns.filter((c) => c !== facetInfo.dim), rows, row_count: rows.length };
  }, [single, facetInfo, result, panels, panelIdx]);
  const effA = useMemo(() => (single ? analyze(effResult) : a), [single, effResult, a]);
  const effKind: ChartKind = single
    ? (effA.kind === "none" || effA.kind === "kpi" ? "bar" : effA.kind)
    : type;

  // Grafik yalnız çizilebilir + ölçü varsa hesaplanır (0 satır / ölçüsüz → tablo, çökme yok).
  const option = useMemo(
    () => (chartable && measure ? buildOption(effResult, effA, { kind: effKind, measure, dark }) : null),
    [chartable, effResult, effA, effKind, measure, dark],
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
                  options={[
                    // "tümü": kombo görünüm — miktarlar sütun, oranlar sağ eksende çizgi
                    { value: ALL_MEASURES, label: "tümü" },
                    ...a.measures.map((m) => ({ value: m, label: m })),
                  ]}
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
        <>
          {wantsChart && a.kind === "none" && (
            <p className="mb-2 font-mono text-[11px] text-neutral-400">
              bu sonuç grafik için çok boyutlu — bir kırılımı azaltmayı dene
              (ör. &quot;sadece vardiya bazında&quot;)
            </p>
          )}
          <ResultTable result={result} />
        </>
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
            {facetInfo && (
              <div className="mb-1 flex items-center justify-center gap-3 font-mono text-[11px] text-neutral-400">
                <button
                  aria-label="Önceki panel"
                  className="px-1 transition-colors hover:text-foreground"
                  onClick={() => setPanelIdx((i) => (i < 0 ? panels.length - 1 : i - 1))}
                >
                  ◀
                </button>
                <span className="min-w-[9rem] text-center">
                  {single ? `${panels[panelIdx]} · ${panelIdx + 1}/${panels.length}` : "tüm paneller"}
                </span>
                <button
                  aria-label="Sonraki panel"
                  className="px-1 transition-colors hover:text-foreground"
                  onClick={() => setPanelIdx((i) => (i >= panels.length - 1 ? -1 : i + 1))}
                >
                  ▶
                </button>
              </div>
            )}
            <EChart
              option={option}
              onSeriesClick={
                facetInfo && !single
                  ? (si) => {
                      // panel ÖNE ÇIKARMA: paneldeki bir seriye tıkla → o panel tam boy.
                      // seriler panels.flatMap(groups) sırasında → panel = si / grupSayısı.
                      const groups = Math.max(
                        1,
                        (Array.isArray(option.series) ? option.series.length : 1) / Math.max(1, panels.length),
                      );
                      setPanelIdx(Math.floor(si / groups));
                    }
                  : undefined
              }
            />
          </div>
        ) : (
          <ResultTable result={result} />
        )
      )}
    </div>
  );
}
