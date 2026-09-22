"use client";

import { useEffect, useState } from "react";
import { Skeleton } from "@dima/ui/primitives/skeleton";
import { cn } from "@dima/ui/utils";

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
  /** Dosyadan okunan hücre stili (yalnız .xlsx — bkz. loadStyled). */
  bold?: boolean;
  fill?: string;
  color?: string;
  align?: "left" | "center" | "right";
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

/** ARGB ("FF1F4E79") → CSS. ExcelJS renkleri bu biçimde verir. */
function argb(v?: string): string | undefined {
  if (!v || v.length < 6) return undefined;
  const hex = v.length === 8 ? v.slice(2) : v;
  return `#${hex}`;
}

/**
 * .xlsx için stilli yol (ExcelJS): dolgu, kalın, yazı rengi ve hizalama okunur.
 * SheetJS'in topluluk sürümü stil VERMİYOR — dosyanın görsel kimliği (başlık
 * bantları, renk rehberi) ancak böyle korunuyor.
 * .xls (eski BIFF) ve .csv ExcelJS'te desteklenmiyor; onlar SheetJS yolunda kalır.
 */
async function loadStyled(file: File): Promise<Grid[]> {
  const ExcelJS = (await import("exceljs")).default;
  const wb = new ExcelJS.Workbook();
  await wb.xlsx.load(await file.arrayBuffer());

  return wb.worksheets.map((ws) => {
    const totalRows = ws.rowCount;
    const rowCount = Math.min(totalRows, MAX_ROWS);
    const cols = Math.min(ws.columnCount, MAX_COLS);

    // Birleştirmeler: kapsanan koordinatları atla, sol-üste span ver.
    const covered = new Set<string>();
    const spanAt = new Map<string, { colSpan: number; rowSpan: number }>();
    const merges: string[] = Object.values(
      (ws as unknown as { _merges?: Record<string, { model?: unknown }> })._merges ?? {},
    )
      .map((m) => (m as { model?: { tl?: string; br?: string } }).model)
      .filter((m): m is { tl: string; br: string } => !!m?.tl && !!m?.br)
      .map((m) => `${m.tl}:${m.br}`);

    for (const range of merges) {
      const [tl, br] = range.split(":");
      const a = ws.getCell(tl);
      const b = ws.getCell(br);
      const r0 = Number(a.row);
      const c0 = Number(a.col);
      const r1 = Number(b.row);
      const c1 = Number(b.col);
      spanAt.set(`${r0}:${c0}`, { colSpan: c1 - c0 + 1, rowSpan: r1 - r0 + 1 });
      for (let r = r0; r <= r1; r++) {
        for (let c = c0; c <= c1; c++) {
          if (r !== r0 || c !== c0) covered.add(`${r}:${c}`);
        }
      }
    }

    const rows: Cell[][] = [];
    for (let r = 1; r <= rowCount; r++) {
      const row: Cell[] = [];
      for (let c = 1; c <= cols; c++) {
        if (covered.has(`${r}:${c}`)) {
          row.push(null);
          continue;
        }
        const cell = ws.getRow(r).getCell(c);
        const font = cell.font;
        const f = cell.fill;
        const fill =
          f && f.type === "pattern" && f.pattern === "solid"
            ? argb((f.fgColor as { argb?: string } | undefined)?.argb)
            : undefined;
        const h = cell.alignment?.horizontal;
        const span = spanAt.get(`${r}:${c}`);
        row.push({
          text: cell.text ?? "",
          numeric: typeof cell.value === "number",
          bold: font?.bold,
          fill,
          color: argb((font?.color as { argb?: string } | undefined)?.argb),
          align: h === "center" ? "center" : h === "right" ? "right" : h === "left" ? "left" : undefined,
          colSpan: span?.colSpan,
          rowSpan: span?.rowSpan,
        });
      }
      rows.push(row);
    }

    const widths = ws.columns?.map((c) => c?.width ?? 0) ?? [];
    return { name: ws.name, rows, cols, widths, truncated: totalRows > MAX_ROWS };
  });
}

export default function SheetView({ file }: { file: File }) {
  const [sheets, setSheets] = useState<Grid[] | null>(null);
  const [active, setActive] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        // .xlsx → ExcelJS (stilli). .xls / .csv → SheetJS (ExcelJS okumuyor).
        if (/\.xlsx$/i.test(file.name)) {
          const styled = await loadStyled(file);
          if (alive) setSheets(styled);
          return;
        }
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
                      style={{
                        backgroundColor: cell.fill,
                        color: cell.color,
                        fontWeight: cell.bold ? 600 : undefined,
                      }}
                      className={cn(
                        "truncate border-r border-b border-border px-2 py-1",
                        cell.align === "center"
                          ? "text-center"
                          : cell.align === "right"
                            ? "text-right"
                            : cell.align === "left"
                              ? "text-left"
                              : cell.numeric
                                ? "text-right tabular-nums"
                                : "text-left",
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
