"use client";

import { EyeOff } from "lucide-react";
import { useConversations } from "@/stores/conversations";
import { Button } from "@dima/ui/primitives/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@dima/ui/primitives/tooltip";
import { cn } from "@dima/ui/utils";

/**
 * Gizli sohbet düğmesi. Açıkken konuşma yerel geçmişe HİÇ yazılmaz.
 *
 * DÜRÜSTLÜK: bu YEREL bir söz. Sorgu yine backend'e gidiyor ve orada
 * loglanabilir/`session_id` ile ilişkilenebilir — tooltip bunu açıkça söylüyor,
 * yoksa kullanıcı "hiçbir yerde iz kalmıyor" sanır.
 */
export function IncognitoToggle() {
  const incognito = useConversations((s) => s.incognito);
  const setIncognito = useConversations((s) => s.setIncognito);

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          aria-pressed={incognito}
          onClick={() => setIncognito(!incognito)}
          className={cn(
            "h-8 gap-1.5 px-2 text-xs transition-colors",
            incognito
              ? "bg-brand/10 text-brand hover:bg-brand/15"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          <EyeOff className="size-4" />
          Gizli
        </Button>
      </TooltipTrigger>
      <TooltipContent side="bottom" className="max-w-64">
        {incognito
          ? "Gizli sohbet açık — bu konuşma geçmişe kaydedilmiyor."
          : "Gizli sohbet: konuşma yerel geçmişe yazılmaz. Sorgular yine sunucuya gider."}
      </TooltipContent>
    </Tooltip>
  );
}
