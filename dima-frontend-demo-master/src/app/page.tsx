"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { apiErrorMessage, ask, askCube, getConversation, uploadDataset } from "@/lib/api-client";
import { AnalysisCanvas } from "@/components/AnalysisCanvas";
import { ChatPanel } from "@/components/ChatPanel";
import { ConnectionReviewPanel } from "@/components/ConnectionReviewPanel";
import { DashboardsPanel } from "@/components/DashboardsPanel";
import { DashboardView } from "@/components/DashboardView";
import { FloatingControls } from "@/components/FloatingControls";
import { HelpPanel } from "@/components/HelpPanel";
import { HistoryPanel } from "@/components/HistoryPanel";
import { Landing } from "@/components/Landing";
import { NotificationsPanel } from "@/components/NotificationsBell";
import { ReportPanel } from "@/components/ReportPanel";
import { SchemaPanel } from "@/components/SchemaPanel";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import { useHistory } from "@/stores/history";
import { useFeature } from "@/lib/useFeature";
import { usePermission } from "@/lib/usePermission";
import type { AskResponse } from "@/lib/types";

type Drawer = "settings" | "help" | "notifications" | "history" | "dashboards" | null;

// Oturum kimliği — crypto.randomUUID yalnız güvenli bağlamda (https/localhost) var;
// http://*.localtld'de yok, bu yüzden fallback.
function makeSessionId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
  } catch {
    /* güvenli bağlam değil */
  }
  return `s-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

// Dosya → base64 (data-url önekini at) — /ask/upload multipart yerine JSON+base64 alır.
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result).split(",")[1] ?? "");
    r.onerror = () => reject(r.error);
    r.readAsDataURL(file);
  });
}

export default function Home() {
  const [active, setActive] = useState<AskResponse | null>(null);
  // Takip bağlamı: bir sonraki mesajla gönderilecek CubeQuery. Rapor VE clarify notu (kısmi
  // cube_query) bunu günceller — "bu ay" chip'i doğru sorguya uygulansın (ADR-0007 Faz C).
  const [contextCq, setContextCq] = useState<AskResponse["cube_query"]>(null);
  // Strict-agentic (wren_sql) takip bağlamı: bir önceki /ask cevabının SQL'i — cube_query'den
  // AYRI (bkz. lib/types.ts AskRequest.prev_sql); "aylara göre" gibi bir takip mesajı backend'de
  // bu SQL'i düzenleyerek yanıtlanır (generate_followup_sql), sıfırdan bağlamsız üretmez.
  const [prevSql, setPrevSql] = useState<string | null>(null);
  // Görünüm ipucu ("grafik ver") — sağ paneldeki raporun görünümünü değiştirir.
  const [viewHint, setViewHint] = useState<{ kind: string; nonce: number } | null>(null);
  const [drawer, setDrawer] = useState<Drawer>(null);
  // "Ayarlar" drawer'ı içi iki sekmeli (Faz 4.5): mevcut şema görünümü + DB bağlama
  // sihirbazı — YENİ bir rail ikonu/Drawer değeri EKLEMEDEN, en düşük riskli entegrasyon.
  const [settingsTab, setSettingsTab] = useState<"sema" | "baglanti">("sema");
  // Açık pano (main-area overlay) — set ise chat/rapor yerine pano grid'i gösterilir (§9).
  const [openDashboard, setOpenDashboard] = useState<string | null>(null);
  const dashStage = useFeature("dashboards");
  const canReview = usePermission("measure:read");
  const router = useRouter();
  const [startedLatch, setStarted] = useState(false);
  const [sessionId, setSessionId] = useState(makeSessionId);
  const qc = useQueryClient();
  // "✓ doğru" etiketi: raporu üreten SON GERÇEK soru (chip düzenlemeleri soru değildir —
  // "chip: kova → month" VQR'a yazılamaz; öğrenme orijinal soru metniyle anlamlı).
  const [verifyLabel, setVerifyLabel] = useState<string | null>(null);
  const items = useHistory((s) => s.items);
  const addHistory = useHistory((s) => s.add);
  const loadHistory = useHistory((s) => s.load);
  const clearHistory = useHistory((s) => s.clear);

  // Faz 4.11 — Analiz Tuvali (dış yol haritası 2.6+2.10): EKLEYİCİ, opsiyonel ikinci görünüm.
  // `active` (tek-rapor akışı) HİÇ değişmiyor; tuval modu açıkken ÜSTÜNE, her yeni gerçek
  // rapor (soru/chip/sonraki-adım/öneri) `canvasItems`'a da eklenir — üsttekini SİLMEZ.
  const [canvasMode, setCanvasMode] = useState(false);
  const [canvasItems, setCanvasItems] = useState<AskResponse[]>([]);
  const addToCanvas = (data: AskResponse) => {
    if (!canvasMode) return;
    if (!(data.result || data.kpi)) return; // yalnız gerçek rapor/KPI (not/clarify değil)
    setCanvasItems((prev) => [...prev, data]);
  };
  const reorderCanvas = (from: number, to: number) => {
    setCanvasItems((prev) => {
      const next = [...prev];
      const [moved] = next.splice(from, 1);
      next.splice(to, 0, moved);
      return next;
    });
  };
  const removeFromCanvas = (index: number) => {
    setCanvasItems((prev) => prev.filter((_, i) => i !== index));
  };

  // Resume: kayıtlı sohbeti yükle — mesajlar (seq eski→yeni) store'a newest-first konur;
  // session_id o sohbete geçer (takip soruları aynı sohbete eklenir).
  const resumeConversation = async (id: string) => {
    const det = await getConversation(id);
    const msgs = [...det.messages].reverse(); // seq artan → store newest-first
    loadHistory(msgs);
    setSessionId(det.session_id);
    setContextCq(null);
    // NOT: `note` bir raporun VARLIĞINI dışlamaz (Faz 1.5 — konu-değişimi cevapları hem
    // `note` hem gerçek `result` taşıyabilir, KPI kartlarıyla aynı desen). "Son rapor" =
    // gerçek sonuç taşıyan (ya da KPI) SON mesaj, notu olsun ya da olmasın.
    const lastReport = msgs.find((m) => m.result || m.kpi) ?? null;
    setActive(lastReport);
    setCanvasItems([]); // tuval sohbet-oturumu kapsamlı — devralınan sohbette sıfırdan başlar
    setViewHint(lastReport?.view_hint ? { kind: lastReport.view_hint, nonce: Date.now() } : null);
    setPrevSql(lastReport?.sql || null);
    setStarted(true);
    setDrawer(null);
  };

  const newChat = () => {
    setSessionId(makeSessionId());
    clearHistory();
    setActive(null);
    setContextCq(null);
    setPrevSql(null);
    setCanvasItems([]); // tuval sohbet-oturumu kapsamlı — yeni sohbet sıfırdan başlar
    setStarted(false);
    setDrawer(null);
  };

  // Faz 4.12 (1 Ağustos 2026) — dış yol haritası 2.9 "canlı düşünme adımları": backend
  // Discovery'yi arka-plana kuyrukladıysa (ask_async_discovery bayrağı) api-client.ts
  // bunu poll ederken biriken adımları BURAYA iletir; ChatPanel statik "yürütülüyor…"
  // yerine SON adımı gösterir. Bayrak kapalıyken (varsayılan) callback hiç tetiklenmez.
  const [liveTrace, setLiveTrace] = useState<string[]>([]);

  const mutation = useMutation<AskResponse, unknown, { question: string }>({
    mutationFn: ({ question }) => {
      setLiveTrace([]);
      return ask(
        {
          question,
          cube_query: contextCq,
          prev_sql: prevSql,
          history: items.map((i) => i.question).slice(0, 8),
          session_id: sessionId,
        },
        setLiveTrace,
      );
    },
    onSuccess: (data) => {
      addHistory(data);
      // Rapor → sağ paneli güncelle; salt-not (result YOK) → mevcut raporu koru. `note`'un
      // VARLIĞI tek başına raporu göstermeyi engellemez (Faz 1.5 — konu-değişimi cevapları
      // hem `note` hem gerçek `result` taşır, "Konu değişti: X → Y"; KPI yanıtı da NOT
      // taşısa bir RAPORDUR — aynı desenin bir örneği, aşağıya genelleştirildi).
      if (data.result || data.kpi) setActive(data);
      addToCanvas(data); // Faz 4.11 — tuval modu açıksa üste EKLENİR (active'i değiştirmez)
      // Görünüm ipucu: yeni raporla geldiyse onunla; salt-görünüm yanıtında mevcut rapora.
      if (data.view_hint) setViewHint({ kind: data.view_hint, nonce: Date.now() });
      else if (data.result) setViewHint(null);
      // Bağlam: rapor ya da clarify (kısmi cube_query) her ikisi de bir sonraki mesaj için.
      setContextCq(data.cube_query ?? null);
      // wren_sql takip bağlamı: sql yoksa (meta/katalog/hata notu) bir sonraki soru
      // bağlamsız (fresh) sayılır — stale SQL'e "düzenleme" uygulanmaz.
      setPrevSql(data.sql || null);
      qc.invalidateQueries({ queryKey: ["conversations"] }); // geçmiş listesi tazelensin
    },
  });

  const submit = (q: string) => {
    setDrawer(null);
    setStarted(true); // ilk sorudan sonra çalışma alanında kal (hata olsa da landing'e dönme)
    setVerifyLabel(q); // gerçek kullanıcı sorusu — verify etiketi bu olur
    mutation.mutate({ question: q });
  };

  // Yorum çubuğu chip düzenlemesi → deterministik /cube (LLM yok); transkripte de düşer.
  const cubeMutation = useMutation<AskResponse, unknown, { cq: NonNullable<AskResponse["cube_query"]>; label: string }>({
    mutationFn: ({ cq, label }) => askCube({ cube_query: cq, label, session_id: sessionId }),
    onSuccess: (data) => {
      addHistory(data);
      setActive(data);
      addToCanvas(data); // Faz 4.11 — chip/sonraki-adım/öneri tıklaması da tuvale eklenir
      // chip düzenlemesi RAPOR ŞEKLİNİ küçük değiştirir — mevcut görünüm tercihi
      // (ör. panelli) KORUNUR; yeni ipucu yalnız /ask cevabından gelir.
      setContextCq(data.cube_query ?? null);
      // /cube deterministik cube_query akışıdır — wren_sql takip bağlamıyla ilgisiz;
      // bir sonraki /ask sıfırdan (fresh) başlasın diye temizlenir.
      setPrevSql(null);
    },
  });

  // Chat-scoped Excel/CSV yükleme (base modu) → dataset hazır notu + örnek sorgular sohbete düşer.
  const uploadMut = useMutation<import("@/lib/types").UploadResponse, unknown, File>({
    mutationFn: async (file) =>
      uploadDataset({
        session_id: sessionId,
        filename: file.name,
        content_b64: await fileToBase64(file),
      }),
    onSuccess: (r, file) => {
      setStarted(true);
      setContextCq(null); // yeni veri kaynağı — eski cube bağlamı düşer
      setPrevSql(null); // yeni veri kaynağı — eski wren_sql takip bağlamı da düşer
      const cols = r.columns.map((c) => c.orig).join(", ");
      addHistory({
        question: `📎 ${file.name}`,
        sql: "",
        result: null,
        source: null,
        cube_query: null,
        note: `"${r.dataset}" yüklendi — ${r.row_count.toLocaleString("tr-TR")} satır. ` +
          `Kolonlar: ${cols}. Örnek sorularla başlayın:`,
        suggestions: r.suggestions,
        trace: [] as string[],
      } as unknown as AskResponse);
    },
  });
  const onUpload = (file: File) => uploadMut.mutate(file);

  const started = startedLatch || items.length > 0 || mutation.isPending || uploadMut.isPending;
  const pendingQuestion = mutation.isPending ? mutation.variables?.question : undefined;

  return (
    // pr-12: sağdaki kalıcı ikon kolonu (rail) içeriği örtmesin.
    <div className="h-full pr-12">
      {openDashboard ? (
        <DashboardView id={openDashboard} onClose={() => setOpenDashboard(null)} />
      ) : !started ? (
        <Landing onSubmit={submit} onUpload={onUpload} uploading={uploadMut.isPending} />
      ) : (
        <div className="flex h-full min-h-0">
          <section
            data-no-print
            className="flex w-[38%] min-w-[320px] max-w-[440px] shrink-0 flex-col border-r border-hairline"
          >
            <ChatPanel
              items={items}
              active={active}
              pending={mutation.isPending}
              pendingQuestion={pendingQuestion}
              liveTrace={liveTrace}
              contextLabel={contextCq ? String(contextCq.cube ?? "rapor") : null}
              onClearContext={() => setContextCq(null)}
              onSelect={(item) => {
                setActive(item);
                setContextCq(item.cube_query ?? null); // seçilen rapor bağlam olur
                setPrevSql(item.sql || null); // wren_sql takibi de seçilen rapordan devam eder
                // Seçilen mesajın KENDİ görünüm ipucunu geri yükle (ör. "facet:kumas_cinsi")
                // — aksi halde sayfa-seviyesi viewHint eski/başka bir mesajdan kalıp yanlış
                // görünümü zorlar (Faz 1.5'in "hangi kırılıma göre" chip akışı bunu sıklaştırdı).
                setViewHint(item.view_hint ? { kind: item.view_hint, nonce: Date.now() } : null);
                if (!item.question.startsWith("chip:")) setVerifyLabel(item.question);
              }}
              onSubmit={submit}
              onUpload={onUpload}
              uploading={uploadMut.isPending}
            />
          </section>
          <section className="flex min-w-0 flex-1 flex-col overflow-auto">
            <div
              data-no-print
              className="flex shrink-0 items-center justify-end gap-2 border-b border-hairline px-3 py-1.5"
            >
              {/* Kullanıcı tuval moduna GEÇ bir noktada geçmiş olabilir — ekrandaki mevcut
                  raporu (soru/chip/geçmiş-seçimi FARK ETMEKSİZİN) elle de ekleyebilsin, yalnız
                  otomatik-eklemenin (chip/sonraki-adım) başladığı ANDAN sonrasına bağlı kalmasın. */}
              {canvasMode && active && (active.result || active.kpi) && (
                <button
                  onClick={() =>
                    setCanvasItems((prev) => (prev[prev.length - 1] === active ? prev : [...prev, active]))
                  }
                  title="Ekrandaki mevcut raporu tuvale ekle"
                  className="flex h-[22px] items-center border border-hairline px-2 font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent"
                >
                  + şu anki raporu ekle
                </button>
              )}
              <button
                onClick={() => setCanvasMode((m) => !m)}
                title="Tıklanan sonraki-adım/öneri raporlarını biriktiren, sürükle-sıralanabilir ek görünüm"
                className={`flex h-[22px] items-center border px-2 font-mono text-[11px] transition-colors ${
                  canvasMode
                    ? "border-accent/40 text-accent"
                    : "border-hairline text-neutral-400 hover:text-foreground"
                }`}
              >
                🗂 tuval{canvasItems.length > 0 ? ` (${canvasItems.length})` : ""}
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-auto">
              {canvasMode ? (
                <AnalysisCanvas
                  items={canvasItems}
                  onReorder={reorderCanvas}
                  onRemove={removeFromCanvas}
                  onClear={() => setCanvasItems([])}
                />
              ) : (
                <ReportPanel
                  data={active}
                  pending={mutation.isPending || cubeMutation.isPending}
                  viewHint={viewHint}
                  onCubeEdit={({ cq, label }) => cubeMutation.mutate({ cq, label })}
                  error={mutation.isError ? apiErrorMessage(mutation.error) : null}
                  verifyLabel={verifyLabel}
                  sessionId={sessionId}
                />
              )}
            </div>
          </section>
        </div>
      )}

      {/* Aynı ikona ikinci tıklama sheet'i KAPATIR (toggle); farklıysa içerik değişir. */}
      <FloatingControls
        onHistory={() => setDrawer((d) => (d === "history" ? null : "history"))}
        onNotifications={() => setDrawer((d) => (d === "notifications" ? null : "notifications"))}
        onDashboards={
          dashStage
            ? () => setDrawer((d) => (d === "dashboards" ? null : "dashboards"))
            : undefined
        }
        onReview={canReview ? () => router.push("/review") : undefined}
        onHelp={() => setDrawer((d) => (d === "help" ? null : "help"))}
        onSettings={() => setDrawer((d) => (d === "settings" ? null : "settings"))}
      />

      <SettingsDrawer
        open={drawer !== null}
        onClose={() => setDrawer(null)}
        title={
          drawer === "help"
            ? "dima · yardım"
            : drawer === "notifications"
              ? "Bildirimler"
              : drawer === "history"
                ? "Sohbet Geçmişi"
                : drawer === "dashboards"
                  ? "Panolar"
                  : "Ayarlar · Veri Modeli"
        }
      >
        {drawer === "help" ? (
          <HelpPanel onPick={submit} />
        ) : drawer === "notifications" ? (
          <NotificationsPanel />
        ) : drawer === "history" ? (
          <HistoryPanel
            onResume={resumeConversation}
            onNewChat={newChat}
            activeSessionId={sessionId}
          />
        ) : drawer === "dashboards" ? (
          <DashboardsPanel
            onOpen={(id) => {
              setOpenDashboard(id);
              setDrawer(null);
            }}
          />
        ) : (
          <div>
            <div className="mb-4 flex gap-1 border-b border-hairline text-xs">
              <button
                onClick={() => setSettingsTab("sema")}
                className={`px-3 py-2 ${settingsTab === "sema" ? "border-b-2 border-accent text-foreground" : "text-muted"}`}
              >
                Şema
              </button>
              <button
                onClick={() => setSettingsTab("baglanti")}
                className={`px-3 py-2 ${settingsTab === "baglanti" ? "border-b-2 border-accent text-foreground" : "text-muted"}`}
              >
                Veri Kaynağı Bağla
              </button>
            </div>
            {settingsTab === "sema" ? <SchemaPanel /> : <ConnectionReviewPanel />}
          </div>
        )}
      </SettingsDrawer>
    </div>
  );
}
