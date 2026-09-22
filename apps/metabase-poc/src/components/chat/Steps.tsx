"use client";

import { AnimatePresence, motion } from "motion/react";
import { useTranslations } from "next-intl";
import { Database, FileSearch, Loader, PenLine, type LucideIcon } from "lucide-react";
import { LiveStep, Reasoning, Shimmer } from "@dima/ui/ai/thinking";
import { cn } from "@dima/ui/utils";

export interface Step {
  id: number;
  text: string;
  done: boolean;
}

/** Icon guessed from the step's own wording — no second source of truth. */
function iconFor(text: string): LucideIcon {
  if (/şema/i.test(text)) return FileSearch;
  if (/yazıl|düzelt|hazırlan/i.test(text)) return PenLine;
  if (/çalış|sorgu/i.test(text)) return Database;
  return Loader;
}

/**
 * Live steps while an answer is produced. Unlike apps/web's timed placeholder,
 * every line here is an event the server actually sent.
 */
export function LiveSteps({
  steps,
  streaming = false,
  className,
}: {
  steps: Step[];
  /** The answer itself is arriving — the "looking at data" line is over. */
  streaming?: boolean;
  className?: string;
}) {
  const t = useTranslations("chat");
  if (steps.length === 0) return null;
  return (
    <div className={cn("flex min-w-0 flex-col gap-1.5 pt-1", className)} role="status">
      {!streaming && <Shimmer className="text-sm font-medium">{t("thinking")}</Shimmer>}
      <div className="flex flex-col gap-1 border-l border-border pl-3">
        <AnimatePresence initial={false}>
          {steps.map((s) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            >
              <LiveStep label={s.text} done={s.done} icon={iconFor(s.text)} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

/** Settled steps above a finished answer: "7 sn düşündü", collapsed. */
export function Thought({ steps, durationMs }: { steps: string[]; durationMs?: number }) {
  const t = useTranslations("chat");
  if (steps.length === 0) return null;
  return <Reasoning trace={steps} durationMs={durationMs} summary={(n) => t("thought", { seconds: n })} />;
}
