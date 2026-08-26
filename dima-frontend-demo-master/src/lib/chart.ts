// Sonuç tablosunun ŞEKLİNDEN otomatik grafik tipi çıkarımı + ECharts option üretimi.
// Desteklenen: KPI (tek satır), bar, line (zaman), pie, heatmap (2 boyut × ölçü matrisi).
// Tüm sayılar birim-farkında biçimlendirilir (₺, kg, L, kWh, %, dk...) — bkz. format.ts.

import type { EChartsOption } from "echarts";
import type { QueryResult, Row, VizSpec } from "./types";
import { fmtAxis, fmtTemporal, fmtValue, unitSuffix } from "./format";

// Eksen ETİKETİ: zaman kovalarını okunur yap ("Oca 2026") — sıralama ham değerle kalır.
const axisLabel = (v: string, col: string | null) => (col ? fmtTemporal(v, col) ?? v : v);

// 🔴🔴 `§K5` — kategori sayısına göre eksen etiketi SIKIŞTIRMA — TEK karar noktası (KAT-1).
// Ölçüldü (canlı, Playwright kampanyası — 11 makine): döndürme TEK BAŞINA (35°, sabit
// font) yetmiyor, etiketler üst üste biniyor. Kategori sayısı arttıkça döndürme + küçük
// font + (izin varsa) ECharts'ın kendi çakışma-önleme atlaması (`interval:"auto"`) birlikte
// devreye girer. Domain-agnostik: yalnız `n`'e (kategori SAYISINA) bakar, hangi boyut
// (makine/hesap/şube/…) olduğuna değil.
// `allowSkip=false`: hücre-hizalı eksenler (heatmap) — etiket ASLA atlanmaz (her sütun bir
// hücreye haritalanır, atlanırsa okuyucu hangi hücrenin hangi değere ait olduğunu kaybeder);
// yalnız döndürme/küçültme ile sıkıştırılır.
const axisLabelSpacing = (
  n: number,
  allowSkip = true,
): { interval: 0 | "auto"; rotate: number; fontSize?: number } => {
  if (allowSkip && n > 10) return { interval: "auto", rotate: 45, fontSize: 10 };
  if (n > 8) return { interval: 0, rotate: 40, fontSize: 10 };
  if (n > 5) return { interval: 0, rotate: 30, fontSize: 11 };
  return { interval: 0, rotate: 0 };
};

// ADR-0024: backend viz.kind ile FE ChartKind hizası. "table"/"pivot" grafik değil → "none".
export type ChartKind =
  | "kpi" | "bar" | "line" | "pie" | "heatmap" | "facet"
  | "facet_measure" | "scatter" | "stacked" | "treemap" | "none";

// SÜREKLI zaman (trend → çizgi). "gün/vardiya" gibi DÖNGÜSEL kategorikler kasıtlı olarak
// burada YOK — onlar ısı haritasına gitsin (ör. vardiya × haftanın günü). Gerçek tarih
// kolonları zaten değer biçiminden (looksDate) yakalanır.
const TIME_NAMES = new Set(["donem", "dönem", "tarih", "ay", "hafta", "period", "yil", "yıl", "year", "ceyrek", "çeyrek"]);
const PALETTE = ["#4F8CFF", "#22C55E", "#F59E0B", "#EF4444", "#A855F7", "#06B6D4", "#EC4899", "#84CC16"];
const HEAT = ["#EF4444", "#F59E0B", "#FDE047", "#84CC16", "#22C55E"]; // düşük→yüksek (kırmızı→yeşil)
// YÖN SEMANTİĞİ: yüksek=KÖTÜ ölçülerde ısı paleti ters çevrilir (yüksek=kırmızı).
// ASIL kaynak metadata'dır (/schema cubes[].lower_is_better → BuildOpts.lowerSet):
// yeni sektör pack'i frontend değişikliği İSTEMEZ. Regex yalnız metadata'sız
// eski/serbest ölçüler için yedektir.
const LOWER_IS_BETTER = /fire|durus|sapma|maliyet|tuketim|yogunluk|su_|enerji/i;
const heatPalette = (measure: string, lowerSet?: ReadonlySet<string>): string[] =>
  lowerSet?.has(measure) || LOWER_IS_BETTER.test(measure) ? [...HEAT].reverse() : HEAT;
const AVG = "∑ Ort.";

const isNum = (v: unknown) =>
  typeof v === "number" || (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v)));
const num = (v: unknown) => (typeof v === "number" ? v : Number(v));
const looksDate = (v: unknown) => typeof v === "string" && /^\d{4}-\d{2}/.test(v);
const distinct = (rows: Row[], c: string) => [...new Set(rows.map((r) => r[c]))];
const fmtCat = (v: unknown) => (looksDate(v) ? String(v).slice(0, 10) : String(v ?? "—"));
const mean = (a: number[]) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);

// Kanonik haftanın-günü sırası — kategori değerleri gün ise kronolojik sırala (Pzt→Paz),
// değilse alfabetik (tarih YYYY-MM zaten kronolojik). Kaynak cube ya da LLM olsun, her yerde.
const WEEKDAY_ORDER = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
const orderCats = (vals: string[]): string[] =>
  vals.length && vals.every((v) => WEEKDAY_ORDER.includes(v))
    ? [...vals].sort((a, b) => WEEKDAY_ORDER.indexOf(a) - WEEKDAY_ORDER.indexOf(b))
    : [...vals].sort();

