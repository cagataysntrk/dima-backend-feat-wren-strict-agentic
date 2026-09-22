import type { Metadata } from "next";
import Link from "next/link";
import { BarChart3, FileSpreadsheet, LayoutDashboard } from "lucide-react";
import { listItems, type Item } from "@/server/metabase/api";
import { GatewayError } from "@/server/metabase/errors";
import { requireTenant } from "@/server/metabase/guard";
import { NewDashboardButton } from "@/components/analytics/DashboardActions";
import { ItemMenu, LibrarySearch } from "@/components/analytics/LibraryTools";

export const metadata: Metadata = { title: "Genel bakış" };

const GROUPS: { kind: Item["kind"]; title: string; icon: typeof BarChart3; empty: string }[] = [
  { kind: "dashboard", title: "Panolar", icon: LayoutDashboard, empty: "Henüz pano yok." },
  { kind: "card", title: "Analizler", icon: BarChart3, empty: "Henüz kayıtlı analiz yok." },
  { kind: "model", title: "Yüklenen veriler", icon: FileSpreadsheet, empty: "Henüz veri yüklenmedi." },
];

export default async function Overview() {
  let items: Item[];
  let tenantName = "";
  let canEdit = false;
  try {
    const ctx = await requireTenant();
    tenantName = ctx.tenant.name;
    canEdit = ctx.role === "owner" || ctx.role === "admin";
    items = await listItems(ctx);
  } catch (e) {
    const msg = e instanceof GatewayError ? e.publicMessage : "Veriler yüklenemedi.";
    return <p className="text-sm text-muted-foreground">{msg}</p>;
  }

  return (
    <div className="space-y-10">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">{tenantName}</p>
          <h1 className="text-2xl font-semibold tracking-tight">Genel bakış</h1>
        </div>
        <div className="flex items-center gap-2">
          {canEdit && (
            <Link
              href="/app/trash"
              className="rounded-md px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              Çöp kutusu
            </Link>
          )}
          {canEdit && <NewDashboardButton />}
        </div>
      </header>
      <LibrarySearch canEdit={canEdit} />
      {GROUPS.map(({ kind, title, icon: Icon, empty }) => {
        const list = items.filter((i) => i.kind === kind);
        if (kind === "model" && list.length === 0) return null;
        return (
          <section key={kind} className="space-y-3" aria-labelledby={`h-${kind}`}>
            <h2 id={`h-${kind}`} className="text-sm font-medium text-muted-foreground">
              {title}
            </h2>
            {list.length === 0 ? (
              <p className="text-sm text-muted-foreground">{empty}</p>
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
