"use client";

import { useMemo, useState } from "react";
import type { QueryResult } from "@dima/contracts";
import { ALL_MEASURES, analyze, splitAxes, type ChartKind } from "@dima/domain";
import { Chart } from "./chart/Chart";
import { KpiGrid } from "./chart/kpi";
import { PivotTable } from "./PivotTable";
import { Facet } from "./chart/Facet";
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

// POC COPY of apps/web/src/components/ResultView.tsx.
// Differences: no dima-backend /schema call (units come from column-name
// suffixes via @dima/domain unitFor), and an optional `onDrill` hook that
// makes bars clickable when the result has exactly one categorical dimension.
const EMPTY_LOWER: ReadonlySet<string> = new Set();

// Metadata yoksa (eski/serbest ölçüler) ad kalıbından yedek çıkarım.
const LOWER_IS_BETTER_RE = /fire|durus|duruş|sapma|maliyet|tuketim|tüketim|yogunluk|yoğunluk|hata|iade|gecikme/i;

const TYPE_LABEL: Record<ChartKind, string> = {
  bar: "Sütun",
  "bar-stacked": "Yığılmış sütun",
  "bar-h": "Yatay sütun",
  line: "Çizgi",
  area: "Alan",
  combo: "Sütun + çizgi",
  pie: "Pasta",
  radial: "Radyal",
  radar: "Radar",
  scatter: "Dağılım",
  heatmap: "Isı haritası",
  facet: "Panelli",
  kpi: "KPI",
  none: "—",
};

// Çizilebilen tipler. heatmap ve facet Recharts primitifi değil ama kendi
// bileşenleri var (chart/Heatmap, chart/Facet) — artık tabloya DÜŞMÜYORLAR.
const CHARTABLE: ChartKind[] = [
  "bar",
  "bar-stacked",
  "bar-h",
  "line",
  "area",
  "combo",
  "pie",
  "radial",
  "scatter",
  "radar",
  "heatmap",
  "facet",
];

// Not: yeni sonuçta/görünüm ipucunda seçimlerin sıfırlanması için ana bileşen bunu
// `key={...}` ile remount eder; viewHint ("grafik ver") başlangıç görünümünü belirler.
/**
 * Grafik kutusunun ölçüsü — SATIR İÇİ STİL, utility sınıfı değil.
 *
 * Sebep: bunlar dinamik olarak seçilen ölçülerdi ve `aspect-[21/9]` gibi
 * arbitrary sınıflar üretilen CSS'e girmediğinde kutu yüksekliği 0 oluyor,
 * grafik boş bir şeride çöküyordu (canlı 2026-07-29). Satır içi stil ne
 * purge'lanır ne de sınıf birleştirmede kaybolur.
 *
 * Tam ekranda ORAN değil YÜKSEKLİK sabitlenir: ekran oranı ne olursa olsun
 * grafik dikeyde ekranı doldurmalı. Geniş kartta 16/10 fazla uzun bir grafik
 * üretirdi (kart genişledi, oran sabit kalsa yükseklik de büyürdü) → daha
 * yatay bir orana geçilir.
 */
const SIZE_BOX: Record<"normal" | "wide" | "full", React.CSSProperties> = {
  normal: { aspectRatio: "16 / 10" },
  wide: { aspectRatio: "21 / 9" },
  // Tam ekranda kalan dikey alanın tamamı: diyalog dolgusu + başlık + kontrol
  // satırı ≈ 10rem. Sabit bir vh oranı bırakılsa altta ölü boşluk kalırdı.
  full: { aspectRatio: "auto", height: "calc(100svh - 11rem)" },
};