export interface Analysis {
  kind: ChartKind;
  measures: string[];
  dims: string[];
  timeCol: string | null;
  primaryDim: string | null;
  heat: { row: string; col: string } | null;
  // Açık istek için serbest eşleme: "ısı haritası olarak ver" min-eksen≥3 otomatik
  // kuralına takılmamalı (kural yalnız OTOMATİK tip seçimi içindir; log 2026-07-20).
  heatAny: { row: string; col: string } | null;
  // 3 kırılım → small multiples (facet/trellis): en az-değerli boyut panellere bölünür,
  // her panel gruplu sütun (BI best practice; stack oran metriklerinde YANLIŞ olurdu).
  facet: { dim: string; x: string; series: string } | null;
  // ADR-0024 çok-birim: ≥3 farklı birim → ölçüye-göre small multiples (her ölçü kendi paneli+birimi).
  facetMeasure?: { measures: string[]; x: string; series: string | null } | null;
  // Korelasyon: 2 ölçü x/y ekseninde (+ opsiyonel boyut = nokta boyutu, renk = kategori).
  scatter?: { x: string; y: string; color?: string; size?: string } | null;
  // Seri (renk) boyutu — gruplu/yığılı bar & çok-serili çizgi için (backend belirler).
  seriesDim?: string | null;
  dualAxis?: boolean;   // 2 birim → birincil bar + ikincil çizgi (çift eksen)
  stackable?: boolean;  // additive + seri → yığma toggle sunulabilir
  partition?: boolean;  // tek boyut + additive → pay grafiği (pie/treemap) sunulabilir
  alternatives?: string[]; // kullanıcı-toggle önerileri (ör. ["pie"]/["treemap"])
  // §E (1 Ağustos 2026, Madde 11 kalan kısım): tek boyut + tek ölçü (kart≥4) → ölçünün
  // ORTALAMASI yatay referans çizgisi olarak AYNI bar grafiğinde ("kim ortalamanın
  // üstünde/altında" — kişi/varlık bazlı karşılaştırma, backend hesaplar).
  referenceLine?: { kind: string; measure: string; value: number } | null;
}

// Backend VizSpec → FE Analysis adaptörü (ADR-0024). `data.viz` geldiğinde yerel analyze()
// yerine bu kullanılır → grafik/tablo/pivot KARARI backend'de tek kaynaktan gelir. Kind eşlemesi:
// "table"/"pivot" grafik değil → "none" (FE view state pivot/tablo'yu ayrıca yönetir).
export function analysisFromViz(v: VizSpec): Analysis {
  // ⚠️ **FAZ 5.11 — `cumle` EKLENDİ.** Backend §15.6'nın dört kuralıyla artık bazı
  // raporlarda *"grafik çizilmez"* diyor ve `kind: "cumle"` döndürüyor. Bu değer
  // eşlemede olmasaydı `as ChartKind` ile sessizce geçer, ECharts tanımadığı bir tip
  // görür ve kullanıcı **boş bir kart** alırdı — *yani "çizmeme kararı" bir arıza gibi
  // görünürdü.* Bu depo aynı sınıfı beşinci kez görüyor (top · order · delta/streak ·
  // segment_delta · bu): **backend bir tür üretir, FE sözlüğünde yoksa sessizce bozulur.**
  const kind: ChartKind =
    v.kind === "table" || v.kind === "pivot" || v.kind === "cumle"
      ? "none"
      : (v.kind as ChartKind);
  return {
    kind,
    measures: v.measures ?? [],
    dims: v.dims ?? [],
    timeCol: v.time_col ?? null,
    primaryDim: v.primary_dim ?? null,
    heat: v.heat ?? null,
    heatAny: v.heat_any ?? null,
    facet: v.facet ?? null,
    facetMeasure: v.facet_measure ?? null,
    scatter: v.scatter ?? null,
    seriesDim: v.series_dim ?? null,
    dualAxis: v.dual_axis ?? false,
    stackable: v.stackable ?? false,
    partition: v.partition ?? false,
    alternatives: v.alternatives ?? [],
    referenceLine: v.reference_line ?? null,
  };
}

