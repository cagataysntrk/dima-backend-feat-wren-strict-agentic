"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { motion } from "motion/react";
import { Composer } from "@/components/shell/Composer";
import { Badge } from "@/components/ui/badge";
import { enterUp, stagger } from "@/lib/motion";

const STORY_KEYS = Array.from({ length: 12 }, (_, index) => `s${index + 1}` as const);

/** Editorial empty state: brand, headline, composer, and example prompts. */
export function Landing({ onSubmit }: { onSubmit: (q: string) => void }) {
  const t = useTranslations();
  const [value, setValue] = useState("");

  const send = () => {
    const q = value.trim();
    if (q) onSubmit(q);
  };

  return (
    <div className="flex h-full justify-center overflow-auto px-6 py-10">
      <motion.div variants={stagger()} initial="hidden" animate="show" className="my-auto w-full max-w-4xl">
        <motion.div variants={enterUp} className="mb-7 flex flex-col items-center text-center">
          <Badge variant="brand-subtle" className="mb-4">
            {t("digitalTwin.synthetic")}
          </Badge>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            {t("common.tagline")}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Deterministic · Intelligent · Modeled · Agentic
          </p>
        </motion.div>

        <motion.div variants={enterUp} className="mx-auto max-w-2xl">
          <Composer value={value} onChange={setValue} onSubmit={send} autoFocus size="hero" />
        </motion.div>

        <motion.div variants={stagger(0.05)} className="mt-6 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {STORY_KEYS.map((key) => {
            const question = t(`digitalTwin.stories.${key}`);
            return (
            <motion.button key={key} variants={enterUp} type="button" onClick={() => onSubmit(question)}>
              <Badge
                variant="outline"
                className="h-full w-full cursor-pointer justify-start whitespace-normal px-3 py-2 text-left text-xs font-normal leading-relaxed transition-colors hover:border-brand/40 hover:bg-brand/5"
              >
                {question}
              </Badge>
            </motion.button>
            );
          })}
        </motion.div>
        <p className="mt-4 text-center text-xs text-muted-foreground">
          {t("digitalTwin.notice")}
        </p>
      </motion.div>
    </div>
  );
}
