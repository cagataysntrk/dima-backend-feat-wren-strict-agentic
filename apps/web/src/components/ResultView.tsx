"use client";

import { useEffect, useMemo, useState } from "react";
import { getSchema } from "@dima/api-client";
import { setSchemaUnits } from "@dima/domain";
import type { QueryResult } from "@dima/contracts";
import { ALL_MEASURES, analyze, type ChartKind } from "@dima/domain";
import { Chart } from "./chart/Chart";
import { KpiGrid } from "./chart/kpi";
import { PivotTable } from "./PivotTable";
import { Heatmap } from "./chart/Heatmap";
import { ResultTable } from "./ResultTable";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

// Ölçü metadata'sı (/schema cubes[]) TEK okumadan iki şey besler:
//   • units            → format katmanı (₺, kg, %…)
//   • lower_is_better  → ısı haritası yön semantiği (yüksek = kötü ölçülerde rampa ters)
// Metadata'da bir kez tanımlanır, şirket/cube başına UI değişikliği gerekmez.
// Açılışta bir kez okunur, modül düzeyinde tutulur (useFeature deseni).
let _schemaLoaded = false;
let _lowerSet: ReadonlySet<string> = new Set();

function useSchemaMeta(): ReadonlySet<string> {
  const [lower, setLower] = useState<ReadonlySet<string>>(_lowerSet);
  useEffect(() => {
    if (_schemaLoaded) return;
    getSchema()
      .then((s) => {
        const cubes =
          (s as { cubes?: { units?: Record<string, string>; lower_is_better?: string[] }[] })
            .cubes ?? [];
        setSchemaUnits(Object.assign({}, ...cubes.map((c) => c.units ?? {})));
        _lowerSet = new Set(cubes.flatMap((c) => c.lower_is_better ?? []));
        _schemaLoaded = true;
        setLower(_lowerSet);
      })
      .catch(() => {});
  }, []);
  return lower;
}

// Metadata yoksa (eski/serbest ölçüler) ad kalıbından yedek çıkarım.
const LOWER_IS_BETTER_RE = /fire|durus|duruş|sapma|maliyet|tuketim|tüketim|yogunluk|yoğunluk|hata|iade|gecikme/i;

const TYPE_LABEL: Record<ChartKind, string> = {
  bar: "Sütun",
  "bar-stacked": "Yığılmış sütun",
  "bar-h": "Yatay sütun",
  line: "Çizgi",
  area: "Alan",
  pie: "Pasta",
  radial: "Radyal",
  radar: "Radar",
  scatter: "Dağılım",
  heatmap: "Isı haritası",
  facet: "Panelli",
  kpi: "KPI",
  none: "—",
};

// Recharts façade'ının çizebildiği tipler (heatmap/facet şimdilik tabloya düşer).
const CHARTABLE: ChartKind[] = [
  "bar",
  "bar-stacked",
  "bar-h",
  "line",
  "area",
  "pie",
  "radial",
  "scatter",
  "radar",
  "heatmap",
];

