"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { apiErrorMessage, ask, askCube, getConversation, uploadDataset } from "@/lib/api-client";
import { ChatPanel } from "@/components/ChatPanel";
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
  // Görünüm ipucu ("grafik ver") — sağ paneldeki raporun görünümünü değiştirir.
  const [viewHint, setViewHint] = useState<{ kind: string; nonce: number } | null>(null);
  const [drawer, setDrawer] = useState<Drawer>(null);
  // Açık pano (main-area overlay) — set ise chat/rapor yerine pano grid'i gösterilir (§9).
  const [openDashboard, setOpenDashboard] = useState<string | null>(null);
  const dashStage = useFeature("dashboards");
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

  // Resume: kayıtlı sohbeti yükle — mesajlar (seq eski→yeni) store'a newest-first konur;
  // session_id o sohbete geçer (takip soruları aynı sohbete eklenir).
  const resumeConversation = async (id: string) => {
    const det = await getConversation(id);
    const msgs = [...det.messages].reverse(); // seq artan → store newest-first
    loadHistory(msgs);
    setSessionId(det.session_id);
    setContextCq(null);
    const lastReport = msgs.find((m) => (m.result && !m.note) || m.kpi) ?? null;
    setActive(lastReport);
    setStarted(true);
    setDrawer(null);
  };

  const newChat = () => {
    setSessionId(makeSessionId());
    clearHistory();
    setActive(null);
    setContextCq(null);
    setStarted(false);
    setDrawer(null);
  };

  const mutation = useMutation<AskResponse, unknown, { question: string }>({
    mutationFn: ({ question }) =>
      ask({
        question,
        cube_query: contextCq,
        history: items.map((i) => i.question).slice(0, 8),
        session_id: sessionId,
      }),
    onSuccess: (data) => {
      addHistory(data);
      // Rapor → sağ paneli güncelle; salt-not → mevcut raporu koru. KPI yanıtı NOT taşısa
      // da bir RAPORDUR (kart+trend) — sağ panele düşmeli (yoksa kart hiç render edilmezdi).
      if (!data.note || data.kpi) setActive(data);
      // Görünüm ipucu: yeni raporla geldiyse onunla; salt-görünüm yanıtında mevcut rapora.
      if (data.view_hint) setViewHint({ kind: data.view_hint, nonce: Date.now() });
      else if (data.result && !data.note) setViewHint(null);
      // Bağlam: rapor ya da clarify (kısmi cube_query) her ikisi de bir sonraki mesaj için.
      setContextCq(data.cube_query ?? null);
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
      // chip düzenlemesi RAPOR ŞEKLİNİ küçük değiştirir — mevcut görünüm tercihi
      // (ör. panelli) KORUNUR; yeni ipucu yalnız /ask cevabından gelir.
      setContextCq(data.cube_query ?? null);
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
          <section className="flex w-[38%] min-w-[320px] max-w-[440px] shrink-0 flex-col border-r border-hairline">
            <ChatPanel
              items={items}
              active={active}
              pending={mutation.isPending}
              pendingQuestion={pendingQuestion}
              contextLabel={contextCq ? String(contextCq.cube ?? "rapor") : null}
              onClearContext={() => setContextCq(null)}
              onSelect={(item) => {
                setActive(item);
                setContextCq(item.cube_query ?? null); // seçilen rapor bağlam olur
                if (!item.question.startsWith("chip:")) setVerifyLabel(item.question);
              }}
              onSubmit={submit}
              onUpload={onUpload}
              uploading={uploadMut.isPending}
            />
          </section>
          <section className="min-w-0 flex-1 overflow-auto">
            <ReportPanel
              data={active}
              pending={mutation.isPending || cubeMutation.isPending}
              viewHint={viewHint}
              onCubeEdit={({ cq, label }) => cubeMutation.mutate({ cq, label })}
              error={mutation.isError ? apiErrorMessage(mutation.error) : null}
              verifyLabel={verifyLabel}
              sessionId={sessionId}
            />
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
          <SchemaPanel />
        )}
      </SettingsDrawer>
    </div>
  );
}
