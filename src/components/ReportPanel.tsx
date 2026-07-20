"use client";

import { useState } from "react";
import type { AskResponse } from "@/lib/types";
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
      <div className="mb-5 flex items-start justify-between gap-3 border-b border-hairline pb-4">
        <h2 className="font-mono text-[15px] leading-snug text-foreground">{data.question}</h2>
        <div className="shrink-0 pt-0.5">
          <SourceBadge source={data.source} />
        </div>
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

function Center({ children }: { children: React.ReactNode }) {
  return <div className="flex h-full items-center justify-center p-6">{children}</div>;
}
