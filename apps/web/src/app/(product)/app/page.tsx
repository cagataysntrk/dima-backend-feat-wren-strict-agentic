"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiErrorMessage, ask, askCube, uploadDataset } from "@dima/api-client";
import { markThinking } from "@/lib/thinking";
import { markAttachments } from "@/lib/attachments";
import { isDatasetFile, markDataset } from "@/lib/dataset";
import { AppShell } from "@/components/shell/AppShell";
import { ChatPanel } from "@/components/ChatPanel";
import { HelpPanel } from "@/components/HelpPanel";
import { Landing } from "@/components/Landing";
import { AttachmentsPanel } from "@/components/shell/AttachmentsPanel";
import { SourcesPanel } from "@/components/shell/SourcesPanel";
import { ChatPanelsPanel } from "@/components/shell/ChatPanelsPanel";
import { PANEL_TABS, type PanelTab } from "@/components/shell/ArtifactPanel";
import { SearchDialog } from "@/components/shell/SearchDialog";
import { ShortcutsDialog } from "@/components/shell/ShortcutsDialog";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { selectActive, useConversations } from "@/stores/conversations";
import type { AskResponse, UploadResponse } from "@dima/contracts";

// Panel sekmeleri artık tek kaynaktan (ArtifactPanel.PANEL_TABS).
type Artifact = PanelTab | null;

const PANEL_IDS: readonly PanelTab[] = PANEL_TABS.map((t) => t.id);

