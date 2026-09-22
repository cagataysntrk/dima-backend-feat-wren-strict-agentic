"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Boxes, PlayCircle, ScanText, ShieldCheck, SquareCode, type LucideIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { LiveStep, Reasoning as UiReasoning, Shimmer } from "@dima/ui/ai/thinking";
import { cn } from "@dima/ui/utils";

export { Shimmer } from "@dima/ui/ai/thinking";

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
              <LiveStep
                label={i < current ? t(`stepsDone.${key}`) : t(`steps.${key}`)}
                done={i < current}
                icon={STEP_ICON[key]}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

/** Settled chain of thought — the shared block, with this app's wording. */
export function Reasoning(props: Omit<React.ComponentProps<typeof UiReasoning>, "summary">) {
  const t = useTranslations("chat");
  return <UiReasoning {...props} summary={(seconds) => t("thought", { seconds })} />;
}
