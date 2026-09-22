"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { gateway, type Filters, type Widget, type WidgetData } from "@/lib/gateway";
import { cn } from "@/lib/utils";
import { ResultView } from "@/components/ResultView";
import { FilterBar } from "@/components/analytics/FilterBar";
import { ExportMenu } from "@/components/analytics/ExportMenu";
import { DrillSheet, type DrillTarget } from "@/components/analytics/DrillSheet";
import { Skeleton } from "@/components/ui/skeleton";

function filtersFromParams(sp: URLSearchParams): Filters {
  const f: Filters = {};
  for (const [k, v] of sp) (f[k] ??= []).push(v);
  return f;
}

export function DashboardView({ id }: { id: number }) {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const filters = useMemo(() => filtersFromParams(new URLSearchParams(sp.toString())), [sp]);
  const [drill, setDrill] = useState<DrillTarget | null>(null);

  const meta = useQuery({ queryKey: ["dashboard", id], queryFn: () => gateway.dashboard(id) });
  const data = useQuery({
    queryKey: ["dashboard-data", id, filters],
    queryFn: () => gateway.dashboardData(id, filters),
    placeholderData: keepPreviousData,
  });

  const setFilters = (next: Filters) => {
    const p = new URLSearchParams();
    for (const [k, vs] of Object.entries(next)) for (const v of vs) p.append(k, v);
    const s = p.toString();
    router.replace(s ? `${pathname}?${s}` : pathname, { scroll: false });
  };

  const byId = new Map<number, WidgetData>((data.data ?? []).map((w) => [w.id, w]));
  const widgets = meta.data?.widgets ?? [];
  const kpis = widgets.filter((w) => w.display === "scalar");
  const charts = widgets.filter((w) => w.display !== "scalar");

  const card = (w: Widget, kpi: boolean) => {
    const d = byId.get(w.id);
    const scope = { dashboardId: id, dashcardId: w.id, filters };
    return (
      <section
        key={w.id}
        aria-labelledby={`w-${w.id}`}
        className={cn("flex min-w-0 flex-col rounded-xl border bg-card p-4", data.isFetching && "opacity-70")}
      >
        <div className="mb-2 flex items-start justify-between gap-2">
          <h2 id={`w-${w.id}`} className="text-sm font-medium">
            <Link href={`/app/cards/${w.cardId}`} className="hover:underline">
              {w.title}
            </Link>
          </h2>
          {!kpi && <ExportMenu cardId={w.cardId} scope={scope} />}
        </div>
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
            onDrill={(column, value) => setDrill({ cardId: w.cardId, title: w.title, column, value, scope })}
          />
        ) : null}
      </section>
    );
  };

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
          <header className="space-y-1">
            <h1 className="text-2xl font-semibold tracking-tight">{meta.data.name}</h1>
            {meta.data.description && <p className="text-sm text-muted-foreground">{meta.data.description}</p>}
          </header>
          {meta.data.parameters.length > 0 && (
            <FilterBar dashboardId={id} parameters={meta.data.parameters} filters={filters} onChange={setFilters} />
          )}
          {data.isError && (
            <p role="alert" className="text-sm text-destructive">
              {data.error.message}
            </p>
          )}
          {kpis.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{kpis.map((w) => card(w, true))}</div>
          )}
          <div className="grid gap-4 lg:grid-cols-2">{charts.map((w) => card(w, false))}</div>
          <p className="text-xs text-muted-foreground">
            Detay satırlarını görmek için bir sütuna tıklayın. Filtreler bağlantıya kaydedilir.
          </p>
        </>
      )}
      <DrillSheet target={drill} onClose={() => setDrill(null)} />
    </div>
  );
}
