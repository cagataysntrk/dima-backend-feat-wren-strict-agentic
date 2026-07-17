import type { QueryResult } from "@/lib/types";

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return value.toLocaleString("tr-TR");
  return String(value);
}

export function ResultTable({ result }: { result: QueryResult }) {
  if (result.row_count === 0) {
    return <p className="text-sm text-neutral-500">Sonuç yok.</p>;
  }
  return (
    <div className="overflow-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-neutral-50 dark:bg-neutral-900">
            {result.columns.map((col) => (
              <th
                key={col}
                className="px-3 py-2 text-left font-semibold text-neutral-700 dark:text-neutral-300 whitespace-nowrap"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {result.rows.map((row, i) => (
            <tr key={i} className="border-t border-neutral-100 dark:border-neutral-800">
              {result.columns.map((col) => (
                <td key={col} className="px-3 py-2 whitespace-nowrap tabular-nums">
                  {formatCell(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
