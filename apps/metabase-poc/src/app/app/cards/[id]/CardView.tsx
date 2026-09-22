"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { gateway } from "@/lib/gateway";
import { ResultView } from "@/components/ResultView";
import { ExportMenu } from "@/components/analytics/ExportMenu";
import { AddToDashboard } from "@/components/analytics/DashboardActions";
import { DrillSheet, type DrillTarget } from "@/components/analytics/DrillSheet";
import { Skeleton } from "@/components/ui/skeleton";

export function CardView({ id, canEdit }: { id: number; canEdit: boolean }) {
  const q = useQuery({ queryKey: ["card", id], queryFn: () => gateway.card(id) });
  const [drill, setDrill] = useState<DrillTarget | null>(null);

  return (
    <div className="space-y-6">
      <Link href="/app" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="size-4" aria-hidden />
        Genel bakış
      </Link>
      {q.isPending ? (
        <div className="space-y-4">
          <Skeleton className="h-8 w-72" />
          <Skeleton className="aspect-[16/7] w-full" />
        </div>
      ) : q.isError ? (
        <p role="alert" className="text-sm text-destructive">
          {q.error.message}
        </p>
      ) : (
        <>
          <header className="flex items-start justify-between gap-4">
            <div className="space-y-1">
              <h1 className="text-2xl font-semibold tracking-tight">{q.data.card.name}</h1>
              {q.data.card.description && (
                <p className="text-sm text-muted-foreground">{q.data.card.description}</p>
              )}
            </div>
            <div className="flex shrink-0 items-center gap-1">
              {canEdit && <AddToDashboard resolveCardId={async () => id} />}
              <ExportMenu cardId={id} />
            </div>
          </header>
          <div className="surface p-5">
            <ResultView
              result={q.data.result}
              size="wide"
              display={q.data.card.display}
              goal={q.data.card.goal}
              meta={
                <span className="text-xs text-muted-foreground tabular-nums">
                  {q.data.result.row_count.toLocaleString("tr-TR")} satır
                </span>
              }
              onDrill={
                q.data.drillable
                  ? (column, value) => setDrill({ cardId: id, title: q.data.card.name, column, value })
                  : undefined
              }
            />
          </div>
          {q.data.drillable && (
            <p className="text-xs text-muted-foreground">Detay satırlarını görmek için bir sütuna tıklayın.</p>
          )}
        </>
      )}
      <DrillSheet target={drill} onClose={() => setDrill(null)} />
    </div>
  );
}
