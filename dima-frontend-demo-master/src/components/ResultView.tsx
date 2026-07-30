"use client";

import { useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { getSchema } from "@/lib/api-client";
import { setSchemaUnits } from "@/lib/format";
import type { QueryResult, VizSpec } from "@/lib/types";
import { ALL_MEASURES, analyze, analysisFromViz, buildOption, facetPanelValues, kpiCards, type ChartKind } from "@/lib/chart";
import { EChart } from "./EChart";
import { ResultTable } from "./ResultTable";
import { PivotTable } from "./PivotTable";
import { Select } from "./Select";

// "Yüksek=kötü" ölçü kümesi — kaynağı metadata (/schema cubes[].lower_is_better);
// açılışta bir kez okunur, modül düzeyinde tutulur (useFeature deseni). Aynı okumada
// ölçü BİRİMLERİ de (/schema cubes[].units) format katmanına verilir — birim şirket/cube
// başına yeniden tanımlanmaz, metadata'da bir kez, gerisi platform.
let _lowerSet: ReadonlySet<string> | null = null;
function useLowerSet(): ReadonlySet<string> | undefined {
  const [set, setSet] = useState<ReadonlySet<string> | undefined>(_lowerSet ?? undefined);
  useEffect(() => {
    if (_lowerSet) return;
    getSchema()
      .then((s) => {
        const cubes = (s as {
          cubes?: { lower_is_better?: string[]; units?: Record<string, string> }[];
        }).cubes ?? [];
        _lowerSet = new Set(cubes.flatMap((c) => c.lower_is_better ?? []));
        setSchemaUnits(Object.assign({}, ...cubes.map((c) => c.units ?? {})));
        setSet(_lowerSet);
      })
      .catch(() => {});
  }, []);
  return set;
}

const TYPE_LABEL: Record<ChartKind, string> = {
  bar: "Sütun",
  line: "Çizgi",
  pie: "Pasta",
  heatmap: "Isı haritası",
  facet: "Panelli",
  facet_measure: "Ölçü panelleri",
  scatter: "Serpme",
  stacked: "Yığılı",
  treemap: "Ağaç harita",
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
export function ResultView({
  result,
  viewHint,
  viz,
  onViewChange,
}: {
  result: QueryResult;
  viewHint?: string;
  viz?: VizSpec | null;
  // Pano: kullanıcı görünümü/tipi değiştirince ÜSTE bildir → widget'a KAYDET (view_hint).
  onViewChange?: (viewHint: string) => void;
}) {
  // BİLEŞİK view_hint (grafiğin TÜM özellikleri panoya taşınsın): "<main>#<measure>".
  //   main = table | pivot | <grafikTipi> | facet:<dim>  ·  measure = ALL_MEASURES ("__tumu__") | kolon
  // "facet:kumas_cinsi" — panel boyutu KULLANICININ istediği boyut olur; analiz sezgisi ezilir.
  const [vhMain, vhMeasure] = (viewHint ?? "").split("#");
  const hintBase = vhMain ? vhMain.split(":")[0] : undefined;
  const facetDim = vhMain?.startsWith("facet:") ? vhMain.slice(6) : null;
  // ADR-0024: grafik/tablo/pivot KARARI backend'de (data.viz) verilir → yerel analyze()
  // yerine onu kullan. viz yoksa (yüklenen serbest veri / eski yanıt) analyze()'e düş.
  // view_hint (facetDim) ve kullanıcı toggle bu kararın ÜSTÜNE biner (aşağıda).
  const a = useMemo(() => {
    const b = viz ? analysisFromViz(viz) : analyze(result);
    if (facetDim && b.dims.length === 3 && b.dims.includes(facetDim)) {
      const others = b.dims.filter((d) => d !== facetDim);
      const x = b.timeCol && b.timeCol !== facetDim ? b.timeCol : others[0];
      const series = others.find((d) => d !== x) ?? others[0];
      return { ...b, kind: "facet" as ChartKind, facet: { dim: facetDim, x, series } };
    }
    return b;
  }, [result, facetDim, viz]);
  const chartable = a.kind !== "none" && a.kind !== "kpi";

  // PIVOT: çapraz tablo (satır × sütun × ölçü). Backend viz.kind==="pivot" ise rolleri (rows/cols/
  // measures) oradan gelir (dim×dim); yoksa klasik zaman-kovası × TEK varlık boyutu şekli. Uzun
  // "N ürün × ay × metrik" sonucunu okunur matrise çevirir. PivotTable.timeCol jeneriktir
  // (fmtTemporal zaman-dışı kolonda ham değere düşer) → kategori sütunu da güvenli.
  const bp = viz?.kind === "pivot" ? viz.pivot : null;
  const pivotCol = bp?.cols?.[0] ?? a.timeCol ?? null;              // sütun ekseni
  const pivotRow =
    bp?.rows?.[0] ??
    (a.timeCol && a.dims.length === 2 && a.measures.length >= 1
      ? a.dims.find((d) => d !== a.timeCol) ?? null
      : null);
  const pivotMeasure = bp?.measures?.[0] ?? null;
  const pivotable = pivotCol != null && pivotRow != null && a.measures.length >= 1;

  const hintKind = (["line", "bar", "pie", "heatmap", "facet", "facet_measure", "scatter", "stacked", "treemap"] as ChartKind[]).find((k) => k === hintBase);
  const wantsChart = viewHint != null && hintBase !== "table";
  // BAŞLANGIÇ GÖRÜNÜMÜ: backend viz kararı (ADR-0024) belirler → GRAFİK varsayılan. viz yoksa
  // (yüklenen serbest veri) eski sezgiye düşülür. view_hint ("tablo olarak"/"ısı haritası") üstüne biner.
  const defaultView = (): "chart" | "table" | "pivot" => {
    // 1) AÇIK kullanıcı/hint tercihi (pano widget'ının kayıtlı view_hint'i dahil) her şeyin ÜSTÜNDE.
    if (hintBase === "table") return "table";
    if (hintBase === "pivot") return pivotable ? "pivot" : "table";
    if (hintKind) return "chart";  // açık grafik tipi (bar/line/pie/heatmap/facet) → grafik
    // 2) Backend viz kararı (ADR-0024): pivot → pivot, chartable → GRAFİK, none → tablo. Uzun
    //    zaman-serisinde bile viz "line" dediyse GRAFİK gelir (rapor/pano hep pivot'a DÜŞMEZ).
    if (viz) {
      if (viz.kind === "pivot") return pivotable ? "pivot" : "table";
      return a.kind === "none" ? "table" : "chart";
    }
    // 3) viz YOK (legacy/yüklenen veri): çok-varlıklı zaman serisi → PIVOT sezgisi.
    if (pivotable && a.timeCol && result.rows.length > 12) return "pivot";
    return a.kind === "none" ? "table" : "chart";
  };
  const [view, setView] = useState<"chart" | "table" | "pivot">(defaultView);
  const [type, setType] = useState<ChartKind>(hintKind ?? a.kind);
  // Ölçü seçimi: kayıtlı view_hint'teki ölçü (kombo "tümü" ya da kolon) geçerliyse onu KORU;
  // yoksa çok-ölçü → "tümü" (kombo), tek ölçü → kendisi.
  const measureDefault = () =>
    vhMeasure && (vhMeasure === ALL_MEASURES || a.measures.includes(vhMeasure))
      ? vhMeasure
      : a.measures.length > 1 ? ALL_MEASURES : (a.measures[0] ?? "");
  const [measure, setMeasure] = useState<string>(measureDefault);
  // ŞEKİL DEĞİŞİNCE (chip edit: dönem/kırılım/kova → farklı kolonlar/viz.kind) görünümü backend
  // kararına SIFIRLA — bayat "tablo" seçimi yeni raporda kalmasın (parent remount'a bağlı kalmadan).
  // Yalnız ŞEKİL imzası değişince tetiklenir: pano 60sn refetch'i (aynı sorgu) kullanıcının manuel
  // seçimini BOZMAZ. İlk mount'ta useState zaten ayarladı → atla.
  const shapeSig = `${result.columns.join(",")}|${viz?.kind ?? ""}`;
  const mounted = useRef(false);
  useEffect(() => {
    if (!mounted.current) { mounted.current = true; return; }
    setView(defaultView());
    setType(hintKind ?? a.kind);
    setMeasure(measureDefault());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shapeSig]);

  // Güncel görünümün BİLEŞİK view_hint'i (grafiğin TÜM özellikleri): main#measure.
  //   main = table | pivot | facet:<dim> | <grafikTipi>   ·   measure yalnız grafik + çok-ölçüde
  const currentViewHint = (): string => {
    if (view === "table") return "table";
    if (view === "pivot") return "pivot";
    const main = type === "facet" && a.facet ? `facet:${a.facet.dim}` : type;
    return a.measures.length > 1 && measure ? `${main}#${measure}` : main;
  };
  // GÖRÜNÜM KAYDET (pano/panoya-ekle): kullanıcı view/tip/ÖLÇÜ değiştirince üste bildir. Mount'ta
  // ve şekil-reset'inde tetiklenmez (yalnız GERÇEK kullanıcı değişimi). Chat'te ReportPanel bunu
  // "panoya ekle"de kullanır; pano widget'ı PATCH ile kalıcılaştırır (yeniden yüklemede aynı grafik).
  const vcMounted = useRef(false);
  useEffect(() => {
    if (!vcMounted.current) { vcMounted.current = true; return; }
    onViewChange?.(currentViewHint());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, type, measure]);
  const dark = usePrefersDark();

  const availableTypes = useMemo<ChartKind[]>(() => {
    const t: ChartKind[] = [];
    if (a.facet) t.push("facet");
    if (a.facetMeasure) t.push("facet_measure");
    if (a.scatter) t.push("scatter");
    if (a.timeCol) t.push("line");
    if (!a.facet && !a.facetMeasure && !a.scatter) t.push("bar");
    if (a.stackable) t.push("stacked");  // additive + seri → yığılı toggle (ADR-0024)
    if (a.heat || a.heatAny) t.push("heatmap");  // açık seçim min-eksen kuralına takılmaz
    // PARTITION (pay): tek boyut + additive → backend'in önerdiği alternatif (pie≤6 / treemap)
    if (a.partition && a.alternatives?.includes("pie")) t.push("pie");
    if (a.partition && a.alternatives?.includes("treemap")) t.push("treemap");
    // klasik yedek (viz yokken): az-satırlı tek-boyut → pasta
    else if (!a.timeCol && a.primaryDim && a.measures.length >= 1 && result.rows.length <= 12 && !a.partition) t.push("pie");
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
  const lowerSet = useLowerSet();
  const option = useMemo(
    () =>
      chartable && measure
        ? buildOption(effResult, effA, { kind: effKind, measure, dark, lowerSet })
        : null,
    [chartable, effResult, effA, effKind, measure, dark, lowerSet],
  );

  const cards = a.kind === "kpi" ? kpiCards(result, a) : [];

  const seg = "px-3 py-1 font-mono text-[11px] tracking-wide transition-colors";
  const segOn = "bg-foreground text-background";
  const segOff = "text-neutral-500 hover:text-foreground";

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-mono text-[11px] uppercase tracking-wider text-neutral-400">
          sonuç · {result.row_count} satır
        </h3>
        <div className="flex flex-wrap items-center gap-1.5">
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
          {(a.kind !== "none" || pivotable) && (
            <div className="inline-flex border border-hairline">
              {chartable && (
                <button className={`${seg} ${view === "chart" ? segOn : segOff}`} onClick={() => setView("chart")}>
                  grafik
                </button>
              )}
              <button
                className={`${chartable ? "border-l border-hairline " : ""}${seg} ${view === "table" ? segOn : segOff}`}
                onClick={() => setView("table")}
              >
                tablo
              </button>
              {pivotable && (
                <button
                  className={`border-l border-hairline ${seg} ${view === "pivot" ? segOn : segOff}`}
                  onClick={() => setView("pivot")}
                >
                  pivot
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {view === "pivot" && pivotable && pivotCol && pivotRow ? (
        <PivotTable
          result={result}
          timeCol={pivotCol}
          entityDim={pivotRow}
          measure={pivotMeasure ?? (!measure || measure === ALL_MEASURES ? a.measures[0] : measure)}
        />
      ) : view === "table" || (a.kind === "none" && view !== "pivot") ? (
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
