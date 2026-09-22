"use client";

import { fmtTemporal, fmtValue } from "@dima/domain";
import type { QueryResult } from "@dima/contracts";
import { isAdditive } from "../viz";

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
  // Subtotals only when summing is meaningful (not for %, ratios or averages).
  const additive = isAdditive(measure);
  const colTotals = new Map<string, number>();
  for (const r of result.rows) {
    const b = String(r[timeCol]);
    colTotals.set(b, (colTotals.get(b) ?? 0) + (Number(r[measure]) || 0));
  }
  const grand = [...totals.values()].reduce((a, b) => a + b, 0);

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
            {additive && (
              <th className="whitespace-nowrap border-l border-border px-3 py-2 text-right font-medium text-foreground">
                Toplam
              </th>
            )}
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
              {additive && (
                <td className="border-l border-border px-3 py-1.5 text-right font-medium tabular-nums text-foreground">
                  {fmtValue(totals.get(e) ?? 0, measure)}
                </td>
              )}
            </tr>
          ))}
        </tbody>
        {additive && (
          <tfoot>
            <tr className="border-t border-border bg-muted/40 font-medium">
              <td className="sticky left-0 z-10 bg-background px-3 py-2 text-left">Toplam</td>
              {buckets.map((b) => (
                <td key={b} className="px-3 py-2 text-right tabular-nums">
                  {fmtValue(colTotals.get(b) ?? 0, measure)}
                </td>
              ))}
              <td className="border-l border-border px-3 py-2 text-right tabular-nums">{fmtValue(grand, measure)}</td>
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );
}
