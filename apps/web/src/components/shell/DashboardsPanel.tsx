"use client";

import { LayoutDashboard, Sparkles } from "lucide-react";
import type { AskResponse } from "@dima/contracts";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SourceBadge } from "@/components/report/SourceBadge";

/**
 * Paneller — üretilen cube'ların/panellerin yaşayacağı yüzey.
 *
 * BUGÜN: sohbette üretilmiş, cube_query taşıyan sonuçları "kaydedilebilir panel
 * adayı" olarak listeler. Gerçek panel ÜRETİMİ (birden çok tile'lı düzen) henüz
 * yok — o adım generative-UI entegrasyonuyla gelecek. Boş vaat vermemek için
 * durum panelde açıkça yazılı.
 */
export function DashboardsPanel({
  items,
  onSelect,
}: {
  items: AskResponse[];
  onSelect: (item: AskResponse) => void;
}) {
  const candidates = items.filter((i) => i.cube_query && i.result);

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-2 rounded-lg border border-border bg-muted/40 px-3 py-2">
        <Sparkles className="mt-0.5 size-3.5 shrink-0 text-brand" />
        <p className="text-xs leading-relaxed text-muted-foreground">
          Çok bileşenli paneller henüz üretilmiyor. Aşağıda bu sohbetteki
          deterministik (cube) sonuçlar listeleniyor — panel üretimi geldiğinde
          panellerin yapı taşları bunlar olacak.
        </p>
      </div>

      {candidates.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
          <LayoutDashboard className="size-5 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Henüz panel adayı yok.</p>
          <p className="max-w-xs text-xs text-muted-foreground/80">
            Bir metrik sorusu sor — cube&apos;dan gelen her sonuç buraya düşer.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {candidates.map((item, i) => (
            <Card
              key={`${item.question}-${i}`}
              className="cursor-pointer gap-2 p-3 transition-colors hover:border-brand/40"
              onClick={() => onSelect(item)}
            >
              <div className="flex items-center gap-2">
                <SourceBadge source={item.source} />
                {item.result && (
                  <span className="text-xs text-muted-foreground">
                    {item.result.row_count} satır
                  </span>
                )}
                {item.contract_id && (
                  <Badge variant="outline" className="ml-auto font-mono text-[10px]">
                    {item.contract_id}
                  </Badge>
                )}
              </div>
              <p className="truncate text-sm text-foreground">{item.question}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