export function ResultView({
  result,
  viewHint,
  meta,
  size = "normal",
  actions,
  onDrill,
}: {
  result: QueryResult;
  viewHint?: string;
  /** Başlık satırının solunda gösterilecek içerik (provenance rozeti, satır sayısı…). */
  meta?: React.ReactNode;
  /** Grafik alanı boyutu — kartı genişleten/tam ekrana alan çağıran belirler. */
  size?: "normal" | "wide" | "full";
  /** Kontrol satırının sonuna eklenen düğmeler (genişlet / tam ekran). */
  actions?: React.ReactNode;
  /** POC drill-down: (column, clicked value). Only offered for one categorical dimension. */
  onDrill?: (column: string, value: string) => void;
}) {
  const lowerSet = EMPTY_LOWER;
  const hintBase = viewHint?.split(":")[0];
  // "facet:kumas_cinsi" — panel boyutu KULLANICININ istediği boyut olur ("her kumaş
  // türü için ayrı grafik"). analyze()'ın sezgisi (en düşük kardinalite) kasıtlı
  // olarak ezilir: kullanıcı hangi kırılımı istediğini açıkça söylemişse tahmin
  // etmenin anlamı yok.
  const facetDim = viewHint?.startsWith("facet:") ? viewHint.slice(6) : null;
  const a = useMemo(() => {
    const base = analyze(result);
    if (!facetDim || base.dims.length !== 3 || !base.dims.includes(facetDim)) return base;
    const others = base.dims.filter((d) => d !== facetDim);
    // x ekseni: zaman varsa her zaman zaman (aylar seri olursa lejant okunmaz).
    const x = base.timeCol && base.timeCol !== facetDim ? base.timeCol : others[0];
    const series = others.find((d) => d !== x) ?? others[0];
    return { ...base, kind: "facet" as ChartKind, facet: { dim: facetDim, x, series } };
  }, [result, facetDim]);

  // Yalnız BU veri için anlamlı tipler listelenir — kullanıcıya geçersiz seçenek
  // sunulmaz. Otomatik seçim (analyze().kind) her zaman listenin başındadır.
  const availableTypes = useMemo<ChartKind[]>(() => {
    const t: ChartKind[] = [];
    const hasCat = Boolean(a.primaryDim) && a.measures.length >= 1;
    // birden fazla seri = ikinci kırılım ya da çok ölçü
    const multiSeries = a.measures.length > 1 || a.dims.length > 1;
    // Parça-bütün grafikleri açı karşılaştırmasına dayanır: altıdan fazla dilim
    // karşılaştırma yerine dekor olur. Radar da yalnız kısa, tek ölçülü profilde
    // anlamlıdır; diğer tüm durumlarda sütun/detay tablosu daha dürüsttür.
    const categoryCount = a.primaryDim
      ? new Set(result.rows.map((row) => String(row[a.primaryDim!]))).size
      : 0;
    const canUsePie = !a.timeCol && hasCat && categoryCount >= 2 && categoryCount <= 6;
    const canUseProfile = canUsePie && categoryCount <= 5 && a.measures.length === 1;
    const xCol = a.timeCol ?? a.primaryDim;

    if (a.timeCol) {
      t.push("line", "area");
    }
    if (hasCat) {
      t.push("bar");
      if (multiSeries) t.push("bar-stacked");
      t.push("bar-h");
    }
    // ÇAPRAZ KARŞILAŞTIRMA (sütun + çizgi, çift eksen): birden çok ölçü VE tek
    // kategorik eksen ister. İkinci bir kırılım varsa seri kaynağı ikiye çıkar
    // (hem ölçü hem grup) — lejant okunmaz olurdu, o yüzden sunulmaz.
    if (
      a.measures.length >= 2 &&
      xCol &&
      !a.dims.some((d) => d !== xCol) &&
      splitAxes(result.rows, a.measures).right.length > 0
    ) {
      t.push("combo");
    }
    if (canUsePie) {
      t.push("pie");
      if (canUseProfile) t.push("radial", "radar");
    }
    // ısı haritası: iki kategorik boyut × bir ölçü eşlemesi kurulabiliyorsa
    if ((a.heatAny ?? a.heat) && a.measures.length >= 1) t.push("heatmap");
    // panelli: 3 kırılım facet'lenebiliyorsa (analyze ≤6 panel kuralını uygular)
    if (a.facet && a.measures.length >= 1) t.push("facet");
    // Dağılım yalnız iki nicel ölçüyle anlamlı. Üç+ ölçüde hangi ikilinin
    // çizildiği belirsiz kalır; çok nokta da yoğunluk yaklaşımı gerektirir.
    if (a.measures.length === 2 && result.rows.length >= 3 && a.dims.length <= 1) t.push("scatter");

    const seed = CHARTABLE.includes(a.kind) ? [a.kind] : [];
    return [...new Set([...seed, ...t])];
  }, [a, result.rows]);

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
    // heatmap (chart/Heatmap) ve facet (chart/Facet) artık çiziliyor — yalnız
    // hiç grafik çıkarılamayan sonuç tabloya düşer.
    if (a.kind === "none") return "table";
    return "chart";
  });
  const [type, setType] = useState<ChartKind>(hintKind ?? availableTypes[0] ?? "bar");
  const [measure, setMeasure] = useState<string>(
    a.measures.length > 1 ? ALL_MEASURES : (a.measures[0] ?? ""),
  );

  const showControls = view === "chart" && canChart;
  const selectType = (next: ChartKind) => {
    setType(next);
    // Kombo ve dağılım iki ölçünün ilişkisidir; tek ölçü seçimi ekseni sessizce
    // kendisiyle karşılaştırmaya indirgerdi. Bu modlar her zaman iki ölçüyle açılır.
    if ((next === "combo" || next === "scatter") && a.measures.length > 1) {
      setMeasure(ALL_MEASURES);
    }
  };
  // Not: ısı haritası/panel için "yakında" uyarısı kaldırıldı — tabloya sessizce düşüyoruz.
  const advisory =
    a.kind === "none" && hintBase != null && hintBase !== "table"
      ? "bu sonuç grafik için çok boyutlu — bir kırılımı azaltmayı dene"
      : null;

  return (
    <div className="space-y-3">
      {/* SARAR: dar sütunda (sağ panel genişletilmişken sohbet ~250px'e iner)
          kontroller tek satıra sığmayıp kartı yatay taşırıyordu — rozetin üstüne
          binen "Sütun" seçici, kırpılan grafik, yatay kaydırma çubuğu. */}
      <div className="flex flex-wrap items-center justify-between gap-x-2 gap-y-1.5">
        {/* sol taraf çağıranındır (ör. sohbette provenance rozeti + satır sayısı);
            böylece kartta ikinci bir "sonuç · N satır" satırı oluşmuyor. */}
        <div className="flex min-w-0 items-center gap-2">{meta}</div>
        <div className="flex min-w-0 shrink items-center gap-1.5">
          {showControls && availableTypes.length > 1 && (
            <Select value={type} onValueChange={(v) => selectType(v as ChartKind)}>
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
          {/* Kombo TANIMI GEREĞİ çok ölçülüdür (sütun + çizgi karşılaştırması);
              tek ölçü seçmek onu sıradan bir sütun grafiğine indirger — bu yüzden
              o tipteyken ölçü seçici gizlenir. */}
          {showControls && a.measures.length > 1 && type !== "combo" && type !== "scatter" && (
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
          {actions}
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
          box={SIZE_BOX[size]}
          onPointClick={
            onDrill && a.primaryDim && a.primaryDim !== a.timeCol && a.dims.length === 1
              ? (x) => onDrill(a.primaryDim!, x)
              : undefined
          }
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
  box,
  onPointClick,
}: {
  result: QueryResult;
  analysis: ReturnType<typeof analyze>;
  type: ChartKind;
  measure: string;
  /** /schema cubes[].lower_is_better — "yüksek = kötü" ölçüler. */
  lowerSet: ReadonlySet<string>;
  /** Grafik kutusu ölçüsü — satır içi stil (bkz. SIZE_BOX). */
  box: React.CSSProperties;
  onPointClick?: (x: string) => void;
}) {
  // Isı haritası ve panelli görünüm Recharts primitifi değil — kendi bileşenleri
  // var. Geri kalan her tip <Chart> façade'ından geçer (DESIGN.md: tek motor).
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
        <Facet result={result} analysis={analysis} measure={measure} box={box} />
      ) : (
        <Chart
          result={result}
          analysis={analysis}
          kind={type}
          measure={measure}
          box={box}
          onPointClick={onPointClick}
        />
      )}
    </div>
  );
}
