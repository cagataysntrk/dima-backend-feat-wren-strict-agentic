"use client";

import Link from "next/link";
import { ArrowUpRight, BarChart3, LayoutDashboard } from "lucide-react";
import type { AskResponse, CubeQuery } from "@dima/contracts";
import { analyze } from "@dima/domain";
import { DecisionTools } from "@/components/report/DecisionTools";
import { SourceBadge } from "@/components/report/SourceBadge";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

/**
 * PANELLER (sohbet kapsamlı) — bu sohbetin ürettiği her sonuç bir paneldir.
 *
 * Rapor ayrı bir nesne değil: kayıtlı sorgu + görünüm = panel. Bu yüzden sağ
 * panelde "Rapor" sekmesi yok, onun yerine bu sohbetin TÜM panelleri var.
 * Hesabın kayıtlı panoları sol taraftaki /dashboards sayfasında.
 *
 * Tıklama SOHBETTEKİ karta götürür (kopyasını burada çizmez): rapor zaten
 * sohbetin içinde yaşıyor, ikinci bir render hem bakımı ikiye katlar hem de
 * "hangisi asıl?" sorusunu doğurur. Burası bir İÇİNDEKİLER listesi.
 */

const KIND_LABEL: Record<string, string> = {
  kpi: "KPI",
  bar: "Sütun",
  line: "Çizgi",
  pie: "Pasta",
  heatmap: "Isı haritası",
  facet: "Panelli",
  none: "Tablo",
};

export function ChatPanelsPanel({
  items,
  onFocus,
  sessionId,
  onCubeEdit,
}: {
  items: AskResponse[];
  /** Sohbetteki karta götür (kaydır + vurgula). */
  onFocus: (item: AskResponse) => void;
  sessionId?: string;
  /** Analist iddiası kanıtı aynı deterministik cube yoluyla yeniden açar. */
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  // Sonucu olan her cevap bir panel. Eskiden yeniye — sohbetteki sırayla aynı.
  const panels = [...items].reverse().filter((i) => i.result || i.kpi);

  if (panels.length === 0) {
    return (
      <div className="flex h-full flex-col justify-center gap-5 text-center">
        <div className="flex flex-col items-center gap-2">
          <BarChart3 className="size-5 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Bu sohbette henüz panel yok.</p>
          <p className="max-w-xs text-xs text-muted-foreground/80">
            Bir metrik sorusu sor — her sonuç burada bir panel olarak listelenir.
          </p>
        </div>
        <DecisionTools items={items} sessionId={sessionId} onEvidence={onCubeEdit} />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="space-y-2">
        {panels.map((item, i) => {
          const kind = item.kpi ? "kpi" : item.result ? analyze(item.result).kind : "none";
          return (
            <Card
              key={`${item.question}-${i}`}
              onClick={() => onFocus(item)}
              className="cursor-pointer gap-1.5 p-3 transition-colors hover:border-brand/40"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-muted-foreground tabular-nums">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <SourceBadge source={item.source} />
                <Badge variant="outline" className="ml-auto shrink-0 text-[10px] font-normal">
                  {KIND_LABEL[kind] ?? "Grafik"}
                </Badge>
              </div>
              <p className="truncate text-sm text-foreground" title={item.question}>
                {item.question}
              </p>
              {item.result && (
                <span className="font-mono text-[10px] text-muted-foreground">
                  {item.result.row_count} satır
                </span>
              )}
            </Card>
          );
        })}
      </div>

      <Link
        href="/dashboards"
        className="inline-flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
      >
        <LayoutDashboard className="size-3.5" />
        Kayıtlı panolar
        <ArrowUpRight className="size-3.5" />
      </Link>

      <DecisionTools items={items} sessionId={sessionId} onEvidence={onCubeEdit} />
    </div>
  );
}
