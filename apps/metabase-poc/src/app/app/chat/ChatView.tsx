"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { BarChart3, Code2, Database, PanelRight, Save, X } from "lucide-react";
import { toast } from "sonner";
import { ThinkingOrb } from "thinking-orbs";
import { gateway, type ChatAnswer, type ChatTurn } from "@/lib/gateway";
import { cn } from "@/lib/utils";
import { useConversations, type Entry } from "@/stores/conversations";
import { TopbarActions } from "@/components/shell/AppShell";
import { Composer } from "@/components/chat/Composer";
import { AddToDashboard } from "@/components/analytics/DashboardActions";
import { ResultView } from "@/components/ResultView";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

// Suggested first questions per company (org slug); generic fallback otherwise.
const STARTERS: Record<string, string[]> = {
  boyahane: [
    "Geçen yıl en yüksek cirolu 5 müşteri kim?",
    "Aylık üretim nasıl bir trend izliyor?",
    "Hangi makinede en çok duruş var ve neden?",
    "Makine bazında ortalama OEE nedir?",
  ],
  tenant2: [
    "Aylık fatura tutarı nasıl değişiyor?",
    "Fatura türlerine göre toplam tutar nedir?",
    "Stok hareketlerinde en çok hangi hareket tipi var?",
    "Cari tipine göre borç ve alacak dağılımı nedir?",
  ],
};
const GENERIC = ["Elimde hangi veriler var?", "Son 12 ayın özetini çıkar.", "En önemli 5 göstergeyi listele."];

type Done = Extract<Entry, { status: "done" }>;

/** Below lg the right panel is a slide-over sheet: a docked panel would squeeze the chat column. */
function useIsNarrow() {
  return useSyncExternalStore(
    (cb) => {
      const mq = window.matchMedia("(max-width: 1023px)");
      mq.addEventListener("change", cb);
      return () => mq.removeEventListener("change", cb);
    },
    () => window.matchMedia("(max-width: 1023px)").matches,
    () => false,
  );
}

/** True once the persisted chat history has been loaded into the store. */
function useHydrated() {
  return useSyncExternalStore(
    (cb) => useConversations.persist.onFinishHydration(cb),
    () => useConversations.persist.hasHydrated(),
    () => false,
  );
}

