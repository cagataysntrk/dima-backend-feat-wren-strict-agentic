"use client";

// Pano görünümü (main-area overlay) — widget grid'i CANLI (§9 pull ayağı). Meta
// (widget listesi) + /data (dönem çözülmüş sonuçlar) ayrı sorgu; /data 60sn poll
// eder (onview + periyodik). Widget sonucu mevcut ResultView ile render edilir.

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteDashboardWidget,
  getDashboard,
  getDashboardData,
  patchDashboardWidget,
  postReport,
} from "@/lib/api-client";
import type { Report } from "@/lib/types";
import { ResultView } from "@/components/ResultView";
import { ReportView } from "@/components/ReportView";

// Doğrulama turu düzeltmesi (1 Ağustos 2026, P2-22): widget-BAŞINA yenileme sıklığı
// (`DashboardWidget.refresh` — backend'de zaten vardı, yalnız YAZMA ucu eksikti, bkz.
// app/routers/dashboards.py::WidgetPatch). `/dashboards/{id}/data` TEK bir birleşik uçtur
// (widget-başına ayrı istek YOK) — bu yüzden GERÇEK per-widget polling yerine, PRAGMATİK
// bir yaklaşım: pano en HIZLI (en kısa) yapılandırılmış widget'ın sıklığında yenilenir
// (diğer widget'lar biraz fazla-sıklıkta tazelenir ama YANLIŞ/eksik veri GÖSTERMEZ).
const REFRESH_OPTIONS = [
  { value: "onview", label: "yalnız açılışta" },
  { value: "cache:300", label: "5 dakikada bir" },
  { value: "cache:60", label: "dakikada bir" },
  { value: "live", label: "canlı (10sn)" },
] as const;

function refreshMs(refresh: string | undefined | null): number | null {
  if (!refresh || refresh === "onview") return null;
  if (refresh === "live") return 10_000;
  const m = /^cache:(\d+)$/.exec(refresh);
  return m ? Number(m[1]) * 1000 : null;
}

