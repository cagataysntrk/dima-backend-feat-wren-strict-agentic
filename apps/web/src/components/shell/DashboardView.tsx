"use client";

import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { ArrowLeft, RefreshCw, Trash2, TriangleAlert } from "lucide-react";
import {
  deleteDashboardWidget,
  getDashboard,
  getDashboardData,
} from "@dima/api-client";
import { ResultView } from "@/components/ResultView";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

/**
 * Tek panonun CANLI görünümü.
 *
 * Karolar sonuç saklamaz: `/dashboards/{id}/data` her çağrıldığında göreli
 * dönemler yeniden çözülür ve cube_query yeniden koşar. Bu yüzden "yenile"
 * gerçek bir yenilemedir, önbellek tazeleme değil.
 *
 * Bir karo patlarsa backend o karo için `error` döndürür ve diğerleri gelir —
 * pano tek bozuk sorgu yüzünden komple düşmez. Burada da öyle gösteriyoruz.
 */
export function DashboardView({ id, onBack }: { id: string; onBack: () => void }) {
  const qc = useQueryClient();

  const { data: dash, isPending: dashPending } = useQuery({
    queryKey: ["dashboard", id],
    queryFn: () => getDashboard(id),
  });
  const {
    data: widgets,
    isFetching,
    refetch,
  } = useQuery({
    queryKey: ["dashboard-data", id],
    queryFn: () => getDashboardData(id),
    // Canlı izleme panosu: sekmeye dönünce tazelensin, ama arka planda sürekli
    // sorgu koşturmasın (her çağrı gerçek SQL demek).
    refetchOnWindowFocus: true,
    staleTime: 60_000,
  });

  const removeWidget = useMutation({
    mutationFn: (widgetId: string) => deleteDashboardWidget(id, widgetId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dashboard", id] });
      void qc.invalidateQueries({ queryKey: ["dashboard-data", id] });
      void qc.invalidateQueries({ queryKey: ["dashboards"] });
    },
  });

  const dataById = new Map((widgets ?? []).map((w) => [w.id, w]));

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <Button variant="ghost" size="sm" onClick={onBack} className="-ml-2 gap-1.5">
          <ArrowLeft className="size-4" />
          Panolar
        </Button>
        <div className="flex items-center gap-1">
          {dash && !dash.own && (
            <Badge variant="outline" className="text-[10px]">
              salt okunur
            </Badge>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label="Yenile"
                onClick={() => void refetch()}
                disabled={isFetching}
                className="text-muted-foreground hover:text-foreground"
              >
                <RefreshCw className={isFetching ? "size-4 animate-spin" : "size-4"} />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Karoları yeniden çalıştır</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {dash && <h3 className="text-sm font-medium text-foreground">{dash.title}</h3>}

      {dashPending ? (
        <div className="space-y-3">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      ) : !dash || dash.widgets.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
          <p className="text-sm text-muted-foreground">Bu panoda henüz karo yok.</p>
          <p className="max-w-xs text-xs text-muted-foreground/80">
            Bir cevabın altındaki <span className="font-medium">panoya ekle</span> ile karo
            ekleyebilirsin.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {dash.widgets.map((w) => {
            const d = dataById.get(w.id);
            return (
              <Card key={w.id} className="gap-2 p-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate text-sm text-foreground">{w.title || "Karo"}</p>
                    {w.period && (
                      <span className="font-mono text-[10px] text-muted-foreground">
                        {w.period}
                      </span>
                    )}
                  </div>
                  {dash.own && (
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label="Karoyu kaldır"
                      onClick={() => removeWidget.mutate(w.id)}
                      className="shrink-0 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  )}
                </div>

                {d?.error ? (
                  <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2">
                    <TriangleAlert className="mt-0.5 size-3.5 shrink-0 text-destructive" />
                    <p className="text-xs leading-relaxed text-destructive">{d.error}</p>
                  </div>
                ) : d?.result ? (
                  <ResultView result={d.result} viewHint={w.view_hint ?? undefined} />
                ) : (
                  <Skeleton className="h-32 w-full" />
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
