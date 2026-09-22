"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BarChart3, LayoutDashboard, Trash2, Undo2 } from "lucide-react";
import { toast } from "sonner";
import { EmptyState } from "@/components/shell/EmptyState";
import { gateway, type Item } from "@/lib/gateway";
import { Button } from "@dima/ui/primitives/button";
import { Skeleton } from "@dima/ui/primitives/skeleton";

/** Archived analyses and dashboards; restoring keeps their ids, so links survive. */
export function TrashView() {
  const queryClient = useQueryClient();
  const items = useQuery({ queryKey: ["trash"], queryFn: gateway.trash });
  const restore = useMutation({
    mutationFn: (i: Item) => gateway.restore(i.kind === "dashboard" ? "dashboard" : "card", i.id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["trash"] });
      void queryClient.invalidateQueries({ queryKey: ["items"] });
      toast.success("Geri alındı.");
    },
    onError: (e) => toast.error(e.message),
  });

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Çöp kutusu</h1>
        <p className="text-sm text-muted-foreground">
          Silinen analiz ve panolar burada durur; geri aldığınızda bağlantıları ve panolardaki yerleri korunur.
        </p>
      </header>

      {items.isPending && <Skeleton className="h-24 w-full" />}
      {items.isError && (
        <p role="alert" className="text-sm text-destructive">
          {items.error.message}
        </p>
      )}
      {items.data?.length === 0 && (
        <div className="surface-sm">
          <EmptyState
            icon={Trash2}
            title="Çöp kutusu boş."
            hint="Sildiğiniz pano ve analizler kalıcı olarak silinmeden önce burada bekler."
          />
        </div>
      )}

      <ul className="space-y-2">
        {items.data?.map((i) => (
          <li key={`${i.kind}-${i.id}`} className="surface-sm flex items-center gap-3 px-3 py-2.5">
            <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-muted text-muted-foreground">
              {i.kind === "dashboard" ? (
                <LayoutDashboard className="size-4" aria-hidden />
              ) : (
                <BarChart3 className="size-4" aria-hidden />
              )}
            </span>
            <span className="min-w-0 flex-1 truncate">{i.name}</span>
            <Button variant="ghost" size="sm" onClick={() => restore.mutate(i)} disabled={restore.isPending}>
              <Undo2 className="size-4" aria-hidden />
              Geri al
            </Button>
          </li>
        ))}
      </ul>
    </div>
  );
}
