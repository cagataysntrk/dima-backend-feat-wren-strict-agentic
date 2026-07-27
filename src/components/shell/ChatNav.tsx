"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useConversations } from "@/stores/conversations";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

/**
 * Sohbetler arası gezinme okları — üst barda, kenar çubuğu düğmesinin hemen
 * sağında. Sidebar açık da olsa kapalı da olsa aynı yerde durur; konum
 * değiştirseydi kas hafızası bozulurdu.
 *
 * Sidebar'daki filtreyi DEĞİL tüm listeyi gezer: oklar bir gezinme aracı,
 * görünüm filtresinin uzantısı değil.
 */
export function ChatNav({ onSelect }: { onSelect: (id: string) => void }) {
  const conversations = useConversations((s) => s.conversations);
  const activeId = useConversations((s) => s.activeId);

  const idx = conversations.findIndex((c) => c.id === activeId);
  const go = (delta: number) => {
    if (!conversations.length) return;
    const next = idx < 0 ? 0 : Math.min(conversations.length - 1, Math.max(0, idx + delta));
    onSelect(conversations[next].id);
  };

  if (conversations.length < 2) return null;

  return (
    <div className="flex items-center">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="Önceki sohbet"
            disabled={idx <= 0}
            onClick={() => go(-1)}
            className="text-muted-foreground transition-transform hover:-translate-x-0.5 hover:text-foreground disabled:translate-x-0"
          >
            <ChevronLeft className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">Önceki sohbet</TooltipContent>
      </Tooltip>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="Sonraki sohbet"
            disabled={idx < 0 || idx >= conversations.length - 1}
            onClick={() => go(1)}
            className="text-muted-foreground transition-transform hover:translate-x-0.5 hover:text-foreground disabled:translate-x-0"
          >
            <ChevronRight className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">Sonraki sohbet</TooltipContent>
      </Tooltip>
    </div>
  );
}
