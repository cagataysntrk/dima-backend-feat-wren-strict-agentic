"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Languages } from "lucide-react";
import { setLocale } from "@/i18n/actions";
import { LOCALES, LOCALE_LABELS } from "@/i18n/config";
import { cn } from "@dima/ui/utils";

/**
 * Locale switcher. The choice is a cookie read on the server, so the whole
 * tree re-renders translated — no client-side message swap, no flash.
 */
export function LanguagePicker() {
  const locale = useLocale();
  const t = useTranslations("settings.account");
  const [pending, startTransition] = useTransition();

  return (
    <div className="space-y-1.5">
      <p className="text-xs text-muted-foreground">{t("language")}</p>
      <div role="radiogroup" aria-label={t("language")} className="flex flex-wrap gap-2">
        {LOCALES.map((l) => {
          const active = l === locale;
          return (
            <button
              key={l}
              type="button"
              role="radio"
              aria-checked={active}
              disabled={pending}
              onClick={() => startTransition(() => setLocale(l))}
              className={cn(
                "inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors",
                active
                  ? "border-brand/40 bg-brand/10 text-foreground"
                  : "border-[var(--surface-edge)] text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              <Languages className="size-4" aria-hidden />
              {LOCALE_LABELS[l]}
            </button>
          );
        })}
      </div>
    </div>
  );
}
