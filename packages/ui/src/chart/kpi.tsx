"use client";

import { motion } from "motion/react";
import type { QueryResult } from "@dima/contracts";
import { kpiCards, type Analysis } from "@dima/domain";
import { enterUp, stagger } from "../motion";
import { Card } from "../primitives/card";
import { cn } from "../utils";

/**
 * KPI / stat tiles for single-row results (the Tremor "metric card" pattern,
 * implemented on shadcn + our tokens to stay Tailwind-v4 native).
 */
export function KpiGrid({
  result,
  analysis,
  className,
}: {
  result: QueryResult;
  analysis: Analysis;
  className?: string;
}) {
  const cards = kpiCards(result, analysis);
  return (
    <motion.div
      variants={stagger()}
      initial="hidden"
      animate="show"
      className={cn("grid grid-cols-2 gap-3 sm:grid-cols-3", className)}
    >
      {cards.map((c) => (
        <motion.div key={c.label} variants={enterUp}>
        <Card className="min-w-0 gap-1.5 p-4">
          <div
            title={c.value}
            className="truncate font-mono text-xl leading-none tracking-tight tabular-nums text-foreground sm:text-2xl"
          >
            {c.value}
          </div>
          <div className="mt-1 truncate text-xs font-medium tracking-wide text-muted-foreground uppercase">
            {c.label}
          </div>
          {c.ctx && <div className="font-mono text-xs text-muted-foreground">{c.ctx}</div>}
        </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
