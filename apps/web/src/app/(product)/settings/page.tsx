"use client";

import { useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { ArrowLeft, Database, Monitor, Moon, Sun, User } from "lucide-react";
import { useTheme } from "next-themes";
import { useMe } from "@/lib/access";
import { setLocale } from "@/i18n/actions";
import { LOCALES, LOCALE_LABELS } from "@/i18n/config";
import { Button } from "@dima/ui/primitives/button";
import { Separator } from "@dima/ui/primitives/separator";
import { ToggleGroup, ToggleGroupItem } from "@dima/ui/primitives/toggle-group";
import { IntegrationWizard, NoIntegrations } from "@/components/settings/IntegrationWizard";

/**
 * Ayarlar — panel değil AYRI SAYFA: kalıcı, derin ve paylaşılabilir bir URL
 * ister (/settings). Sağ panel geçici bağlam içindir.
 */
export default function SettingsPage() {
  const t = useTranslations();
  const me = useMe();
  const { theme, setTheme } = useTheme();
  const [wizard, setWizard] = useState(false);

  return (
    <main className="dima-page-in mx-auto max-w-3xl space-y-10 px-6 py-10">
      <header className="space-y-3">
        <Button variant="ghost" size="sm" asChild className="-ml-2 gap-1.5">
          <Link href="/app">
            <ArrowLeft className="size-4" />
            Sohbete dön
          </Link>
        </Button>
        <h1 className="text-2xl font-semibold tracking-tight">{t("common.settings")}</h1>
      </header>

      <Section icon={User} title="Hesap">
        <Row label="E-posta">
          <span className="text-sm text-muted-foreground">{me?.email ?? "…"}</span>
        </Row>
        {me?.roles?.length ? (
          <Row label="Roller">
            <span className="text-sm text-muted-foreground">{me.roles.join(", ")}</span>
          </Row>
        ) : null}
      </Section>

      <Section icon={Sun} title="Görünüm">
        <Row label="Tema">
          <ToggleGroup
            type="single"
            size="sm"
            variant="outline"
            value={theme}
            onValueChange={(v) => v && setTheme(v)}
          >
            <ToggleGroupItem value="light" className="gap-1.5 px-2.5 text-xs">
              <Sun className="size-3.5" />
              {t("common.themeLight")}
            </ToggleGroupItem>
            <ToggleGroupItem value="dark" className="gap-1.5 px-2.5 text-xs">
              <Moon className="size-3.5" />
              {t("common.themeDark")}
            </ToggleGroupItem>
            <ToggleGroupItem value="system" className="gap-1.5 px-2.5 text-xs">
              <Monitor className="size-3.5" />
              {t("common.themeSystem")}
            </ToggleGroupItem>
          </ToggleGroup>
        </Row>
        <Row label={t("common.language")}>
          <ToggleGroup
            type="single"
            size="sm"
            variant="outline"
            onValueChange={(v) => v && void setLocale(v)}
          >
            {LOCALES.map((l) => (
              <ToggleGroupItem key={l} value={l} className="px-2.5 text-xs">
                {LOCALE_LABELS[l]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </Row>
      </Section>

      <Section icon={Database} title="Veri kaynakları">
        {wizard ? (
          <IntegrationWizard onCancel={() => setWizard(false)} />
        ) : (
          <NoIntegrations onAdd={() => setWizard(true)} />
        )}
      </Section>
    </main>
  );
}

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4">
      <div className="flex items-center gap-2">
        <Icon className="size-4 text-muted-foreground" />
        <h2 className="text-sm font-medium">{title}</h2>
      </div>
      <Separator />
      <div className="space-y-4">{children}</div>
    </section>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <span className="text-sm text-foreground">{label}</span>
      {children}
    </div>
  );
}