// Not: yeni sonuçta/görünüm ipucunda seçimlerin sıfırlanması için ana bileşen bunu
// `key={...}` ile remount eder; viewHint ("grafik ver") başlangıç görünümünü belirler.
export function ResultView({
  result,
  viewHint,
  meta,
}: {
  result: QueryResult;
  viewHint?: string;
  /** Başlık satırının solunda gösterilecek içerik (provenance rozeti, satır sayısı…). */
  meta?: React.ReactNode;
}) {
  const lowerSet = useSchemaMeta();
  const hintBase = viewHint?.split(":")[0];
  const a = useMemo(() => analyze(result), [result]);

  // Yalnız BU veri için anlamlı tipler listelenir — kullanıcıya geçersiz seçenek
  // sunulmaz. Otomatik seçim (analyze().kind) her zaman listenin başındadır.
  const availableTypes = useMemo<ChartKind[]>(() => {
    const t: ChartKind[] = [];
    const hasCat = Boolean(a.primaryDim) && a.measures.length >= 1;
    // birden fazla seri = ikinci kırılım ya da çok ölçü
    const multiSeries = a.measures.length > 1 || a.dims.length > 1;
    const few = result.rows.length <= 12;

    if (a.timeCol) {
      t.push("line", "area");
    }
    if (hasCat) {
      t.push("bar");
      if (multiSeries) t.push("bar-stacked");
      t.push("bar-h");
    }
    if (!a.timeCol && hasCat && few) {
      t.push("pie");
      if (a.measures.length === 1) t.push("radial", "radar");
    }
    // ısı haritası: iki kategorik boyut × bir ölçü eşlemesi kurulabiliyorsa
    if ((a.heatAny ?? a.heat) && a.measures.length >= 1) t.push("heatmap");
    // iki ölçü → korelasyon bakışı anlamlı
    if (a.measures.length >= 2) t.push("scatter");

    const seed = CHARTABLE.includes(a.kind) ? [a.kind] : [];
    return [...new Set([...seed, ...t])];
  }, [a, result.rows.length]);

  const hintKind = (CHARTABLE as ChartKind[]).find((k) => k === hintBase);
  const canChart = availableTypes.length > 0;
  const wantsTable = hintBase === "table";

  // PIVOT: zaman kovası + TEK varlık boyutu + ölçü → çapraz tablo (varlık satır × kova sütun).
  // Uzun "N ürün × ay × metrik" sonucunu okunur matrise çevirir (canlı 2026-07-25: 98 satır
  // yerine 20×7). Jenerik — herhangi bir varlık×zaman×ölçü.
  const pivotDim =
    a.timeCol && a.dims.length === 2 && a.measures.length >= 1
      ? a.dims.find((d) => d !== a.timeCol) ?? null
      : null;
  const pivotable = pivotDim != null;

  const [view, setView] = useState<"chart" | "table" | "pivot">(() => {
    if (wantsTable) return "table";
    // Çok-varlıklı zaman serisi: çizgi kalabalık, tablo çok uzun → PIVOT varsayılan.
    if (pivotable && result.rows.length > 12) return "pivot";
    if (!canChart) return "table";
    // facet hâlâ çizilemiyor → tablo. heatmap ARTIK çiziliyor (chart/Heatmap.tsx).
    if (a.kind === "none" || a.kind === "facet") return "table";
    return "chart";
  });
  const [type, setType] = useState<ChartKind>(hintKind ?? availableTypes[0] ?? "bar");
  const [measure, setMeasure] = useState<string>(
    a.measures.length > 1 ? ALL_MEASURES : (a.measures[0] ?? ""),
  );

  const showControls = view === "chart" && canChart;
  // Not: ısı haritası/panel için "yakında" uyarısı kaldırıldı — tabloya sessizce düşüyoruz.
  const advisory =
    a.kind === "none" && hintBase != null && hintBase !== "table"
      ? "bu sonuç grafik için çok boyutlu — bir kırılımı azaltmayı dene"
      : null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        {/* sol taraf çağıranındır (ör. sohbette provenance rozeti + satır sayısı);
            böylece kartta ikinci bir "sonuç · N satır" satırı oluşmuyor. */}
        <div className="flex min-w-0 items-center gap-2">{meta}</div>
        <div className="flex shrink-0 items-center gap-1.5">
          {showControls && availableTypes.length > 1 && (
            <Select value={type} onValueChange={(v) => setType(v as ChartKind)}>
              <SelectTrigger size="sm" className="h-7 w-auto gap-1.5 text-xs" aria-label="Grafik tipi">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {availableTypes.map((t) => (
                  <SelectItem key={t} value={t} className="text-xs">
                    {TYPE_LABEL[t]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {showControls && a.measures.length > 1 && (
            <Select value={measure} onValueChange={setMeasure}>
              <SelectTrigger size="sm" className="h-7 w-auto gap-1.5 text-xs" aria-label="Ölçü">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL_MEASURES} className="text-xs">tümü</SelectItem>
                {a.measures.map((m) => (
                  <SelectItem key={m} value={m} className="text-xs">
                    {m}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {((a.kind !== "none" && canChart) || pivotable) && (
            <ToggleGroup
              type="single"
              size="sm"
              variant="outline"
              value={view}
              onValueChange={(v) => v && setView(v as "chart" | "table" | "pivot")}
            >
              {a.kind !== "none" && canChart && (
                <ToggleGroupItem value="chart" className="px-2.5 text-xs">
                  grafik
                </ToggleGroupItem>
              )}
              <ToggleGroupItem value="table" className="px-2.5 text-xs">
                tablo
              </ToggleGroupItem>
              {pivotable && (
                <ToggleGroupItem value="pivot" className="px-2.5 text-xs">
                  pivot
                </ToggleGroupItem>
              )}
            </ToggleGroup>
          )}
        </div>
      </div>

      {advisory && <p className="text-xs text-muted-foreground">{advisory}</p>}

      {a.kind === "kpi" ? (
        <KpiGrid result={result} analysis={a} />
      ) : view === "pivot" && pivotDim && a.timeCol ? (
        <PivotTable
          result={result}
          timeCol={a.timeCol}
          entityDim={pivotDim}
          measure={!measure || measure === ALL_MEASURES ? a.measures[0] : measure}
        />
      ) : view === "chart" && canChart ? (
        <ChartOrTable
          result={result}
          analysis={a}
          type={type}
          measure={measure}
          lowerSet={lowerSet}
        />
      ) : (
        <div className="overflow-x-auto">
          <ResultTable result={result} />
        </div>
      )}
    </div>
  );
}

// Chart null dönerse (heatmap/facet/çizilemez) temiz tabloya düş.
function ChartOrTable({
  result,
  analysis,
  type,
  measure,
  lowerSet,
}: {
  result: QueryResult;
  analysis: ReturnType<typeof analyze>;
  type: ChartKind;
  measure: string;
  /** /schema cubes[].lower_is_better — "yüksek = kötü" ölçüler. */
  lowerSet: ReadonlySet<string>;
}) {
  const rendered = (
    <Chart result={result} analysis={analysis} kind={type} measure={measure} />
  );
  // Chart, çizemediğinde null döndürür; bunu render sırasında bilemeyiz, bu yüzden
  // buildSeries çıktısına göre karar veririz.
  return (
    <div className="rounded-lg border border-border p-3">
      {type === "heatmap" ? (
        <Heatmap
          result={result}
          analysis={analysis}
          measure={measure}
          // Yön ASIL metadata'dan gelir; regex yalnız metadata'sız ölçüler için yedek.
          lowerIsBetter={lowerSet.has(measure) || LOWER_IS_BETTER_RE.test(measure)}
        />
      ) : type === "facet" ? (
        <div className="overflow-x-auto">
          <ResultTable result={result} />
        </div>
      ) : (
        rendered
      )}
    </div>
  );
}
