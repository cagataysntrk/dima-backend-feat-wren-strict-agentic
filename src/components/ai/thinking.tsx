"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  Check,
  ChevronRight,
  Boxes,
  PlayCircle,
  ScanText,
  ShieldCheck,
  SquareCode,
  type LucideIcon,
} from "lucide-react";
import { useTranslations } from "next-intl";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Marker, MarkerContent, MarkerIcon } from "@/components/ui/marker";
import { cn } from "@/lib/utils";

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

// Backend `/ask` tek atımlık: yanıt GELMEDEN ara adımları bilemiyoruz. Bekleme
// sırasında pipeline'ın gerçek SIRASINI zamana yayıyoruz; yanıt gelince yerini
// backend'in GERÇEK `trace` dizisi alıyor (bkz. Reasoning).
const STEP_KEYS = ["parse", "catalog", "plan", "verify", "run"] as const;
const STEP_MS = 900;

const STEP_ICON: Record<(typeof STEP_KEYS)[number], LucideIcon> = {
  parse: ScanText,
  catalog: Boxes,
  plan: SquareCode,
  verify: ShieldCheck,
  run: PlayCircle,
};

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
function LiveStep({
  stepKey,
  done,
}: {
  stepKey: (typeof STEP_KEYS)[number];
  done: boolean;
}) {
  const t = useTranslations("chat");
  const Icon = STEP_ICON[stepKey];
  // Aktifken şimdiki zaman ("çözümleniyor"), bitince geçmiş ("çözümlendi").
  const label = done ? t(`stepsDone.${stepKey}`) : t(`steps.${stepKey}`);

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

/** Live chain of thought — the steps dima is working through while it answers. */
export function ChainOfThought({ className }: { className?: string }) {
  const t = useTranslations("chat");
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (current >= STEP_KEYS.length - 1) return;
    const id = setTimeout(() => setCurrent((i) => i + 1), STEP_MS);
    return () => clearTimeout(id);
  }, [current]);

  return (
    <div className={cn("flex min-w-0 flex-col gap-1.5 pt-1", className)}>
      <Shimmer className="text-sm">{t("thinking")}</Shimmer>

      <div className="flex flex-col gap-1 border-l border-border pl-3">
        <AnimatePresence initial={false}>
          {STEP_KEYS.slice(0, current + 1).map((key, i) => (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            >
              <LiveStep stepKey={key} done={i < current} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
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
  className,
}: {
  durationMs?: number;
  trace?: string[];
  className?: string;
}) {
  const t = useTranslations("chat");
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
        {t("thought", { seconds })}
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
