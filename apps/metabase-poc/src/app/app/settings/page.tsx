import type { Metadata } from "next";
import Link from "next/link";
import { getTranslations } from "next-intl/server";
import { Building2, Database, MessagesSquare, UserCog, Users } from "lucide-react";
import { browseTables } from "@/server/metabase/browse";
import { GatewayError } from "@/server/metabase/errors";
import { requireTenant } from "@/server/metabase/guard";
import { shellContext } from "@/server/session";
import { chatPrefs } from "@/server/prefs";
import { Appearance } from "./Appearance";
import { ChatSettings } from "./ChatSettings";
import { CompanySwitcher } from "./CompanySwitcher";
import { Members } from "./Members";
import { LanguagePicker } from "./LanguagePicker";
import { Section } from "./Section";

export const metadata: Metadata = { title: "Ayarlar" };

export default async function SettingsPage() {
  const t = await getTranslations("settings");
  const ctx = await shellContext();

  // The data-source card is informational; a tenant without a database should
  // not take the whole settings page down with it.
  let tableCount: number | null = null;
  let databaseName = "";
  try {
    const tenant = await requireTenant();
    databaseName = tenant.tenant.name;
    tableCount = (await browseTables(tenant)).length;
  } catch (e) {
    if (!(e instanceof GatewayError)) throw e;
  }

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="text-sm text-muted-foreground">{t("subtitle")}</p>
      </header>

      <Section icon={UserCog} title={t("account.title")} hint={t("account.hint")}>
        <dl className="grid gap-3 sm:grid-cols-2">
          <div>
            <dt className="text-xs text-muted-foreground">{t("account.name")}</dt>
            <dd className="text-sm font-medium">{ctx.user.name}</dd>
          </div>
          <div className="min-w-0">
            <dt className="text-xs text-muted-foreground">{t("account.email")}</dt>
            <dd className="truncate text-sm font-medium">{ctx.user.email}</dd>
          </div>
        </dl>
        <Appearance />
        <LanguagePicker />
      </Section>

      <Section icon={Building2} title={t("company.title")} hint={t("company.hint")}>
        <CompanySwitcher orgs={ctx.orgs} activeOrgId={ctx.activeOrgId} />
      </Section>

      <Section icon={Users} title={t("members.title")} hint={t("members.hint")}>
        <Members />
      </Section>

      <Section icon={Database} title={t("sources.title")} hint={t("sources.hint")}>
        {tableCount === null ? (
          <p className="text-sm text-muted-foreground">{t("sources.none")}</p>
        ) : (
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm">
              <span className="font-medium">{databaseName}</span>{" "}
              <span className="text-muted-foreground">· {t("sources.tableCount", { count: tableCount })}</span>
            </p>
            <Link href="/app/data" className="text-sm font-medium text-brand hover:underline">
              {t("sources.viewTables")}
            </Link>
          </div>
        )}
        <p className="text-xs text-muted-foreground">{t("sources.managedElsewhere")}</p>
      </Section>

      <Section icon={MessagesSquare} title={t("chat.title")} hint={t("chat.hint")}>
        <ChatSettings initial={await chatPrefs()} canEdit={ctx.role === "owner" || ctx.role === "admin"} />
      </Section>
    </div>
  );
}
