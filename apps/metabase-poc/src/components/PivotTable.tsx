// POC COPY of apps/web/src/components/PivotTable.tsx — only change: card/tooltip edges use the app surface tokens. Follow-up: extract to packages/ui.
"use client";

import { fmtTemporal, fmtValue } from "@dima/domain";
import type { QueryResult } from "@dima/contracts";

// JENERİK çapraz tablo (pivot): VARLIK satır × ZAMAN-KOVA sütun × ÖLÇÜ hücre. "N ürün × ay ×
// ortalama fiyat" gibi uzun (N×kova satır) sonuçları okunur matrise çevirir. Zaman kovaları
// ham değerle sıralanır (etiket Türkçeye çevrilir); varlıklar ölçü toplamına göre (büyük üstte).
export function PivotTable({
  result,
  timeCol,
  entityDim,
  measure,
}: {
  result: QueryResult;
  timeCol: string;
  entityDim: string;
  measure: string;
}) {
  const buckets = [...new Set(result.rows.map((r) => String(r[timeCol])))].sort();
  const totals = new Map<string, number>();
  const cell = new Map<string, unknown>();
  for (const r of result.rows) {
    const e = String(r[entityDim]);
    totals.set(e, (totals.get(e) ?? 0) + (Number(r[measure]) || 0));
    cell.set(`${e} ${String(r[timeCol])}`, r[measure]);
  }
  const entities = [...totals.keys()].sort((a, b) => (totals.get(b) ?? 0) - (totals.get(a) ?? 0));

  return (
    <div className="surface-inset overflow-auto">
      <table className="w-full border-collapse font-mono text-[12px]">
        <thead>
          <tr className="border-b border-border bg-muted/40">
            <th className="sticky left-0 z-10 bg-background px-3 py-2 text-left font-normal text-muted-foreground">
              {entityDim}
            </th>
            {buckets.map((b) => (
              <th
                key={b}
                className="whitespace-nowrap px-3 py-2 text-right font-normal text-muted-foreground"
              >
                {fmtTemporal(b, timeCol) ?? b}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {entities.map((e) => (
            <tr key={e} className="border-b border-border/60 hover:bg-muted/50">
              <td className="sticky left-0 z-10 whitespace-nowrap bg-background px-3 py-1.5 text-left text-foreground">
                {e}
              </td>
              {buckets.map((b) => {
                const v = cell.get(`${e} ${b}`);
                return (
                  <td
                    key={b}
                    className="px-3 py-1.5 text-right tabular-nums text-foreground/80"
                  >
                    {v == null ? "—" : fmtValue(v, measure)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
