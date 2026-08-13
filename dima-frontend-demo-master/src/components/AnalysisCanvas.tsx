"use client";

// Analiz Tuvali (Faz 4.11, 1 Ağustos 2026 — dış yol haritası 2.6+2.10).
//
// Bugünkü "tek aktif rapor" modeli (page.tsx `active` + ReportPanel) HİÇ DEĞİŞMEDİ — bu
// bileşen TAMAMEN EKLEYİCİ bir ikinci görünüm. page.tsx her yeni rapor üretildiğinde (soru
// sorma / chip tıklama / sonraki-adım / öneri) `active`'e YAZMAYA devam eder VE (kullanıcı
// "tuval" moduna geçtiyse) AYNI raporu `canvasItems`'a da EKLER — üsttekini SİLMEZ, biriktirir.
// Tuval modu kapalıyken (varsayılan) bu bileşen hiç render edilmez, sıfır regresyon riski.
//
// Sürükle-bırak sıralama: doğrulama turu düzeltmesi (1 Ağustos 2026, P2-18) — İLK sürümde
// yeni bir bağımlılık EKLEMEDEN native HTML5 DnD kullanılmıştı (kurulum bu oturumda
// doğrulanamıyordu); şimdi `@dnd-kit/core`+`sortable` GERÇEKTEN kuruldu (kullanıcı onayıyla)
// — daha akıcı sürükleme + native HTML5 DnD'nin SAHİP OLMADIĞI klavye-erişilebilir sıralamayı
// (Tab ile odakla → Space ile "kaldır" → ok tuşlarıyla taşı → Space ile "bırak") ÜCRETSİZE
// getirir. ▲/▼ butonları YİNE DE korunur — basit, her zaman görünür bir yedek (iki mekanizma
// birbirini dışlamaz).
//
// "Rapor oluştur": DashboardView.tsx'teki AYNI postReport→ReportView deseni yeniden
// kullanılır (yeni bir rapor-render mantığı İCAT edilmedi, mevcut mekanizmanın YENİ bir
// giriş noktası).

import { SourceBadge } from "@/components/ChatPanel";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  DndContext, KeyboardSensor, PointerSensor, closestCenter,
  useSensor, useSensors, type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext, sortableKeyboardCoordinates, useSortable, rectSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { addDashboardWidget, createDashboard, listDashboards, postReport } from "@/lib/api-client";
import type { AskResponse, DashboardListItem, Report } from "@/lib/types";
import { ResultView } from "@/components/ResultView";
import { ReportView } from "@/components/ReportView";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { useAdSor } from "@/components/AdSor";

