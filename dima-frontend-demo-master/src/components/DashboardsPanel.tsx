"use client";

// Pano listesi (rail drawer) — oluştur/sil + aç (§9). HistoryPanel deseniyle aynı:
// React Query ile liste + mutation'da invalidate. Açma → page main-area overlay'i.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createDashboard, deleteDashboard, listDashboards, patchDashboard } from "@/lib/api-client";
import { useAdSor } from "@/components/AdSor";
import { useState } from "react";
import { HataSeridi } from "@/components/HataSeridi";
import { hataMetni } from "@/lib/mutasyonHatasi";

export function DashboardsPanel({ onOpen }: { onOpen: (id: string) => void }) {
  // 🔴 Denetim F3: bu panelde mutasyonların **hiçbiri** hata yüzeyi taşımıyordu —
  // 403 dönen bir silme ekranda hiçbir iz bırakmıyordu. *Sessizce başarısız olan
  // bir eylem, kullanıcıya ürünün bozuk olduğunu değil KENDİSİNİN yanlış yaptığını
  // düşündürür.*
  const [hata, setHata] = useState<string | null>(null);
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["dashboards"], queryFn: listDashboards });
  const create = useMutation({
    onError: (e) => setHata(hataMetni(e, "Pano oluşturma")),
    mutationFn: (title: string) => createDashboard(title),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboards"] }),
  });
  const del = useMutation({
    onError: (e) => setHata(hataMetni(e, "Pano silme")),
    mutationFn: (id: string) => deleteDashboard(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboards"] }),
  });
  // Doğrulama turu düzeltmesi (1 Ağustos 2026) — PATCH /dashboards/{id} zaten vardı ama
  // hiç çağrılmıyordu: kullanıcı bir panoyu oluşturduktan sonra adını/görünürlüğünü ASLA
  // değiştiremiyordu.
  const { sor: adSor, alan: adSorAlani } = useAdSor();
  const patch = useMutation({
    onError: (e) => setHata(hataMetni(e, "Pano güncelleme")),
    mutationFn: ({ id, body }: { id: string; body: Parameters<typeof patchDashboard>[1] }) =>
      patchDashboard(id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dashboards"] }),
  });
  const rename = async (id: string, currentTitle: string) => {
    const title = await adSor("Panoyu yeniden adlandır:", currentTitle);
    if (title && title !== currentTitle) patch.mutate({ id, body: { title } });
  };
  const toggleVisibility = (id: string, current: string) => {
    patch.mutate({ id, body: { visibility: current === "tenant" ? "private" : "tenant" } });
  };

  const list = data?.dashboards ?? [];
  const ownCount = list.filter((d) => d.own).length;
  const atMax = data ? ownCount >= data.max_per_user : false;

  const newDash = async () => {
    const title = await adSor("Yeni pano adı:", "Panom");
    if (title) create.mutate(title);
  };

  return (
    <div className="space-y-3">
      <HataSeridi metin={hata} onKapat={() => setHata(null)} />
      {adSorAlani}
      <button
        onClick={newDash}
        disabled={atMax || create.isPending}
        className="w-full border border-hairline px-2 py-1.5 text-left font-mono text-[12px] text-neutral-500 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
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
                <span className="ml-2 flex shrink-0 items-center gap-1.5">
                  <button
                    onClick={() => rename(d.id, d.title)}
                    disabled={patch.isPending}
                    title="Yeniden adlandır"
                    aria-label="Yeniden adlandır"
                    className="font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
                  >
                    ✎
                  </button>
                  <button
                    onClick={() => toggleVisibility(d.id, d.visibility)}
                    disabled={patch.isPending}
                    title={d.visibility === "tenant" ? "Şirket geneli — özel yap" : "Özel — şirket geneline aç"}
                    aria-label="Görünürlüğü değiştir"
                    className="font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
                  >
                    {d.visibility === "tenant" ? "🏢" : "🔒"}
                  </button>
                  <button
                    onClick={() => del.mutate(d.id)}
                    disabled={del.isPending}
                    title="Panoyu sil"
                    aria-label="Panoyu sil"
                    className="font-mono text-[13px] text-neutral-400 transition-colors hover:text-red-500"
                  >
                    ×
                  </button>
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
