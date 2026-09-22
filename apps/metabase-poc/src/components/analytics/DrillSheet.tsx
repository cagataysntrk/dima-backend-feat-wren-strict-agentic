"use client";

import { useQuery } from "@tanstack/react-query";
import { gateway, type DrillScope } from "@/lib/gateway";
import { ResultTable } from "@/components/ResultTable";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";

export interface DrillTarget {
  cardId: number;
  title: string;
  column: string;
  value: string;
  scope?: DrillScope;
}

/** Detail rows behind one clicked bar, in a side sheet. */
export function DrillSheet({ target, onClose }: { target: DrillTarget | null; onClose: () => void }) {
  const q = useQuery({
    queryKey: ["drill", target],
    queryFn: () => gateway.drill(target!.cardId, target!.column, target!.value, target!.scope),
    enabled: target != null,
  });
  return (
    <Sheet open={target != null} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="w-full gap-0 sm:max-w-3xl">
        <SheetHeader className="border-b">
          <SheetTitle>{target?.value}</SheetTitle>
          <SheetDescription>
            {target?.title} · {target?.column} = {target?.value}
            {q.data ? ` · ${q.data.row_count.toLocaleString("tr-TR")} satır (en fazla 500)` : ""}
          </SheetDescription>
        </SheetHeader>
        <div className="min-h-0 flex-1 overflow-auto p-4">
          {q.isPending ? (
            <div className="space-y-2">
              {Array.from({ length: 8 }, (_, i) => (
                <Skeleton key={i} className="h-7 w-full" />
              ))}
            </div>
          ) : q.isError ? (
            <p role="alert" className="text-sm text-destructive">
              {q.error.message}
            </p>
          ) : q.data ? (
            <ResultTable result={q.data} />
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  );
}
