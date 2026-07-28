"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { motion } from "motion/react";
import { BrandMark } from "@/components/BrandMark";
import { ThemeToggle } from "@/components/shell/ThemeToggle";
import { LocaleSwitcher } from "@/components/shell/LocaleSwitcher";

const PILLARS = ["Deterministic", "Intelligent", "Modeled", "Agentic"];

/**
 * Premium split-screen auth layout: a forced-dark editorial brand panel (left,
 * desktop only) beside the form (right). The `dark` class on the panel pins it
 * to the dark palette in both themes for a consistent marketing surface.
 */
export function AuthShell({ children }: { children: React.ReactNode }) {
  const t = useTranslations("auth");
  return (
    <div className="grid min-h-svh lg:grid-cols-[1.05fr_1fr]">
      {/* brand panel */}
      <aside className="dark relative hidden flex-col justify-between overflow-hidden bg-background p-10 text-foreground lg:flex">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-[0.06]"
          style={{
            backgroundImage:
              "linear-gradient(var(--foreground) 1px, transparent 1px), linear-gradient(90deg, var(--foreground) 1px, transparent 1px)",
            backgroundSize: "44px 44px",
          }}
        />
        <div
          aria-hidden
          className="pointer-events-none absolute -top-24 -right-24 size-96 rounded-full opacity-20 blur-3xl"
          style={{ background: "var(--brand)" }}
        />
        <div className="relative">
          <BrandMark size="md" />
        </div>
        <div className="relative max-w-md">
          <h1 className="text-4xl font-semibold leading-tight tracking-tight">
            {t("brandHeadline")}
          </h1>
          <p className="mt-4 text-sm text-muted-foreground">{t("brandSub")}</p>
        </div>
        <div className="relative flex flex-wrap gap-2">
          {PILLARS.map((p) => (
            <span
              key={p}
              className="rounded-full border border-border px-3 py-1 font-mono text-[11px] text-muted-foreground"
            >
              {p}
            </span>
          ))}
        </div>
      </aside>

      {/* form panel */}
      <main className="relative flex items-center justify-center px-6 py-10">
        <div className="absolute top-4 right-4 flex items-center gap-1">
          <LocaleSwitcher />
          <ThemeToggle />
        </div>
        <div className="lg:hidden">
          <Link href="/" aria-label="dima" className="absolute top-4 left-4">
            <BrandMark size="sm" />
          </Link>
        </div>
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-sm"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
