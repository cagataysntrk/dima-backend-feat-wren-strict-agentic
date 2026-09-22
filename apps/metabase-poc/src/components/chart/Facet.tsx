// POC COPY of apps/web/src/components/chart/Facet.tsx — unchanged. Follow-up: extract to packages/ui.
"use client";

import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis } from "recharts";
import { ChevronLeft, ChevronRight, Grid2x2 } from "lucide-react";
import type { QueryResult } from "@dima/contracts";
import { analyze, buildFacet, fmtAxis, fmtValue, type Analysis } from "@dima/domain";
import { ChartContainer, type ChartConfig } from "@/components/ui/chart";
import { Button } from "@/components/ui/button";
import { Chart } from "./Chart";
import { cn } from "@/lib/utils";

/**
 * PANELLİ görünüm (small multiples / trellis) — 3 kırılımlı sonuçlar için.
 *
 * En düşük kardinaliteli boyut PANELLERE bölünür, kalan ikisi panel içinde
 * x-ekseni ve renk serisi olur. Yığın DEĞİL gruplu sütun: oran metriklerinde
 * yığın toplamı anlamsızdır (BI best practice).
 *
 * Paneller ORTAK y-tavanını paylaşır (`FacetData.yMax`). Panel başına serbest
 * ölçek görsel olarak daha "dolu" görünürdü ama paneller arası karşılaştırmayı
 * yalan söyler — küçük panel büyük panelle aynı yükseklikte çizilirdi.
 *
 * Recharts ile çiziliyor: DESIGN.md tek motor diyor (ikinci bir grafik motoru
 * yok). ECharts'ın `grid[]` dizisi yerine burada CSS grid + panel başına bir
 * küçük BarChart var; lejant paneller arası PAYLAŞILIR çünkü seri adları aynı.
 */