export function DashboardView({ id, onClose }: { id: string; onClose: () => void }) {
  const qc = useQueryClient();
  const [report, setReport] = useState<Report | null>(null);
  const meta = useQuery({ queryKey: ["dashboard", id], queryFn: () => getDashboard(id) });
  const fastestMs = Math.min(
    60_000, // varsayılan taban — hiçbir widget daha hızlısını istemiyorsa bu korunur
    ...(meta.data?.widgets ?? []).map((w) => refreshMs(w.refresh) ?? Infinity),
  );
  const data = useQuery({
    queryKey: ["dashboard-data", id],
    queryFn: () => getDashboardData(id),
    refetchInterval: Number.isFinite(fastestMs) ? fastestMs : 60_000,
  });
  const del = useMutation({
    mutationFn: (wid: string) => deleteDashboardWidget(id, wid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard", id] });
      qc.invalidateQueries({ queryKey: ["dashboard-data", id] });
    },
  });

  const dataById = new Map((data.data ?? []).map((w) => [w.id, w]));
  const widgets = meta.data?.widgets ?? [];
  const btn =
    "flex h-[26px] items-center border border-hairline px-2 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground";

  // Panoyu çok-SAYFA rapora dışa aktar (ADR-0024): widget'lar → bloklar → /report (deterministik,
  // her blok kendi viz kararını alır). Sonuç ReportView'de yazdırılabilir/PDF olarak açılır.
  const exportReport = useMutation({
    mutationFn: () =>
      postReport({
        title: meta.data?.title ? `${meta.data.title} — Rapor` : "Pano Raporu",
        blocks: widgets.map((w) => ({
          cube_query: w.cube_query,
          title: w.title || null,
          period: w.period || null,
          view_hint: w.view_hint || null, // widget'ın kayıtlı görünümü rapora taşınır
        })),
      }),
    onSuccess: (r) => setReport(r),
  });

  // GÖRÜNÜM KAYDET: kullanıcı panoda bir widget'ın tip/görünümünü değiştirince kalıcılaştır
  // (view_hint). Meta cache'i optimistik güncelle → refetch churn'ü olmadan seçim korunur.
  const saveView = useMutation({
    mutationFn: ({ wid, viewHint }: { wid: string; viewHint: string }) =>
      patchDashboardWidget(id, wid, { view_hint: viewHint }),
  });
  const onWidgetView = (wid: string, viewHint: string) => {
    saveView.mutate({ wid, viewHint });
    qc.setQueryData(["dashboard", id], (old: typeof meta.data) =>
      old ? { ...old, widgets: old.widgets.map((w) => (w.id === wid ? { ...w, view_hint: viewHint } : w)) } : old,
    );
  };

  // YENİLEME SIKLIĞI + GENİŞLİK kaydet (P2-22) — AYNI optimistik-güncelleme deseni.
  const saveRefresh = useMutation({
    mutationFn: ({ wid, refresh }: { wid: string; refresh: string }) =>
      patchDashboardWidget(id, wid, { refresh }),
  });
  const onWidgetRefresh = (wid: string, refresh: string) => {
    saveRefresh.mutate({ wid, refresh });
    qc.setQueryData(["dashboard", id], (old: typeof meta.data) =>
      old ? { ...old, widgets: old.widgets.map((w) => (w.id === wid ? { ...w, refresh } : w)) } : old,
    );
  };
  const saveWidth = useMutation({
    mutationFn: ({ wid, w }: { wid: string; w: 1 | 2 }) =>
      patchDashboardWidget(id, wid, { pos: { x: 0, y: 0, w, h: 1 } }),
  });
  const onWidgetWidth = (wid: string, w: 1 | 2) => {
    saveWidth.mutate({ wid, w });
    qc.setQueryData(["dashboard", id], (old: typeof meta.data) =>
      old ? { ...old, widgets: old.widgets.map((wg) =>
        wg.id === wid ? { ...wg, pos: { x: 0, y: 0, w, h: 1 } } : wg) } : old,
    );
  };

  // Rapor açıksa pano yerine onu göster (aynı overlay içinde).
  if (report) return <ReportView report={report} onClose={() => setReport(null)} />;

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-center justify-between border-b border-hairline px-6 py-3">
        <h2 className="truncate font-mono text-[15px] text-foreground">
          {meta.data?.title ?? "Pano"}
        </h2>
        <div className="flex shrink-0 items-center gap-2">
          {widgets.length > 0 && (
            <button
              onClick={() => exportReport.mutate()}
              disabled={exportReport.isPending}
              className={btn}
              title="Panoyu çok-sayfa rapora dışa aktar"
            >
              {exportReport.isPending ? "derleniyor…" : "⎙ raporu dışa aktar"}
            </button>
          )}
          <button onClick={() => data.refetch()} className={btn} title="Yenile">
            ↻ yenile
          </button>
          <button onClick={onClose} className={btn}>
            ✕ kapat
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto p-4">
        {meta.isLoading ? (
          <p className="font-mono text-[12px] text-neutral-400">yükleniyor…</p>
        ) : widgets.length === 0 ? (
          <p className="mx-auto max-w-md pt-16 text-center font-mono text-[12px] leading-relaxed text-neutral-400">
            bu pano boş — chat&apos;te bir rapor üretip{" "}
            <span className="text-foreground">+ panoya ekle</span> ile widget ekle.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {widgets.map((w) => {
              const wd = dataById.get(w.id);
              const wide = w.pos?.w === 2;
              return (
                <div
                  key={w.id}
                  className={`flex flex-col border border-hairline bg-background p-3 ${wide ? "xl:col-span-2" : ""}`}
                >
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <span className="truncate font-mono text-[12px] text-foreground">
                      {w.title ||
                        (typeof w.cube_query.cube === "string" ? w.cube_query.cube : "widget")}
                      {w.period ? (
                        <span className="ml-1 text-neutral-400">· {w.period}</span>
                      ) : null}
                    </span>
                    <span className="flex shrink-0 items-center gap-2">
                      {/* P2-22: genişlik + yenileme sıklığı — ikisi de backend'de zaten
                          var olan (pos_json/refresh) alanları KULLANIR, yeni bir kavram
                          İCAT ETMEZ. */}
                      <button
                        onClick={() => onWidgetWidth(w.id, wide ? 1 : 2)}
                        title={wide ? "Normal genişliğe al" : "Geniş yap (2 kolon)"}
                        aria-label={wide ? "Normal genişliğe al" : "Geniş yap"}
                        className="font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
                      >
                        {wide ? "⇔ dar" : "⇔ geniş"}
                      </button>
                      <select
                        value={w.refresh ?? "onview"}
                        onChange={(e) => onWidgetRefresh(w.id, e.target.value)}
                        title="Bu widget'ın yenileme sıklığı"
                        className="border border-hairline bg-background font-mono text-[10px] text-neutral-400"
                      >
                        {REFRESH_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                      <button
                        onClick={() => del.mutate(w.id)}
                        title="Widget'ı kaldır"
                        aria-label="Widget'ı kaldır"
                        className="shrink-0 font-mono text-[13px] text-neutral-400 transition-colors hover:text-red-500"
                      >
                        ×
                      </button>
                    </span>
                  </div>
                  {data.isLoading ? (
                    <p className="font-mono text-[11px] text-neutral-400">yürütülüyor…</p>
                  ) : wd?.error ? (
                    <p className="font-mono text-[11px] text-red-500">{wd.error}</p>
                  ) : wd?.result ? (
                    <ResultView
                      result={wd.result}
                      viewHint={w.view_hint ?? undefined}
                      viz={wd.viz}
                      onViewChange={(vh) => onWidgetView(w.id, vh)}
                    />
                  ) : (
                    <p className="font-mono text-[11px] text-neutral-400">veri yok</p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
