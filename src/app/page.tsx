"use client";

import { useMutation } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { apiErrorMessage, ask, askCube } from "@/lib/api-client";
import { markThinking } from "@/lib/thinking";
import { AppShell } from "@/components/shell/AppShell";
import { ChatPanel } from "@/components/ChatPanel";
import { HelpPanel } from "@/components/HelpPanel";
import { Landing } from "@/components/Landing";
import { ReportPanel } from "@/components/ReportPanel";
import { SchemaPanel } from "@/components/SchemaPanel";
import { SearchDialog } from "@/components/shell/SearchDialog";
import { selectActive, useConversations } from "@/stores/conversations";
import type { AskResponse } from "@/lib/types";

type Artifact = "report" | "schema" | "help" | null;

export default function Home() {
  const [active, setActive] = useState<AskResponse | null>(null);
  // Takip bağlamı: bir sonraki mesajla gönderilecek CubeQuery (ADR-0007 Faz C).
  const [contextCq, setContextCq] = useState<AskResponse["cube_query"]>(null);
  const [viewHint, setViewHint] = useState<{ kind: string; nonce: number } | null>(null);
  const [verifyLabel, setVerifyLabel] = useState<string | null>(null);
  const [artifact, setArtifact] = useState<Artifact>(null);
  const [searchOpen, setSearchOpen] = useState(false);

  const activeConv = useConversations(selectActive);
  const items = activeConv?.items ?? [];

  // Aktif konuşmanın oturum kimliğini garanti et (yoksa yeni konuşma aç).
  function ensureSessionId(): string {
    const state = useConversations.getState();
    let conv = selectActive(state);
    if (!conv) {
      state.newConversation();
      conv = selectActive(useConversations.getState());
    }
    return conv!.sessionId;
  }

  // Düşünme süresi ölçümü — cevabın yanında kalan "N sn düşündü" bloğu için.
  const askedAt = useRef(0);

  const mutation = useMutation<AskResponse, unknown, { question: string; sessionId: string }>({
    mutationFn: ({ question, sessionId }) =>
      ask({
        question,
        cube_query: contextCq,
        history: items.map((i) => i.question).slice(0, 8),
        session_id: sessionId,
      }),
    onMutate: () => {
      askedAt.current = Date.now();
    },
    onSuccess: (data) => {
      markThinking(data, Date.now() - askedAt.current);
      useConversations.getState().add(data);
      // Rapor artık sohbetin içinde yaşıyor — sağ paneli KENDİLİĞİNDEN açmıyoruz
      // (panel Yardım/Veri kaynakları ve ileride dashboard'lar için ayrıldı).
      // KPI yanıtı NOT taşısa da bir RAPORDUR (kart+trend) → aktif rapor olmalı.
      if (!data.note || data.kpi) setActive(data);
      if (data.view_hint) setViewHint({ kind: data.view_hint, nonce: Date.now() });
      else if (data.result && !data.note) setViewHint(null);
      setContextCq(data.cube_query ?? null);
    },
  });

  const submit = (q: string) => {
    const sessionId = ensureSessionId();
    setVerifyLabel(q);
    mutation.mutate({ question: q, sessionId });
  };

  const cubeMutation = useMutation<AskResponse, unknown, { cq: NonNullable<AskResponse["cube_query"]>; label: string }>({
    mutationFn: ({ cq, label }) =>
      askCube({ cube_query: cq, label, session_id: ensureSessionId() }),
    onSuccess: (data) => {
      useConversations.getState().add(data);
      setActive(data);
      setContextCq(data.cube_query ?? null);
    },
  });

  function newChat() {
    useConversations.getState().newConversation();
    setActive(null);
    setContextCq(null);
    setArtifact(null);
    setVerifyLabel(null);
  }

  function selectConversation(id: string) {
    useConversations.getState().select(id);
    setActive(null);
    setContextCq(null);
    setArtifact(null);
  }

  const started = items.length > 0 || mutation.isPending;
  const pendingQuestion = mutation.isPending ? mutation.variables?.question : undefined;

  const artifactTitle =
    artifact === "schema"
      ? "Veri modeli"
      : artifact === "help"
        ? "dima · yardım"
        : active?.question
          ? active.question.slice(0, 60)
          : "Rapor";

  const artifactContent =
    artifact === "schema" ? (
      <SchemaPanel />
    ) : artifact === "help" ? (
      <HelpPanel onPick={submit} />
    ) : artifact === "report" ? (
      <ReportPanel
        data={active}
        pending={mutation.isPending || cubeMutation.isPending}
        viewHint={viewHint}
        error={mutation.isError ? apiErrorMessage(mutation.error) : null}
      />
    ) : null;

  return (
    <>
    <SearchDialog
      open={searchOpen}
      onOpenChange={setSearchOpen}
      onNewChat={newChat}
      onSelectConversation={selectConversation}
      onOpenSchema={() => setArtifact("schema")}
      onOpenHelp={() => setArtifact("help")}
    />
    <AppShell
      onNewChat={newChat}
      onSelectConversation={selectConversation}
      onOpenSchema={() => setArtifact("schema")}
      onOpenHelp={() => setArtifact("help")}
      onOpenSearch={() => setSearchOpen(true)}
      onToggleArtifact={() => setArtifact((a) => (a ? null : "help"))}
      artifactOpen={artifact !== null}
      artifactTitle={artifactTitle}
      onArtifactClose={() => setArtifact(null)}
      artifact={artifactContent}
    >
      {!started ? (
        <Landing onSubmit={submit} />
      ) : (
        <ChatPanel
          items={items}
          active={active}
          pending={mutation.isPending}
          pendingQuestion={pendingQuestion}
          onSelect={(item) => {
            setActive(item);
            setArtifact("report");
            setContextCq(item.cube_query ?? null);
            if (!item.question.startsWith("chip:")) setVerifyLabel(item.question);
          }}
          onSubmit={submit}
          onCubeEdit={({ cq, label }) => cubeMutation.mutate({ cq, label })}
          verifyLabel={verifyLabel}
          sessionId={activeConv?.sessionId ?? ""}
        />
      )}
    </AppShell>
    </>
  );
}
