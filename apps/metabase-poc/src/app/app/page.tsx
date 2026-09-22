import type { Metadata } from "next";
import Link from "next/link";
import { getTranslations } from "next-intl/server";
import { BarChart3, FileSpreadsheet, LayoutDashboard } from "lucide-react";
import { listItems, type Item } from "@/server/metabase/api";
import { GatewayError } from "@/server/metabase/errors";
import { requireTenant } from "@/server/metabase/guard";
import { NewDashboardButton } from "@/components/analytics/DashboardActions";
import { ItemMenu, LibrarySearch } from "@/components/analytics/LibraryTools";
import { EmptyState } from "@/components/shell/EmptyState";

export const metadata: Metadata = { title: "dima" };

/** Message keys per group; the wording lives in messages/*.json. */
const GROUPS = [
  { kind: "dashboard", title: "dashboards", icon: LayoutDashboard, empty: "emptyDashboards", hint: "hintDashboards" },
  { kind: "card", title: "analyses", icon: BarChart3, empty: "emptyAnalyses", hint: "hintAnalyses" },
  { kind: "model", title: "uploads", icon: FileSpreadsheet, empty: "emptyUploads", hint: "hintUploads" },
] as const satisfies readonly { kind: Item["kind"]; title: string; icon: typeof BarChart3; empty: string; hint: string }[];

export default async function Overview() {
  const t = await getTranslations("overview");
  const tNav = await getTranslations("nav");
  let items: Item[];
  let tenantName = "";
  let canEdit = false;
  try {
    const ctx = await requireTenant();
    tenantName = ctx.tenant.name;
    canEdit = ctx.role === "owner" || ctx.role === "admin";
    items = await listItems(ctx);
  } catch (e) {
    const msg = e instanceof GatewayError ? e.publicMessage : t("loadFailed");
    return <p className="text-sm text-muted-foreground">{msg}</p>;
  }

  return (
    <div className="space-y-10">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">{tenantName}</p>
          <h1 className="text-2xl font-semibold tracking-tight">{t("title")}</h1>
        </div>
        <div className="flex items-center gap-2">
          {canEdit && (
            <Link
              href="/app/trash"
              className="rounded-md px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {tNav("trash")}
            </Link>
          )}
          {canEdit && <NewDashboardButton />}
        </div>
      </header>
      <LibrarySearch canEdit={canEdit} />
      {GROUPS.map(({ kind, title, icon: Icon, empty, hint }) => {
        const list = items.filter((i) => i.kind === kind);
        if (kind === "model" && list.length === 0) return null;
        return (
          <section key={kind} className="space-y-3" aria-labelledby={`h-${kind}`}>
            <h2 id={`h-${kind}`} className="text-sm font-medium text-muted-foreground">
              {t(title)}
            </h2>
            {list.length === 0 ? (
              <div className="surface-sm">
                <EmptyState
                  icon={Icon}
                  title={t(empty)}
                  hint={t(hint)}
                  action={
                    kind === "card" ? (
                      <Link href="/app/chat" className="text-sm font-medium text-brand hover:underline">
                        {t("goToChat")}
                      </Link>
                    ) : kind === "model" && canEdit ? (
                      <Link href="/app/upload" className="text-sm font-medium text-brand hover:underline">
                        {t("uploadData")}
                      </Link>
                    ) : undefined
                  }
                />
              </div>
            ) : (
              <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {list.map((i) => (
                  <li key={`${i.kind}-${i.id}`} className="relative">
                    {canEdit && i.kind === "card" && (
                      <span className="absolute top-2 right-2 z-10">
                        <ItemMenu item={i} />
                      </span>
                    )}
                    <Link
                      href={i.kind === "dashboard" ? `/app/dashboards/${i.id}` : `/app/cards/${i.id}`}
                      className="group flex h-full min-h-32 flex-col items-center justify-center gap-3 p-5 text-center surface surface-interactive"
                    >
                      <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-brand/10 text-brand">
                        <Icon className="size-4" aria-hidden />
                      </span>
                      <span className="min-w-0 max-w-full">
                        <span className="block font-medium group-hover:text-foreground">{i.name}</span>
                        {i.description && (
                          <span className="mt-0.5 line-clamp-2 block text-sm text-muted-foreground">
                            {i.description}
                          </span>
                        )}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>
        );
      })}
    </div>
  );
}
