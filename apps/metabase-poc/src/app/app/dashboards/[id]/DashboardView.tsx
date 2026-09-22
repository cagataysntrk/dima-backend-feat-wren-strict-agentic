"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowDown, ArrowLeft, ArrowUp, Columns2, FilterX, Pencil, Square, Trash2, X } from "lucide-react";
import { toast } from "sonner";
import { gateway, type Filters, type Widget, type WidgetData, type WidgetWidth } from "@/lib/gateway";
import { cn } from "@/lib/utils";
import { ResultView } from "@/components/ResultView";
import { FilterBar } from "@/components/analytics/FilterBar";
import { ExportMenu } from "@/components/analytics/ExportMenu";
import { DrillSheet, type DrillTarget } from "@/components/analytics/DrillSheet";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

function filtersFromParams(sp: URLSearchParams): Filters {
  const f: Filters = {};
  for (const [k, v] of sp) (f[k] ??= []).push(v);
  return f;
}

type Draft = { name: string; widgets: Widget[] };

export function DashboardView({ id, canEdit }: { id: number; canEdit: boolean }) {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const queryClient = useQueryClient();
  const filters = useMemo(() => filtersFromParams(new URLSearchParams(sp.toString())), [sp]);
  const [drill, setDrill] = useState<DrillTarget | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const editing = draft !== null;

  const meta = useQuery({ queryKey: ["dashboard", id], queryFn: () => gateway.dashboard(id) });
  const data = useQuery({
    queryKey: ["dashboard-data", id, filters],
    queryFn: () => gateway.dashboardData(id, filters),
    placeholderData: keepPreviousData,
  });

  const save = useMutation({
    mutationFn: async (d: Draft) => {
      if (meta.data && d.name.trim() && d.name.trim() !== meta.data.name) {
        await gateway.updateDashboard(id, { name: d.name.trim() });
      }
      await gateway.saveLayout(
        id,
        d.widgets.map((w) => ({ id: w.id, width: w.width })),
      );
    },
    onSuccess: () => {
      setDraft(null);
      void queryClient.invalidateQueries({ queryKey: ["dashboard", id] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-data", id] });
      toast.success("Pano kaydedildi.");
    },
    onError: (e) => toast.error(e.message),
  });

  const remove = useMutation({
    mutationFn: () => gateway.archiveDashboard(id),
    onSuccess: () => {
      toast.success("Pano silindi.");
      router.push("/app");
      router.refresh();
    },
    onError: (e) => toast.error(e.message),
  });

  const setFilters = (next: Filters) => {
    const p = new URLSearchParams();
    for (const [k, vs] of Object.entries(next)) for (const v of vs) p.append(k, v);
    const s = p.toString();
    router.replace(s ? `${pathname}?${s}` : pathname, { scroll: false });
  };

  const byId = new Map<number, WidgetData>((data.data ?? []).map((w) => [w.id, w]));
  const widgets = draft?.widgets ?? meta.data?.widgets ?? [];
  const filtersActive = Object.keys(filters).length > 0;

  const move = (index: number, dir: -1 | 1) =>
    setDraft((d) => {
      if (!d) return d;
      const ws = [...d.widgets];
      const j = index + dir;
      if (j < 0 || j >= ws.length) return d;
      [ws[index], ws[j]] = [ws[j], ws[index]];
      return { ...d, widgets: ws };
    });
  const setWidth = (wid: number, width: WidgetWidth) =>
    setDraft((d) => d && { ...d, widgets: d.widgets.map((w) => (w.id === wid ? { ...w, width } : w)) });
  const drop = (wid: number) => setDraft((d) => d && { ...d, widgets: d.widgets.filter((w) => w.id !== wid) });

  const renderWidget = (w: Widget, index: number) => {
    const d = byId.get(w.id);
    const kpi = w.width === "kpi";
    const scope = { dashboardId: id, dashcardId: w.id, filters };
    return (
      <section
        key={w.id}
        aria-labelledby={`w-${w.id}`}
        className={cn(
          "surface flex min-w-0 flex-col p-5",
          w.width === "full" && "lg:col-span-2",
          data.isFetching && !editing && "opacity-70",
          editing && "outline-2 outline-offset-2 outline-dashed outline-brand/25",
        )}
      >
        <div className="mb-2 flex items-start justify-between gap-2">
          <h2 id={`w-${w.id}`} className="text-sm font-medium">
            <Link href={`/app/cards/${w.cardId}`} className="hover:underline">
              {w.title}
            </Link>
          </h2>
          {editing ? (
            <div className="flex shrink-0 items-center gap-0.5">
              <Button variant="ghost" size="icon-xs" aria-label="Yukarı taşı" disabled={index === 0} onClick={() => move(index, -1)}>
                <ArrowUp />
              </Button>
              <Button
                variant="ghost"
                size="icon-xs"
                aria-label="Aşağı taşı"
                disabled={index === widgets.length - 1}
                onClick={() => move(index, 1)}
              >
                <ArrowDown />
              </Button>
              {!kpi && (
                <Button
                  variant="ghost"
                  size="icon-xs"
                  aria-label={w.width === "full" ? "Yarım genişlik" : "Tam genişlik"}
                  title={w.width === "full" ? "Yarım genişlik" : "Tam genişlik"}
                  onClick={() => setWidth(w.id, w.width === "full" ? "half" : "full")}
                >
                  {w.width === "full" ? <Columns2 /> : <Square />}
                </Button>
              )}
              <Button variant="ghost" size="icon-xs" aria-label="Panodan kaldır" onClick={() => drop(w.id)}>
                <X />
              </Button>
            </div>
          ) : (
            !kpi && <ExportMenu cardId={w.cardId} scope={scope} />
          )}
        </div>
        {!w.filtered && filtersActive && (
          <p className="mb-2 flex items-center gap-1.5 text-xs text-muted-foreground">
            <FilterX className="size-3.5" aria-hidden />
            Filtreler bu grafiğe uygulanmaz.
          </p>
        )}
        {!d ? (
          <Skeleton className={kpi ? "h-16 w-full" : "aspect-[16/10] w-full"} />
        ) : d.error ? (
          <p role="alert" className="text-sm text-destructive">
            {d.error}
          </p>
        ) : d.result ? (
          <ResultView
            key={JSON.stringify(filters)}
            result={d.result}
            size={w.width === "full" ? "wide" : "normal"}
            display={w.display}
            goal={w.goal}
            onDrill={
              editing ? undefined : (column, value) => setDrill({ cardId: w.cardId, title: w.title, column, value, scope })
            }
            onZoom={
              editing
                ? undefined
                : (value) => setDrill({ cardId: w.cardId, title: w.title, column: "", value, scope, mode: "time" })
            }
          />
        ) : null}
      </section>
    );
  };

  const kpis = widgets.map((w, i) => [w, i] as const).filter(([w]) => w.width === "kpi");
  const charts = widgets.map((w, i) => [w, i] as const).filter(([w]) => w.width !== "kpi");

  return (
    <div className="space-y-6">
      <Link href="/app" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="size-4" aria-hidden />
        Genel bakış
      </Link>
      {meta.isPending ? (
        <Skeleton className="h-8 w-64" />
      ) : meta.isError ? (
        <p role="alert" className="text-sm text-destructive">
          {meta.error.message}
        </p>
      ) : (
        <>
          <header className="flex flex-wrap items-start justify-between gap-3">
            {editing ? (
              <div className="min-w-0 flex-1">
                <label htmlFor="dashboard-title" className="sr-only">
                  Pano adı
                </label>
                <Input
                  id="dashboard-title"
                  value={draft.name}
                  onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                  maxLength={120}
                  className="h-10 max-w-md text-lg font-semibold md:text-lg"
                />
              </div>
            ) : (
              <div className="min-w-0 space-y-1">
                <h1 className="text-2xl font-semibold tracking-tight">{meta.data.name}</h1>
                {meta.data.description && <p className="text-sm text-muted-foreground">{meta.data.description}</p>}
              </div>
            )}
            {canEdit && (
              <div className="flex shrink-0 items-center gap-2">
                {editing ? (
                  <>
                    <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive" onClick={() => setConfirmDelete(true)}>
                      <Trash2 className="size-4" aria-hidden />
                      Panoyu sil
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setDraft(null)} disabled={save.isPending}>
                      Vazgeç
                    </Button>
                    <Button
                      variant="brand"
                      size="sm"
                      onClick={() => save.mutate(draft)}
                      disabled={save.isPending || !draft.name.trim()}
                    >
                      {save.isPending ? "Kaydediliyor…" : "Kaydet"}
                    </Button>
                  </>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setDraft({ name: meta.data.name, widgets: [...meta.data.widgets] })}
                  >
                    <Pencil className="size-4" aria-hidden />
                    Düzenle
                  </Button>
                )}
              </div>
            )}
          </header>
          {meta.data.parameters.length > 0 && !editing && (
            <FilterBar dashboardId={id} parameters={meta.data.parameters} filters={filters} onChange={setFilters} />
          )}
          {data.isError && (
            <p role="alert" className="text-sm text-destructive">
              {data.error.message}
            </p>
          )}
          {widgets.length === 0 ? (
            <div className="rounded-[1.25rem] border-2 border-dashed border-[var(--surface-edge-strong)] p-10 text-center">
              <p className="font-medium">Bu pano henüz boş</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Bir analizi ya da sohbet yanıtını “Panoya ekle” ile buraya ekleyin.
              </p>
            </div>
          ) : (
            <>
              {kpis.length > 0 && (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{kpis.map(([w, i]) => renderWidget(w, i))}</div>
              )}
              <div className="grid gap-4 lg:grid-cols-2">{charts.map(([w, i]) => renderWidget(w, i))}</div>
            </>
          )}
          {!editing && widgets.length > 0 && (
            <p className="text-xs text-muted-foreground">
              Keşfetmek için bir sütuna ya da noktaya tıklayın. Filtreler bağlantıya kaydedilir.
            </p>
          )}
        </>
      )}
      <DrillSheet target={drill} onClose={() => setDrill(null)} />
      <Dialog open={confirmDelete} onOpenChange={setConfirmDelete}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Pano silinsin mi?</DialogTitle>
            <DialogDescription>
              “{meta.data?.name}” çöp kutusuna taşınır; içindeki analizler silinmez.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setConfirmDelete(false)}>
              Vazgeç
            </Button>
            <Button variant="destructive" onClick={() => remove.mutate()} disabled={remove.isPending}>
              {remove.isPending ? "Siliniyor…" : "Panoyu sil"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
