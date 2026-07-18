"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { apiErrorMessage, ask } from "@/lib/api-client";
import { ResultView } from "@/components/ResultView";
import { SchemaPanel } from "@/components/SchemaPanel";
import { useHistory } from "@/stores/history";
import type { AskResponse } from "@/lib/types";

const EXAMPLES = [
  "Vardiya × haftanın günü verimliliği (son 3 ay)",
  "Makine bazında verim ve fire oranı",
  "Personel bazında ortalama OEE nedir?",
  "Aşama bazında toplam fire",
  "Müşteri bazında ciro",
  "En pahalı reçete hangisi?",
  "Geciken siparişler",
  "Aylık fire trendi",
  "Marmara boya aylara göre cirosu",
  "Reddedilen partileri listele",
];

export default function Home() {
  const [question, setQuestion] = useState("");
  const addHistory = useHistory((s) => s.add);

  const mutation = useMutation<AskResponse, unknown, string>({
    mutationFn: (q: string) => ask({ question: q }),
    onSuccess: (data) => addHistory(data),
  });

  const submit = (q: string) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    setQuestion(trimmed);
    mutation.mutate(trimmed);
  };

  const data = mutation.data;

  return (
    <div className="flex flex-1 min-h-0">
      <SchemaPanel />

      <main className="flex-1 overflow-auto">
        <div className="mx-auto max-w-3xl px-6 py-10">
          <header className="mb-8">
            <h1 className="text-2xl font-bold">Veriyle Konuş</h1>
            <p className="mt-1 text-sm text-neutral-500">
              Doğal dille sor — dima güvenilir SQL üretir, doğrular ve çalıştırır.
            </p>
          </header>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              submit(question);
            }}
            className="flex gap-2"
          >
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Örn. Makine bazında ortalama OEE nedir?"
              className="flex-1 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-transparent px-4 py-2.5 text-sm outline-none focus:border-neutral-500"
            />
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-lg bg-neutral-900 dark:bg-white px-5 py-2.5 text-sm font-medium text-white dark:text-black disabled:opacity-50"
            >
              {mutation.isPending ? "Düşünüyor…" : "Sor"}
            </button>
          </form>

          <div className="mt-3 flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => submit(ex)}
                className="rounded-full border border-neutral-200 dark:border-neutral-800 px-3 py-1 text-xs text-neutral-600 dark:text-neutral-400 hover:border-neutral-400"
              >
                {ex}
              </button>
            ))}
          </div>

          {mutation.isError && (
            <div className="mt-6 rounded-lg border border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-900 p-4 text-sm text-red-700 dark:text-red-400">
              {apiErrorMessage(mutation.error)}
            </div>
          )}

          {data && (
            <section className="mt-8 space-y-5">
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-neutral-500 mb-2">
                  Üretilen SQL
                </h3>
                <pre className="overflow-auto rounded-lg bg-neutral-900 p-4 text-xs text-neutral-100 font-mono">
                  {data.sql}
                </pre>
              </div>

              {data.result && <ResultView result={data.result} />}
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