export function Facet({
  result,
  analysis,
  measure,
  className,
  box,
}: {
  result: QueryResult;
  analysis: Analysis;
  measure: string;
  className?: string;
  /** Tek panel görünümünün kutu ölçüsü (satır içi stil); ızgarada sütun sayısını
   *  da etkiler — daha çok yer varsa 3 sütuna çıkılır. */
  box?: React.CSSProperties;
}) {
  const facet = useMemo(
    () => buildFacet(result, analysis, measure),
    [result, analysis, measure],
  );

  const [hidden, setHidden] = useState<ReadonlySet<string>>(() => new Set());
  // −1 = tüm paneller (ızgara); ≥0 = tek panel TAM BOY (carousel).
  const [panelIdx, setPanelIdx] = useState(-1);
  const signature = facet?.series.map((s) => s.key).join("|") ?? "";
  const [lastSignature, setLastSignature] = useState(signature);
  if (signature !== lastSignature) {
    setLastSignature(signature);
    setHidden(new Set());
    setPanelIdx(-1);
  }

  // TEK PANEL: satırlar o panele süzülür ve facet boyutu KOLONDAN DÜŞÜRÜLÜR —
  // böylece kalan şekil (zaman × seri) yeniden analiz edilip normal grafik
  // hattından geçer. Sonuç: tek panelde zaman ekseni varsa çizgi, yoksa gruplu
  // sütun; yani küçük panelin sıkıştırılmış hali değil, tam bir grafik.
  const single = useMemo(() => {
    const dim = analysis.facet?.dim;
    if (!dim || !facet || panelIdx < 0 || panelIdx >= facet.panels.length) return null;
    const value = facet.panels[panelIdx].value;
    const rows = result.rows
      .filter((r) => String(r[dim]) === value)
      .map((r) => Object.fromEntries(Object.entries(r).filter(([k]) => k !== dim)));
    const sub: QueryResult = {
      ...result,
      columns: result.columns.filter((c) => c !== dim),
      rows,
      row_count: rows.length,
    };
    const subAnalysis = analyze(sub);
    return {
      value,
      result: sub,
      analysis: subAnalysis,
      // kpi/none tek panelde anlamsız — sütuna düş.
      kind:
        subAnalysis.kind === "none" || subAnalysis.kind === "kpi" ? "bar" : subAnalysis.kind,
    };
  }, [analysis.facet?.dim, facet, panelIdx, result]);

  const config = useMemo<ChartConfig>(() => {
    const c: ChartConfig = {};
    facet?.series.forEach((s, i) => {
      c[s.key] = { label: s.label, color: `var(--chart-${(i % 5) + 1})` };
    });
    return c;
  }, [facet]);

  if (!facet || facet.panels.length === 0) return null;

  const colorOf = (key: string) => {
    const i = facet.series.findIndex((s) => s.key === key);
    return `var(--chart-${((i < 0 ? 0 : i) % 5) + 1})`;
  };
  const toggle = (key: string) =>
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });

  const yTick = (v: number) => fmtAxis(v, facet.measure);
  // 1-2 panel yan yana; 3+ panel sarar. Dar kartta 2 sütun, geniş/tam ekranda 3 —
  // tek satırda 7 panel her iki durumda da okunmazdı. "Geniş"in ölçütü: çağıran
  // varsayılan 16/10 oranından başka bir ölçü vermiş olması.
  const roomy = box != null && box.aspectRatio !== "16 / 10";
  const maxCols = roomy ? 3 : 2;
  const cols = Math.min(facet.panels.length, maxCols);
  const step = (d: number) =>
    setPanelIdx((i) => (i + d + facet.panels.length) % facet.panels.length);

  // Panel gezinme şeridi — ızgarada "panele gir", tek panelde ◀ ▶ + ızgaraya dön.
  const nav = (
    <div className="flex items-center justify-between gap-2">
      {single ? (
        <>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPanelIdx(-1)}
            className="h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground"
          >
            <Grid2x2 className="size-3.5" />
            tüm paneller
          </Button>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Önceki panel"
              onClick={() => step(-1)}
              className="text-muted-foreground hover:text-foreground"
            >
              <ChevronLeft className="size-4" />
            </Button>
            <span className="min-w-24 text-center text-xs font-medium text-foreground">
              {single.value}
            </span>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Sonraki panel"
              onClick={() => step(1)}
              className="text-muted-foreground hover:text-foreground"
            >
              <ChevronRight className="size-4" />
            </Button>
            <span className="ml-1 font-mono text-[10px] text-muted-foreground">
              {panelIdx + 1}/{facet.panels.length}
            </span>
          </div>
        </>
      ) : (
        <p className="text-xs text-muted-foreground">
          {facet.panels.length} panel · ortak ölçek — bir panele tıklayıp tam boy aç
        </p>
      )}
    </div>
  );

  if (single) {
    return (
      <div className={cn("space-y-2", className)}>
        {nav}
        <Chart
          result={single.result}
          analysis={single.analysis}
          kind={single.kind}
          measure={facet.measure}
          box={box}
        />
      </div>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {nav}
      <div
        className="grid gap-x-4 gap-y-3"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
      >
        {facet.panels.map((panel, i) => (
          <div key={panel.value} className="min-w-0 space-y-1">
            {/* Başlık aynı zamanda o panele giriş — ayrı bir "aç" ikonu eklemek
                yerine zaten oradaki etiketi tıklanır yapmak daha az gürültü. */}
            <button
              type="button"
              onClick={() => setPanelIdx(i)}
              title={`${panel.value} — tam boy aç`}
              className="block w-full truncate rounded-sm px-1 text-center text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
            >
              {panel.value}
            </button>
            <ChartContainer config={config} className="aspect-[4/3] w-full">
              <BarChart data={panel.data} margin={{ left: 0, right: 4, top: 4, bottom: 0 }}>
                <CartesianGrid vertical={false} stroke="var(--border)" strokeOpacity={0.6} />
                <XAxis
                  dataKey={facet.xKey}
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  tickMargin={6}
                  interval={0}
                  angle={panel.data.length > 5 ? -35 : 0}
                  textAnchor={panel.data.length > 5 ? "end" : "middle"}
                  height={panel.data.length > 5 ? 46 : 24}
                />
                {/* ORTAK tavan — paneller aynı ölçekte okunsun. */}
                <YAxis
                  domain={[0, facet.yMax ?? "auto"]}
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  width={44}
                  tickFormatter={yTick}
                />
                <Tooltip
                  cursor={{ fill: "var(--muted)", opacity: 0.4 }}
                  content={<FacetTooltip measure={facet.measure} />}
                />
                {facet.series.map((s) => (
                  <Bar
                    key={s.key}
                    dataKey={s.key}
                    hide={hidden.has(s.key)}
                    fill={colorOf(s.key)}
                    radius={[2, 2, 0, 0]}
                    maxBarSize={18}
                    isAnimationActive={false}
                  />
                ))}
              </BarChart>
            </ChartContainer>
          </div>
        ))}
      </div>

      {/* Tek lejant tüm panelleri yönetir — seri adları paneller arası ortak. */}
      {facet.series.length > 1 && (
        <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs">
          {facet.series.map((s) => {
            const off = hidden.has(s.key);
            return (
              <button
                key={s.key}
                type="button"
                onClick={() => toggle(s.key)}
                aria-pressed={!off}
                title={off ? `${s.label} — göster` : `${s.label} — gizle`}
                className={cn(
                  "flex cursor-pointer items-center gap-1.5 rounded-sm px-1 py-0.5 transition-colors",
                  "hover:bg-accent focus-visible:ring-ring/50 focus-visible:ring-2 focus-visible:outline-none",
                  off ? "text-muted-foreground/60 line-through" : "text-muted-foreground",
                )}
              >
                <span
                  className="size-2 shrink-0 rounded-[2px]"
                  style={{ background: colorOf(s.key), opacity: off ? 0.3 : 1 }}
                />
                {s.label}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function FacetTooltip({
  active,
  payload,
  label,
  measure,
}: {
  active?: boolean;
  payload?: { name?: string; dataKey?: string; value?: number | null; color?: string }[];
  label?: string;
  measure: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="grid min-w-[9rem] gap-1.5 rounded-lg border border-border/60 bg-popover px-2.5 py-2 text-xs shadow-lg">
      {label != null && <div className="font-medium text-foreground">{label}</div>}
      <div className="grid gap-1">
        {payload
          .filter((p) => p.value != null)
          .map((p, i) => (
            <div key={i} className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span
                  className="size-2 shrink-0 rounded-[2px]"
                  style={{ background: p.color }}
                />
                {String(p.dataKey ?? p.name ?? "")}
              </span>
              <span className="font-mono font-medium tabular-nums text-foreground">
                {fmtValue(p.value, measure)}
              </span>
            </div>
          ))}
      </div>
    </div>
  );
}
