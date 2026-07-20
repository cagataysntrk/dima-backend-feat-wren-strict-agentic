import type { QueryResult } from "@/lib/types";
import { fmtTemporal, fmtValue } from "@/lib/format";

function formatCell(value: unknown, col: string): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return fmtValue(value, col);
  // Zaman kovaları ham timestamp değil okunur biçim: "Oca 2026" / "5 Tem 2026"
  const t = fmtTemporal(value, col);
  if (t) return t;
  return String(value);
}

export function ResultTable({ result }: { result: QueryResult }) {
  if (result.row_count === 0) {
    return <p className="font-mono text-[13px] text-neutral-500">sonuç yok.</p>;
  }
  return (
    <div className="overflow-auto border border-hairline">
      <table className="w-full border-collapse font-mono text-[13px]">
        <thead>
          <tr className="border-b border-hairline">
            {result.columns.map((col) => (
              <th
                key={col}
                className="whitespace-nowrap px-3 py-2 text-left text-[11px] uppercase tracking-wide text-neutral-400"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {result.rows.map((row, i) => (
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