export default function AppPage() {
  const [active, setActive] = useState<AskResponse | null>(null);
  // Takip bağlamı: bir sonraki mesajla gönderilecek CubeQuery (ADR-0007 Faz C).
  const [contextCq, setContextCq] = useState<AskResponse["cube_query"]>(null);
  const [verifyLabel, setVerifyLabel] = useState<string | null>(null);
  // İkincil sayfalardan (/settings, /chats) bir panel girişine basılınca buraya
  // ?panel=... ile dönülür. Yalnız AÇILIŞTA anlamlı olduğu için effect değil
  // lazy başlangıç değeri (effect içinde setState zincirleme render yapar).
  const panelParam = useSearchParams().get("panel");
  const [artifact, setArtifact] = useState<Artifact>(() =>
    PANEL_IDS.includes(panelParam as PanelTab) ? (panelParam as PanelTab) : null,
  );
  // Panel düğmesi neyi geri açacağını bilsin (yardım DEĞİL — yardımın kendi
  // menü girişi var). Sekme şeridi de kapalıyken hangi sekmenin seçili
  // görüneceğini buradan okur, o yüzden ref değil state.
  const [lastArtifact, setLastArtifact] = useState<PanelTab>("panels");
  const router = useRouter();
  const [helpOpen, setHelpOpen] = useState(false);
  // Sağ panelden seçilen sonuç — sohbette o karta kaydırılır.
  const [focus, setFocus] = useState<{ item: AskResponse; nonce: number } | null>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);

  const activeConv = useConversations(selectActive);
  const incognito = useConversations((st) => st.incognito);
  const incognitoItems = useConversations((st) => st.incognitoItems);
  // Gizli modda konuşma kalıcı listeye hiç yazılmaz — ayrı bir tamponda yaşar.
  const items = incognito ? incognitoItems : (activeConv?.items ?? []);

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
  // Gönderilen ekler — yanıt gelince o mesaja iliştirilir (lib/attachments.ts).
  const sentFiles = useRef<File[]>([]);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);

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
    // Hata artık sağ panelde gösterilemiyor (rapor sekmesi kalktı) — geçici bir
    // başarısızlığın doğru yeri zaten toast: sohbet akışını bozmadan görünür.
    onError: (error) => toast.error(apiErrorMessage(error)),
    onSuccess: (data) => {
      markThinking(data, Date.now() - askedAt.current);
      markAttachments(data, sentFiles.current);
      sentFiles.current = [];
      setPendingFiles([]);
      useConversations.getState().add(data);
      // Rapor artık sohbetin içinde yaşıyor — sağ paneli KENDİLİĞİNDEN açmıyoruz
      // (panel Yardım/Veri kaynakları ve ileride dashboard'lar için ayrıldı).
      // KPI yanıtı NOT taşısa da bir RAPORDUR (kart+trend) → aktif rapor olmalı.
      if (!data.note || data.kpi) setActive(data);
      setContextCq(data.cube_query ?? null);
    },
  });

  // Yükleme sohbetin bir OLAYIdır: dosya /ask/upload'a gider, dönen çıkarım
  // (kolonlar + örnek sorular) kendi turu olarak akışa düşer. Böylece "kurulum =
  // konuşma" (D1) gerçekten sohbetin içinde oluyor, ayrı bir sihirbaz ekranında
  // değil. Yükleme BİTMEDEN soru gönderilmez — aksi halde soru henüz var olmayan
  // tabloyu sorardı.
  const uploadMutation = useMutation<
    { res: UploadResponse; name: string },
    unknown,
    { file: File; sessionId: string }
  >({
    mutationFn: async ({ file, sessionId }) => ({
      res: await uploadDataset(file, sessionId),
      name: file.name,
    }),
    onError: (error) => toast.error(apiErrorMessage(error)),
    onSuccess: ({ res, name }) => {
      // Yükleme turu AskResponse şeklinde taşınır (sohbet tek tip item tutar);
      // çıkarım detayı yan kanalda (lib/dataset.ts) — sözleşme kirlenmez.
      const item: AskResponse = {
        question: name,
        sql: "",
        planned_sql: null,
        result: null,
        source: "cube",
        cube_query: null,
        note: null,
        trace: [],
        suggestions: [],
        view_hint: null,
        contract_id: null,
      };
      markDataset(item, res);
      useConversations.getState().add(item);
      setActive(null);
    },
  });

  const submit = (q: string, files: File[] = []) => {
    const sessionId = ensureSessionId();
    // Tablolaşabilen dosyalar YÜKLENİR; diğerleri eskisi gibi mesaja iliştirilir.
    const datasets = files.filter(isDatasetFile);
    const rest = files.filter((f) => !isDatasetFile(f));

    const run = () => {
      if (!q.trim()) return;
      setVerifyLabel(q);
      sentFiles.current = rest;
      setPendingFiles(rest);
      mutation.mutate({ question: q, sessionId });
    };

    if (datasets.length === 0) return run();
    // Sırayla yükle (oturum DuckDB'si aynı; paralel ingest yarışa girer), sonra sor.
    void datasets
      .reduce(
        (chain, file) => chain.then(() => uploadMutation.mutateAsync({ file, sessionId })),
        Promise.resolve() as Promise<unknown>,
      )
      .then(run)
      .catch(() => {});
  };

  const cubeMutation = useMutation<AskResponse, unknown, { cq: NonNullable<AskResponse["cube_query"]>; label: string }>({
    mutationFn: ({ cq, label }) =>
      askCube({ cube_query: cq, label, session_id: ensureSessionId() }),
    onError: (error) => toast.error(apiErrorMessage(error)),
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

  const started = items.length > 0 || mutation.isPending || cubeMutation.isPending || uploadMutation.isPending;
  // Chip düzenlemeleri de bekleme durumu gösterir — aksi halde × basınca hiçbir
  // şey olmuyormuş gibi duruyordu (canlı geri bildirim 2026-07-26).
  const pendingQuestion = mutation.isPending
    ? mutation.variables?.question
    : cubeMutation.isPending
      ? cubeMutation.variables?.label
      : undefined;

  // Sağ panel YALNIZ AÇIK SOHBET hakkında: kaynaklar (veri nereden geldi) ve
  // belgeler (bu sohbetin ekleri/çıktıları). Veri kataloğu, kayıtlı panolar ve
  // yardım hesap kapsamlı sayfalara taşındı — sol kenar çubuğundan açılırlar.
  const artifactContent =
    artifact === "panels" ? (
      <ChatPanelsPanel
        items={items}
        sessionId={activeConv?.sessionId}
        onCubeEdit={({ cq, label }) => cubeMutation.mutate({ cq, label })}
        onFocus={(item) => {
          setActive(item);
          // aynı panele ikinci kez basmak da kaydırsın → nonce
          setFocus({ item, nonce: Date.now() });
        }}
      />
    ) : artifact === "sources" ? (
      <SourcesPanel
        items={items}
        onRerun={({ cq, label }) => cubeMutation.mutate({ cq, label })}
      />
    ) : artifact === "attachments" ? (
      <AttachmentsPanel items={items} conversationId={activeConv?.id} />
    ) : null;

  return (
    <>
    <ShortcutsDialog open={shortcutsOpen} onOpenChange={setShortcutsOpen} />
    {/* Yardım artık sağ panelde DEĞİL: sağ panel yalnız açık sohbet hakkında,
        yardım ise sohbetten bağımsız. Diyalog olarak her yerden açılabilir. */}
    <Dialog open={helpOpen} onOpenChange={setHelpOpen}>
      <DialogContent className="max-h-[85svh] overflow-auto sm:max-w-lg">
        <DialogTitle className="sr-only">dima · yardım</DialogTitle>
        <HelpPanel
          onPick={(q) => {
            setHelpOpen(false);
            submit(q);
          }}
        />
      </DialogContent>
    </Dialog>
    <SearchDialog
      open={searchOpen}
      onOpenChange={setSearchOpen}
      onNewChat={newChat}
      onSelectConversation={selectConversation}
      onOpenSchema={() => router.push("/data-sources")}
      onOpenHelp={() => setHelpOpen(true)}
    />
    <AppShell
      onNewChat={newChat}
      onSelectConversation={selectConversation}
      onOpenHelp={() => setHelpOpen(true)}
      onOpenShortcuts={() => setShortcutsOpen(true)}
      onOpenSearch={() => setSearchOpen(true)}
      onToggleArtifact={() =>
        setArtifact((a) => {
          if (a) {
            setLastArtifact(a);
            return null;
          }
          return lastArtifact;
        })
      }
      started={started}
      artifactOpen={artifact !== null}
      artifactTab={artifact ?? lastArtifact}
      onArtifactTabChange={setArtifact}
      onArtifactClose={() => setArtifact(null)}
      artifact={artifactContent}
    >
      {!started ? (
        <Landing onSubmit={submit} />
      ) : (
        <ChatPanel
          items={items}
          active={active}
          pending={mutation.isPending || cubeMutation.isPending || uploadMutation.isPending}
          pendingQuestion={pendingQuestion}
          pendingFiles={pendingFiles}
          conversationId={incognito ? "incognito" : activeConv?.id}
          onSelect={(item) => {
            setActive(item);
            setArtifact("panels");
            setContextCq(item.cube_query ?? null);
            if (!item.question.startsWith("chip:")) setVerifyLabel(item.question);
          }}
          onSubmit={submit}
          onCubeEdit={({ cq, label }) => cubeMutation.mutate({ cq, label })}
          verifyLabel={verifyLabel}
          sessionId={activeConv?.sessionId ?? ""}
          focus={focus}
        />
      )}
    </AppShell>
    </>
  );
}
