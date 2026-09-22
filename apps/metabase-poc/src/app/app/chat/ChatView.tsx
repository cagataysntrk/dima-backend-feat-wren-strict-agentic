"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { ArrowUp, Code2, Save, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { gateway, type ChatAnswer, type ChatTurn } from "@/lib/gateway";
import { cn } from "@/lib/utils";
import { ResultView } from "@/components/ResultView";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type Entry = { id: number; question: string } & (
  | { status: "pending" }
  | { status: "done"; reply: ChatAnswer }
  | { status: "error"; message: string }
);

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

export function ChatView({
  company,
  slug,
  configured,
  canSave,
}: {
  company: string;
  slug: string;
  configured: boolean;
  canSave: boolean;
}) {
  const starters = STARTERS[slug] ?? GENERIC;
  const [entries, setEntries] = useState<Entry[]>([]);
  const [draft, setDraft] = useState("");
  const bottom = useRef<HTMLDivElement>(null);
  const nextId = useRef(1);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [entries]);

  const ask = useMutation({
    mutationFn: ({ history }: { id: number; history: ChatTurn[] }) => gateway.chat(history),
    onSuccess: (reply, { id }) =>
      setEntries((es) => es.map((e) => (e.id === id ? { ...e, status: "done", reply } : e))),
    onError: (err, { id }) =>
      setEntries((es) => es.map((e) => (e.id === id ? { ...e, status: "error", message: err.message } : e))),
  });

  const submit = (text: string) => {
    const question = text.trim();
    if (!question || ask.isPending) return;
    // Prior turns as plain text: the question, the answer, and the SQL behind it
    // (so follow-ups like "only for RAM-1" can build on the previous query).
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
    const id = nextId.current++;
    setEntries((es) => [...es, { id, question, status: "pending" }]);
    setDraft("");
    ask.mutate({ id, history: [...history, { role: "user", content: question }] });
  };

  return (
    <div className="mx-auto flex min-h-[calc(100svh-8rem)] max-w-4xl flex-col">
      <div className="flex-1 space-y-8 pb-6">
        {entries.length === 0 && (
          <div className="space-y-6 pt-10 text-center">
            <div className="space-y-2">
              <h1 className="text-2xl font-semibold tracking-tight">Verinize sorun</h1>
              <p className="text-sm text-muted-foreground">
                {company ? `${company} verisi üzerinde` : "Şirket verinizde"} doğal dilde soru sorun; yanıt, grafik ve
                kullanılan sorguyla gelsin.
              </p>
            </div>
            {!configured && (
              <p className="mx-auto max-w-md rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-sm text-amber-700 dark:text-amber-300">
                Sohbet servisi henüz yapılandırılmadı. Yöneticinizden anahtar tanımlamasını isteyin.
              </p>
            )}
            <div className="mx-auto grid max-w-2xl gap-2 sm:grid-cols-2">
              {starters.map((s) => (
                <button
                  key={s}
                  type="button"
                  disabled={!configured}
                  onClick={() => submit(s)}
                  className="rounded-xl border bg-card px-4 py-3 text-left text-sm transition-colors hover:border-brand/40 hover:bg-accent/40 disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {entries.map((e) => (
          <article key={e.id} className="space-y-3">
            <div className="flex justify-end">
              <p className="max-w-[85%] rounded-2xl rounded-br-md bg-brand px-4 py-2 text-sm text-brand-foreground">
                {e.question}
              </p>
            </div>
            {e.status === "pending" ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
                <Sparkles className="size-4 animate-pulse text-brand" aria-hidden />
                Veriye bakılıyor…
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

      <form
        className="sticky bottom-0 bg-gradient-to-t from-background via-background to-background/0 pt-4 pb-4"
        onSubmit={(ev) => {
          ev.preventDefault();
          submit(draft);
        }}
      >
        <div className="flex items-end gap-2 rounded-2xl border bg-card p-2 shadow-sm focus-within:border-brand/50">
          <label htmlFor="question" className="sr-only">
            Soru
          </label>
          <Textarea
            id="question"
            value={draft}
            onChange={(ev) => setDraft(ev.target.value)}
            onKeyDown={(ev) => {
              if (ev.key === "Enter" && !ev.shiftKey) {
                ev.preventDefault();
                submit(draft);
              }
            }}
            placeholder={configured ? "Bir soru sorun…" : "Sohbet servisi yapılandırılmadı"}
            disabled={!configured}
            rows={1}
            className="max-h-40 min-h-10 resize-none border-0 bg-transparent shadow-none focus-visible:ring-0 dark:bg-transparent"
          />
          <Button
            type="submit"
            variant="brand"
            size="icon"
            aria-label="Gönder"
            disabled={!configured || !draft.trim() || ask.isPending}
          >
            <ArrowUp className="size-4" aria-hidden />
          </Button>
        </div>
      </form>
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
        <div className="rounded-xl border bg-card p-4">
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
        <pre className={cn("overflow-x-auto rounded-lg border bg-muted/40 p-3 font-mono text-xs leading-relaxed")}>
          {reply.sql}
        </pre>
      )}
    </div>
  );
}
