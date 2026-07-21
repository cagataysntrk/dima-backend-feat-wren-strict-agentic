"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { apiErrorMessage, ask, askCube } from "@/lib/api-client";
import { ChatPanel } from "@/components/ChatPanel";
import { FloatingControls } from "@/components/FloatingControls";
import { HelpPanel } from "@/components/HelpPanel";
import { Landing } from "@/components/Landing";
import { ReportPanel } from "@/components/ReportPanel";
import { SchemaPanel } from "@/components/SchemaPanel";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import { useHistory } from "@/stores/history";
import type { AskResponse } from "@/lib/types";

type Drawer = "settings" | "help" | null;

// Oturum kimliği — crypto.randomUUID yalnız güvenli bağlamda (https/localhost) var;
// http://*.localtld.sh'de yok, bu yüzden fallback.
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

export default function Home() {
  const [active, setActive] = useState<AskResponse | null>(null);
  // Takip bağlamı: bir sonraki mesajla gönderilecek CubeQuery. Rapor VE clarify notu (kısmi
  // cube_query) bunu günceller — "bu ay" chip'i doğru sorguya uygulansın (ADR-0007 Faz C).
  const [contextCq, setContextCq] = useState<AskResponse["cube_query"]>(null);
  // Görünüm ipucu ("grafik ver") — sağ paneldeki raporun görünümünü değiştirir.
  const [viewHint, setViewHint] = useState<{ kind: string; nonce: number } | null>(null);
  const [drawer, setDrawer] = useState<Drawer>(null);
  const [startedLatch, setStarted] = useState(false);
  const [sessionId] = useState(makeSessionId);
  // "✓ doğru" etiketi: raporu üreten SON GERÇEK soru (chip düzenlemeleri soru değildir —
  // "chip: kova → month" VQR'a yazılamaz; öğrenme orijinal soru metniyle anlamlı).
  const [verifyLabel, setVerifyLabel] = useState<string | null>(null);
  const items = useHistory((s) => s.items);
  const addHistory = useHistory((s) => s.add);

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
      // Rapor → sağ paneli güncelle; not → mevcut raporu koru.
      if (!data.note) setActive(data);
      // Görünüm ipucu: yeni raporla geldiyse onunla; salt-görünüm yanıtında mevcut rapora.
      if (data.view_hint) setViewHint({ kind: data.view_hint, nonce: Date.now() });
      else if (data.result && !data.note) setViewHint(null);
      // Bağlam: rapor ya da clarify (kısmi cube_query) her ikisi de bir sonraki mesaj için.
      setContextCq(data.cube_query ?? null);
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
      setViewHint(null);
      setContextCq(data.cube_query ?? null);
    },
  });

  const started = startedLatch || items.length > 0 || mutation.isPending;
  const pendingQuestion = mutation.isPending ? mutation.variables?.question : undefined;

  return (
    <div className="h-full">
      {!started ? (
        <Landing onSubmit={submit} />
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

      <FloatingControls onHelp={() => setDrawer("help")} onSettings={() => setDrawer("settings")} />

      <SettingsDrawer
        open={drawer !== null}
        onClose={() => setDrawer(null)}
        title={drawer === "help" ? "dima · yardım" : "Ayarlar · Veri Modeli"}
      >
        {drawer === "help" ? <HelpPanel onPick={submit} /> : <SchemaPanel />}
      </SettingsDrawer>
    </div>
  );
}
