import type { AskResponse } from "@dima/contracts";
import { analyze, unitSuffix } from "@dima/domain";

/**
 * SONUÇ KATALOĞU — generative pano tasarımının kalbi.
 *
 * Model pano "üretirken" sayı YAZMAZ. Yalnız hangi sonucu nerede göstereceğini
 * seçer ve sonuca `resultId` ile atıf yapar; renderer o kimlikten gerçek
 * `AskResponse`'u bulup satırları kendisi basar.
 *
 * 1. DOĞRULUK — dima deterministik-önce bir BI ürünü. Modelin uydurduğu rakam
 *    hatadan öte, sorumluluk doğurur. Burada uydurabileceği bir yer yok.
 * 2. MAHREMİYET — modele giden katalog yalnız ŞEKİL taşır. Müşteri adları,
 *    ciro rakamları, stok seviyeleri sağlayıcıya HİÇ gitmez. Kurumsal on-prem
 *    müşteri "veri binamdan çıkmayacak" dediğinde uyum, sonradan eklenen bir
 *    önlem değil mimarinin kendisi olur.
 * 3. DENETLENEBİLİRLİK — her karo kendi `source`, `sql`, `cube_query` ve
 *    `contract_id` bilgisini taşımaya devam eder.
 *
 * DİKKAT: `ColumnMeta.values` (düşük kardinaliteli kolonların olası değerleri)
 * kataloğa ASLA girmez — orada müşteri/tedarikçi adları bulunur.
 */

export interface CatalogEntry {
  /** Modelin atıf yapacağı kısa kimlik: "q1", "q2"… */
  id: string;
  response: AskResponse;
}

/** Bir karonun ne tür gösterime uygun olduğu — deterministik düzenleyici kullanır. */
export interface EntryShape {
  id: string;
  title: string;
  /** Tek skaler / KPI kartı → büyük punto */
  isKpi: boolean;
  /** Grafiğe uygun mu (çizilebilir tür + en az bir ölçü) */
  isChartable: boolean;
  /** Deterministik yorum var mı */
  hasInsight: boolean;
  rowCount: number;
}

export function catalogEntries(items: AskResponse[]): CatalogEntry[] {
  // Sohbette en yeni önce tutuluyor; panoda kronolojik okumak daha doğal.
  return [...items]
    .reverse()
    .filter((r) => r.result?.rows.length || r.kpi)
    .map((response, i) => ({ id: `q${i + 1}`, response }));
}

export function shapeOf({ id, response }: CatalogEntry): EntryShape {
  const title = response.question || "Sonuç";
  if (response.kpi) {
    return { id, title, isKpi: true, isChartable: false, hasInsight: false, rowCount: 1 };
  }

  const result = response.result;
  if (!result?.rows.length) {
    return { id, title, isKpi: false, isChartable: false, hasInsight: false, rowCount: 0 };
  }

  const a = analyze(result);
  const drawable = a.kind !== "none" && a.kind !== "heatmap" && a.kind !== "facet";
  return {
    id,
    title,
    // Tek satır + tek ölçü → grafik anlamsız, KPI karosu doğru gösterim.
    isKpi: result.rows.length === 1 && a.dims.length === 0,
    isChartable: drawable && a.measures.length > 0 && result.rows.length > 1,
    hasInsight: Boolean(response.interpretation),
    rowCount: result.row_count,
  };
}

/**
 * Modele gönderilen katalog metni — YALNIZ ŞEKİL.
 *
 *   q1 · "Aylara göre üretim" · boyut: ay(6) · ölçü: uretim_kg(kg) · 6 satır · önerilen: line
 *
 * Satır değeri, kategori değeri veya örnek veri yok — bilerek.
 */
export function catalogSummary(entries: CatalogEntry[]): string {
  return entries.map((e) => describe(e)).join("\n");
}

function describe({ id, response }: CatalogEntry): string {
  const parts: string[] = [`${id} · "${response.question}"`];

  if (response.kpi) {
    const unit = response.kpi.unit ? `(${response.kpi.unit})` : "";
    const comp = response.kpi.components.length
      ? ` · ${response.kpi.components.length} bileşen`
      : "";
    const series = response.kpi.series?.length
      ? ` · ${response.kpi.series.length} dönemlik seri`
      : "";
    parts.push(`KPI: ${response.kpi.label}${unit}${comp}${series}`);
    return parts.join(" · ");
  }

  const result = response.result;
  if (!result?.rows.length) return [...parts, "sonuç yok"].join(" · ");

  const a = analyze(result);
  if (a.dims.length) {
    // Kardinalite SAYI olarak verilir; değerler verilmez.
    const dims = a.dims
      .map((d) => `${d}(${new Set(result.rows.map((row) => row[d])).size})`)
      .join(", ");
    parts.push(`boyut: ${dims}`);
  }
  if (a.measures.length) {
    parts.push(`ölçü: ${a.measures.map((m) => `${m}${unitSuffix(m)}`).join(", ")}`);
  }
  parts.push(`${result.row_count} satır`, `önerilen: ${a.kind}`);
  if (response.interpretation) parts.push("yorum var");

  return parts.join(" · ");
}
