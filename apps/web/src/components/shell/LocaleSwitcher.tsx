"use client";

import { useTransition } from "react";
import { useLocale } from "next-intl";
import { useRouter } from "next/navigation";
import { Check, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { setLocale } from "@/i18n/actions";
import { LOCALES, LOCALE_LABELS } from "@/i18n/config";
import { cn } from "@/lib/utils";

/**
 * Locale picker. A server action writes the locale cookie, then we refresh so
 * `i18n/request.ts` re-reads it and re-renders the tree in the new language.
 */
export function LocaleSwitcher({ className }: { className?: string } = {}) {
  const locale = useLocale();
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  function onSelect(next: string) {
    if (next === locale) return;
    startTransition(async () => {
      await setLocale(next);
      router.refresh();
    });
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Language"
          disabled={pending}
          className={cn("text-muted-foreground hover:text-foreground", className)}
        >
          <Languages className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {LOCALES.map((l) => (
          <DropdownMenuItem key={l} onSelect={() => onSelect(l)} className="gap-2">
            <Check className={cn("size-3.5", l === locale ? "opacity-100 text-brand" : "opacity-0")} />
            {LOCALE_LABELS[l]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
