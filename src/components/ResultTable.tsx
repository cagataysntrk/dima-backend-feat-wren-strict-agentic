"use client";

import { useMemo, useState } from "react";
import type { QueryResult } from "@/lib/types";
import { fmtTemporal, fmtValue, unitFor } from "@/lib/format";

function formatCell(value: unknown, col: string): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return fmtValue(value, col);
  // DECIMAL/BIGINT sürücüden STRING gelebilir ("40474542.81000000"). Yalnız BİRİMLİ
  // ölçü kolonlarında sayı biçimle (para/kg/vb.) — cari_kodu "6403" gibi ID'ler
  // (birimsiz) ham kalır, yanlışlıkla "6.403" olmaz.
  if (typeof value === "string" && value.trim() !== "" && !Number.isNaN(Number(value)) && unitFor(col)) {
    return fmtValue(Number(value), col);
  }
  const t = fmtTemporal(value, col);
  if (t) return t;
  return String(value);
}

// Sayısal (DECIMAL-string dahil) ya da metinsel sıralama için karşılaştırma anahtarı.
function sortKey(v: unknown): number | string {
  if (v === null || v === undefined) return "";
  if (typeof v === "number") return v;
  if (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v))) return Number(v);
  return String(v).toLocaleLowerCase("tr-TR");
}

export function ResultTable({ result }: { result: QueryResult }) {
  const [sort, setSort] = useState<{ col: string; dir: "asc" | "desc" } | null>(null);

  const rows = useMemo(() => {
    if (!sort) return result.rows;
    const dir = sort.dir === "asc" ? 1 : -1;
    return [...result.rows].sort((a, b) => {
      const ka = sortKey(a[sort.col]);
      const kb = sortKey(b[sort.col]);
      if (ka < kb) return -1 * dir;
      if (ka > kb) return 1 * dir;
      return 0;
    });
  }, [result.rows, sort]);

  if (result.row_count === 0) {
    return <p className="font-mono text-[13px] text-neutral-500">sonuç yok.</p>;
  }

  const toggle = (col: string) =>
    setSort((s) =>
      s?.col === col
        ? s.dir === "desc"
          ? { col, dir: "asc" }
          : null // desc → asc → sırasız (üçüncü tık)
        : { col, dir: "desc" },
    );

  return (
    <div className="overflow-auto border border-hairline">
      <table className="w-full border-collapse font-mono text-[13px]">
        <thead>
          <tr className="border-b border-hairline">
            {result.columns.map((col) => {
              const active = sort?.col === col;
              return (
                <th
                  key={col}
                  onClick={() => toggle(col)}
                  title="Sıralamak için tıkla"
                  className="cursor-pointer select-none whitespace-nowrap px-3 py-2 text-left text-[11px] uppercase tracking-wide text-neutral-400 hover:text-neutral-200"
                >
                  {col}
                  <span className="ml-1 text-neutral-500">
                    {active ? (sort!.dir === "desc" ? "▼" : "▲") : "⇅"}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-hairline/70 odd:bg-neutral-500/[0.03]">
              {result.columns.map((col) => (
                <td key={col} className="whitespace-nowrap px-3 py-2 tabular-nums">
                  {formatCell(row[col], col)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
