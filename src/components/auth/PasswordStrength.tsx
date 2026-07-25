"use client";

import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

// Lightweight heuristic (no zxcvbn dep): length + character-class variety → 0–4.
export function scorePassword(pw: string): number {
  if (!pw) return 0;
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  const classes = [/[a-z]/, /[A-Z]/, /\d/, /[^A-Za-z0-9]/].filter((r) => r.test(pw)).length;
  if (classes >= 2) score++;
  if (classes >= 3) score++;
  return Math.min(4, score);
}

const BAR = ["bg-destructive", "bg-destructive", "bg-amber-500", "bg-amber-400", "bg-emerald-500"];

/** Four-segment strength meter with a label. Shown once the user starts typing. */
export function PasswordStrength({ value }: { value: string }) {
  const t = useTranslations("auth.strength");
  if (!value) return null;
  const score = scorePassword(value);
  const labels = [t("weak"), t("weak"), t("fair"), t("good"), t("strong")];

  return (
    <div className="space-y-1" aria-live="polite">
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            className={cn(
              "h-1 flex-1 rounded-full transition-colors",
              i < score ? BAR[score] : "bg-border",
            )}
          />
        ))}
      </div>
      <p className="text-[11px] text-muted-foreground">
        {t("label")}: <span className="text-foreground">{labels[score]}</span>
      </p>
    </div>
  );
}
