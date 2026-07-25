"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
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

// Backend `/ask` tek atımlık: ara adımları stream etmiyor. Bu yüzden liste,
// gerçek pipeline sırasını (çözümleme → cube kataloğu → SQL planı → dry-plan →
// çalıştırma) zamana yayarak gösterir; son adım yanıt gelene kadar aktif kalır.
// Backend adım event'leri (SSE) eklendiğinde `steps` prop'u dışarıdan beslenir.
const STEP_KEYS = ["parse", "catalog", "plan", "verify", "run"] as const;
const STEP_MS = 900;

// Her adım kendi işini anlatan bir ikon taşır — jenerik tik/nokta yerine.
const STEP_ICON: Record<(typeof STEP_KEYS)[number], LucideIcon> = {
  parse: ScanText, // soruyu çözümle
  catalog: Boxes, // cube kataloğu
  plan: SquareCode, // SQL planı
  verify: ShieldCheck, // dry-plan guard
  run: PlayCircle, // çalıştır
};

/** One step row: its own icon, brand-tinted + shimmering label while active. */
function Step({ stepKey, done }: { stepKey: (typeof STEP_KEYS)[number]; done: boolean }) {
  const t = useTranslations("chat");
  const label = t(`steps.${stepKey}`);
  const Icon = STEP_ICON[stepKey];
  return (
    <Marker className="text-xs">
      <MarkerIcon className="flex items-center justify-center">
        <Icon
          className={cn("size-3.5", done ? "text-muted-foreground" : "animate-pulse text-brand")}
        />
      </MarkerIcon>
      <MarkerContent>{done ? label : <Shimmer>{label}</Shimmer>}</MarkerContent>
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
              <Step stepKey={key} done={i < current} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

/**
 * Settled chain of thought — stays in the thread above the answer (ChatGPT /
 * Claude style), collapsed by default: "N sn düşündü" + chevron.
 */
export function Reasoning({
  durationMs,
  className,
}: {
  durationMs?: number;
  className?: string;
}) {
  const t = useTranslations("chat");
  const [open, setOpen] = useState(false);
  // Saniye altını da göster (0,2 sn). 10 sn'ye kadar tek ondalık, sonrası tam sayı;
  // sayıyı ICU'ya sayı olarak veriyoruz ki ondalık ayracı yerelden gelsin (tr: virgül).
  const s = (durationMs ?? 0) / 1000;
  const seconds = s < 10 ? Math.max(0.1, Math.round(s * 10) / 10) : Math.round(s);

  return (
    <Collapsible open={open} onOpenChange={setOpen} className={cn("min-w-0", className)}>
      <CollapsibleTrigger className="group flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground">
        <ChevronRight className="size-3.5 transition-transform duration-200 group-data-[state=open]:rotate-90" />
        {t("thought", { seconds })}
      </CollapsibleTrigger>
      <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
        <div className="mt-1.5 flex flex-col gap-1 border-l border-border pl-3">
          {STEP_KEYS.map((key) => (
            <Step key={key} stepKey={key} done />
          ))}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
