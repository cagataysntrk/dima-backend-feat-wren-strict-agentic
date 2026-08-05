"use client";

import { useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { getSchema } from "@/lib/api-client";
import { setSchemaUnits, unitSuffix } from "@/lib/format";
import type { QueryResult, VizSpec } from "@/lib/types";
import { ALL_MEASURES, analyze, analysisFromViz, buildOption, facetPanelValues, kpiCards, type ChartKind } from "@/lib/chart";
import { exportChartImage, exportTableCsv, printReport } from "@/lib/export";
import { EChart } from "./EChart";
import { ResultTable } from "./ResultTable";
import { PivotTable } from "./PivotTable";
import { Select } from "./Select";

// Dışa aktarma açılır menüsü — grafik PNG/SVG (yalnız grafik görünümdeyken anlamlı), tablo
// CSV (her zaman), rapor yazdır/PDF (her zaman). `Select` gibi "seçili değer" taşımaz —
// her tıklama ANINDA bir eylem tetikler (indirme/yazdırma), bu yüzden ayrı, basit bir menü.
function ExportMenu({
  onPng,
  onSvg,
  onCsv,
  onPrint,
}: {
  onPng?: () => void;
  onSvg?: () => void;
  onCsv: () => void;
  onPrint: () => void;
}) {
  const [open, setOpen] = useState(false);
  const item =
    "flex w-full items-center gap-1.5 whitespace-nowrap px-2.5 py-1.5 text-left font-mono text-[11px] text-neutral-600 transition-colors hover:bg-neutral-500/[0.06] dark:text-neutral-300";
  return (
    <div className="relative">
      <button
        type="button"
        aria-label="Dışa aktar"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-600 transition-colors hover:border-neutral-400 dark:text-neutral-300 dark:hover:border-neutral-600"
      >
        <span>⬇ dışa aktar</span>
      </button>
      {open && (
        <>
          <button
            type="button"
            aria-hidden
            tabIndex={-1}
            onClick={() => setOpen(false)}
            className="fixed inset-0 z-20 cursor-default"
          />
          <div className="absolute right-0 z-30 mt-1 min-w-full border border-hairline bg-background shadow-lg">
            {onPng && (
              <button type="button" className={item} onClick={() => { setOpen(false); onPng(); }}>
                Grafik · PNG
              </button>
            )}
            {onSvg && (
              <button type="button" className={item} onClick={() => { setOpen(false); onSvg(); }}>
                Grafik · SVG
              </button>
            )}
            <button type="button" className={item} onClick={() => { setOpen(false); onCsv(); }}>
              Tablo · CSV
            </button>
            <button type="button" className={item} onClick={() => { setOpen(false); onPrint(); }}>
              Yazdır / PDF olarak kaydet
            </button>
          </div>
        </>
      )}
    </div>
  );
}

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
  result: rawResult,
  viewHint,
  viz,
  onViewChange,
  onDataPointClick,
}: {
  result: QueryResult;
  viewHint?: string;
  viz?: VizSpec | null;
  // Pano: kullanıcı görünümü/tipi değiştirince ÜSTE bildir → widget'a KAYDET (view_hint).
  onViewChange?: (viewHint: string) => void;
  // Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-2) — grafikte TEK bir çubuğa/dilime
  // tıklamayı kök-neden dallanmasına (DrillDownPanel action:"select") bağlar. Yalnız
  // TEK bir birincil kategorik boyutlu, basit grafik biçimlerinde (bar/line/pie; facet/
  // scatter/heatmap HARİÇ) — bu şekillerde "hangi kategori tıklandı" belirsizleşir,
  // yanlış bir dallanma UYDURMAKTANSA hiç tetiklenmemesi tercih edilir.
  /** ⚠ `ek` (FAZ 4B): ÇOK-ÇAPALI seçim. Panelli grafik ve ısı haritası tam olarak
   *  bunun yokluğu yüzünden kapalıydı. */
  onDataPointClick?: (dimension: string, value: string,
                      ek?: { dimension: string; value: string }[]) => void;
}) {
  // Yüzdelik oranların (0-1) dinamik olarak 0-100 ölçeğine çekilmesi.
  // Bu sayede 0.8 (Kullanılabilirlik) ve 60 (OEE) aynı grafikte patlamadan çizilir.
  const result = useMemo(() => {
    const isNum = (v: unknown) => typeof v === "number" || (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v)));
    const num = (v: unknown) => typeof v === "number" ? v : Number(v);
    
    const pctMeasures = rawResult.columns.filter(c => unitSuffix(c) === "%");
    if (pctMeasures.length === 0) return rawResult;

    const rows = rawResult.rows.map(r => ({ ...r }));
    let changed = false;

    for (const m of pctMeasures) {
      const maxVal = Math.max(0, ...rows.map(r => num(r[m])).filter(v => !Number.isNaN(v)));
      if (maxVal > 0 && maxVal <= 1.2) {
        changed = true;
        for (const r of rows) {
          if (isNum(r[m])) {
            r[m] = num(r[m]) * 100;
          }
        }
      }
    }
    return changed ? { ...rawResult, rows } : rawResult;
  }, [rawResult]);

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
    if (hintKind || hintBase === "chart") return "chart";  // açık grafik tipi VEYA jenerik "grafik yap"
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
  // 🔴 FAZ 6 — **RENDER SIRASINDA AYARLAMA**, effect DEĞİL.
  //
  // Eski hâl bir effect + `mounted` ref + `eslint-disable` üçlüsüydü ve iki bedeli vardı:
  //   1. Kullanıcı **bayat görünümü bir kare görüyordu** (effect commit'ten sonra koşar;
  //      yeni sonuç eski "tablo" seçimiyle bir an çiziliyordu).
  //   2. `mounted` ref'i *"ilk mount'ta atla"* demek için vardı — yani durum, kendini
  //      ne zaman sıfırlayacağını **hatırlamak** zorundaydı.
  //
  // React'ın bu iş için belgelediği desen: **önceki değeri durumda tut, render sırasında
  // karşılaştır.** Değişim anında yeniden render edilir ve bayat çıktı hiç commit edilmez;
  // `mounted` bayrağı da gereksizleşir (ilk render'da `onceki === shapeSig`).
  //
  // ⚠ Pano 60sn yenilemesi (aynı sorgu → aynı imza) kullanıcının manuel seçimini
  // BOZMAZ — imza değişmediği için dal hiç girilmez.
  const [oncekiSekil, setOncekiSekil] = useState(shapeSig);
  if (shapeSig !== oncekiSekil) {
    setOncekiSekil(shapeSig);
    setView(defaultView());
    setType(hintKind ?? a.kind);
    setMeasure(measureDefault());
  }

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

  // P1-2: TEK bir çubuğa/dilime tıkla → kök-neden dallanması. Yalnız BASİT, tek birincil
  // boyutlu şekillerde (facet/scatter/heatmap HARİÇ) — bu diğerlerinde "hangi kategori"
  // belirsizleşir. ECharts'ın gösterdiği `name` BİÇİMLENDİRİLMİŞ olabilir (ör. tarih) —
  // ham satırlarda TAM eşleşen değeri ARARIZ; bulunamazsa (biçim farklıysa) SESSİZCE
  // atlanır (yanlış bir filtre göndermektense hiç göndermemek daha güvenlidir).
  // Madde 2/3 (1 Ağustos 2026, §C1): `onDataPointClick` YOKSA (cube_query yok — Discovery/LLM
  // yanıtı) önceden tıklama SESSİZCE hiçbir şey yapmıyordu ("tıklasam da açılmıyor" hissi TAM
  // BURADAN geliyordu). Diğer erken-çıkışlar (facet/scatter şekli, değer eşleşmedi) BİLİNÇLİ
  // kalır — yanlış bir filtre göndermektense hiç göndermemek DAHA GÜVENLİDİR, onlara DOKUNULMAZ.
  const [noDrillHint, setNoDrillHint] = useState<string | null>(null);
  /** 🔴 FAZ 7.3/e — **sessiz ret bitti; her ret bir SEBEP söyler.**
   *
   * Yol haritası *"facet/scatter/heatmap kısıtı kaldırılır"* diyor. Kısıt **ölçüldü** ve
   * üçü aynı sınıf değil:
   *
   * | şekil | çapa türetilebilir mi | karar |
   * |---|---|---|
   * | `scatter` | ✅ nokta = `primaryDim`'in bir değeri (x/y **ölçüdür**, boyut değil) | **kısıt KALKTI** |
   * | `facet` | ❌ panel = facet değeri **ve** çubuk = birincil boyut → **İKİ filtre** | kısıt kalır |
   * | `heatmap` | ❌ hücre = satır boyutu **ve** sütun boyutu → **İKİ filtre** | kısıt kalır |
   *
   * 🔴 Facet/heatmap'te tek bir çapa göndermek, kullanıcının tıkladığından **daha geniş**
   * bir kırılım açardı — *"bu hücreye tıkladım, bana tüm satırı gösterdi"*. Ve drill
   * sözleşmesi (`DrillRequest`: `dimension` + `filter_value`, **tekil**) iki filtreyi
   * taşıyamıyor: bu bir **sözleşme değişikliğidir**, bir UI ayarı değil.
   *
   * ⚠ **Ama sessizlik bir karar değildi, bir kusurdu.** Kodun kendi yorumu kullanıcının
   * şikâyetini yazıyordu: *"tıklasam da açılmıyor" hissi TAM BURADAN geliyordu.* Artık
   * her erken-çıkış **neden** olduğunu söylüyor — *bir sınırı söylemek, onu bir kusur
   * olmaktan çıkarır.*
   */
  const handleChartDataPointClick = (info: { seriesIndex: number; dataIndex: number;
                                             name: string; data?: unknown }) => {
    if (!onDataPointClick) {
      setNoDrillHint(
        "bu sonuç LLM tarafından üretildi, kırılım için cube sorgusu yok — \"+ sql göster\"e bakabilirsin",
      );
      return;
    }
    // 🔴 FAZ 4B (D.3) — **KISIT KALKTI: her grafik türü bir giriş noktasıdır.**
    // Nokta kendi çapalarını taşıyorsa (panelli grafik · ısı haritası) onları
    // OLDUĞU GİBİ göndeririz; sözleşme artık çoklu çapa kabul ediyor
    // (`DrillRequest.ek_filtreler`). ⚠ Bu bir UI ayarı değil, bir SÖZLEŞME
    // genişlemesiydi — eski kısıt bir tercih değil bir sınırdı.
    const capalar = (info.data as { capalar?: { dimension: string; value: string }[] } | undefined)
      ?.capalar;
    if (capalar?.length) {
      const [ilk, ...kalan] = capalar;
      onDataPointClick(ilk.dimension, ilk.value, kalan);
      return;
    }
    const dim = effA.primaryDim;
    if (!dim) {
      setNoDrillHint("bu grafikte kırılacak tek bir kategorik boyut yok");
      return;
    }
    // ⚠ Çapasız bir panelli/ısı noktası **kenar özetidir** (satır/sütun ortalaması) —
    // bir kesişim değil. Orada kırılacak tek bir satır kümesi YOKTUR ve bunu söylemek,
    // yanlış bir filtre göndermekten dürüsttür.
    if (effA.facet || effA.facetMeasure || effA.heat || effA.heatAny) {
      setNoDrillHint(
        "bu nokta bir kesişim değil bir ÖZET (satır/sütun ortalaması) — kırılacak tek bir satır kümesi yok; bir hücreye tıklayabilirsin",
      );
      return;
    }
    const rawValue = effResult.rows.find((r) => String(r[dim] ?? "") === info.name)?.[dim];
    if (rawValue == null) {
      // ⚠ ECharts'ın gösterdiği `name` BİÇİMLENDİRİLMİŞ olabilir (ör. tarih). Ham satırda
      // tam eşleşme yoksa yanlış bir filtre göndermektense hiç göndermemek doğrudur —
      // ama artık **sessiz değil**.
      setNoDrillHint("tıklanan etiket ham veriyle eşleşmedi — yanlış bir filtre göndermek yerine durduk");
      return;
    }
    onDataPointClick(dim, String(rawValue));
  };
  useEffect(() => {
    if (!noDrillHint) return;
    // ⚠ 3 sn → 6 sn: sebep artık bir cümle, ve okunamayan bir açıklama yok sayılır.
    const t = setTimeout(() => setNoDrillHint(null), 6000);
    return () => clearTimeout(t);
  }, [noDrillHint]);

  // Grafik yalnız çizilebilir + ölçü varsa hesaplanır (0 satır / ölçüsüz → tablo, çökme yok).
  //
  // YÖN KAYNAĞI (Faz I): backend'in VizSpec'i `lower_set`'i CUBE KAPSAMINDA taşır ve
  // bu cevabın otoritesidir. Şemadan okunan küme ise TÜM CUBE'LARIN BİRLEŞİMİDİR ve
  // ölçüldü (2 Ağustos 2026): `toplam_dogalgaz_sm3` `surdurulebilirlik`'te düşük-iyi,
  // `enerji_makine`'de DEĞİL — birleşim ikisinde de ısı paletini ters çeviriyordu.
  // Yani aynı sayı, yanlış cube'da yanlış renkle okunuyordu.
  //
  // VizSpec varsa O kazanır; yoksa (grafik kararı FE'nin yerel analyze()'ından geldiyse)
  // şema birleşimi YEDEK kalır — yönü hiç bilmemekten iyidir.
  const semaLowerSet = useLowerSet();
  // `vizLower` ayrı bir değişkene alınır: `useMemo` bağımlılığında `viz?.lower_set`
  // yazmak react-compiler'ın çıkarımıyla (`viz`) uyuşmuyor ve derleyici komponentin
  // TAMAMINI optimize etmeyi bırakıyor (eslint yakaladı). Alan önce okunur, bağımlılık
  // o değişken olur — çıkarım ile kaynak aynı şeyi gösterir.
  const vizLower = viz?.lower_set;
  const lowerSet = useMemo(
    () => (vizLower ? new Set(vizLower) : semaLowerSet),
    [vizLower, semaLowerSet],
  );
  const option = useMemo(
    () =>
      chartable && measure
        ? buildOption(effResult, effA, { kind: effKind, measure, dark, lowerSet })
        : null,
    [chartable, effResult, effA, effKind, measure, dark, lowerSet],
  );

  // YÜKSEKLİK (canlı bulgu, 31 Temmuz 2026): EChart'ın sabit min/max aralığı (240-460px,
  // genişlik×0.56) grafiğin İÇERİK KARMAŞIKLIĞINI hesaba katmıyordu — 2-satırlı panel
  // grid'i (facet/facet_measure, N panel eşiği aşınca) ya da çok-satırlı ısı haritası
  // AYNI dar aralığa sıkışıp okunaksızlaşıyordu ("aşırı küçülebiliyor" şikâyeti). Panel/satır
  // sayısına göre taban/tavan büyütülür; basit tek-panel grafikler ESKİ (240-460) davranışta kalır.
  const { chartMinHeight, chartMaxHeight } = useMemo(() => {
    let minH = 240, maxH = 460;
    if (effKind === "facet_measure" && effA.facetMeasure) {
      if (effA.facetMeasure.measures.length > 3) { minH = 420; maxH = 720; } // 2 satır
    } else if (effKind === "facet" && effA.facet && !single) {
      if (panels.length > 4) { minH = 420; maxH = 720; } // 2 satır
    } else if (effKind === "heatmap" && (effA.heat || effA.heatAny)) {
      const rowDim = (effA.heat ?? effA.heatAny)!.row;
      const rowCount = new Set(effResult.rows.map((r) => String(r[rowDim]))).size;
      if (rowCount > 8) {
        const px = Math.min(700, 140 + rowCount * 22); // başlık/marj + satır başına yer
        minH = Math.max(minH, px);
        maxH = Math.max(maxH, px);
      }
    }
    return { chartMinHeight: minH, chartMaxHeight: maxH };
  }, [effKind, effA, panels.length, single, effResult]);

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
        <div data-no-print className="flex flex-wrap items-center gap-1.5">
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
          {/* 🔴 FAZ 5.11 (§15.6) — **ÇİZİLMEME GEREKÇESİ**. *Çizilmeyen bir grafik, neden
              çizilmediğini söylemeli* — aksi hâlde kullanıcı ürünün bunu BECEREMEDİĞİNİ
              sanar ve deterministik bir karar bir arıza gibi görünür. Gerekçe backend'de
              üretilir (tek sahip); burada yalnız gösterilir. */}
          {viz?.cizilmedi && (
            <span
              className="font-mono text-[var(--text-etiket)] text-neutral-400"
              title="Görsel dilbilgisi kararı (deterministik, §15.6)"
            >
              ⓘ grafik yerine {viz.kind === "table" ? "tablo" : "özet"} — {viz.cizilmedi}
            </span>
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
          <ExportMenu
            onPng={
              view === "chart" && option
                ? () => exportChartImage(option, "png", "dima-grafik", { dark })
                : undefined
            }
            onSvg={
              view === "chart" && option
                ? () => exportChartImage(option, "svg", "dima-grafik", { dark })
                : undefined
            }
            onCsv={() => exportTableCsv(effResult, "dima-tablo")}
            onPrint={printReport}
          />
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
              minHeight={chartMinHeight}
              maxHeight={chartMaxHeight}
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
              onDataPointClick={handleChartDataPointClick}
            />
            {noDrillHint && (
              <p role="status" className="mt-1 font-mono text-[11px] text-neutral-400">
                {noDrillHint}
              </p>
            )}
          </div>
        ) : (
          <ResultTable result={result} />
        )
      )}
    </div>
  );
}
