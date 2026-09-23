"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@dima/ui/primitives/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@dima/ui/primitives/tooltip";
import { useConversations } from "@/stores/conversations";

/**
 * Arrows between conversations, next to the sidebar toggle (apps/web pattern).
 * They walk the whole list in the sidebar's order — newest first — so the
 * position never depends on which chat is open. Hidden below two chats.
 */
export function ChatNav({ orgId, activeId }: { orgId: string; activeId: string | null }) {
  const t = useTranslations("chatNav");
  const router = useRouter();
  // Selector must return a stable reference: filtering inside it hands zustand
  // a new array every render and the component re-renders forever (React #185).
  const conversations = useConversations((s) => s.conversations);
  const ordered = conversations
    .filter((c) => c.orgId === orgId && c.entries.length > 0)
    .sort((a, b) => b.updatedAt - a.updatedAt);
  const idx = ordered.findIndex((c) => c.id === activeId);
  if (ordered.length < 2) return null;

  const go = (delta: number) => {
    const next = idx < 0 ? 0 : Math.min(ordered.length - 1, Math.max(0, idx + delta));
    router.push(`/app/chat?c=${ordered[next].id}`);
  };

  return (
    <div className="flex items-center">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t("previous")}
            disabled={idx <= 0}
            onClick={() => go(-1)}
            className="text-muted-foreground transition-transform hover:-translate-x-0.5 hover:text-foreground disabled:translate-x-0"
          >
            <ChevronLeft className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">{t("previous")}</TooltipContent>
      </Tooltip>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={t("next")}
            disabled={idx < 0 || idx >= ordered.length - 1}
            onClick={() => go(1)}
            className="text-muted-foreground transition-transform hover:translate-x-0.5 hover:text-foreground disabled:translate-x-0"
          >
            <ChevronRight className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">{t("next")}</TooltipContent>
      </Tooltip>
    </div>
  );
}
