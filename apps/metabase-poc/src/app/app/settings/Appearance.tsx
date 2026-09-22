"use client";

import { useSyncExternalStore } from "react";
import { useTheme } from "next-themes";
import { useTranslations } from "next-intl";
import { Monitor, Moon, Sun } from "lucide-react";
import { cn } from "@dima/ui/utils";

const OPTIONS = [
  { value: "light", key: "light", icon: Sun },
  { value: "dark", key: "dark", icon: Moon },
  { value: "system", key: "system", icon: Monitor },
] as const;

/** Theme is read from the client only: on the server it is always unknown. */
function useMounted() {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
}

export function Appearance() {
  const { theme, setTheme } = useTheme();
  const t = useTranslations("settings.account");
  const mounted = useMounted();
  const current = mounted ? (theme ?? "system") : null;

  return (
    <div role="radiogroup" aria-label={t("theme")} className="flex flex-wrap gap-2">
      {OPTIONS.map(({ value, key, icon: Icon }) => {
        const active = current === value;
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => setTheme(value)}
            className={cn(
              "inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors",
              active
                ? "border-brand/40 bg-brand/10 text-foreground"
                : "border-[var(--surface-edge)] text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            <Icon className="size-4" aria-hidden />
            {t(key)}
          </button>
        );
      })}
    </div>
  );
}
