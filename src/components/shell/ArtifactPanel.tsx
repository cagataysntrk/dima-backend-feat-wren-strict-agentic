"use client";

import { X, Maximize2, Minimize2 } from "lucide-react";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useIsMobile } from "@/hooks/use-mobile";
import { cn } from "@/lib/utils";

/**
 * Right-hand artifact panel (Claude-Artifacts analog): hosts the report/dashboard
 * or the schema browser. Desktop → a collapsible side panel; mobile → a Sheet.
 */
export function ArtifactPanel({
  open,
  title,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  const t = useTranslations("common");
  const isMobile = useIsMobile();
  const [expanded, setExpanded] = useState(false);

  if (isMobile) {
    return (
      <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
        <SheetContent side="right" className="w-full gap-0 p-0 sm:max-w-lg">
          <SheetHeader className="border-b border-border">
            <SheetTitle className="text-base font-medium">{title}</SheetTitle>
          </SheetHeader>
          <div className="min-h-0 flex-1 overflow-auto p-4">{children}</div>
        </SheetContent>
      </Sheet>
    );
  }

  // Panel HER ZAMAN mount'lu kalır; açılıp kapanma genişlik geçişiyle olur — sol
  // sidebar ile aynı davranış (shadcn `transition-[width]`). Unmount edilseydi
  // genişlik anında sıçrardı; şimdi içerik yumuşakça itilip geri alınıyor.
  return (
    <aside
      data-state={open ? "open" : "closed"}
      aria-hidden={!open}
      className={cn(
        "flex min-h-0 shrink-0 flex-col overflow-hidden border-border bg-card/40",
        "transition-[width,border-left-width] duration-300 ease-[var(--ease-drawer)]",
        "motion-reduce:transition-none",
        open
          ? cn("border-l", expanded ? "w-[min(70vw,900px)]" : "w-[min(46vw,600px)]")
          : "w-0 border-l-0",
      )}
    >
      {/* İç sarmalayıcı sabit genişlikte: panel daralırken içerik yeniden akmasın
          (aksi halde kapanışta metin sıkışıp titriyor). */}
      <div
        className={cn(
          "flex min-h-0 flex-1 flex-col transition-opacity duration-200",
          expanded ? "w-[min(70vw,900px)]" : "w-[min(46vw,600px)]",
          open ? "opacity-100" : "opacity-0",
        )}
      >
        <header className="flex h-14 shrink-0 items-center justify-between gap-2 border-b border-border px-4">
          <h2 className="truncate text-sm font-medium tracking-tight">{title}</h2>
          <div className="flex items-center gap-0.5">
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={expanded ? "Daralt" : "Genişlet"}
              className="text-muted-foreground hover:text-foreground"
              onClick={() => setExpanded((e) => !e)}
            >
              {expanded ? <Minimize2 className="size-4" /> : <Maximize2 className="size-4" />}
            </Button>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={t("close")}
              className="text-muted-foreground hover:text-foreground"
              onClick={onClose}
            >
              <X className="size-4" />
            </Button>
          </div>
        </header>
        <div className="min-h-0 flex-1 overflow-auto p-4">{children}</div>
      </div>
    </aside>
  );
}
