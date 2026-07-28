"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { AskResponse, QueryResult } from "@dima/contracts";
import { analyze, unitSuffix } from "@dima/domain";

/**
 * SONUÇ KATALOĞU — generative pano tasarımının kalbi.
 *
 * Model bir pano "üretirken" sayı YAZMAZ. Yalnız hangi sonucu nerede
 * göstereceğini seçer ve sonuca `resultId` ile atıf yapar. Renderer o kimlikten
 * gerçek `AskResponse`'u bulur ve satırları kendisi basar.
 *
 * Neden bu kadar önemli:
 *
 * 1. DOĞRULUK — dima deterministik-önce bir BI ürünü. Modelin uydurduğu bir
 *    rakam hatadan öte, sorumluluk doğurur. Bu tasarımda model satırları ne
 *    görür ne yazar; uydurabileceği bir yer yok.
 *
 * 2. MAHREMİYET — modele giden katalog yalnız ŞEKİL taşır: kaç boyut, kaç
 *    ölçü, kaç satır, hangi birim. Müşteri adları, ciro rakamları, stok
 *    seviyeleri sağlayıcıya HİÇ gitmez. Kurumsal on-prem müşteri "veri binamdan
 *    çıkmayacak" dediğinde uyum sonradan eklenen bir önlem değil, mimarinin
 *    kendisi oluyor.
 *
 * 3. DENETLENEBİLİRLİK — her karo hâlâ kendi `source`, `sql`, `cube_query` ve
 *    `contract_id` bilgisini taşır. Panoyu üreten model kanıt zincirini kıramaz.
 *
 * DİKKAT: `ColumnMeta.values` (düşük kardinaliteli kolonların olası değerleri)
 * kataloğa ASLA girmez — orada müşteri/tedarikçi adları bulunur.
 */

export interface CatalogEntry {
  /** Modelin atıf yapacağı kısa kimlik: "q1", "q2"… */
  id: string;
  response: AskResponse;
}

const CatalogContext = createContext<Map<string, AskResponse>>(new Map());

export function CatalogProvider({
  entries,
  children,
}: {
  entries: CatalogEntry[];
  children: ReactNode;
}) {
  const map = new Map(entries.map((e) => [e.id, e.response]));
  return <CatalogContext.Provider value={map}>{children}</CatalogContext.Provider>;
}

export function useResult(resultId: string): AskResponse | null {
  return useContext(CatalogContext).get(resultId) ?? null;
}

/**
 * Modele gönderilen katalog metni — YALNIZ ŞEKİL.
 *
 * Örnek çıktı:
 *   q1 · "2025 Q2 aylık ciro" · boyut: ay(3) · ölçü: toplam_ciro(₺) · 3 satır · önerilen: bar
 *
 * Satır değeri, kategori değeri veya örnek veri yok — bilerek.
 */
export function catalogSummary(entries: CatalogEntry[]): string {
  return entries.map((e) => describeEntry(e.id, e.response)).join("\n");
}

function describeEntry(id: string, r: AskResponse): string {
  const parts: string[] = [`${id} · "${r.question}"`];

  if (r.kpi) {
    const unit = r.kpi.unit ? `(${r.kpi.unit})` : "";
    const comp = r.kpi.components.length ? ` · ${r.kpi.components.length} bileşen` : "";
    const series = r.kpi.series?.length ? ` · ${r.kpi.series.length} dönemlik seri` : "";
    parts.push(`KPI: ${r.kpi.label}${unit}${comp}${series}`);
    return parts.join(" · ");
  }

  const result: QueryResult | null = r.result;
  if (!result || !result.rows.length) {
    parts.push("sonuç yok");
    return parts.join(" · ");
  }

  const a = analyze(result);
  if (a.dims.length) {
    // Kardinalite sayı olarak verilir; DEĞERLER verilmez.
    const dims = a.dims
      .map((d) => `${d}(${new Set(result.rows.map((row) => row[d])).size})`)
      .join(", ");
    parts.push(`boyut: ${dims}`);
  }
  if (a.measures.length) {
    const measures = a.measures.map((m) => `${m}${unitSuffix(m)}`).join(", ");
    parts.push(`ölçü: ${measures}`);
  }
  parts.push(`${result.row_count} satır`);
  parts.push(`önerilen: ${a.kind}`);
  if (r.interpretation) parts.push("yorum var");

  return parts.join(" · ");
}
