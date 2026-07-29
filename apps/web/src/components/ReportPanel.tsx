"use client";

import { useState } from "react";
import { HelpCircle } from "lucide-react";
import type { AskResponse, CubeQuery } from "@dima/contracts";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { NextSteps, Recommendations } from "@/components/report/NextSteps";
import { ResultCard } from "@/components/report/ResultCard";
import { SqlBlock } from "@/components/report/SqlBlock";
import { SourceBadge } from "@/components/report/SourceBadge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Salt-okunur rapor görünümü. Yorum çubuğu ve doğru/yanlış/zamanla aksiyonları
 * SOHBETE taşındı (bkz. ChatPanel + report/MessageActions) — burada kopyası yok.
 *
 * İSTİSNA: K2/K4 yönlendirmeleri burada da var. Onlar geri bildirim değil
 * GEZİNME — raporu panelde açmış bir kullanıcının sohbete dönüp aynı chip'i
 * araması gerekmesin. Tıklama yine sohbete yeni bir mesaj olarak düşer.
 */
export function ReportPanel({
  data,
  pending,
  viewHint,
  error,
  onCubeEdit,
}: {
  data: AskResponse | null;
  pending: boolean;
  viewHint?: { kind: string; nonce: number } | null;
  error: string | null;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
}) {
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
        <ResultCard
          key={`${data.question}·${data.sql}·${viewHint?.nonce ?? 0}`}
          result={data.result}
          viewHint={viewHint?.kind}
          // Genişlet YOK: panelin genişliği panelin kendi işi, kartın değil.
          // Daha çok yer gerekiyorsa tam ekran düğmesi zaten burada.
          meta={
            <span className="text-xs text-muted-foreground">
              {data.result.row_count} satır
            </span>
          }
        />
      )}

      {/* Evrensel çıktı yorumu + K3 proaktif sinyaller — KPI/tablo/grafik altında. */}
      <OutputInsight interpretation={data.interpretation} />

      {onCubeEdit && (
        <div className="space-y-2">
          <Recommendations items={data.recommendations} onDrill={onCubeEdit} />
          <NextSteps steps={data.next_steps} onDrill={onCubeEdit} />
        </div>
      )}

      <div className="space-y-2">
        {/* Sohbetteki ile AYNI blok: yeniden akıtılmış cümlecikler, satır
            numaralı oluk, grafik paletinden token renkleri. Panelde ham `<pre>`
            duruyordu — aynı sorgunun iki farklı görünümü olmasının sebebi yoktu. */}
        {data.sql && <SqlBlock sql={data.sql} />}
        {data.contract_id && (
          <span
            className="block truncate font-mono text-[10px] tracking-wider text-muted-foreground/60"
            title="Query Contract — bu raporun kanıt kaydı: soru + sorgu + sonuç özeti mühürlendi; yeniden oynatılıp doğrulanabilir"
          >
            {data.contract_id}
          </span>
        )}
      </div>
    </div>
  );
}
