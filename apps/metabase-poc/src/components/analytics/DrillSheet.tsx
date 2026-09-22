"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { gateway, type DrillScope } from "@/lib/gateway";
import { cn } from "@dima/ui/utils";
import { ResultView } from "@dima/ui/result/ResultView";
import { ResultTable } from "@dima/ui/result/ResultTable";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@dima/ui/primitives/sheet";
import { Skeleton } from "@dima/ui/primitives/skeleton";

export interface DrillTarget {
  cardId: number;
  title: string;
  /** Category column (category mode); unused for time. */
  column: string;
  value: string;
  scope?: DrillScope;
  /** "time": zoom into the clicked period; default "category": break out / rows. */
  mode?: "category" | "time";
}

const UNIT_TR: Record<string, string> = { day: "günlük", week: "haftalık", month: "aylık", quarter: "çeyreklik", year: "yıllık" };

function periodLabel(value: string) {
  const d = new Date(`${value.slice(0, 10)}T00:00:00Z`);
  return Number.isNaN(d.getTime())
    ? value
    : d.toLocaleDateString("tr-TR", { month: "long", year: "numeric", timeZone: "UTC" });
}

/**
 * Explore sheet for one clicked chart point:
 *   time point  → the period at the next finer granularity (zoom)
 *   category    → "Kırılım" (split by another column) or "Satırlar" (detail rows)
 */
export function DrillSheet({ target, onClose }: { target: DrillTarget | null; onClose: () => void }) {
  const time = target?.mode === "time";
  return (
    <Sheet open={target != null} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="w-full gap-0 sm:max-w-3xl">
        <SheetHeader className="border-b">
          <SheetTitle>{target ? (time ? periodLabel(target.value) : target.value) : ""}</SheetTitle>
          <SheetDescription>{target?.title}</SheetDescription>
        </SheetHeader>
        <div className="min-h-0 flex-1 overflow-auto p-4">
          {target && (time ? <Zoom target={target} /> : <Category key={`${target.cardId}:${target.value}`} target={target} />)}
        </div>
      </SheetContent>
    </Sheet>
  );
}

function Loading() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 6 }, (_, i) => (
        <Skeleton key={i} className="h-7 w-full" />
      ))}
    </div>
  );
}

function Failed({ message }: { message: string }) {
  return (
    <p role="alert" className="text-sm text-destructive">
      {message}
    </p>
  );
}

function Zoom({ target }: { target: DrillTarget }) {
  const q = useQuery({
    queryKey: ["zoom", target],
    queryFn: () => gateway.zoom(target.cardId, target.value, target.scope),
  });
  if (q.isPending) return <Loading />;
  if (q.isError) return <Failed message={q.error.message} />;
  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        {UNIT_TR[q.data.unit] ?? q.data.unit} görünüm · {q.data.result.row_count.toLocaleString("tr-TR")} dönem
      </p>
      <div className="surface p-4">
        <ResultView result={q.data.result} size="wide" />
      </div>
    </div>
  );
}

function Category({ target }: { target: DrillTarget }) {
  const [tab, setTab] = useState<"breakout" | "rows">("breakout");
  const fields = useQuery({ queryKey: ["breakouts", target.cardId], queryFn: () => gateway.breakouts(target.cardId) });
  const [picked, setPicked] = useState<number | null>(null);
  const fieldId = picked ?? fields.data?.[0]?.id ?? null;
  const split = useQuery({
    queryKey: ["breakout", target, fieldId],
    queryFn: () => gateway.breakout(target.cardId, target.value, fieldId!, target.scope),
    enabled: tab === "breakout" && fieldId != null,
  });
  const rows = useQuery({
    queryKey: ["drill", target],
    queryFn: () => gateway.drill(target.cardId, target.column, target.value, target.scope),
    enabled: tab === "rows",
  });
  // Cards that can't be split (no other categorical column) go straight to rows.
  const canSplit = !fields.isError && (fields.isPending || (fields.data?.length ?? 0) > 0);
  const active = canSplit ? tab : "rows";

  return (
    <div className="space-y-4">
      {canSplit && (
        <div role="tablist" aria-label="Keşif" className="inline-flex rounded-lg bg-muted p-0.5">
          {(
            [
              ["breakout", "Kırılım"],
              ["rows", "Satırlar"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={active === id}
              onClick={() => setTab(id)}
              className={cn(
                "rounded-md px-3 py-1 text-sm transition-colors",
                active === id ? "bg-card font-medium text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground",
              )}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {active === "breakout" ? (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-1.5" role="radiogroup" aria-label="Kırılım sütunu">
            {fields.data?.map((f) => (
              <button
                key={f.id}
                type="button"
                role="radio"
                aria-checked={f.id === fieldId}
                onClick={() => setPicked(f.id)}
                className={cn(
                  "h-8 rounded-md border px-2.5 text-sm transition-colors",
                  f.id === fieldId
                    ? "border-brand/30 bg-brand/10 font-medium text-foreground"
                    : "border-dashed text-muted-foreground hover:bg-accent hover:text-foreground",
                )}
              >
                {f.label}
              </button>
            ))}
          </div>
          {fields.isPending || split.isPending ? (
            <Loading />
          ) : split.isError ? (
            <Failed message={split.error.message} />
          ) : split.data ? (
            <div className="surface p-4">
              <ResultView key={`${fieldId}`} result={split.data.result} />
            </div>
          ) : null}
        </div>
      ) : rows.isPending ? (
        <Loading />
      ) : rows.isError ? (
        <Failed message={rows.error.message} />
      ) : rows.data ? (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            {target.column} = {target.value} · {rows.data.row_count.toLocaleString("tr-TR")} satır (en fazla 500)
          </p>
          <ResultTable result={rows.data} />
        </div>
      ) : null}
    </div>
  );
}
