"use client";

import { useState } from "react";
import { HelpCircle } from "lucide-react";
import type { AskResponse } from "@/lib/types";
import { ResultView } from "@/components/ResultView";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { SourceBadge } from "@/components/report/SourceBadge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Salt-okunur rapor görünümü. Yorum çubuğu ve doğru/yanlış/zamanla aksiyonları
 * SOHBETE taşındı (bkz. ChatPanel + report/MessageActions) — burada kopyası yok.
 */
export function ReportPanel({
  data,
  pending,
  viewHint,
  error,
}: {
  data: AskResponse | null;
  pending: boolean;
  viewHint?: { kind: string; nonce: number } | null;
  error: string | null;
}) {
  const [showSql, setShowSql] = useState(false);
  const [showTrace, setShowTrace] = useState(false);

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-destructive">
        {error}
      </div>
    );
  }

  if (pending && !data) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-5 w-2/3" />
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-56 w-full" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
        Bir soru sor — rapor burada belirir.
      </div>
    );
  }


  return (
    <div className="space-y-5">
      <div className="space-y-3 border-b border-border pb-4">
        <div className="flex items-start justify-between gap-3">
          <h2 className="text-lg font-medium leading-snug tracking-tight text-foreground">
            {data.question}
          </h2>
          {data.trace && data.trace.length > 0 && (
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Trace"
              title="Bu sorgu nasıl çözüldü?"
              onClick={() => setShowTrace((s) => !s)}
              className={showTrace ? "text-brand" : "text-muted-foreground"}
            >
              <HelpCircle className="size-4" />
            </Button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <SourceBadge source={data.source} />
        </div>

        {showTrace && data.trace && (
          <div className="rounded-lg border border-border bg-muted/40 p-3">
            <div className="mb-1.5 font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
              nasıl çözüldü
            </div>
            <ol className="space-y-0.5">
              {data.trace.map((tr, i) => (
                <li key={i} className="font-mono text-[11px] text-muted-foreground">
                  <span className="mr-1 text-brand">{String(i + 1).padStart(2, "0")}</span>
                  {tr}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>

      {/* Cross-cube KPI kartı (CCC / likidite) — cube tablosu değil bileşke skaler.
          (Yorum çubuğu buraya DEĞİL sohbete taşındı — bkz. ChatPanel.) */}
      {data.kpi && <KpiCardView card={data.kpi} />}

      {data.result && (
        <div className="rounded-lg border border-border p-4">
          <ResultView
            key={`${data.question}·${data.sql}·${viewHint?.nonce ?? 0}`}
            result={data.result}
            viewHint={viewHint?.kind}
            meta={
              <span className="text-xs text-muted-foreground">
                {data.result.row_count} satır
              </span>
            }
          />
        </div>
      )}

      {/* Evrensel çıktı yorumu (feature flag'li) — KPI/tablo/grafik altında. */}
      <OutputInsight interpretation={data.interpretation} />

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSql((s) => !s)}
            className="font-mono text-[11px] tracking-wider text-muted-foreground uppercase"
          >
            {showSql ? "— sql gizle" : "+ sql göster"}
          </Button>
          {data.contract_id && (
            <span
              className="truncate font-mono text-[10px] tracking-wider text-muted-foreground/60"
              title="Query Contract — bu raporun kanıt kaydı: soru + sorgu + sonuç özeti mühürlendi; yeniden oynatılıp doğrulanabilir"
            >
              {data.contract_id}
            </span>
          )}
        </div>
        {showSql && (
          <pre className="overflow-auto rounded-lg border border-border bg-muted/50 p-4 font-mono text-xs leading-relaxed text-foreground">
            {data.sql}
          </pre>
        )}
      </div>
    </div>
  );
}
