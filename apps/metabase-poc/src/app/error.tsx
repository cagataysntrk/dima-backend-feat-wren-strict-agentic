"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { RotateCw } from "lucide-react";
import { BrandMark } from "@dima/ui/brand/BrandMark";
import { Button } from "@dima/ui/primitives/button";

/**
 * Route-level error boundary. Anything thrown while rendering /app lands here
 * instead of on a blank page. The message stays generic on purpose: `digest`
 * is the only safe handle on the server-side cause.
 */
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const t = useTranslations("errors");
  return (
    <main className="flex min-h-screen items-center justify-center px-5">
      <div className="max-w-md text-center">
        <BrandMark size="md" />
        <h1 className="mt-8 text-2xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="mt-3 text-sm text-muted-foreground">{t("body")}</p>
        <div className="mt-7 flex items-center justify-center gap-2">
          <Button variant="brand" onClick={reset}>
            <RotateCw className="size-4" aria-hidden />
            {t("retry")}
          </Button>
          <Button asChild variant="outline">
            <Link href="/app">{t("home")}</Link>
          </Button>
        </div>
        {error.digest && (
          // Destek istenirse aranacak tek tutamak bu — sunucu günlüğündeki
          // kaydın kimliği.
          <p className="mt-6 font-mono text-[11px] text-muted-foreground/70">{t("code", { digest: error.digest })}</p>
        )}
      </div>
    </main>
  );
}
