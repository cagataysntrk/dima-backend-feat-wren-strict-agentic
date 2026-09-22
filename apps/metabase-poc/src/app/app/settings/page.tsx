import type { Metadata } from "next";
import Link from "next/link";
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
import { Section } from "./Section";

export const metadata: Metadata = { title: "Ayarlar" };

export default async function SettingsPage() {
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
        <h1 className="text-2xl font-semibold tracking-tight">Ayarlar</h1>
        <p className="text-sm text-muted-foreground">Hesabınız, şirketiniz ve sohbetin nasıl çalıştığı.</p>
      </header>

      <Section icon={UserCog} title="Hesap ve görünüm" hint="Oturum açtığınız hesap ve arayüz teması.">
        <dl className="grid gap-3 sm:grid-cols-2">
          <div>
            <dt className="text-xs text-muted-foreground">Ad</dt>
            <dd className="text-sm font-medium">{ctx.user.name}</dd>
          </div>
          <div className="min-w-0">
            <dt className="text-xs text-muted-foreground">E-posta</dt>
            <dd className="truncate text-sm font-medium">{ctx.user.email}</dd>
          </div>
        </dl>
        <Appearance />
      </Section>

      <Section icon={Building2} title="Şirket" hint="Verilerini gördüğünüz şirket.">
        <CompanySwitcher orgs={ctx.orgs} activeOrgId={ctx.activeOrgId} />
      </Section>

      <Section icon={Users} title="Üyeler ve roller" hint="Kimin neye erişebildiği. Rolleri şirket sahibi yönetir.">
        <Members />
      </Section>

      <Section icon={Database} title="Veri kaynakları" hint="Sorguların çalıştığı veritabanı.">
        {tableCount === null ? (
          <p className="text-sm text-muted-foreground">Bu şirket için tanımlı veri kaynağı bulunamadı.</p>
        ) : (
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm">
              <span className="font-medium">{databaseName}</span>{" "}
              <span className="text-muted-foreground">· {tableCount} tablo</span>
            </p>
            <Link href="/app/data" className="text-sm font-medium text-brand hover:underline">
              Tabloları görüntüle
            </Link>
          </div>
        )}
        <p className="text-xs text-muted-foreground">
          Bağlantı ayarları yönetici tarafında tutulur; buradan değiştirilemez.
        </p>
      </Section>

      <Section icon={MessagesSquare} title="Sohbet tercihleri" hint="Sorularınızı hangi modelin yanıtladığı.">
        <ChatSettings initial={await chatPrefs()} canEdit={ctx.role === "owner" || ctx.role === "admin"} />
      </Section>
    </div>
  );
}
