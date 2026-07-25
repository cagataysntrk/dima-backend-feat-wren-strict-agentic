"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { motion } from "motion/react";
import { Composer } from "@/components/shell/Composer";
import { Badge } from "@/components/ui/badge";
import { enterUp, stagger } from "@/lib/motion";

// Örnek sorular — boyahane demo alanı (docs/research terminoloji). Tıklanınca gönderilir.
const EXAMPLES = [
  "Makine bazında OEE",
  "Bu ay toplam üretim",
  "Aşama bazında toplam fire",
  "Vardiya × haftanın günü verimliliği",
];

/** Editorial empty state: brand, headline, composer, and example prompts. */
export function Landing({ onSubmit }: { onSubmit: (q: string) => void }) {
  const t = useTranslations();
  const [value, setValue] = useState("");

  const send = () => {
    const q = value.trim();
    if (q) onSubmit(q);
  };

  return (
    <div className="flex h-full items-center justify-center overflow-auto px-6 py-10">
      <motion.div variants={stagger()} initial="hidden" animate="show" className="w-full max-w-2xl">
        <motion.div variants={enterUp} className="mb-8 flex flex-col items-center text-center">
          <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            {t("common.tagline")}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Deterministic · Intelligent · Modeled · Agentic
          </p>
        </motion.div>

        <motion.div variants={enterUp}>
          <Composer value={value} onChange={setValue} onSubmit={send} autoFocus size="hero" />
        </motion.div>

        <motion.div variants={stagger(0.1)} className="mt-4 flex flex-wrap justify-center gap-2">
          {EXAMPLES.map((ex) => (
            <motion.button key={ex} variants={enterUp} type="button" onClick={() => onSubmit(ex)}>
              <Badge
                variant="outline"
                className="cursor-pointer px-3 py-1 text-xs font-normal transition-colors hover:border-brand/40 hover:bg-brand/5"
              >
                {ex}
              </Badge>
            </motion.button>
          ))}
        </motion.div>
      </motion.div>
    </div>
  );
}
