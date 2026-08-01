"use client";

// Analiz Tuvali (Faz 4.11, 1 Ağustos 2026 — dış yol haritası 2.6+2.10).
//
// Bugünkü "tek aktif rapor" modeli (page.tsx `active` + ReportPanel) HİÇ DEĞİŞMEDİ — bu
// bileşen TAMAMEN EKLEYİCİ bir ikinci görünüm. page.tsx her yeni rapor üretildiğinde (soru
// sorma / chip tıklama / sonraki-adım / öneri) `active`'e YAZMAYA devam eder VE (kullanıcı
// "tuval" moduna geçtiyse) AYNI raporu `canvasItems`'a da EKLER — üsttekini SİLMEZ, biriktirir.
// Tuval modu kapalıyken (varsayılan) bu bileşen hiç render edilmez, sıfır regresyon riski.
//
// Sürükle-bırak sıralama: yeni bir npm bağımlılığı (ör. @dnd-kit) EKLEMEDEN native HTML5
// Drag and Drop API ile (package.json'da mevcut bir DnD kütüphanesi yok, ağ erişimi
// gerektiren bir kurulum bu oturumda doğrulanamaz).
//
// "Rapor oluştur": DashboardView.tsx'teki AYNI postReport→ReportView deseni yeniden
// kullanılır (yeni bir rapor-render mantığı İCAT edilmedi, mevcut mekanizmanın YENİ bir
// giriş noktası).

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { addDashboardWidget, createDashboard, listDashboards, postReport } from "@/lib/api-client";
import type { AskResponse, DashboardListItem, Report } from "@/lib/types";
import { ResultView } from "@/components/ResultView";
import { ReportView } from "@/components/ReportView";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";

