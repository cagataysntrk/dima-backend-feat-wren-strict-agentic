"use client";

import type { EChartsOption } from "echarts";
import { EChart } from "@/components/EChart";
import type { KpiCard } from "@/lib/types";

const GRAN_TR: Record<string, string> = {
  day: "günlük", week: "haftalık", month: "aylık", quarter: "çeyreklik", year: "yıllık",
};

// Cross-cube KPI kartı (CCC / likidite oranları): tek headline skaler + bileşenleri
// (DSO/DIO/DPO, dönen varlık/KV kaynak…) + formül + açıklama. Cube tablosu değil bileşke.

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

const COMP_COLORS = ["#10b981", "#f59e0b", "#ef4444", "#0ea5e9", "#a855f7"];

// KPI dönem-serisi → çizgi grafik (evrensel kova trendi). Headline çizgisi + AYNI BİRİMDEKİ
// bileşenler otomatik ayrı çizgi (CCC → DSO/DIO/DPO). Farklı birim (likidite: ₺ vs oran) →
// skala bozulmasın diye yalnız headline. Jenerik: hiçbir KPI'ya özel kod yok, veriden çizer.
function trendOption(card: KpiCard, series: NonNullable<KpiCard["series"]>): EChartsOption {
  const u = card.unit ?? "";
  const n = (v: number) => {
    const s = new Intl.NumberFormat("tr-TR", {
      notation: Math.abs(v) >= 10000 ? "compact" : "standard", maximumFractionDigits: 1,
    }).format(v);
    return u === "%" ? `%${s}` : u ? `${s} ${u}` : s;
  };
  const comps = series[0]?.components ?? [];
  // Bileşenler headline ile AYNI birimde mi? (öyleyse ayrı çizgi mantıklı — aynı eksen)
  const plotComps = comps.length > 0 && comps.every((c) => (c.unit ?? "") === u);

  const lines: { name: string; data: (number | null)[]; color: string; head: boolean }[] = [
    { name: shortName(card.label), color: "#6366f1", head: true,
      data: series.map((s) => s.value) },
  ];
  if (plotComps) {
    comps.forEach((c, i) => lines.push({
      name: shortName(c.label), color: COMP_COLORS[i % COMP_COLORS.length], head: false,
      data: series.map((s) => s.components?.find((x) => x.key === c.key)?.value ?? null),
    }));
  }
  return {
    legend: plotComps
      ? { top: 0, right: 0, icon: "roundRect", itemWidth: 10, itemHeight: 3,
          textStyle: { fontSize: 10, color: "#9ca3af" } }
      : undefined,
    grid: { left: 8, right: 16, top: plotComps ? 28 : 12, bottom: 20, containLabel: true },
    xAxis: {
      type: "category", data: series.map((s) => s.bucket), boundaryGap: false,
      axisLabel: { fontSize: 10, color: "#9ca3af" }, axisTick: { show: false },
      axisLine: { lineStyle: { color: "#e5e7eb" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { fontSize: 10, color: "#9ca3af", formatter: (v: number) => n(v) },
      splitLine: { lineStyle: { color: "rgba(120,120,120,0.12)" } },
    },
    tooltip: { trigger: "axis", valueFormatter: (v) => n(v as number) },
    series: lines.map((l) => ({
      type: "line", name: l.name, smooth: true, symbol: "circle",
      symbolSize: l.head ? 5 : 3, data: l.data,
      lineStyle: { width: l.head ? 2.5 : 1.5, color: l.color, type: l.head ? "solid" : "dashed" },
      itemStyle: { color: l.color },
      areaStyle: l.head && !plotComps ? { opacity: 0.06, color: l.color } : undefined,
    })),
  };
}

export function KpiCardView({ card }: { card: KpiCard }) {
  const series = (card.series ?? []).filter((s) => s.value !== null && s.value !== undefined);
  const gran = card.granularity ? GRAN_TR[card.granularity] ?? card.granularity : null;

  return (
    <div className="border border-hairline bg-background p-5">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[var(--text-etiket)] uppercase tracking-wider text-neutral-400">
          KPI{gran ? ` · ${gran} trend` : ""}
        </span>
        {card.lower_is_better && (
          <span className="font-mono text-[var(--text-etiket)] tracking-wider text-neutral-400" title="Düşük değer daha iyi">
            ↓ düşük iyi
          </span>
        )}
      </div>

      <div className="mt-1 flex items-baseline gap-3">
        <span className="text-3xl font-semibold tabular-nums text-foreground">
          {fmt(card.value, card.unit)}
        </span>
        <span className="text-sm text-neutral-500">
          {card.label}
          {gran && <span className="text-neutral-400"> · son dönem</span>}
        </span>
      </div>

      {series.length > 1 && (
        <div className="mt-4">
          <EChart height={220} option={trendOption(card, series)} />
        </div>
      )}

      {card.components?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-3 border-t border-hairline pt-4">
          {card.components.map((c) => (
            <div key={c.key} className="flex flex-col">
              <span className="text-[11px] text-neutral-400">{c.label}</span>
              <span className="font-mono text-sm tabular-nums text-neutral-700 dark:text-neutral-300">
                {fmt(c.value, c.unit)}
              </span>
            </div>
          ))}
        </div>
      )}

      {card.formula && (
        <div className="mt-3 font-mono text-[11px] text-neutral-400">= {card.formula}</div>
      )}
      {card.explain && (
        <p className="mt-3 max-w-prose whitespace-pre-line text-xs leading-relaxed text-neutral-500">
          {card.explain}
        </p>
      )}
    </div>
  );
}
