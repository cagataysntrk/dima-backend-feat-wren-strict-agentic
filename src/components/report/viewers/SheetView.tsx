"use client";

import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

type Sheet = { name: string; rows: (string | number | null)[][] };

/** Satır tavanı: 50 bin satırlık bir dosyayı DOM'a basmak sekmeyi kilitler. */
const MAX_ROWS = 500;

/** XLSX / XLS / CSV → tablo (SheetJS). Sekmeler arasında geçiş yapılabilir. */
export default function SheetView({ file }: { file: File }) {
  const [sheets, setSheets] = useState<Sheet[] | null>(null);
  const [active, setActive] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [XLSX, buffer] = await Promise.all([import("xlsx"), file.arrayBuffer()]);
        const wb = XLSX.read(buffer, { type: "array" });
        const out: Sheet[] = wb.SheetNames.map((name) => ({
          name,
          rows: XLSX.utils.sheet_to_json<(string | number | null)[]>(wb.Sheets[name], {
            header: 1,
            defval: null,
          }) as (string | number | null)[][],
        }));
        if (alive) setSheets(out);
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "bilinmeyen hata");
      }
    })();
    return () => {
      alive = false;
    };
  }, [file]);

  if (error) {
    return (
      <p className="rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-xs text-destructive">
        Tablo açılamadı: {error}
      </p>
    );
  }
  if (!sheets) return <Skeleton className="h-72 w-full" />;
  if (!sheets.length) return <p className="text-sm text-muted-foreground">Boş dosya.</p>;

  const sheet = sheets[active];
  const rows = sheet.rows.slice(0, MAX_ROWS);
  const truncated = sheet.rows.length > MAX_ROWS;

  return (
    <div className="flex min-h-0 flex-col gap-2">
      {sheets.length > 1 && (
        <div className="flex shrink-0 items-center gap-1 overflow-x-auto">
          {sheets.map((s, i) => (
            <button
              key={s.name}
              type="button"
              onClick={() => setActive(i)}
              className={cn(
                "shrink-0 rounded-md px-2.5 py-1 text-xs transition-colors",
                i === active
                  ? "bg-accent font-medium text-foreground"
                  : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
              )}
            >
              {s.name}
            </button>
          ))}
        </div>
      )}

      <div className="min-h-0 flex-1 overflow-auto rounded-lg border border-border">
        <table className="w-full border-collapse font-mono text-xs">
          <tbody>
            {rows.map((row, r) => (
              <tr key={r} className={r === 0 ? "bg-muted/60 font-medium" : "odd:bg-muted/20"}>
                {row.map((cell, c) => (
                  <td key={c} className="border border-border px-2 py-1 whitespace-nowrap">
                    {cell ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {truncated && (
        <p className="shrink-0 text-xs text-muted-foreground">
          İlk {MAX_ROWS} satır gösteriliyor ({sheet.rows.length} satırdan).
        </p>
      )}
    </div>
  );
}
