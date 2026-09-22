import "server-only";
import { mbGet, mbPost, mbPut } from "./client";
import { GatewayError } from "./errors";
import { assertCard, assertDashboard, requireAnalyst, type EngineDashboard, type TenantContext } from "./guard";
import { flow, widthOf, type Width } from "./layout";

// Dashboard authoring (owner/admin). Every write goes through the tenant's own
// API key and is checked against the tenant collection first.

const DATE_PARAM = { id: "p_tarih", name: "Tarih", slug: "tarih", type: "date/all-options", sectionId: "date" };

export async function createDashboard(ctx: TenantContext, name: string): Promise<{ id: number }> {
  requireAnalyst(ctx);
  const d = await mbPost<{ id: number }>(ctx.tenant, "/api/dashboard", {
    name,
    collection_id: ctx.tenant.collectionId,
    // Every new dashboard starts with a date filter; cards are wired to it as they're added.
    parameters: [DATE_PARAM],
  });
  return { id: d.id };
}

export async function updateDashboard(
  ctx: TenantContext,
  id: number,
  patch: { name?: string; description?: string | null },
): Promise<void> {
  requireAnalyst(ctx);
  await assertDashboard(ctx, id);
  await mbPut(ctx.tenant, `/api/dashboard/${id}`, patch);
}

/** Soft delete (the engine's trash) — restorable. */
export async function archiveDashboard(ctx: TenantContext, id: number): Promise<void> {
  requireAnalyst(ctx);
  await assertDashboard(ctx, id);
  await mbPut(ctx.tenant, `/api/dashboard/${id}`, { archived: true });
}

type EngineCardPayload = {
  id: number;
  card_id: number | null;
  row: number;
  col: number;
  size_x: number;
  size_y: number;
  parameter_mappings: unknown[];
  visualization_settings: Record<string, unknown>;
};

function currentCards(d: EngineDashboard): EngineCardPayload[] {
  return d.dashcards.map((dc) => ({
    id: dc.id,
    card_id: dc.card_id,
    row: dc.row,
    col: dc.col,
    size_x: dc.size_x,
    size_y: dc.size_y,
    parameter_mappings: dc.parameter_mappings,
    visualization_settings: dc.visualization_settings ?? {},
  }));
}

/**
 * Wire a card to the dashboard's filters where its table has a matching field:
 * date filter → the table's date column (prefer "tarih"); category filter →
 * the column named like the filter slug. Native-SQL cards can't be wired
 * (their filters need template tags) and simply ignore the filters.
 */
async function mappingsFor(ctx: TenantContext, d: EngineDashboard, cardId: number) {
  const card = await assertCard(ctx, cardId);
  if (card.query_type !== "query" || card.table_id == null) return { mappings: [], wired: false };
  const meta = await mbGet<{ fields: { id: number; name: string; base_type: string }[] }>(
    ctx.tenant,
    `/api/table/${card.table_id}/query_metadata`,
  );
  const dates = meta.fields.filter((f) => f.base_type.startsWith("type/Date"));
  const mappings = d.parameters.flatMap((p) => {
    const field = p.type.startsWith("date")
      ? (dates.find((f) => f.name === "tarih") ?? dates[0])
      : meta.fields.find((f) => f.name === p.slug);
    return field
      ? [{ parameter_id: p.id, card_id: cardId, target: ["dimension", ["field", field.id, null]] }]
      : [];
  });
  return { mappings, wired: mappings.length > 0 };
}

export async function addCard(
  ctx: TenantContext,
  dashboardId: number,
  cardId: number,
): Promise<{ wired: boolean }> {
  requireAnalyst(ctx);
  const d = await assertDashboard(ctx, dashboardId);
  const card = await assertCard(ctx, cardId);
  const { mappings, wired } = await mappingsFor(ctx, d, cardId);
  const cards = currentCards(d);
  const width: Width = card.display === "scalar" ? "kpi" : "half";
  const existing = d.dashcards.map((dc) => widthOf(dc.size_x, dc.card?.display ?? ""));
  const placed = flow([...existing, width]);
  cards.forEach((c, i) => Object.assign(c, placed[i]));
  cards.push({
    id: -1,
    card_id: cardId,
    ...placed[placed.length - 1],
    parameter_mappings: mappings,
    visualization_settings: {},
  });
  await mbPut(ctx.tenant, `/api/dashboard/${dashboardId}/cards`, { cards });
  return { wired };
}

/**
 * Save order + width. Widgets missing from `widgets` are removed from the
 * dashboard (the card itself stays in the collection).
 */
export async function saveLayout(
  ctx: TenantContext,
  dashboardId: number,
  widgets: { id: number; width: Width }[],
): Promise<void> {
  requireAnalyst(ctx);
  const d = await assertDashboard(ctx, dashboardId);
  const byId = new Map(currentCards(d).map((c) => [c.id, c]));
  if (widgets.some((w) => !byId.has(w.id))) throw new GatewayError(400, "Geçersiz pano düzeni.");
  const placed = flow(widgets.map((w) => w.width));
  const cards = widgets.map((w, i) => ({ ...byId.get(w.id)!, ...placed[i] }));
  await mbPut(ctx.tenant, `/api/dashboard/${dashboardId}/cards`, { cards });
}