// KOPYA-MANTIK DURUMU (31 Temmuz 2026 — bağımsız araştırmayla denetlendi, eşlenik not:
// backend app/viz.py modül docstring'i): bu fonksiyon backend'in `viz.analyze()`'iyle taban
// karar (kpi/bar/line/heatmap/facet/table) düzeyinde birebir eşdeğer KALMALI (drift YOK,
// doğrulandı) ama backend'in `recommend()` katmanını (scatter/facet_measure/stacked/pivot/
// partition, birim-farkındalığı) BİLEREK taşımıyor — bu yüzden bu fonksiyon HER ZAMAN
// backend'inkinden daha zayıf bir karar üretir. Artık genel bir "viz yoksa yedek" değil,
// YALNIZ ResultView'in facet tek-panel drill-down'ı için kullanılmalı (o alt-küme backend'e
// hiç gitmediğinden `data.viz` onu kapsamaz — mimari olarak gerekli, dar kapsamlı bir
// istisna). Üst-seviye `data.viz` YOKSA/eskiyse artık backend kendini onarır: `/ask` hiçbir
// zaman `viz=null` bırakmaz (recommend() patlarsa çıplak analyze()'e düşer) ve sohbet
// resume'i (`/conversations/{id}`) `viz`'i her seferinde taze hesaplar — bu fonksiyonu genel
// bir yedek olarak çağırmak YENİ kod için artık YANLIŞ.
export function analyze(result: QueryResult): Analysis {
  const { columns, rows } = result;
  const measures: string[] = [];
  const dims: string[] = [];
  for (const c of columns) {
    const vals = rows.map((r) => r[c]).filter((v) => v != null);
    (vals.length > 0 && vals.every(isNum) ? measures : dims).push(c);
  }
  const timeCol =
    dims.find((d) => TIME_NAMES.has(d.toLowerCase())) ??
    dims.find((d) => rows.length > 0 && rows.every((r) => r[d] == null || looksDate(r[d]))) ??
    null;

  let heat: { row: string; col: string } | null = null;
  if (dims.length >= 2 && measures.length >= 1 && rows.length >= 4) {
    for (let i = 0; i < dims.length && !heat; i++) {
      for (let j = i + 1; j < dims.length && !heat; j++) {
        const ca = distinct(rows, dims[i]).length;
        const cb = distinct(rows, dims[j]).length;
        const prod = ca * cb;
        // min eksen 3+: 2 kategorili boyut (ör. cinsiyet) ısı haritası değil GRUPLU
        // sütun olarak daha okunur (farklı renk + lejant).
        if (ca > 1 && cb > 1 && Math.min(ca, cb) >= 3 && prod <= rows.length * 1.6 && prod >= rows.length * 0.5) {
          const [row, col] = ca <= cb ? [dims[i], dims[j]] : [dims[j], dims[i]];
          heat = { row, col };
        }
      }
    }
  }

  // Açık "ısı haritası" isteği için: 2+ boyutta her zaman kurulabilir bir eşleme
  // (küçük kardinalite → satır). Otomatik seçim yine `heat` kuralını kullanır.
  let heatAny: Analysis["heatAny"] = heat;
  if (!heatAny && dims.length >= 2 && measures.length >= 1) {
    const multi = [...dims].filter((d) => distinct(rows, d).length > 1)
      .sort((a, b) => distinct(rows, a).length - distinct(rows, b).length);
    if (multi.length >= 2) heatAny = { row: multi[0], col: multi[multi.length - 1] };
  }

  const primaryDim =
    timeCol ??
    (dims.length
      ? dims.slice().sort((a, b) => distinct(rows, b).length - distinct(rows, a).length)[0]
      : null);

  // 3 kırılım → facet adayı: en düşük kardinaliteli boyut panel olur (≤6 panel),
  // kalan ikisinden büyüğü x-ekseni, küçüğü renk serisi.
  let facet: Analysis["facet"] = null;
  if (dims.length === 3 && measures.length >= 1) {
    if (timeCol) {
      // ZAMAN ekseni varsa x HER ZAMAN zamandır (aylar seri olursa okunmaz — ISO
      // lejant karmaşası); kalan iki boyuttan küçüğü panel, diğeri renk serisi.
      const [a, b] = dims.filter((d) => d !== timeCol)
        .sort((x, y) => distinct(rows, x).length - distinct(rows, y).length);
      if (distinct(rows, a).length <= 6) facet = { dim: a, x: timeCol, series: b };
    } else {
      const sorted = [...dims].sort((a, b) => distinct(rows, a).length - distinct(rows, b).length);
      const [fd, sd, xd] = sorted;
      if (distinct(rows, fd).length <= 6) facet = { dim: fd, x: xd, series: sd };
    }
  }

  let kind: ChartKind = "none";
  if (rows.length === 1 && measures.length >= 1 && dims.length <= 1) kind = "kpi";
  else if (measures.length === 0) kind = "none";
  else if (dims.length === 3 && facet) kind = "facet";
  // Geniş detay/liste (3+ kırılım facet'lenemedi ya da 4+) → grafik değil, TABLO.
  else if (dims.length > 2) kind = "none";
  // Zaman ekseni varsa TREND önce gelir (çizgi), ısı haritasından önce.
  else if (timeCol && measures.length >= 1) kind = "line";
  else if (heat) kind = "heatmap";
  else if (primaryDim && measures.length >= 1) kind = "bar";

  return { kind, measures, dims, timeCol, primaryDim, heat, heatAny, facet };
}

interface BuildOpts {
  kind: ChartKind;
  measure: string;
  dark: boolean;
  // Metadata kaynaklı "yüksek=kötü" ölçü kümesi (/schema'dan) — ısı paleti yönü.
  lowerSet?: ReadonlySet<string>;
}

// Panelli görünümde gezinme (carousel): panel değerleri kanonik sırayla.
export const facetPanelValues = (result: QueryResult, dim: string): string[] =>
  orderCats(distinct(result.rows, dim).map(String));

// Ölçü seçicide "tümü" nöbetçisi — çok-ölçülü kombo görünüm (ADR/log 2026-07-21).
export const ALL_MEASURES = "__tumu__";

// KAYDIRMA/YAKINLAŞTIRMA (canlı bulgu, 31 Temmuz 2026): grafiklerde ASLA yaklaşma imkanı
// yoktu (dataZoom hiç eklenmemişti) — çok-kategorili bar/line/heatmap'te (ör. onlarca
// müşteri/kumaş türü) etiketler sıkışıp okunaksızlaşıyordu ve kullanıcının bunu düzeltecek
// hiçbir yolu yoktu. `type: "inside"` (fare tekerleği/pinch — GÖRÜNÜR yer kaplamaz, mevcut
// grid/layout'a dokunmadan EKLENİR) TEK kategorik eksenli (bar/line/combo/stacked/gruplu-bar/
// heatmap) grafiklere post-hoc uygulanır; çok-panelli (facet_measure/pivot, xAxis DİZİ) ve
// value-eksenli (scatter) grafiklere KARIŞMAZ — onların KENDİ etkileşim modeli var/farklı.
function withZoom(option: EChartsOption): EChartsOption {
  const xAxis = option.xAxis;
  const yAxis = option.yAxis;
  if (!xAxis || Array.isArray(xAxis)) return option;
  const ax = xAxis as { type?: string; data?: unknown[] };
  const ay = !yAxis || Array.isArray(yAxis) ? null : (yAxis as { type?: string; data?: unknown[] });
  const xZoomable = ax.type === "category" && (ax.data?.length ?? 0) > 8;
  const yZoomable = ay?.type === "category" && (ay.data?.length ?? 0) > 8;
  if (!xZoomable && !yZoomable) return option;
  return {
    ...option,
    dataZoom: [
      ...(xZoomable ? [{ type: "inside" as const, xAxisIndex: 0 }] : []),
      ...(yZoomable ? [{ type: "inside" as const, yAxisIndex: 0 }] : []),
    ],
  };
}

export function buildOption(result: QueryResult, a: Analysis, o: BuildOpts): EChartsOption {
  return withZoom(buildOptionInner(result, a, o));
}

