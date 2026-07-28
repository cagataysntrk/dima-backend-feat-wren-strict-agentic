"use client";

import { AlertTriangle } from "lucide-react";
import type { AskResponse } from "@dima/contracts";
import { analyze, type ChartKind } from "@dima/domain";

import { Chart } from "@/components/chart/Chart";
import { KpiGrid } from "@/components/chart/kpi";
import { KpiCardView } from "@/components/KpiCard";
import { OutputInsight } from "@/components/OutputInsight";
import { ResultTable } from "@/components/ResultTable";
import { SourceBadge } from "@/components/report/SourceBadge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

import { useResult } from "./catalog";

/**
 * Pano karolarının web görünümleri.
 *
 * Bunlar YENİ bileşen değil — sohbette zaten kullanılan `Chart`, `KpiGrid`,
 * `KpiCardView`, `ResultTable`, `OutputInsight` sarmalanıyor. Pano ayrı bir
 * görsel dil kurmamalı: kullanıcı sohbette gördüğü grafiği panoda da aynı
 * görmeli, yoksa "aynı veri iki farklı çizim" sorusu doğar.
 */

const ALLOWED_KINDS = new Set<ChartKind>([
  "bar",
  "line",
  "area",
  "pie",
  "bar-stacked",
  "bar-h",
  "scatter",
  "radial",
  "radar",
]);

/**
 * Üretilen grafik türünü DOĞRULAR.
 *
 * OpenUI parser'ı enum üyeliğini denetlemiyor — üretilen spec yapısal tip değil
 * imza METNİ taşıyor, yani `ChartTile("q1", "sankey")` ayrıştırmadan geçiyor.
 * Tanınmayan tür sessizce sütuna düşürülmez; `analyze()`'ın deterministik
 * seçimine dönülür, çünkü o seçim zaten veri şekline en uygun olandır.
 */
export function resolveKind(requested: string | undefined, fallback: ChartKind): ChartKind {
  if (!requested) return fallback;
  return ALLOWED_KINDS.has(requested as ChartKind) ? (requested as ChartKind) : fallback;
}

function Tile({
  response,
  children,
  className,
}: {
  response: AskResponse;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn("flex min-w-0 flex-col gap-2 p-3", className)}>
      <header className="flex min-w-0 items-center gap-2">
        <h3 className="min-w-0 flex-1 truncate text-xs font-medium text-muted-foreground">
          {response.question}
        </h3>
        {/* Kanıt zinciri panoda da görünür kalır: yerleşimi model kursa da
            SQL'i kimin ürettiği bilgisi kaybolmaz. */}
        <SourceBadge source={response.source} />
      </header>
      {children}
    </Card>
  );
}

/**
 * Katalogda olmayan kimlik.
 *
 * Sessizce boş dönmek ya da örnek veri koymak en kötü davranış olurdu —
 * kullanıcı gerçek bir pano gördüğünü sanardı. Eksik olan görünür olmalı.
 */
export function MissingTile({ resultId }: { resultId: string }) {
  return (
    <Card className="flex items-start gap-2 border-dashed p-3">
      <AlertTriangle className="mt-0.5 size-3.5 shrink-0 text-muted-foreground" aria-hidden />
      <div className="min-w-0">
        <p className="text-xs font-medium text-foreground">Sonuç bulunamadı: {resultId}</p>
        <p className="text-xs text-muted-foreground">
          Bu kimlik bu sohbette yok. Karo boş bırakıldı — veri uydurulmadı.
        </p>
      </div>
    </Card>
  );
}

export function KpiTileView({ resultId }: { resultId: string }) {
  const response = useResult(resultId);
  if (!response) return <MissingTile resultId={resultId} />;

  // Cross-cube KPI kartı (CCC, likidite) kendi görünümüne sahip.
  if (response.kpi) {
    return (
      <Tile response={response}>
        <KpiCardView card={response.kpi} />
      </Tile>
    );
  }

  if (!response.result?.rows.length) return <MissingTile resultId={resultId} />;
  return (
    <Tile response={response}>
      <KpiGrid result={response.result} analysis={analyze(response.result)} />
    </Tile>
  );
}

export function ChartTileView({
  resultId,
  kind,
  measure,
}: {
  resultId: string;
  kind?: string;
  measure?: string;
}) {
  const response = useResult(resultId);
  if (!response?.result?.rows.length) return <MissingTile resultId={resultId} />;

  const analysis = analyze(response.result);
  return (
    <Tile response={response}>
      <Chart
        result={response.result}
        analysis={analysis}
        kind={resolveKind(kind, analysis.kind)}
        measure={measure ?? ""}
      />
    </Tile>
  );
}

export function TableTileView({ resultId, limit = 10 }: { resultId: string; limit?: number }) {
  const response = useResult(resultId);
  if (!response?.result?.rows.length) return <MissingTile resultId={resultId} />;

  const { result } = response;
  const shown = { ...result, rows: result.rows.slice(0, limit) };
  const hidden = result.row_count - shown.rows.length;

  return (
    <Tile response={response}>
      <ResultTable result={shown} />
      {hidden > 0 ? (
        <p className="text-xs text-muted-foreground">+{hidden} satır daha</p>
      ) : null}
    </Tile>
  );
}

/** Backend'in DETERMİNİSTİK yorumu. Metin üreten taraftan GELMEZ. */
export function InsightTileView({ resultId }: { resultId: string }) {
  const response = useResult(resultId);
  if (!response?.interpretation) return null;
  return <OutputInsight interpretation={response.interpretation} />;
}
