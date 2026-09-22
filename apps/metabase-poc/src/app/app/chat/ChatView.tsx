"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useMutation } from "@tanstack/react-query";
import { BarChart3, Database, PanelRight, Save, X } from "lucide-react";
import { toast } from "sonner";
import { ThinkingOrb } from "thinking-orbs";
import { gateway, type ChatAnswer, type ChatTurn } from "@/lib/gateway";
import { cn } from "@dima/ui/utils";
import { useConversations, type Entry, type Step } from "@/stores/conversations";
import { LiveSteps, Thought } from "@/components/chat/Steps";
import { TopbarActions, TopbarLead } from "@/components/shell/AppShell";
import { ChatNav } from "@/components/chat/ChatNav";
import { ChatTitle } from "@/components/chat/ChatTitle";
import { Composer } from "@/components/chat/Composer";
import { Bubble, DimaAvatar, Message, MessageScroller, UserAvatar } from "@dima/ui/ai/chat";
import { Markdown } from "@/components/chat/Markdown";
import { AddToDashboard } from "@/components/analytics/DashboardActions";
import { ResultView } from "@dima/ui/result/ResultView";
import { SqlBlock } from "@dima/ui/report/SqlBlock";
import { Button } from "@dima/ui/primitives/button";
import { Sheet, SheetContent, SheetTitle } from "@dima/ui/primitives/sheet";
import { Tooltip, TooltipContent, TooltipTrigger } from "@dima/ui/primitives/tooltip";

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
  const t = useTranslations("chat");
  const convId = useSearchParams().get("c");
  const hydrated = useHydrated();
  const conv = useConversations((s) => s.conversations.find((c) => c.id === convId && c.orgId === orgId));
  const { create, addEntry, progress, settle } = useConversations.getState();
  // Held while an answer streams, so Stop (and leaving the page) can cancel it.
  const inflight = useRef<AbortController | null>(null);
  const [draft, setDraft] = useState("");
  const [panelOpen, setPanelOpen] = useState(false);
  const [tab, setTab] = useState<PanelTab>("results");
  // Answers requested during this visit get the reveal; restored history renders still.
  const [fresh, setFresh] = useState<ReadonlySet<string>>(() => new Set());

  const entries = conv?.entries ?? [];
  const pending = entries.some((e) => e.status === "pending");
  const started = entries.length > 0;
  // Suggested first questions per company (org slug), generic fallback.
  const tStarters = useTranslations("starters");
  const starters = tStarters.raw(["boyahane", "tenant2"].includes(slug) ? slug : "generic") as string[];

  // An unknown / other-company chat id falls back to a fresh chat.
  useEffect(() => {
    if (hydrated && convId && !conv) router.replace("/app/chat");
  }, [hydrated, convId, conv, router]);

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
    setFresh((prev) => new Set(prev).add(`${id}:${entryId}`));
    setDraft("");

    const controller = new AbortController();
    inflight.current = controller;
    void (async () => {
      const steps: Step[] = [];
      let text = "";
      let flushedAt = 0;
      try {
        for await (const ev of gateway.chatStream([...history, { role: "user", content: question }], controller.signal)) {
          if (ev.type === "step") {
            const at = steps.findIndex((s) => s.id === ev.id);
            if (at >= 0) steps[at] = { id: ev.id, text: ev.text, done: ev.done };
            else steps.push({ id: ev.id, text: ev.text, done: ev.done });
            progress(id, entryId, { steps: [...steps] });
          } else if (ev.type === "token") {
            text += ev.text;
            // Repainting Markdown on every token is wasteful; ~60ms reads as live.
            const now = Date.now();
            if (now - flushedAt > 60) {
              flushedAt = now;
              progress(id, entryId, { partial: text });
            }
          } else if (ev.type === "done") {
            settle(id, entryId, {
              id: entryId,
              question,
              status: "done",
              reply: { answer: ev.answer, sql: ev.sql, result: ev.result },
              steps: ev.steps,
              durationMs: ev.durationMs,
            });
            return;
          } else {
            settle(id, entryId, { id: entryId, question, status: "error", message: ev.message });
            return;
          }
        }
        // Stream ended without a verdict: keep whatever text arrived.
        settle(id, entryId, {
          id: entryId,
          question,
          status: text ? "done" : "error",
          ...(text
            ? { reply: { answer: text, sql: null, result: null }, steps: steps.map((s) => s.text) }
            : { message: t("interrupted") }),
        } as Extract<Entry, { status: "done" | "error" }>);
      } catch (err) {
        if (controller.signal.aborted) {
          settle(id, entryId, {
            id: entryId,
            question,
            status: text ? "done" : "error",
            ...(text
              ? { reply: { answer: text, sql: null, result: null }, steps: steps.map((s) => s.text) }
              : { message: t("stopped") }),
          } as Extract<Entry, { status: "done" | "error" }>);
        } else {
          settle(id, entryId, { id: entryId, question, status: "error", message: (err as Error).message });
        }
      } finally {
        if (inflight.current === controller) inflight.current = null;
      }
    })();
  };

  const stop = () => inflight.current?.abort();

  const scrollTo = (entryId: number) =>
    document.getElementById(`entry-${entryId}`)?.scrollIntoView({ behavior: "smooth", block: "start" });

  return (
    <div className="flex h-full min-h-0">
      <TopbarLead>
        <ChatNav orgId={orgId} activeId={conv?.id ?? null} />
        <ChatTitle convId={conv?.id ?? null} />
      </TopbarLead>
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
          <div className="flex min-h-0 flex-1 flex-col items-center overflow-y-auto py-6">
            <div className="my-auto w-full max-w-3xl space-y-6 px-4 pb-10">
              <div className="space-y-2 text-center">
                <h1 className="text-2xl font-semibold tracking-tight">{t("heroTitle")}</h1>
                <p className="text-sm text-muted-foreground">
                  {company ? t("heroBodyCompany", { company }) : t("heroBodyGeneric")}
                </p>
              </div>
              {!configured && (
                <p className="rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-center text-sm text-amber-700 dark:text-amber-300">
                  {t("notConfigured")}
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
          <div className="relative flex min-h-0 flex-1 flex-col">
            {/* Fade instead of an opaque bar: content passes *behind* the top bar
                and the floating composer, the way apps/web does it. */}
            <MessageScroller
              className="[mask-image:linear-gradient(to_bottom,transparent_0,#000_4rem)]"
              scrollKey={`${conv?.id ?? ""}::${entries.length}:${pending ? "1" : "0"}`}
            >
              <div className="mx-auto w-full max-w-3xl space-y-9 px-4 pt-12 pb-36">
                {entries.map((e) => (
                  <article key={e.id} id={`entry-${e.id}`} className="scroll-mt-4 space-y-4">
                    <Message from="user" className="items-start gap-3 pl-10">
                      <Bubble from="user" className="max-w-[calc(100%-2.5rem)]">
                        {e.question}
                      </Bubble>
                      <UserAvatar className="mt-0.5 shrink-0" />
                    </Message>
                    <Message from="assistant" className="items-start gap-3 pr-10">
                      {e.status === "pending" ? (
                        // libraries.dev thinking orb in the avatar's place — it
                        // stays for the whole turn, including while text streams.
                        // Theme and reduced motion are handled by the library.
                        <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center" aria-hidden>
                          <ThinkingOrb state="searching" size={32} color="#7e38f8" />
                        </span>
                      ) : (
                        <DimaAvatar className="mt-0.5 shrink-0" />
                      )}
                      <Bubble from="assistant">
                        {e.status === "pending" ? (
                          <div className="space-y-3">
                            {/* Steps stay put once text starts arriving — they are
                                what was done to get it, not a placeholder for it. */}
                            <LiveSteps steps={e.steps ?? []} streaming={Boolean(e.partial)} />
                            {e.partial && <Markdown>{e.partial}</Markdown>}
                          </div>
                        ) : e.status === "error" ? (
                          <p role="alert" className="text-sm text-destructive">
                            {e.message}
                          </p>
                        ) : (
                          <div className="space-y-2">
                            <Thought steps={e.steps ?? []} durationMs={e.durationMs} />
                            <Reply
                              reply={e.reply}
                              question={e.question}
                              canSave={canSave}
                              animate={fresh.has(`${conv?.id}:${e.id}`)}
                            />
                          </div>
                        )}
                      </Bubble>
                    </Message>
                  </article>
                ))}
              </div>
            </MessageScroller>

            {/* The composer floats over the thread at the thread's own width. */}
            <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10">
              <div className="pointer-events-auto mx-auto w-full max-w-3xl px-4 pb-3">
                <Composer
                  value={draft}
                  onChange={setDraft}
                  onSubmit={() => submit(draft)}
                  disabled={!configured}
                  busy={pending}
                  onStop={stop}
                  // Back to the box when the conversation changes or an answer
                  // lands, so the next question can just be typed.
                  focusKey={`${conv?.id ?? ""}:${pending ? "busy" : "idle"}`}
                />
              </div>
            </div>
          </div>
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

function Reply({
  reply,
  question,
  canSave,
  animate,
}: {
  reply: ChatAnswer;
  question: string;
  canSave: boolean;
  animate: boolean;
}) {
  const t = useTranslations("chat");
  const save = useMutation({
    mutationFn: () => gateway.saveSql(question.slice(0, 120), reply.sql!),
    onSuccess: () => toast.success("Analiz kaydedildi."),
    onError: (err) => toast.error(err.message),
  });

  return (
    <div className="space-y-3">
      <Markdown className={cn(animate && "dima-reveal dima-reveal-rows")}>{reply.answer}</Markdown>
      {reply.result && reply.result.row_count > 0 && (
        <div className={cn("surface p-5", animate && "dima-reveal-late dima-reveal-rows")}>
          <ResultView
            result={reply.result}
            meta={
              <span className="text-xs text-muted-foreground tabular-nums">
                {t("rows", { count: reply.result.row_count })}
              </span>
            }
          />
        </div>
      )}
      {reply.sql && (
        <div
          className={cn("flex flex-wrap items-center gap-1", animate && "dima-reveal-late")}
          style={animate ? ({ "--reveal-delay": "260ms" } as React.CSSProperties) : undefined}
        >
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
              {t("open")}
            </Link>
          )}
        </div>
      )}
      {reply.sql && (
        <SqlBlock
          sql={reply.sql}
          label={t("showSql")}
          copyLabel={t("copySql")}
          className={cn(animate && "dima-reveal-late")}
        />
      )}
    </div>
  );
}

// ── Right panel: about THIS chat only (apps/web ArtifactPanel pattern) ──────

const PANEL_TABS = [
  { id: "results", icon: BarChart3 },
  { id: "sources", icon: Database },
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
  const t = useTranslations("chat");
  const isNarrow = useIsNarrow();
  const body = (
    <>
      <div className="flex h-12 shrink-0 items-center justify-between gap-2 border-b px-2">
        <div role="tablist" aria-label={t("panelSections")} className="flex items-center gap-0.5">
          {PANEL_TABS.map(({ id, icon: Icon }) => (
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
              {t(id)}
            </button>
          ))}
        </div>
        <Button variant="ghost" size="icon-sm" aria-label="Paneli kapat" onClick={onClose}>
          <X className="size-4" />
        </Button>
      </div>
      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
        {entries.length === 0 && <p className="p-2 text-sm text-muted-foreground">{t("noResults")}</p>}
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
                    {t("rows", { count: e.reply.result!.row_count })} · {e.reply.result!.columns.join(", ")}
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
                  <SqlBlock sql={e.reply.sql!} label={t("sqlShort")} copyLabel={t("copySql")} />
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
