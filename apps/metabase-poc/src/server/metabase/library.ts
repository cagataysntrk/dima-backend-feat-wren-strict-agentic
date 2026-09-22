import "server-only";
import { mbGet, mbPost, mbPut } from "./client";
import { GatewayError } from "./errors";
import { assertCard, assertDashboard, requireAnalyst, type TenantContext } from "./guard";
import type { Item, ItemKind } from "./api";

// Organizing (feature 6): search, duplicate, archive and restore.
// Archiving is the engine's trash — reversible, and the card/dashboard keeps
// its id, so links and dashboards survive a restore.

interface SearchHit {
  model: string;
  id: number;
  name: string;
  description: string | null;
  display?: string;
  collection?: { id?: number | null; type?: string | null } | null;
  archived?: boolean;
}

const KIND: Record<string, ItemKind> = { card: "card", dashboard: "dashboard", dataset: "model" };

async function search(ctx: TenantContext, q: string, archived: boolean): Promise<Item[]> {
  const params = new URLSearchParams({ q, archived: String(archived) });
  for (const m of ["card", "dashboard", "dataset"]) params.append("models", m);
  const res = await mbGet<{ data: SearchHit[] }>(ctx.tenant, `/api/search?${params}`);
  return res.data
    // Live items must sit in the tenant's own collection. Archived ones are
    // reported in the engine's trash collection instead; those are already
    // permission-scoped per tenant (another tenant's trash is not returned).
    .filter((h) => KIND[h.model] && (archived ? h.collection?.type === "trash" : h.collection?.id === ctx.tenant.collectionId))
    .map((h) => ({
      kind: KIND[h.model],
      id: h.id,
      name: h.name,
      description: h.description,
      display: h.display ?? null,
    }));
}

export const searchLibrary = (ctx: TenantContext, q: string) => search(ctx, q.trim().slice(0, 100), false);
export const trashItems = (ctx: TenantContext) => search(ctx, "", true);

type Kind = "card" | "dashboard";

async function assertItem(ctx: TenantContext, kind: Kind, id: number) {
  if (kind === "card") await assertCard(ctx, id);
  else await assertDashboard(ctx, id);
}

/** Move to / restore from the engine's trash (owner/admin). */
export async function setArchived(ctx: TenantContext, kind: Kind, id: number, archived: boolean) {
  requireAnalyst(ctx);
  if (!archived) {
    // An archived item is not visible to the collection checks, so verify by
    // looking it up in this tenant's trash instead.
    const inTrash = (await trashItems(ctx)).some((i) => i.id === id && (i.kind === kind || (kind === "card" && i.kind === "model")));
    if (!inTrash) throw new GatewayError(404, "Kayıt bulunamadı.");
  } else {
    await assertItem(ctx, kind, id);
  }
  await mbPut(ctx.tenant, `/api/${kind}/${id}`, { archived });
  return { ok: true };
}

/** Copy a card into the same collection (owner/admin). */
export async function duplicateCard(ctx: TenantContext, cardId: number) {
  requireAnalyst(ctx);
  await assertCard(ctx, cardId);
  const copy = await mbPost<{ id: number; name: string }>(ctx.tenant, `/api/card/${cardId}/copy`);
  return { id: copy.id, name: copy.name };
}
