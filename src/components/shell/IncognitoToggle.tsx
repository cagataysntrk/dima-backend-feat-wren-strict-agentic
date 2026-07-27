"use client";

import { EyeOff } from "lucide-react";
import { useConversations } from "@/stores/conversations";
import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

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

/**
 * Gizli modun zemini — MagicUI flickering grid, mor noktalar. Sohbetin ARKASINDA
 * durur; `pointer-events-none` ile tıklamaları geçirir, `aria-hidden` ile ekran
 * okuyucudan gizlenir (süs, bilgi değil).
 */
export function IncognitoBackdrop() {
  const incognito = useConversations((s) => s.incognito);
  if (!incognito) return null;

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 z-0 overflow-hidden"
    >
      <FlickeringGrid
        className="size-full"
        squareSize={3}
        gridGap={7}
        // marka moru — token'dan değil sabit, çünkü canvas CSS değişkeni okuyamaz
        color="rgb(139, 92, 246)"
        maxOpacity={0.18}
        flickerChance={0.08}
      />
      {/* okunurluk için merkeze doğru sönümlenir — metin ızgaranın üstünde kalsın */}
      <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/85 to-background/60" />
    </div>
  );
}
