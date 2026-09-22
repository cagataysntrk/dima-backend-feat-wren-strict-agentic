import Link from "next/link";
import { useTranslations } from "next-intl";
import { BrandMark } from "@dima/ui/brand/BrandMark";
import { Button } from "@dima/ui/primitives/button";

export default function NotFound() {
  const t = useTranslations("errors");
  return (
    <main className="flex min-h-screen items-center justify-center px-5">
      <div className="max-w-md text-center">
        <BrandMark size="md" />
        <p className="mt-8 font-mono text-xs tracking-[0.2em] text-brand">404</p>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight">{t("notFoundTitle")}</h1>
        <p className="mt-3 text-sm text-muted-foreground">{t("notFoundBody")}</p>
        <Button asChild variant="brand" className="mt-7">
          <Link href="/app">{t("home")}</Link>
        </Button>
      </div>
    </main>
  );
}