function buildOptionInner(result: QueryResult, a: Analysis, o: BuildOpts): EChartsOption {
  const { rows } = result;
  const axis = o.dark ? "#9ca3af" : "#6b7280";
  const split = o.dark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.07)";
  const multi = o.measure === ALL_MEASURES && a.measures.length > 1;
  const measure = (!o.measure || o.measure === ALL_MEASURES) ? a.measures[0] : o.measure;
  const base = {
    color: PALETTE,
    textStyle: { fontFamily: "inherit" },
    grid: { left: 8, right: 18, top: 30, bottom: 8, containLabel: true },
  } as const;

  // -- KOMBO (çok ölçü, "tümü"): miktarlar yan yana SÜTUN; ölçek olarak ezilen
  //    ölçüler (oranlar: %2 vs 100.000 kg) SAĞ EKSENDE ÇİZGİ — klasik BI kombosu.
  //    Yalnız tek kategorik eksen (ya da zaman ekseni, seri boyutu yokken) desteklenir;
  //    boyut-serili görünümlerde ölçü teke düşer (iki seri kaynağı aynı anda olmaz).
  const comboX = a.timeCol ?? a.primaryDim;
  const comboSeriesDim = comboX ? a.dims.find((d) => d !== comboX) ?? null : null;
  if (multi && (o.kind === "bar" || o.kind === "line") && comboX && !comboSeriesDim) {
    const xs = orderCats(distinct(rows, comboX).map(fmtCat));
    const maxOf = (m: string) =>
      Math.max(0, ...rows.map((r) => num(r[m])).filter((v) => !Number.isNaN(v)));
    const gmax = Math.max(...a.measures.map(maxOf));
    // Eksen ayrımı BİRİME göre: kg ölçüleri birlikte SOL (sütun), farklı birimdekiler
    // (%) SAĞ (çizgi). fire_kg ~1000 vs agirlik ~50k aynı birimdir — ölçek sezgisi
    // onları yanlış ayırıyordu (ekran görüntüsü 2026-07-21). Birimler ayrışmazsa
    // ölçek sezgisine düşülür.
    const dominant = [...a.measures].sort((x, y) => maxOf(y) - maxOf(x))[0];
    let primary: string[];
    let secondary: string[];
    // YoY: "_degisim_yuzde" bir TÜREVdir (%'nin/ölçünün değişim yüzdesi) — ASLA sütun değil,
    // İKİNCİL eksende çizgi. Baz ölçü + "_gecen" (geçen yıl) birincil sütun (gecen soluk). Bu,
    // birim sezgisinden ÖNCE gelir: oee gibi % ölçülerde birim-ayrımı yanlış bölerdi.
    const changeMs = a.measures.filter((m) => m.endsWith("_degisim_yuzde"));
    if (changeMs.length) {
      secondary = changeMs;
      primary = a.measures.filter((m) => !changeMs.includes(m));
    } else {
      // Genel kombo: eksen ayrımı BİRİME göre (kg birlikte SOL sütun, farklı birim SAĞ çizgi);
      // birimler ayrışmazsa ölçek sezgisine düşülür (küçük ölçüler ikincil).
      primary = a.measures.filter((m) => unitSuffix(m) === unitSuffix(dominant));
      secondary = a.measures.filter((m) => !primary.includes(m));
      if (secondary.length === 0 && primary.length > 1) {
        secondary = a.measures.filter((m) => maxOf(m) < gmax / 50);
        primary = a.measures.filter((m) => !secondary.includes(m));
      }
    }
    const val = (m: string, x: string) => {
      const r = rows.find((rr) => fmtCat(rr[comboX]) === x);
      return r ? num(r[m]) : null;
    };
    return {
      ...base,
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        // her seri KENDİ birimiyle biçimlenir (819.4000000000001 ham değeri değil)
        formatter: (ps: unknown) => {
          const arr = ps as { marker: string; seriesName: string; value: number | null }[];
          const head = arr.length ? `${(arr[0] as unknown as { name: string }).name}<br/>` : "";
          return head + arr
            .map((p) => `${p.marker}${p.seriesName}: <b>${fmtValue(p.value, p.seriesName)}</b>`)
            .join("<br/>");
        },
      },
      legend: { type: "scroll", top: 0, textStyle: { color: axis } },
      grid: { left: 8, right: secondary.length ? 8 : 18, top: 30, bottom: 8, containLabel: true },
      xAxis: {
        type: "category",
        data: xs.map((x) => axisLabel(x, comboX)),
        axisLabel: { color: axis, ...axisLabelSpacing(xs.length) },
        axisLine: { lineStyle: { color: split } },
      },
      yAxis: [
        {
          type: "value",
          axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, primary[0] ?? measure) },
          splitLine: { lineStyle: { color: split } },
        },
        ...(secondary.length
          ? [{
              type: "value" as const,
              axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, secondary[0]) },
              splitLine: { show: false },
            }]
          : []),
      ],
      series: [
        ...primary.map((m) => {
          // YoY: "_gecen" (geçen yıl) SOLUK aynı-tip — sütun grafikte SOLUK SÜTUN, çizgide
          // soluk kesikli çizgi (kullanıcı: aynı birim=sütun, geçen yıl soluk sütun). Farklı
          // birim (%_degisim_yuzde) zaten secondary'de (aşağıda) — çizgi + ikincil eksen.
          const ghost = m.endsWith("_gecen");
          const bar = o.kind === "bar";
          return {
            name: m,
            type: (bar ? "bar" : "line") as "line" | "bar",
            data: xs.map((x) => val(m, x)),
            ...(bar
              ? { itemStyle: { borderRadius: [3, 3, 0, 0] as [number, number, number, number], opacity: ghost ? 0.4 : 1 }, barMaxWidth: 34, barGap: "10%" }
              : { smooth: true, showSymbol: false,
                  ...(ghost ? { lineStyle: { type: "dashed" as const, opacity: 0.5 }, itemStyle: { opacity: 0.5 } } : {}) }),
          };
        }),
        ...secondary.map((m) => ({
          name: m,
          type: "line" as const,
          yAxisIndex: 1,
          smooth: true,
          ...(m.endsWith("_degisim_yuzde")
            ? { lineStyle: { type: "dotted" as const, opacity: 0.7 }, showSymbol: false }
            : {}),
          data: xs.map((x) => val(m, x)),
        })),
      ],
    };
  }

  // -- SCATTER (korelasyon, ADR-0024): 2 ölçü x/y; kategori=renk, 3. ölçü=nokta boyutu ---
  if (o.kind === "scatter" && a.scatter) {
    const { x, y, size } = a.scatter;
    const sizes = size ? rows.map((r) => num(r[size])).filter((v) => !Number.isNaN(v)) : [];
    const smax = sizes.length ? Math.max(...sizes) : 1;
    return {
      ...base,
      tooltip: {
        trigger: "item",
        formatter: (p: unknown) => {
          const r = (p as { data: { r: Row } }).data.r;
          const nm = a.scatter!.color ? String(r[a.scatter!.color!] ?? "") : "";
          return (nm ? `${nm}<br/>` : "")
            + `${x}: <b>${fmtValue(r[x], x)}</b><br/>${y}: <b>${fmtValue(r[y], y)}</b>`
            + (size ? `<br/>${size}: <b>${fmtValue(r[size], size)}</b>` : "");
        },
      },
      xAxis: { type: "value", name: unitSuffix(x), nameTextStyle: { color: axis },
        axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, x) },
        splitLine: { lineStyle: { color: split } } },
      yAxis: { type: "value", name: unitSuffix(y), nameTextStyle: { color: axis },
        axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, y) },
        splitLine: { lineStyle: { color: split } } },
      series: [{
        type: "scatter",
        symbolSize: ((_v: unknown, p: unknown) => {
          if (!size) return 13;
          const s = num((p as { data: { r: Row } }).data.r[size]);
          return 8 + (Number.isNaN(s) ? 0 : (s / (smax || 1)) * 28);
        }) as unknown as number,
        data: rows.map((r) => ({ value: [num(r[x]), num(r[y])], r })),
        itemStyle: { color: PALETTE[0], opacity: 0.8 },
      }],
    };
  }

  // -- FACET-BY-MEASURE (çok-birim small multiples): her ÖLÇÜ kendi paneli + kendi birimi/y --
  //    ADR-0024 §3: ≥3 farklı birim tek eksene binmez; ortak x-ekseninde ölçü başına panel.
  if (o.kind === "facet_measure" && a.facetMeasure) {
    const { measures: ms, x: xDim, series: seriesDim } = a.facetMeasure;
    const isTime = a.timeCol === xDim;
    const xs = orderCats(distinct(rows, xDim).map(fmtCat));
    // Madde 10 (1 Ağustos 2026): kırılım boyutu (series) VARSA her panelde TEK seri yerine
    // seri-değeri başına AYRI bar/line üretilir (ör. "ay VE makine bazında oee ve duruş
    // dakikası" — önceden series HİÇ okunmuyordu, valOf ilk eşleşen satırı alıp diğer
    // makineleri SESSİZCE kaybediyordu). series YOKKEN davranış BİREBİR korunur.
    const seriesVals = seriesDim ? orderCats(distinct(rows, seriesDim).map(String)) : null;
    const N = ms.length;
    const cols = N > 3 ? Math.ceil(N / 2) : N;
    const twoRows = N > cols;
    const w = 100 / cols;
    const colOf = (i: number) => i % cols;
    const rowOf = (i: number) => Math.floor(i / cols);
    const valOf = (m: string, x: string, sv?: string) => {
      const r = rows.find((rr) =>
        fmtCat(rr[xDim]) === x && (sv === undefined || String(rr[seriesDim!]) === sv));
      return r ? num(r[m]) : null;
    };
    // Legend eklenince (yalnız seriesVals varken) panel başlığı/grid'i biraz aşağı kayar.
    const topPad = seriesVals ? 1 : 0;
    return {
      ...base,
      tooltip: { trigger: "axis", axisPointer: { type: isTime ? "line" : "shadow" } },
      ...(seriesVals ? { legend: { type: "scroll" as const, top: 0, textStyle: { color: axis } } } : {}),
      title: ms.map((m, i) => ({
        text: `${m}${unitSuffix(m) ? ` (${unitSuffix(m)})` : ""}`,
        left: `${colOf(i) * w + w / 2}%`,
        textAlign: "center" as const,
        top: twoRows ? (rowOf(i) === 0 ? `${6 + topPad * 5}%` : "53%") : 18 + topPad * 18,
        textStyle: { fontSize: 11, color: axis, fontWeight: "normal" as const },
      })),
      grid: ms.map((_, i) => ({
        left: `${colOf(i) * w + 6}%`,
        width: `${w - 10}%`,
        ...(twoRows
          ? { top: rowOf(i) === 0 ? `${13 + topPad * 5}%` : "60%", height: "30%" }
          : { top: 44 + topPad * 18, bottom: 28 }),
      })),
      xAxis: ms.map((_, i) => ({
        type: "category" as const,
        gridIndex: i,
        data: xs.map((x) => axisLabel(x, xDim)),
        axisLabel: { color: axis, ...axisLabelSpacing(xs.length) },
        axisLine: { lineStyle: { color: split } },
      })),
      yAxis: ms.map((m, i) => ({
        type: "value" as const,
        gridIndex: i,
        axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, m) },
        splitLine: { lineStyle: { color: split } },
      })),
      series: seriesVals
        ? ms.flatMap((m, i) => seriesVals.map((sv, si) => ({
            name: sv,
            type: (isTime ? "line" : "bar") as "line" | "bar",
            xAxisIndex: i,
            yAxisIndex: i,
            data: xs.map((x) => valOf(m, x, sv)),
            ...(isTime
              ? { smooth: true, showSymbol: false, lineStyle: { color: PALETTE[si % PALETTE.length] }, itemStyle: { color: PALETTE[si % PALETTE.length] } }
              : { itemStyle: { color: PALETTE[si % PALETTE.length], borderRadius: [3, 3, 0, 0] as [number, number, number, number] }, barMaxWidth: 34 }),
          })))
        : ms.map((m, i) => ({
            name: m,
            type: (isTime ? "line" : "bar") as "line" | "bar",
            xAxisIndex: i,
            yAxisIndex: i,
            data: xs.map((x) => valOf(m, x)),
            ...(isTime
              ? { smooth: true, showSymbol: false, areaStyle: { opacity: 0.1 }, lineStyle: { color: PALETTE[i % PALETTE.length] }, itemStyle: { color: PALETTE[i % PALETTE.length] } }
              : { itemStyle: { color: PALETTE[i % PALETTE.length], borderRadius: [3, 3, 0, 0] as [number, number, number, number] }, barMaxWidth: 34 }),
          })),
    };
  }

  // -- TREEMAP (çok-kategorili pay): pie'ın okunmadığı >6 kategoride pay grafiği ----------
  if (o.kind === "treemap" && a.primaryDim) {
    const dim = a.primaryDim;
    return {
      ...base,
      tooltip: {
        trigger: "item",
        formatter: (p: unknown) => {
          const d = p as { name: string; value: number };
          return `${d.name}<br/><b>${fmtValue(d.value, measure)}</b>`;
        },
      },
      series: [{
        type: "treemap",
        roam: false,
        breadcrumb: { show: false },
        label: { show: true, formatter: (p: unknown) => (p as { name: string }).name, color: "#fff" },
        data: rows.map((r, i) => ({
          name: fmtCat(r[dim]),
          value: num(r[measure]),
          itemStyle: { color: PALETTE[i % PALETTE.length] },
        })),
      }],
    };
  }

  // -- HEATMAP: satır × sütun matrisi + kenar ortalamaları (marj) ---------
  // Açık istek otomatik min-eksen kuralını ezer: a.heat yoksa a.heatAny kullanılır.
  if (o.kind === "heatmap" && (a.heat || a.heatAny)) {
    const { row, col } = (a.heat ?? a.heatAny)!;
    const rowKeys = orderCats(distinct(rows, row).map(String));
    // Sütun sırası: haftanın günü ise kanonik (Pzt→Paz), değilse alfabetik/kronolojik.
    const colKeys = orderCats(distinct(rows, col).map(fmtCat));
    const val = new Map<string, number>();
    rows.forEach((r) => {
      const ri = rowKeys.indexOf(String(r[row]));
      const ci = colKeys.indexOf(fmtCat(r[col]));
      if (ri >= 0 && ci >= 0) val.set(`${ri}|${ci}`, num(r[measure]));
    });

    const rowLabels = [...rowKeys.map((k) => axisLabel(k, row)), AVG];
    const colLabels = [...colKeys.map((k) => axisLabel(k, col)), AVG];
    const R = rowKeys.length;
    const C = colKeys.length;
    const marginStyle = { borderColor: axis, borderWidth: 1, borderType: "dashed" as const };
    type Cell = { value: [number, number, number]; itemStyle?: object };
    const data: Cell[] = [];

    for (let ri = 0; ri < R; ri++)
      for (let ci = 0; ci < C; ci++) {
        const v = val.get(`${ri}|${ci}`);
        if (v != null) data.push({ value: [ci, ri, v] });
      }
    // satır ortalamaları (sağ kenar sütunu)
    for (let ri = 0; ri < R; ri++) {
      const m = mean([...Array(C).keys()].map((ci) => val.get(`${ri}|${ci}`)).filter((x): x is number => x != null));
      if (m != null) data.push({ value: [C, ri, m], itemStyle: marginStyle });
    }
    // sütun ortalamaları (alt kenar satırı)
    for (let ci = 0; ci < C; ci++) {
      const m = mean([...Array(R).keys()].map((ri) => val.get(`${ri}|${ci}`)).filter((x): x is number => x != null));
      if (m != null) data.push({ value: [ci, R, m], itemStyle: marginStyle });
    }
    // genel ortalama (köşe)
    const all = [...val.values()];
    const grand = mean(all);
    if (grand != null) data.push({ value: [C, R, grand], itemStyle: { ...marginStyle, borderWidth: 1.5 } });

    const vals = data.map((d) => d.value[2]);
    return {
      ...base,
      title: {
        text: `Ortalama ${fmtValue(grand, measure)}`,
        subtext: `en düşük ${fmtValue(Math.min(...all), measure)} · en yüksek ${fmtValue(Math.max(...all), measure)}`,
        left: 8,
        top: 4,
        textStyle: { fontSize: 13, color: o.dark ? "#e5e7eb" : "#374151" },
        subtextStyle: { fontSize: 11, color: axis },
      },
      tooltip: {
        position: "top",
        formatter: (p: unknown) => {
          const d = (p as { data: Cell }).data.value;
          const rl = d[1] === R ? "Ortalama" : rowLabels[d[1]];
          const cl = d[0] === C ? "Ortalama" : colLabels[d[0]];
          return `${rl} · ${cl}<br/><b>${fmtValue(d[2], measure)}</b>`;
        },
      },
      grid: { left: 8, right: 18, top: 54, bottom: 64, containLabel: true },
      xAxis: {
        type: "category",
        data: colLabels,
        splitArea: { show: true },
        // kategorik eksende etiket ATLANMAZ (kumaş adları gibi her değer anlamlı) →
        // `allowSkip=false`: yalnız döndürme/küçültme, `interval` hep `0` kalır.
        axisLabel: { color: axis, ...axisLabelSpacing(colLabels.length, false) },
      },
      yAxis: { type: "category", data: rowLabels, splitArea: { show: true }, axisLabel: { color: axis, interval: 0 } },
      visualMap: {
        min: Math.min(...vals),
        max: Math.max(...vals),
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: 4,
        inRange: { color: heatPalette(measure, o.lowerSet) },
        textStyle: { color: axis },
        formatter: (v: number | string | Date | null | undefined) => fmtValue(v, measure),
      },
      series: [
        {
          type: "heatmap",
          data,
          label: {
            show: true,
            formatter: (p: unknown) => {
              const d = (p as { data: Cell }).data.value;
              return fmtValue(d[2], measure);
            },
          },
          emphasis: { itemStyle: { shadowBlur: 8, shadowColor: "rgba(0,0,0,0.3)" } },
        },
      ],
    };
  }

  // -- FACET (small multiples): 3 kırılım → panel başına gruplu sütun ------
  if (o.kind === "facet" && a.facet) {
    const { dim: fDim, x: xDim, series: sDim } = a.facet;
    const panels = orderCats(distinct(rows, fDim).map(String));
    const xs = orderCats(distinct(rows, xDim).map(fmtCat));
    // seri sırası KANONİK + zaman değerleri BİÇİMLİ (ham ISO lejantı olmasın)
    const groups = orderCats(distinct(rows, sDim).map(fmtCat));
    const N = panels.length;
    // 4'ten çok panel İKİ SATIRA sarılır ("her kumaş türü için ayrı grafik" — 7 panel
    // tek satırda okunmazdı). Satır içi konum: i % cols, satır: floor(i / cols).
    const cols = N > 4 ? Math.ceil(N / 2) : N;
    const twoRows = N > cols;
    const w = 100 / cols;
    const colOf = (i: number) => i % cols;
    const rowOf = (i: number) => Math.floor(i / cols);
    // ORTAK y-skala — paneller karşılaştırılabilir olsun (best practice).
    const allVals = rows.map((r) => num(r[measure])).filter((v) => !Number.isNaN(v));
    const yMax = allVals.length ? Math.max(...allVals) * 1.08 : undefined;

    return {
      ...base,
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => fmtValue(v, measure) },
      legend: { type: "scroll", top: 0, textStyle: { color: axis } },
      title: panels.map((p, i) => ({
        text: p,
        left: `${colOf(i) * w + w / 2}%`,
        textAlign: "center" as const,
        top: twoRows ? (rowOf(i) === 0 ? "7%" : "54%") : 22,
        textStyle: { fontSize: 11, color: axis, fontWeight: "normal" as const },
      })),
      grid: panels.map((_, i) => ({
        left: `${colOf(i) * w + 5}%`,
        width: `${w - 8}%`,
        ...(twoRows
          ? { top: rowOf(i) === 0 ? "12%" : "59%", height: "30%" }
          : { top: 46, bottom: 28 }),
      })),
      xAxis: panels.map((_, i) => ({
        type: "category" as const,
        gridIndex: i,
        data: xs.map((x) => axisLabel(x, xDim)),
        axisLabel: { color: axis, ...axisLabelSpacing(xs.length) },
        axisLine: { lineStyle: { color: split } },
      })),
      yAxis: panels.map((_, i) => ({
        type: "value" as const,
        gridIndex: i,
        max: yMax,
        axisLabel: colOf(i) === 0 ? { color: axis, formatter: (v: number) => fmtAxis(v, measure) } : { show: false },
        splitLine: { lineStyle: { color: split } },
        name: i === 0 ? unitSuffix(measure) : undefined,  // birim adı yalnız ilk panelde
        nameTextStyle: { color: axis },
      })),
      series: panels.flatMap((p, i) =>
        groups.map((g) => ({
          name: axisLabel(g, sDim), // aynı ad → lejant panolar arası paylaşılır; ay → "Oca 2026"
          type: "bar" as const,
          xAxisIndex: i,
          yAxisIndex: i,
          data: xs.map((x) => {
            const r = rows.find(
              (rr) => String(rr[fDim]) === p && fmtCat(rr[xDim]) === x && fmtCat(rr[sDim]) === g,
            );
            return r ? num(r[measure]) : null;
          }),
          itemStyle: { borderRadius: [2, 2, 0, 0] as [number, number, number, number] },
          barMaxWidth: 18,
        })),
      ),
    };
  }

  // -- PIE ---------------------------------------------------------------
  if (o.kind === "pie" && a.primaryDim) {
    const dim = a.primaryDim;
    return {
      ...base,
      tooltip: {
        trigger: "item",
        formatter: (p: unknown) => {
          const d = p as { name: string; value: number; percent: number };
          return `${d.name}<br/><b>${fmtValue(d.value, measure)}</b> (%${d.percent})`;
        },
      },
      legend: { type: "scroll", bottom: 0, textStyle: { color: axis } },
      series: [
        {
          type: "pie",
          radius: ["42%", "70%"],
          itemStyle: { borderRadius: 6, borderColor: o.dark ? "#0a0a0a" : "#fff", borderWidth: 2 },
          data: rows.map((r) => ({ name: fmtCat(r[dim]), value: num(r[measure]) })),
          label: { color: axis, formatter: (p: unknown) => (p as { name: string }).name },
        },
      ],
    };
  }

  // -- LINE (zaman, ops. çoklu seri) -------------------------------------
  if (o.kind === "line") {
    const xCol = a.timeCol ?? a.primaryDim!;
    const seriesDim = a.dims.find((d) => d !== xCol) ?? null;
    const xs = orderCats(distinct(rows, xCol).map(fmtCat));
    const series = seriesDim
      ? orderCats(distinct(rows, seriesDim).map(String)).map((g) => ({
          name: g,
          type: "line" as const,
          smooth: true,
          showSymbol: false,
          data: xs.map((x) => {
            const r = rows.find((rr) => fmtCat(rr[xCol]) === x && String(rr[seriesDim]) === g);
            return r ? num(r[measure]) : null;
          }),
        }))
      : [
          {
            name: measure,
            type: "line" as const,
            smooth: true,
            areaStyle: { opacity: 0.12 },
            data: xs.map((x) => {
              const r = rows.find((rr) => fmtCat(rr[xCol]) === x);
              return r ? num(r[measure]) : null;
            }),
          },
        ];
    return {
      ...base,
      tooltip: { trigger: "axis", valueFormatter: (v: unknown) => fmtValue(v, measure) },
      legend: seriesDim ? { type: "scroll", top: 0, textStyle: { color: axis } } : undefined,
      xAxis: { type: "category", data: xs.map((x) => axisLabel(x, xCol)), axisLabel: { color: axis }, axisLine: { lineStyle: { color: split } } },
      yAxis: {
        type: "value",
        name: unitSuffix(measure),
        nameTextStyle: { color: axis },
        axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, measure) },
        splitLine: { lineStyle: { color: split } },
      },
      series,
    };
  }

  // -- BAR — İKİNCİ boyut varsa GRUPLU sütun (ay × müşteri, hafta günü × cinsiyet):
  //    her grup ayrı renk + lejant; 14 tek-renk sütun yerine 7 gün × 2 seri.
  const barX = a.timeCol ?? (a.dims.length >= 2 ? a.primaryDim : null);
  const barSeries = barX ? a.dims.find((d) => d !== barX) ?? null : null;
  if (barX && barSeries) {
    const xs = orderCats(distinct(rows, barX).map(fmtCat));
    const groups = orderCats(distinct(rows, barSeries).map(String));  // kanonik seri sırası
    // YIĞILI (ADR-0024): additive ölçüde kompozisyon → tüm seriler aynı `stack` grubunda.
    const stacked = o.kind === "stacked";
    return {
      ...base,
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => fmtValue(v, measure) },
      legend: { type: "scroll", top: 0, textStyle: { color: axis } },
      xAxis: { type: "category", data: xs.map((x) => axisLabel(x, barX)), axisLabel: { color: axis, ...axisLabelSpacing(xs.length) }, axisLine: { lineStyle: { color: split } } },
      yAxis: {
        type: "value",
        name: unitSuffix(measure),
        nameTextStyle: { color: axis },
        axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, measure) },
        splitLine: { lineStyle: { color: split } },
      },
      series: groups.map((g, gi) => ({
        name: g,
        type: "bar" as const,
        ...(stacked ? { stack: "total" as const } : {}),
        data: xs.map((x) => {
          const r = rows.find((rr) => fmtCat(rr[barX]) === x && String(rr[barSeries]) === g);
          return r ? num(r[measure]) : null;
        }),
        // Yığılıda köşe yuvarlatma yalnız EN ÜST dilimde anlamlı → düz; gruplu bar yuvarlak.
        itemStyle: stacked
          ? { borderRadius: gi === groups.length - 1 ? [3, 3, 0, 0] as [number, number, number, number] : 0 }
          : { borderRadius: [3, 3, 0, 0] as [number, number, number, number] },
        barMaxWidth: stacked ? 46 : 40,
      })),
    };
  }

  // -- BAR (tek boyut → tek seri) ----------------------------------------
  // Kategoriler hafta günüyse KANONİK sıra (Pzt→Paz); değilse SQL sırası korunur
  // ("en düşükleri göster" gibi kasıtlı sıralamalar bozulmasın).
  const dim = a.primaryDim!;
  const rawCats = rows.map((r) => fmtCat(r[dim]));
  const isWeekdays = rawCats.length > 0 && rawCats.every((c) => WEEKDAY_ORDER.includes(c));
  const cats = isWeekdays ? orderCats(rawCats) : rawCats;
  const valByCat = new Map(rows.map((r) => [fmtCat(r[dim]), num(r[measure])]));
  // §E: referans çizgisi yalnız GÖSTERİLEN ölçü İÇİN doluysa uygulanır (kullanıcı ölçü
  // seçiciden farklı bir ölçüye geçmiş olabilir — backend'in hesapladığı ortalama o zaman
  // ALAKASIZ olur, sessizce atlanır).
  const ref = a.referenceLine?.measure === measure ? a.referenceLine : null;
  return {
    ...base,
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: unknown) => fmtValue(v, measure) },
    xAxis: {
      type: "category",
      data: cats,
      axisLabel: { color: axis, ...axisLabelSpacing(cats.length) },
      axisLine: { lineStyle: { color: split } },
    },
    yAxis: {
      type: "value",
      name: unitSuffix(measure),
      nameTextStyle: { color: axis },
      axisLabel: { color: axis, formatter: (v: number) => fmtAxis(v, measure) },
      splitLine: { lineStyle: { color: split } },
    },
    series: [
      {
        type: "bar",
        name: measure,
        data: cats.map((c) => valByCat.get(c) ?? null),
        itemStyle: { borderRadius: [5, 5, 0, 0], color: PALETTE[0] },
        barMaxWidth: 46,
        ...(ref
          ? {
              markLine: {
                symbol: "none" as const,
                silent: true,
                lineStyle: { color: axis, type: "dashed" as const },
                label: {
                  color: axis,
                  // 🔴 FAZ 2.5 — ETİKET `kind`'a BAĞLI. Bir hedef çizgisini "Ort."
                  // diye etiketlemek (ya da tersi) kullanıcıya YANLIŞ bir kıyas
                  // yaptırırdı: kendi ortalamasının üstünde olmakla hedefinin üstünde
                  // olmak aynı şey değildir. Karar backend'de (`app/hedef.py`).
                  formatter: () =>
                    `${ref.kind === "target" ? "Hedef" : "Ort."} ${fmtValue(ref.value, measure)}`,
                },
                data: [{ yAxis: ref.value }],
              },
            }
          : {}),
      },
    ],
  };
}

// KPI kartları (tek satırlık sonuç) — birim-farkında.
export function kpiCards(result: QueryResult, a: Analysis): { label: string; value: string; ctx?: string }[] {
  const row = result.rows[0] ?? {};
  const ctx = a.dims.length ? String(row[a.dims[0]] ?? "") : undefined;
  return a.measures.map((m) => ({ label: m, value: fmtValue(row[m], m), ctx }));
}
