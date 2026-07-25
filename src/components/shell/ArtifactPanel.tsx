"use client";

import { X, Maximize2, Minimize2 } from "lucide-react";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { AnimatePresence, motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useIsMobile } from "@/hooks/use-mobile";
import { EASE_DRAWER } from "@/lib/motion";
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

  return (
    <AnimatePresence>
      {open && (
        <motion.aside
          key="artifact"
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 24 }}
          transition={{ duration: 0.26, ease: EASE_DRAWER }}
          className={cn(
            "flex min-h-0 shrink-0 flex-col border-l border-border bg-card/40",
            expanded ? "w-[min(70vw,900px)]" : "w-[min(46vw,600px)]",
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
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
