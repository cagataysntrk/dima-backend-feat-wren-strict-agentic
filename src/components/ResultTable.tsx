"use client";

import { useMemo, useState } from "react";
import type { QueryResult } from "@/lib/types";
import { ChevronDown, ChevronsUpDown, ChevronUp } from "lucide-react";
import { fmtTemporal, fmtValue } from "@/lib/format";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// KİMLİK/kod kolonları: sayısal olsa da biçimlenMEZ (cari_kodu "6403" → "6.403" olmasın).
function isIdentifierCol(col: string): boolean {
  return /(?:^|_)(kod|kodu|no|ref|id|barkod|tckn|vkn|iban|fis)(?:$|_)/.test(col.toLowerCase());
}

function formatCell(value: unknown, col: string): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return fmtValue(value, col);
  // DECIMAL/BIGINT sürücüden STRING gelebilir ("218123764.00000000"). ID/kod DIŞINDAKİ
  // tüm sayısal ölçüler yerelleştirilir (binlik ayraç; birim tanınıyorsa ₺/kg/% eklenir).
  // Birimsiz ölçüler de (satis_miktari) artık formatlanır — eskiden ham string kalıyordu.
  if (
    typeof value === "string" &&
    value.trim() !== "" &&
    !Number.isNaN(Number(value)) &&
    !isIdentifierCol(col)
  ) {
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

// Sayısal kolonlar sağa yaslanır (BI tablosu okunurluğu). DECIMAL string'ler de sayısaldır.
const isNumericCol = (result: QueryResult, col: string) =>
  !isIdentifierCol(col) &&
  result.rows.some(
    (r) =>
      typeof r[col] === "number" ||
      (typeof r[col] === "string" &&
        (r[col] as string).trim() !== "" &&
        !Number.isNaN(Number(r[col]))),
  );

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
    return <p className="text-sm text-muted-foreground">Sonuç yok.</p>;
  }
  const numeric = new Set(result.columns.filter((c) => isNumericCol(result, c)));

  // desc → asc → sırasız (üçüncü tık)
  const toggle = (col: string) =>
    setSort((cur) =>
      cur?.col === col ? (cur.dir === "desc" ? { col, dir: "asc" } : null) : { col, dir: "desc" },
    );

  return (
    <div className="overflow-auto rounded-lg border border-border">
      <Table className="font-mono text-[13px]">
        <TableHeader>
          <TableRow>
            {result.columns.map((col) => {
              const active = sort?.col === col;
              const Icon = !active ? ChevronsUpDown : sort!.dir === "desc" ? ChevronDown : ChevronUp;
              return (
                <TableHead
                  key={col}
                  onClick={() => toggle(col)}
                  title="Sıralamak için tıkla"
                  aria-sort={active ? (sort!.dir === "desc" ? "descending" : "ascending") : "none"}
                  className={cn(
                    "cursor-pointer text-[11px] tracking-wide uppercase select-none hover:text-foreground",
                    numeric.has(col) && "text-right",
                  )}
                >
                  <span
                    className={cn(
                      "inline-flex items-center gap-1",
                      numeric.has(col) && "flex-row-reverse",
                    )}
                  >
                    {col}
                    <Icon
                      className={cn(
                        "size-3 shrink-0",
                        active ? "text-brand" : "text-muted-foreground/50",
                      )}
                    />
                  </span>
                </TableHead>
              );
            })}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, i) => (
            <TableRow key={i}>
              {result.columns.map((col) => (
                <TableCell
                  key={col}
                  className={
                    numeric.has(col)
                      ? "text-right whitespace-nowrap tabular-nums"
                      : "whitespace-nowrap"
                  }
                >
                  {formatCell(row[col], col)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
