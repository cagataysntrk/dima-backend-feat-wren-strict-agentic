"use client";

import { FormEvent, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { QueryResult } from "@/lib/types";
import { FastResultCard } from "./FastResultCard";

type FastStatus = "SUCCESS" | "CLARIFICATION_REQUIRED" | "UNSUPPORTED" | "FAILED";

type FastEvidence = {
  evidence_id: string;
  resource_ref: string;
  field_refs: Record<string, string>;
  exact_time_bounds: {
    start: string;
    end_exclusive: string;
    kind: string;
  } | null;
  query_fingerprint: string;
  access_fingerprint: string;
  metabase_runtime_version: string;
  result_digest: string;
};

type FastAskResponse = {
  status: FastStatus;
  question: string;
  answer: string | null;
  result: QueryResult | null;
  evidence: FastEvidence | null;
  error: { code: string; message: string } | null;
};

const DEFAULT_QUESTION = "Son 30 günde kaç sipariş var?";
const POC_AS_OF_DATE = process.env.NEXT_PUBLIC_FAST_POC_AS_OF_DATE || undefined;

function shortHash(value?: string | null) {
  return value ? value.slice(0, 12) : "—";
}

function periodLabel(evidence: FastEvidence) {
  if (!evidence.exact_time_bounds) return "Tüm dönem";
  return `${evidence.exact_time_bounds.start} → ${evidence.exact_time_bounds.end_exclusive} (exclusive)`;
}

function StateCard({
  type,
  title,
  message,
}: {
  type: "clarification" | "unsupported" | "failed";
  title: string;
  message: string;
}) {
  return (
    <section
      className="border border-hairline p-4 sm:p-5"
      data-fast-clarification={type === "clarification" ? "true" : undefined}
      data-fast-unsupported={type === "unsupported" ? "true" : undefined}
      data-fast-failed={type === "failed" ? "true" : undefined}
    >
      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
        {type}
      </p>
      <h2 className="mt-2 text-base font-medium">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-neutral-500">{message}</p>
    </section>
  );
}

export function FastAskPoc() {
  const [question, setQuestion] = useState(DEFAULT_QUESTION);
  const [response, setResponse] = useState<FastAskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [transportError, setTransportError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const clean = question.trim();
    if (clean.length < 3 || loading) return;

    setLoading(true);
    setTransportError(null);
    setResponse(null);
    try {
      const { data } = await apiClient.post<FastAskResponse>("/fast/ask", {
        question: clean,
        ...(POC_AS_OF_DATE ? { as_of_date: POC_AS_OF_DATE } : {}),
      });
      setResponse(data);
    } catch {
      setTransportError("Fast Ask servisine ulaşılamadı. İstek güvenli biçimde başarısız oldu.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      data-fast-poc="true"
      data-fast-shell
      className="h-full overflow-y-auto bg-background text-foreground"
    >
      <div className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="border-b border-hairline pb-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-accent">
                DIMA · Fast Track
              </p>
              <h1 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">
                First real Ask
              </h1>
            </div>
            <span className="border border-hairline px-2 py-1 font-mono text-[10px] uppercase text-neutral-500">
              FT-003
            </span>
          </div>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-neutral-500">
            Soruyu Dima’ya sor. Metabase arka planda kaynak keşfi, query construction ve
            execution motorudur; kullanıcı Metabase workspace’i kullanmaz.
          </p>
        </header>

        <form onSubmit={submit} className="py-6" data-fast-ask-form>
          <label htmlFor="fast-question" className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
            Soru
          </label>
          <div className="mt-2 flex flex-col gap-2 sm:flex-row">
            <input
              id="fast-question"
              data-fast-question
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              className="min-w-0 flex-1 border border-hairline bg-background px-3 py-3 text-sm outline-none focus:border-foreground"
              autoComplete="off"
            />
            <button
              type="submit"
              data-fast-submit
              disabled={loading || question.trim().length < 3}
              className="border border-foreground bg-foreground px-5 py-3 text-sm text-background disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
            >
              {loading ? "Araştırılıyor…" : "Sor"}
            </button>
          </div>
        </form>

        {loading ? (
          <section
            data-fast-loading
            className="border border-hairline p-4 font-mono text-xs text-neutral-500"
          >
            Dima araştırıyor… kaynak → dönem → query → kanıt
          </section>
        ) : null}

        {transportError ? (
          <StateCard type="failed" title="İstek tamamlanamadı" message={transportError} />
        ) : null}

        {response?.status === "CLARIFICATION_REQUIRED" ? (
          <StateCard
            type="clarification"
            title="Bir noktayı netleştirmem gerekiyor"
            message={response.error?.message ?? "Kaynak veya alan seçimi belirsiz."}
          />
        ) : null}

        {response?.status === "UNSUPPORTED" ? (
          <StateCard
            type="unsupported"
            title="Bu soru henüz bu Fast Ask kapsamının dışında"
            message={response.error?.message ?? "Desteklenen ilk family COUNT/SUM analizidir."}
          />
        ) : null}

        {response?.status === "FAILED" ? (
          <StateCard
            type="failed"
            title="Analiz güvenli biçimde durduruldu"
            message={response.error?.message ?? "İstek doğrulanamadı."}
          />
        ) : null}

        {response?.status === "SUCCESS" && response.result && response.evidence ? (
          <div data-fast-success className="grid gap-5">
            <section className="border border-hairline p-4 sm:p-5">
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
                Cevap
              </p>
              <p data-fast-answer className="mt-2 text-xl font-medium tracking-tight">
                {response.answer}
              </p>
            </section>

            <FastResultCard result={response.result} />

            <section className="border border-hairline p-4 sm:p-5" data-fast-evidence>
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-500">
                Kanıt özeti
              </p>
              <dl className="mt-3 grid gap-2 text-sm">
                <div className="flex flex-wrap justify-between gap-2 border-b border-hairline pb-2">
                  <dt className="text-neutral-500">Kaynak</dt>
                  <dd data-evidence-source className="font-mono text-[11px]">
                    {response.evidence.resource_ref}
                  </dd>
                </div>
                <div className="flex flex-wrap justify-between gap-2 border-b border-hairline pb-2">
                  <dt className="text-neutral-500">Dönem</dt>
                  <dd data-evidence-period className="font-mono text-[11px]">
                    {periodLabel(response.evidence)}
                  </dd>
                </div>
                <div className="flex flex-wrap justify-between gap-2 border-b border-hairline pb-2">
                  <dt className="text-neutral-500">Ölçü</dt>
                  <dd data-evidence-measure className="font-mono text-[11px]">
                    {response.evidence.field_refs.measure ?? "count"}
                  </dd>
                </div>
                <div className="flex flex-wrap justify-between gap-2 border-b border-hairline pb-2">
                  <dt className="text-neutral-500">Kırılım</dt>
                  <dd data-evidence-breakdown className="font-mono text-[11px]">
                    {response.evidence.field_refs.breakdown ?? "—"}
                  </dd>
                </div>
                <div className="flex flex-wrap justify-between gap-2">
                  <dt className="text-neutral-500">Query fingerprint</dt>
                  <dd data-evidence-query-fingerprint className="font-mono text-[11px]">
                    {shortHash(response.evidence.query_fingerprint)}
                  </dd>
                </div>
              </dl>
            </section>
          </div>
        ) : null}
      </div>
    </main>
  );
}
