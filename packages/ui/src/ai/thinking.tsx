"use client";

import { useState } from "react";
import { motion } from "motion/react";
import {
  Check,
  ChevronRight,
  Loader,
  type LucideIcon,
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../primitives/collapsible";
import { Marker, MarkerContent, MarkerIcon } from "../primitives/marker";
import { cn } from "../utils";

// Bu dosya i18n TANIMAZ: etiketleri çağıran verir (apps/web çevirilerini,
// POC düz Türkçe metni geçer). Böylece paket next-intl'e bağlanmıyor.

/** Shimmering text — indeterminate wait. Replaces the old blinking caret. */
export function Shimmer({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <span className={cn("dima-shimmer", className)}>{children}</span>;
}

/** Tamamlanan adımın tik'i — kısa, hafif yaylı bir "oturdu" hareketi. */
function DoneMark() {
  return (
    <motion.span
      initial={{ scale: 0.4, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.18, ease: [0.34, 1.56, 0.64, 1] }}
      className="flex items-center justify-center"
    >
      <Check className="size-3.5 text-brand" strokeWidth={2.5} />
    </motion.span>
  );
}

/** Canlı adım satırı: aktifken mor shimmer, bitince tik + geçmiş zaman. */
export function LiveStep({
  label,
  done,
  icon: Icon = Loader,
}: {
  /** Already-phrased text: present tense while running, past tense when done. */
  label: string;
  done: boolean;
  icon?: LucideIcon;
}) {

  return (
    <Marker className="text-xs">
      <MarkerIcon className="flex items-center justify-center">
        {done ? <DoneMark /> : <Icon className="size-3.5 animate-pulse text-brand" />}
      </MarkerIcon>
      <MarkerContent className={done ? "text-muted-foreground" : undefined}>
        {done ? label : <Shimmer>{label}</Shimmer>}
      </MarkerContent>
    </Marker>
  );
}

/**
 * Settled chain of thought — cevabın üstünde kalır, varsayılan kapalı.
 *
 * Adımlar backend'in GERÇEK `trace` dizisinden gelir ("nasıl çözüldü"). Trace
 * yoksa (eski kayıt / trace üretmeyen yol) blok yalnız süreyi gösterir ve
 * açılmaz — uydurma adım listelemek, yapılmamış bir işi yapılmış göstermek olur.
 */
export function Reasoning({
  durationMs,
  trace,
  summary,
  className,
}: {
  durationMs?: number;
  trace?: string[];
  /** Trigger text; defaults to "7 sn düşündü". Apps with i18n pass their own. */
  summary?: (seconds: number) => string;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const s = (durationMs ?? 0) / 1000;
  const seconds = s < 10 ? Math.max(0.1, Math.round(s * 10) / 10) : Math.round(s);
  const steps = trace ?? [];
  const hasSteps = steps.length > 0;

  return (
    <Collapsible open={open} onOpenChange={setOpen} className={cn("min-w-0", className)}>
      <CollapsibleTrigger
        disabled={!hasSteps}
        className="group flex items-center gap-1 rounded text-xs text-muted-foreground transition-colors hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none disabled:cursor-default disabled:hover:text-muted-foreground"
      >
        {hasSteps && (
          <ChevronRight className="size-3.5 transition-transform duration-200 group-data-[state=open]:rotate-90" />
        )}
        {(summary ?? ((n: number) => `${n} sn düşündü`))(seconds)}
      </CollapsibleTrigger>

      <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
        <div className="mt-1.5 flex flex-col gap-1 border-l border-border pl-3">
          {steps.map((line, i) => (
            <Marker key={i} className="text-xs">
              <MarkerIcon className="flex items-center justify-center">
                <Check className="size-3.5 text-brand/70" strokeWidth={2.5} />
              </MarkerIcon>
              <MarkerContent className="text-muted-foreground">{line}</MarkerContent>
            </Marker>
          ))}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
