"use client";

// Pano listesi (rail drawer) — oluştur/sil + aç (§9). HistoryPanel deseniyle aynı:
// React Query ile liste + mutation'da invalidate. Açma → page main-area overlay'i.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createDashboard, deleteDashboard, listDashboards } from "@/lib/api-client";

export function DashboardsPanel({ onOpen }: { onOpen: (id: string) => void }) {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["dashboards"], queryFn: listDashboards });
  const create = useMutation({
    mutationFn: (title: string) => createDashboard(title),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboards"] }),
  });
  const del = useMutation({
    mutationFn: (id: string) => deleteDashboard(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboards"] }),
  });

  const list = data?.dashboards ?? [];
  const ownCount = list.filter((d) => d.own).length;
  const atMax = data ? ownCount >= data.max_per_user : false;

  const newDash = () => {
    const title = window.prompt("Yeni pano adı:", "Panom");
    if (title) create.mutate(title);
  };

  return (
    <div className="space-y-3">
      <button
        onClick={newDash}
        disabled={atMax || create.isPending}
        className="w-full border border-hairline px-2 py-1.5 text-left font-mono text-[12px] text-neutral-500 transition-colors hover:text-foreground disabled:opacity-40"
      >
        + yeni pano{atMax ? " · limit doldu" : ""}
      </button>

      {isLoading ? (
        <p className="font-mono text-[12px] text-neutral-400">yükleniyor…</p>
      ) : list.length === 0 ? (
        <p className="font-mono text-[12px] leading-relaxed text-neutral-400">
          henüz pano yok — chat&apos;te bir rapor üretip{" "}
          <span className="text-foreground">+ panoya ekle</span> ile başla.
        </p>
      ) : (
        <ul className="space-y-0.5">
          {list.map((d) => (
            <li
              key={d.id}
              className="flex items-center justify-between border border-hairline px-2 py-1.5 transition-colors hover:bg-neutral-500/[0.04]"
            >
              <button onClick={() => onOpen(d.id)} className="min-w-0 flex-1 text-left">
                <div className="truncate font-mono text-[12px] text-foreground">{d.title}</div>
                <div className="font-mono text-[10px] text-neutral-400">
                  {d.widget_count} widget
                  {d.visibility === "tenant" ? " · şirket" : ""}
                  {!d.own ? " · paylaşılan" : ""}
                </div>
              </button>
              {d.own && (
                <button
                  onClick={() => del.mutate(d.id)}
                  disabled={del.isPending}
                  title="Panoyu sil"
                  className="ml-2 font-mono text-[13px] text-neutral-400 transition-colors hover:text-red-500"
                >
                  ×
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