export function AnalysisCanvas({
  items,
  onReorder,
  onRemove,
  onClear,
}: {
  items: AskResponse[];
  onReorder: (from: number, to: number) => void;
  onRemove: (index: number) => void;
  onClear: () => void;
}) {
  const [report, setReport] = useState<Report | null>(null);
  const [dragIndex, setDragIndex] = useState<number | null>(null);

  // Yalnız gerçek bir cube_query+result taşıyan bloklar rapora girebilir (DashboardView'daki
  // widget→blok dönüşümüyle AYNI kural) — Discovery/ham-SQL veya salt-not öğeleri dürüstçe atlanır.
  const reportableItems = items.filter((it) => it.cube_query && it.result);

  const exportReport = useMutation({
    mutationFn: () =>
      postReport({
        title: "Analiz Tuvali Raporu",
        blocks: reportableItems.map((it) => ({
          cube_query: it.cube_query!,
          title: it.question,
          period: null,
          view_hint: it.view_hint || null,
        })),
      }),
    onSuccess: (r) => setReport(r),
  });

  // Rapor açıksa tuval yerine onu göster (pano akışıyla AYNI desen).
  if (report) return <ReportView report={report} onClose={() => setReport(null)} />;

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-md pt-16 text-center font-mono text-[12px] leading-relaxed text-neutral-400">
        tuval boş — sohbette bir rapor üretip <span className="text-foreground">sonraki adım</span>{" "}
        veya <span className="text-foreground">öneri</span> çipine tıkladıkça buraya eklenir.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-8 py-6">
      <div className="mb-4 flex items-center justify-between border-b border-hairline pb-3">
        <h2 className="font-mono text-[13px] uppercase tracking-wide text-muted">
          Analiz Tuvali <span className="text-neutral-400">· {items.length} blok</span>
        </h2>
        <div className="flex items-center gap-3">
          <button
            onClick={onClear}
            className="font-mono text-[11px] text-neutral-400 transition-colors hover:text-red-500"
          >
            tuvali temizle
          </button>
          <button
            onClick={() => exportReport.mutate()}
            disabled={reportableItems.length === 0 || exportReport.isPending}
            className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-40"
            title="Tuvaldeki blokları çok-sayfa bir rapora derle"
          >
            {exportReport.isPending ? "derleniyor…" : "⎙ rapor oluştur"}
          </button>
        </div>
      </div>

      {/* Bazı bloklar (ör. Discovery/ham-SQL kaynaklı, yapısal cube_query taşımayan
          yanıtlar) rapora GİREMEZ (DashboardView'daki widget→blok kuralıyla AYNI) —
          kullanıcı "N blok" derken raporun neden daha az sayfa çıktığını anlasın. */}
      {reportableItems.length > 0 && reportableItems.length < items.length && (
        <p className="mb-3 font-mono text-[10px] text-neutral-400">
          not: {items.length - reportableItems.length} blok yapısal bir sorgu taşımadığı
          için rapora dahil edilmeyecek (yalnız {reportableItems.length} blok rapora girer).
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {items.map((item, i) => (
          <CanvasCard
            key={i}
            index={i}
            total={items.length}
            item={item}
            dragging={dragIndex === i}
            onDragStart={() => setDragIndex(i)}
            onDragEnd={() => setDragIndex(null)}
            onDropOn={() => {
              if (dragIndex !== null && dragIndex !== i) onReorder(dragIndex, i);
              setDragIndex(null);
            }}
            onMoveUp={() => onReorder(i, i - 1)}
            onMoveDown={() => onReorder(i, i + 1)}
            onRemove={() => onRemove(i)}
          />
        ))}
      </div>
    </div>
  );
}

function CanvasCard({
  index,
  total,
  item,
  dragging,
  onDragStart,
  onDragEnd,
  onDropOn,
  onMoveUp,
  onMoveDown,
  onRemove,
}: {
  index: number;
  total: number;
  item: AskResponse;
  dragging: boolean;
  onDragStart: () => void;
  onDragEnd: () => void;
  onDropOn: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onRemove: () => void;
}) {
  const [dashOpen, setDashOpen] = useState(false);
  const [dashList, setDashList] = useState<DashboardListItem[]>([]);
  const [addedTo, setAddedTo] = useState<string | null>(null);

  const openDashMenu = () => {
    if (!dashOpen) listDashboards().then((r) => setDashList(r.dashboards)).catch(() => {});
    setDashOpen((o) => !o);
  };
  const addToDash = async (dashId: string) => {
    if (!item.cube_query) return;
    try {
      await addDashboardWidget(dashId, {
        title: item.question,
        cube_query: item.cube_query,
        view_hint: item.view_hint ?? null,
      });
      setAddedTo(dashId);
      setDashOpen(false);
    } catch {
      /* best-effort */
    }
  };
  const createAndAdd = async () => {
    const title = window.prompt("Yeni pano adı:", "Panom");
    if (!title) return;
    try {
      const d = await createDashboard(title);
      await addToDash(d.id);
    } catch {
      /* best-effort */
    }
  };

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      onDragOver={(e) => e.preventDefault()}
      onDrop={onDropOn}
      className={`flex flex-col border border-hairline bg-background p-3 transition-opacity ${
        dragging ? "opacity-40" : ""
      }`}
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="flex min-w-0 items-center gap-1.5">
          <span className="cursor-grab text-neutral-400" title="Sürükleyerek sırala" aria-hidden>
            ⠿
          </span>
          {/* Fare-sürükleme dışında (klavye/dokunmatik) da sıralanabilsin diye — native
              HTML5 DnD'nin klavye eşdeğeri yok, bu iki buton onun erişilebilir yedeği. */}
          <span className="flex shrink-0 flex-col leading-none">
            <button
              onClick={onMoveUp}
              disabled={index === 0}
              title="Yukarı taşı"
              aria-label="Yukarı taşı"
              className="text-neutral-400 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-30"
            >
              ▲
            </button>
            <button
              onClick={onMoveDown}
              disabled={index === total - 1}
              title="Aşağı taşı"
              aria-label="Aşağı taşı"
              className="text-neutral-400 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-30"
            >
              ▼
            </button>
          </span>
          <span className="truncate font-mono text-[12px] text-foreground">
            {String(index + 1).padStart(2, "0")} · {item.question}
          </span>
        </span>
        <span className="relative flex shrink-0 items-center gap-2">
          {item.cube_query && (
            <span className="relative">
              <button
                onClick={openDashMenu}
                title="Bu bloğu bir panoya ekle"
                className={`font-mono text-[11px] transition-colors ${
                  addedTo ? "text-accent" : "text-neutral-400 hover:text-foreground"
                }`}
              >
                {addedTo ? "✓ panoda" : "+ panoya"}
              </button>
              {dashOpen && (
                <span className="absolute right-0 top-full z-30 mt-1 flex w-56 flex-col border border-hairline bg-background shadow-lg">
                  {dashList.length === 0 && (
                    <span className="px-2 py-1.5 font-mono text-[11px] text-neutral-400">
                      henüz pano yok
                    </span>
                  )}
                  {dashList.map((d) => (
                    <button
                      key={d.id}
                      onClick={() => addToDash(d.id)}
                      className="px-2 py-1.5 text-left font-mono text-[11px] text-neutral-500 hover:bg-neutral-500/[0.06] hover:text-foreground"
                    >
                      {d.title} · {d.widget_count} widget
                    </button>
                  ))}
                  <button
                    onClick={createAndAdd}
                    className="border-t border-hairline px-2 py-1.5 text-left font-mono text-[11px] text-accent hover:bg-neutral-500/[0.06]"
                  >
                    + yeni pano
                  </button>
                </span>
              )}
            </span>
          )}
          <button
            onClick={onRemove}
            title="Tuvalden kaldır"
            className="font-mono text-[13px] text-neutral-400 transition-colors hover:text-red-500"
          >
            ×
          </button>
        </span>
      </div>

      {item.kpi ? (
        <KpiCardView card={item.kpi} />
      ) : item.result ? (
        <div className="max-h-72 overflow-auto">
          <ResultView result={item.result} viz={item.viz} viewHint={item.view_hint ?? undefined} />
        </div>
      ) : (
        <p className="font-mono text-[11px] text-neutral-400">{item.note || "veri yok"}</p>
      )}
      <OutputInsight interpretation={item.interpretation} />
    </div>
  );
}