export function ChatView({
  company,
  orgId,
  slug,
  configured,
  canSave,
}: {
  company: string;
  orgId: string;
  slug: string;
  configured: boolean;
  canSave: boolean;
}) {
  const router = useRouter();
  const convId = useSearchParams().get("c");
  const hydrated = useHydrated();
  const conv = useConversations((s) => s.conversations.find((c) => c.id === convId && c.orgId === orgId));
  const { create, addEntry, settle } = useConversations.getState();
  const [draft, setDraft] = useState("");
  const [panelOpen, setPanelOpen] = useState(false);
  const [tab, setTab] = useState<PanelTab>("results");
  const bottom = useRef<HTMLDivElement>(null);

  const entries = conv?.entries ?? [];
  const pending = entries.some((e) => e.status === "pending");
  const started = entries.length > 0;
  const starters = STARTERS[slug] ?? GENERIC;

  // An unknown / other-company chat id falls back to a fresh chat.
  useEffect(() => {
    if (hydrated && convId && !conv) router.replace("/app/chat");
  }, [hydrated, convId, conv, router]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [entries.length, pending]);

  const submit = (text: string) => {
    const question = text.trim();
    if (!question || pending || !configured) return;
    // Prior turns as plain text: question, answer and the SQL behind it, so
    // follow-ups ("only for RAM-1") can build on the previous query.
    const history: ChatTurn[] = entries.flatMap((e) =>
      e.status === "done"
        ? [
            { role: "user" as const, content: e.question },
            {
              role: "assistant" as const,
              content: e.reply.sql ? `${e.reply.answer}\n\n[query used]\n${e.reply.sql}` : e.reply.answer,
            },
          ]
        : [],
    );
    const id = conv ? conv.id : create(orgId);
    if (!conv) router.replace(`/app/chat?c=${id}`);
    const entryId = addEntry(id, question);
    setDraft("");
    gateway
      .chat([...history, { role: "user", content: question }])
      .then((reply) => settle(id, entryId, { id: entryId, question, status: "done", reply }))
      .catch((err: Error) => settle(id, entryId, { id: entryId, question, status: "error", message: err.message }));
  };

  const scrollTo = (entryId: number) =>
    document.getElementById(`entry-${entryId}`)?.scrollIntoView({ behavior: "smooth", block: "start" });

  return (
    <div className="flex h-full min-h-0">
      {started && (
        <TopbarActions>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label="Sohbet paneli"
                aria-pressed={panelOpen}
                onClick={() => setPanelOpen((o) => !o)}
                className={cn("text-muted-foreground hover:text-foreground", panelOpen && "bg-accent text-foreground")}
              >
                <PanelRight className="size-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">Sohbet paneli</TooltipContent>
          </Tooltip>
        </TopbarActions>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        {!started ? (
          <div className="flex min-h-0 flex-1 flex-col items-center overflow-y-auto px-4 py-6">
            <div className="my-auto w-full max-w-2xl space-y-6 pb-10">
              <div className="space-y-2 text-center">
                <h1 className="text-2xl font-semibold tracking-tight">Verinize sorun</h1>
                <p className="text-sm text-muted-foreground">
                  {company ? `${company} verisi üzerinde` : "Şirket verinizde"} doğal dilde soru sorun; yanıt, grafik ve
                  kullanılan sorguyla gelsin.
                </p>
              </div>
              {!configured && (
                <p className="rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-center text-sm text-amber-700 dark:text-amber-300">
                  Sohbet servisi henüz yapılandırılmadı. Yöneticinizden anahtar tanımlamasını isteyin.
                </p>
              )}
              <Composer value={draft} onChange={setDraft} onSubmit={() => submit(draft)} disabled={!configured} hero autoFocus />
              <div className="grid gap-2 sm:grid-cols-2">
                {starters.map((s) => (
                  <button
                    key={s}
                    type="button"
                    disabled={!configured}
                    onClick={() => submit(s)}
                    className="surface surface-interactive px-4 py-3 text-left text-sm disabled:opacity-50"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            <div className="min-h-0 flex-1 overflow-y-auto">
              <div className="mx-auto max-w-3xl space-y-8 px-4 pt-2 pb-6">
                {entries.map((e) => (
                  <article key={e.id} id={`entry-${e.id}`} className="scroll-mt-4 space-y-3">
                    <div className="flex justify-end">
                      <p className="max-w-[85%] rounded-2xl rounded-br-md bg-brand px-4 py-2 text-sm text-brand-foreground">
                        {e.question}
                      </p>
                    </div>
                    {e.status === "pending" ? (
                      <div className="flex items-center gap-2.5 text-sm" role="status">
                        {/* libraries.dev thinking orb — follows the .dark class and prefers-reduced-motion on its own. */}
                        <ThinkingOrb state="searching" size={32} color="#7e38f8" aria-hidden />
                        {/* Same shimmer as apps/web's thinking text (components/ai/thinking.tsx). */}
                        <span className="dima-shimmer font-medium">Veriye bakılıyor…</span>
                      </div>
                    ) : e.status === "error" ? (
                      <p role="alert" className="text-sm text-destructive">
                        {e.message}
                      </p>
                    ) : (
                      <Reply reply={e.reply} question={e.question} canSave={canSave} />
                    )}
                  </article>
                ))}
                <div ref={bottom} />
              </div>
            </div>
            <div className="mx-auto w-full max-w-3xl px-4 pb-4">
              <Composer
                value={draft}
                onChange={setDraft}
                onSubmit={() => submit(draft)}
                disabled={!configured}
                busy={pending}
              />
            </div>
          </>
        )}
      </div>

      <ChatPanel
        open={started && panelOpen}
        onClose={() => setPanelOpen(false)}
        tab={tab}
        onTabChange={setTab}
        entries={entries.filter((e): e is Done => e.status === "done")}
        onPick={scrollTo}
      />
    </div>
  );
}

function Reply({ reply, question, canSave }: { reply: ChatAnswer; question: string; canSave: boolean }) {
  const [showSql, setShowSql] = useState(false);
  const save = useMutation({
    mutationFn: () => gateway.saveSql(question.slice(0, 120), reply.sql!),
    onSuccess: () => toast.success("Analiz kaydedildi."),
    onError: (err) => toast.error(err.message),
  });

  return (
    <div className="space-y-3">
      <p className="text-sm leading-relaxed whitespace-pre-wrap">{reply.answer}</p>
      {reply.result && reply.result.row_count > 0 && (
        <div className="surface p-5">
          <ResultView
            result={reply.result}
            meta={
              <span className="text-xs text-muted-foreground tabular-nums">
                {reply.result.row_count.toLocaleString("tr-TR")} satır
              </span>
            }
          />
        </div>
      )}
      {reply.sql && (
        <div className="flex flex-wrap items-center gap-1">
          <Button variant="ghost" size="xs" onClick={() => setShowSql((v) => !v)} aria-expanded={showSql}>
            <Code2 className="size-3.5" aria-hidden />
            {showSql ? "Sorguyu gizle" : "Sorguyu göster"}
          </Button>
          {canSave && (
            // Saves the answer as an analysis first (once), then adds that card.
            <AddToDashboard size="xs" resolveCardId={async () => (save.data ?? (await save.mutateAsync())).id} />
          )}
          {canSave && (
            <Button variant="ghost" size="xs" onClick={() => save.mutate()} disabled={save.isPending || save.isSuccess}>
              <Save className="size-3.5" aria-hidden />
              {save.isSuccess ? "Kaydedildi" : "Analiz olarak kaydet"}
            </Button>
          )}
          {save.data && (
            <Link href={`/app/cards/${save.data.id}`} className="text-xs text-brand hover:underline">
              Aç
            </Link>
          )}
        </div>
      )}
      {showSql && reply.sql && (
        <pre className="surface-inset overflow-x-auto p-3 font-mono text-xs leading-relaxed">
          {reply.sql}
        </pre>
      )}
    </div>
  );
}

// ── Right panel: about THIS chat only (apps/web ArtifactPanel pattern) ──────

const PANEL_TABS = [
  { id: "results", label: "Sonuçlar", icon: BarChart3 },
  { id: "sources", label: "Kaynaklar", icon: Database },
] as const;
type PanelTab = (typeof PANEL_TABS)[number]["id"];

const PANEL_W = "w-[min(40vw,480px,calc(100vw-44rem))]";

/** Tables referenced by a query (schema-qualified names in our generated SQL). */
function tablesIn(sql: string): string[] {
  return [...new Set([...sql.matchAll(/\b(?:from|join)\s+([a-z_][\w]*\.[a-z_][\w]*)/gi)].map((m) => m[1].split(".")[1]))];
}

function ChatPanel({
  open,
  onClose,
  tab,
  onTabChange,
  entries,
  onPick,
}: {
  open: boolean;
  onClose: () => void;
  tab: PanelTab;
  onTabChange: (t: PanelTab) => void;
  entries: Done[];
  onPick: (entryId: number) => void;
}) {
  const isNarrow = useIsNarrow();
  const body = (
    <>
      <div className="flex h-12 shrink-0 items-center justify-between gap-2 border-b px-2">
        <div role="tablist" aria-label="Panel bölümleri" className="flex items-center gap-0.5">
          {PANEL_TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={id === tab}
              onClick={() => onTabChange(id)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs transition-colors focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none",
                id === tab
                  ? "bg-accent font-medium text-foreground"
                  : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
              )}
            >
              <Icon className="size-3.5" aria-hidden />
              {label}
            </button>
          ))}
        </div>
        <Button variant="ghost" size="icon-sm" aria-label="Paneli kapat" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
        {entries.length === 0 && <p className="p-2 text-sm text-muted-foreground">Henüz sonuç yok.</p>}
        {tab === "results"
          ? entries
              .filter((e) => e.reply.result && e.reply.result.row_count > 0)
              .map((e) => (
                <button
                  key={e.id}
                  type="button"
                  onClick={() => onPick(e.id)}
                  className="surface-sm surface-interactive block w-full px-3 py-2.5 text-left"
                >
                  <span className="line-clamp-2 text-sm font-medium">{e.question}</span>
                  <span className="mt-1 block truncate text-xs text-muted-foreground">
                    {e.reply.result!.row_count.toLocaleString("tr-TR")} satır · {e.reply.result!.columns.join(", ")}
                  </span>
                </button>
              ))
          : entries
              .filter((e) => e.reply.sql)
              .map((e) => (
                <div key={e.id} className="surface-sm space-y-2 p-3">
                  <button type="button" onClick={() => onPick(e.id)} className="text-left text-sm font-medium hover:underline">
                    {e.question}
                  </button>
                  <div className="flex flex-wrap gap-1">
                    {tablesIn(e.reply.sql!).map((t) => (
                      <span key={t} className="rounded-md bg-brand/10 px-1.5 py-0.5 font-mono text-[11px] text-brand">
                        {t}
                      </span>
                    ))}
                  </div>
                  <pre className="max-h-40 overflow-auto rounded-md bg-muted/40 p-2 font-mono text-[11px] leading-relaxed">
                    {e.reply.sql}
                  </pre>
                </div>
              ))}
      </div>
    </>
  );

  if (isNarrow) {
    return (
      <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
        <SheetContent side="right" className="w-full gap-0 p-0 sm:max-w-md [&>button]:hidden">
          <SheetTitle className="sr-only">Sohbet paneli</SheetTitle>
          {body}
        </SheetContent>
      </Sheet>
    );
  }

  // Always mounted; opens/closes with a width transition like the left rail.
  return (
    <aside
      aria-hidden={!open}
      inert={!open}
      className={cn(
        "flex min-h-0 shrink-0 flex-col overflow-hidden bg-card/40 transition-[width] duration-300 ease-out motion-reduce:transition-none",
        open ? cn("border-l", PANEL_W) : "w-0",
      )}
    >
      <div className={cn("flex min-h-0 flex-1 flex-col transition-opacity duration-200", PANEL_W, open ? "opacity-100" : "opacity-0")}>
        {body}
      </div>
    </aside>
  );
}