// `AskResponse`'un kendi kalıcı bir kimliği yok (sohbet mesajı DEĞİL, bir tuval öğesi) —
// @dnd-kit her öge için SABİT bir `id` ister (index KULLANILAMAZ, sıralama sırasında anlamı
// değişir). Her item nesnesine (referans eşitliğiyle) BİR KEZ, kalıcı bir id atanır.
const _idFor = new WeakMap<AskResponse, string>();
let _idSeq = 0;
function stableId(item: AskResponse): string {
  let id = _idFor.get(item);
  if (!id) {
    id = `canvas-item-${_idSeq++}`;
    _idFor.set(item, id);
  }
  return id;
}

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
  const ids = items.map(stableId);
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleDragEnd = (e: DragEndEvent) => {
    const { active, over } = e;
    if (!over || active.id === over.id) return;
    const from = ids.indexOf(String(active.id));
    const to = ids.indexOf(String(over.id));
    if (from !== -1 && to !== -1) onReorder(from, to);
  };

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
      // 🔴 Metin **aşağıyı** da söyler (2026-08-13): besteci artık tuvalin altında
      // duruyor (`ReportPanel.tuval`), yani tuvali doldurmanın yolu yalnız chip
      // tıklamak değil. Eski metin bunu söylemiyordu ve tek gerçek yolu gizliyordu —
      // *bir boş durum, çıkış yolunu da göstermek zorundadır.*
      <div className="mx-auto max-w-md pt-16 text-center font-mono text-[12px] leading-relaxed text-neutral-400">
        tuval boş — <span className="text-foreground">aşağıdan sor</span>, ya da sohbette bir
        rapor üretip <span className="text-foreground">sonraki adım</span>{" "}
        veya <span className="text-foreground">öneri</span> çipine tıkla; her rapor buraya eklenir.
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
            className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
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

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={ids} strategy={rectSortingStrategy}>
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {items.map((item, i) => (
              <CanvasCard
                key={ids[i]}
                id={ids[i]}
                index={i}
                total={items.length}
                item={item}
                onMoveUp={() => onReorder(i, i - 1)}
                onMoveDown={() => onReorder(i, i + 1)}
                onRemove={() => onRemove(i)}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}

function CanvasCard({
  id,
  index,
  total,
  item,
  onMoveUp,
  onMoveDown,
  onRemove,
}: {
  id: string;
  index: number;
  total: number;
  item: AskResponse;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onRemove: () => void;
}) {
  const { sor: adSor, alan: adSorAlani } = useAdSor();
  const [dashOpen, setDashOpen] = useState(false);
  const [dashList, setDashList] = useState<DashboardListItem[]>([]);
  const [addedTo, setAddedTo] = useState<string | null>(null);
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

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
    const title = await adSor("Yeni pano adı:", "Panom");
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
      ref={setNodeRef}
      style={style}
      className="flex flex-col border border-hairline bg-background p-3"
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="flex min-w-0 items-center gap-1.5">
          <span
            {...attributes}
            {...listeners}
            className="cursor-grab touch-none text-neutral-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent"
            title="Sürükleyerek sırala (odaklayıp ok tuşlarıyla da taşınabilir)"
            aria-label="Sürükleyerek sırala"
          >
            ⠿
          </span>
          {/* ▲/▼ butonları @dnd-kit'in klavye modunun YANINDA basit, her zaman görünür bir
              yedek olarak korunur (iki mekanizma birbirini dışlamaz). */}
          <span className="flex shrink-0 flex-col leading-none">
            <button
              onClick={onMoveUp}
              disabled={index === 0}
              title="Yukarı taşı"
              aria-label="Yukarı taşı"
              className="text-neutral-400 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
            >
              ▲
            </button>
            <button
              onClick={onMoveDown}
              disabled={index === total - 1}
              title="Aşağı taşı"
              aria-label="Aşağı taşı"
              className="text-neutral-400 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
            >
              ▼
            </button>
          </span>
          <span className="truncate font-mono text-[12px] text-foreground">
            {String(index + 1).padStart(2, "0")} · {item.question}
          </span>
        </span>
        <span className="relative flex shrink-0 items-center gap-2">
          {/* ⚠️ FAZ 0.3 — ROZET SÜS DEĞİL SÖZLEŞMEDİR (MIMARI §5: bir cevabın `source`'unu
              gizlemek ya da eşitlemek YASAKTIR). Ölçüldü [KANIT §0.1-2]: bu dosyada
              `SourceBadge` 0, `explain` 0 — aynı cevap sohbette `▚ LLM` rozetli, tuvalde
              ROZETSİZ görünüyordu. Kullanıcı iki yüzeyde AYNI cevaba bakıp FARKLI garanti
              görüyordu ve bunu fark etmesinin hiçbir yolu yoktu.
              🔴 `ChatPanel.SourceBadge` YENİDEN KULLANILIYOR — ikinci bir render edici
              yazmak, aynı kuralın iki sahibi demekti (bu deponun 1 numaralı kusuru) ve
              iki yüzeyin rozetleri zamanla AYRIŞIRDI. */}
          <SourceBadge source={item.source ?? null} sertifika={item.explain?.sertifika} />
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
            aria-label="Tuvalden kaldır"
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
      {adSorAlani}
    </div>
  );
}
