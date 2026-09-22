"use client";

import { useState } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { ArrowDown, ArrowUp, Table2 } from "lucide-react";
import { gateway } from "@/lib/gateway";
import { fmtValue } from "@dima/domain";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

type Sort = { fieldId: number; dir: "asc" | "desc" } | undefined;

/** Browse the company's tables and preview their first rows, sorted by any column. */
export function BrowseData() {
  const tables = useQuery({ queryKey: ["browse"], queryFn: gateway.browseTables });
  const [tableId, setTableId] = useState<number | null>(null);
  const [sort, setSort] = useState<Sort>(undefined);
  const active = tables.data?.find((t) => t.id === tableId) ?? tables.data?.[0];

  const preview = useQuery({
    queryKey: ["preview", active?.id, sort],
    queryFn: () => gateway.previewTable(active!.id, sort),
    enabled: active != null,
    placeholderData: keepPreviousData,
  });

  const toggleSort = (fieldId: number) =>
    setSort((s) => (s?.fieldId === fieldId ? { fieldId, dir: s.dir === "asc" ? "desc" : "asc" } : { fieldId, dir: "asc" }));

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Veriler</h1>
        <p className="text-sm text-muted-foreground">
          Şirketinizin tablolarına göz atın; ilk 100 satırı görün, sütun başlığına tıklayarak sıralayın.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[16rem_1fr]">
        <nav className="surface h-fit max-h-[32rem] overflow-y-auto p-2 lg:sticky lg:top-2" aria-label="Tablolar">
          {tables.isPending && <Skeleton className="h-40 w-full" />}
          {tables.isError && (
            <p role="alert" className="px-2 py-1.5 text-sm text-destructive">
              {tables.error.message}
            </p>
          )}
          <ul className="space-y-0.5">
            {tables.data?.map((t) => (
              <li key={t.id}>
                <button
                  type="button"
                  aria-current={t.id === active?.id ? "true" : undefined}
                  onClick={() => {
                    setTableId(t.id);
                    setSort(undefined);
                  }}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors",
                    t.id === active?.id ? "bg-brand/10 font-medium" : "hover:bg-accent",
                  )}
                >
                  <Table2 className="size-3.5 shrink-0 text-muted-foreground" aria-hidden />
                  <span className="truncate">{t.name}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <section className="surface min-w-0 overflow-hidden" aria-label="Önizleme">
          {active && (
            <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[var(--surface-edge)] px-4 py-3">
              <h2 className="font-medium">{active.name}</h2>
              <p className="text-xs text-muted-foreground tabular-nums">
                {active.fields.length} sütun · ilk {preview.data?.row_count ?? 0} satır
              </p>
            </div>
          )}
          {preview.isPending ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 8 }, (_, i) => (
                <Skeleton key={i} className="h-6 w-full" />
              ))}
            </div>
          ) : preview.isError ? (
            <p role="alert" className="p-4 text-sm text-destructive">
              {preview.error.message}
            </p>
          ) : preview.data && active ? (
            <div className={cn("overflow-auto", preview.isFetching && "opacity-70")}>
              <table className="w-full border-collapse text-sm">
                <thead className="sticky top-0 bg-card">
                  <tr>
                    {preview.data.columns.map((c) => {
                      const field = active.fields.find((f) => f.name === c);
                      const on = field && sort?.fieldId === field.id;
                      return (
                        <th key={c} className="border-b border-[var(--surface-edge)] px-3 py-2 text-left font-medium">
                          <button
                            type="button"
                            disabled={!field}
                            onClick={() => field && toggleSort(field.id)}
                            aria-label={`${c} sütununa göre sırala`}
                            className={cn(
                              "inline-flex items-center gap-1 whitespace-nowrap transition-colors",
                              field ? "hover:text-brand" : "cursor-default",
                              on && "text-brand",
                            )}
                          >
                            {field?.label ?? c}
                            {on &&
                              (sort.dir === "asc" ? (
                                <ArrowUp className="size-3" aria-hidden />
                              ) : (
                                <ArrowDown className="size-3" aria-hidden />
                              ))}
                          </button>
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody>
                  {preview.data.rows.map((row, i) => (
                    <tr key={i} className="hover:bg-accent/40">
                      {preview.data!.columns.map((c) => (
                        <td key={c} className="border-b border-[var(--surface-edge)] px-3 py-1.5 whitespace-nowrap tabular-nums">
                          {row[c] == null ? "—" : fmtValue(row[c], c)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}
