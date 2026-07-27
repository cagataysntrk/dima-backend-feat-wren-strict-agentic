"use client";

import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

/**
 * XLSX / XLS / CSV → gerçek hesap tablosu ızgarası.
 *
 * NEDEN HAZIR KÜTÜPHANE DEĞİL: değerlendirilenler — Handsontable (ticari
 * kullanımda ücretli), Syncfusion (~$995/geliştirici/yıl), Univer (Apache-2.0
 * ama tam bir ofis motoru; 14 KB'lık bir eki göstermek için megabaytlar),
 * react-spreadsheet / ReactGrid (MIT, ama xlsx AYRIŞTIRMIYOR — yine SheetJS
 * gerekir, yalnız ızgara iskeletini verirler). Burada iş SALT OKUNUR önizleme:
 * formül, düzenleme, işbirliği yok. O yüzden ayrıştırma SheetJS'te kalıyor,
 * ızgarayı kendi tokenlarımızla çiziyoruz. Düzenlenebilir tablo gerekirse doğru
 * adım Univer'dır.
 *
 * NEDEN `sheet_to_json` DEĞİL: satırları dizi olarak verir ve seyrek/birleşik
 * hücrelerde satır uzunlukları değişir — sonuç, sütun hizası olmayan bir liste
 * olur (önceki hâlin sorunu buydu). Bunun yerine sayfanın KULLANILAN ARALIĞINI
 * (`!ref`) gezip her koordinat için hücre üretiyoruz: her satır aynı sütun
 * sayısına sahip, yani gerçek ızgara.
 *
 * Korunan: sütun harfleri, satır numaraları, birleştirmeler (`!merges`), sütun
 * genişlikleri (`!cols`), sayı/tarih biçimi (hücrenin `w` alanı).
 * Korunmayan: yazı tipi, dolgu, kenarlık — SheetJS'in topluluk sürümü stil
 * bilgisini güvenilir vermiyor; uydurmaktansa nötr bırakıyoruz.
 */

type Cell = {
  text: string;
  numeric: boolean;
  colSpan?: number;
  rowSpan?: number;
} | null;

type Grid = {
  name: string;
  rows: Cell[][];
  cols: number;
  widths: number[];
  truncated: boolean;
};

/** Tavanlar: on binlerce hücreyi DOM'a basmak sekmeyi kilitler. */
const MAX_ROWS = 400;
const MAX_COLS = 40;

/** 0 → A, 25 → Z, 26 → AA */
function colName(i: number): string {
  let s = "";
  let n = i;
  while (n >= 0) {
    s = String.fromCharCode((n % 26) + 65) + s;
    n = Math.floor(n / 26) - 1;
  }
  return s;
}

export default function SheetView({ file }: { file: File }) {
  const [sheets, setSheets] = useState<Grid[] | null>(null);
  const [active, setActive] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const XLSX = await import("xlsx");
        // CSV metin olarak okunmalı — ikili verince kodlama bozulabiliyor.
        const isCsv = /\.csv$/i.test(file.name);
        const wb = isCsv
          ? XLSX.read(await file.text(), { type: "string" })
          : XLSX.read(await file.arrayBuffer(), { type: "array" });

        const out: Grid[] = wb.SheetNames.map((name) => {
          const ws = wb.Sheets[name];
          const ref = ws?.["!ref"];
          if (!ref) return { name, rows: [], cols: 0, widths: [], truncated: false };

          const range = XLSX.utils.decode_range(ref);
          const cols = Math.min(range.e.c - range.s.c + 1, MAX_COLS);
          const totalRows = range.e.r - range.s.r + 1;
          const rowCount = Math.min(totalRows, MAX_ROWS);

          // Birleştirme: sol-üst hücre span taşır, kapsanan koordinatlar atlanır.
          const covered = new Set<string>();
          const spanAt = new Map<string, { colSpan: number; rowSpan: number }>();
          for (const m of ws["!merges"] ?? []) {
            spanAt.set(`${m.s.r}:${m.s.c}`, {
              colSpan: m.e.c - m.s.c + 1,
              rowSpan: m.e.r - m.s.r + 1,
            });
            for (let r = m.s.r; r <= m.e.r; r++) {
              for (let c = m.s.c; c <= m.e.c; c++) {
                if (r !== m.s.r || c !== m.s.c) covered.add(`${r}:${c}`);
              }
            }
          }

          const rows: Cell[][] = [];
          for (let r = range.s.r; r < range.s.r + rowCount; r++) {
            const row: Cell[] = [];
            for (let c = range.s.c; c < range.s.c + cols; c++) {
              if (covered.has(`${r}:${c}`)) {
                row.push(null);
                continue;
              }
              const cell = ws[XLSX.utils.encode_cell({ r, c })];
              const span = spanAt.get(`${r}:${c}`);
              row.push({
                // `w` = biçimlendirilmiş görünen metin (para birimi, tarih…)
                text: cell ? (cell.w ?? String(cell.v ?? "")) : "",
                numeric: cell?.t === "n",
                colSpan: span?.colSpan,
                rowSpan: span?.rowSpan,
              });
            }
            rows.push(row);
          }

          const widths = (ws["!cols"] ?? []).map((c) => c?.wch ?? 0);
          return { name, rows, cols, widths, truncated: totalRows > MAX_ROWS };
        });

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

  return (
    <div className="flex min-h-0 flex-col">
      <div className="min-h-0 flex-1 overflow-auto rounded-t-lg border border-border">
        <table className="border-collapse text-xs" style={{ tableLayout: "fixed" }}>
          <thead>
            <tr>
              {/* köşe hücresi — satır numarası sütununun başlığı */}
              <th className="sticky top-0 left-0 z-20 w-10 border-r border-b border-border bg-muted" />
              {Array.from({ length: sheet.cols }, (_, c) => (
                <th
                  key={c}
                  style={{ width: `${Math.max(80, (sheet.widths[c] || 12) * 7)}px` }}
                  className="sticky top-0 z-10 border-r border-b border-border bg-muted px-2 py-1 text-center font-medium text-muted-foreground"
                >
                  {colName(c)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sheet.rows.map((row, r) => (
              <tr key={r}>
                <th className="sticky left-0 z-10 border-r border-b border-border bg-muted px-1 text-center text-[11px] font-normal text-muted-foreground tabular-nums">
                  {r + 1}
                </th>
                {row.map((cell, c) =>
                  cell === null ? null : (
                    <td
                      key={c}
                      colSpan={cell.colSpan}
                      rowSpan={cell.rowSpan}
                      title={cell.text || undefined}
                      className={cn(
                        "truncate border-r border-b border-border px-2 py-1",
                        cell.numeric ? "text-right tabular-nums" : "text-left",
                      )}
                    >
                      {cell.text}
                    </td>
                  ),
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* sayfa sekmeleri — altta, Excel'deki gibi */}
      <div className="flex shrink-0 items-center gap-0.5 overflow-x-auto rounded-b-lg border-r border-b border-l border-border bg-muted/40 px-1 py-1">
        {sheets.map((s, i) => (
          <button
            key={s.name}
            type="button"
            onClick={() => setActive(i)}
            className={cn(
              "shrink-0 rounded-md px-2.5 py-1 text-xs transition-colors",
              "focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none",
              i === active
                ? "bg-card font-medium text-foreground shadow-xs"
                : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
            )}
          >
            {s.name}
          </button>
        ))}
        {sheet.truncated && (
          <span className="ml-auto shrink-0 px-2 text-[11px] text-muted-foreground">
            ilk {MAX_ROWS} satır
          </span>
        )}
      </div>
    </div>
  );
}
