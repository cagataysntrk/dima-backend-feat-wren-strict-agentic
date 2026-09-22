"use client";

import { useTheme } from "next-themes";
import { useTranslations } from "next-intl";
import { Moon, Sun } from "lucide-react";
import { motion } from "motion/react";
import { Button } from "@dima/ui/primitives/button";
import { useMounted } from "@/hooks/use-mounted";
import { cn } from "@dima/ui/utils";

/**
 * Light/dark toggle. `resolvedTheme` is only known on the client, so until
 * mounted we render a stable, theme-agnostic placeholder that matches the SSR
 * output (no hydration mismatch); the theme-aware icon swaps in after mount.
 */
export function ThemeToggle({ className }: { className?: string } = {}) {
  const t = useTranslations("common");
  const { resolvedTheme, setTheme } = useTheme();
  const mounted = useMounted();
  const isDark = resolvedTheme === "dark";

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={t("theme")}
      title={mounted ? (isDark ? t("themeLight") : t("themeDark")) : undefined}
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className={cn("text-muted-foreground hover:text-foreground", className)}
    >
      {!mounted ? (
        <Sun className="size-4" />
      ) : (
        <motion.span
          key={isDark ? "moon" : "sun"}
          initial={{ opacity: 0, rotate: -90, scale: 0.6 }}
          animate={{ opacity: 1, rotate: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="flex"
        >
          {isDark ? <Moon className="size-4" /> : <Sun className="size-4" />}
        </motion.span>
      )}
    </Button>
  );
}
