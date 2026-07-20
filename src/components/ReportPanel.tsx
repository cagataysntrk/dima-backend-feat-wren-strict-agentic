"use client";

import Link from "next/link";
import { useState } from "react";
import type { AskResponse } from "@/lib/types";
import { BrandMark } from "@/components/BrandMark";
import { ResultView } from "@/components/ResultView";
import { SourceBadge } from "@/components/ChatPanel";

// Sağ bölme: seçili raporun canlı görünümü (keskin, mono readout).
export function ReportPanel({
  data,
  pending,
  error,
}: {
  data: AskResponse | null;
  pending: boolean;
  error: string | null;
}) {
  const [showSql, setShowSql] = useState(false);
  const [showTrace, setShowTrace] = useState(false);

  if (error) {
    return (
      <Center>
        <div className="max-w-sm border border-red-300 bg-red-50 px-4 py-3 font-mono text-[13px] text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
          {error}
        </div>
      </Center>
    );
  }

  if (pending && !data) {
    return (
      <Center>
        <div className="flex items-center gap-2 font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} />
          yürütülüyor…
        </div>
      </Center>
    );
  }

  if (!data) {
    return (
      <Center>
        <div className="max-w-xs text-center font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} /> soldan sor — rapor burada belirir
        </div>
      </Center>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-8 py-7">
      <div className="mb-5 border-b border-hairline pb-4">
        <div className="flex items-start justify-between gap-3">
          <h2 className="font-mono text-[15px] leading-snug text-foreground">{data.question}</h2>
          <div className="flex shrink-0 items-center gap-1.5 pt-0.5">
            <SourceBadge source={data.source} />
            {data.trace && data.trace.length > 0 && (
              <button
                onClick={() => setShowTrace((s) => !s)}
                title="Bu sorgu nasıl çözüldü?"
                aria-label="Trace"
                className={`flex h-[18px] w-[18px] items-center justify-center border font-mono text-[11px] transition-colors ${
                  showTrace ? "border-accent/40 text-accent" : "border-hairline text-neutral-400 hover:text-foreground"
                }`}
              >
                ?
              </button>
            )}
          </div>
        </div>
        {showTrace && data.trace && (
          <div className="mt-3 border border-hairline bg-neutral-500/[0.03] p-3">
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              nasıl çözüldü
            </div>
            <ol className="space-y-0.5">
              {data.trace.map((t, i) => (
                <li key={i} className="font-mono text-[11px] text-neutral-500">
                  <span className="mr-1 text-accent">{String(i + 1).padStart(2, "0")}</span>
                  {t}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>

      {data.result && (
        <div className="border border-hairline bg-background p-4">
          <ResultView key={`${data.question}·${data.sql}`} result={data.result} />
        </div>
      )}

      <div className="mt-5">
        <button
          onClick={() => setShowSql((s) => !s)}
          className="font-mono text-[11px] uppercase tracking-wider text-neutral-400 transition-colors hover:text-foreground"
        >
          {showSql ? "— sql gizle" : "+ sql göster"}
        </button>
        {showSql && (
          <pre className="mt-2 overflow-auto border border-hairline bg-neutral-950 p-4 font-mono text-xs leading-relaxed text-neutral-100">
            {data.sql}
          </pre>
        )}
      </div>
    </div>
  );
}

// Boş/bekleme durumlarında landing ile aynı imza: alt-orta ink filigran.
function Center({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex h-full items-center justify-center p-6">
      {children}
      <Link
        href="/brand"
        className="absolute inset-x-0 bottom-8 flex justify-center opacity-30 transition-opacity hover:opacity-80"
      >
        <BrandMark size="sm" ink />
      </Link>
    </div>
  );
}
