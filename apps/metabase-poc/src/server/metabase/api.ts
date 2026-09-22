import "server-only";
import type { QueryResult } from "@dima/contracts";
import { columnRefs, toQueryResult, type EngineDataset } from "./adapter";
import { mbBinary, mbGet, mbPost } from "./client";
import { GatewayError } from "./errors";
import {
  assertCard,
  assertDashboard,
  requireAnalyst,
  type EngineDashboard,
  type EngineDashcard,
  type TenantContext,
} from "./guard";
import { checkSelectOnly } from "./sql-guard";

// High-level gateway operations. Every function takes a resolved TenantContext
// and calls the engine with THAT tenant's API key, so the engine's own
// permissions and the collection checks in guard.ts both apply.

export type ItemKind = "card" | "dashboard" | "model";

export interface Item {
  kind: ItemKind;
  id: number;
  name: string;
  description: string | null;
  display: string | null;
}

export async function listItems(ctx: TenantContext): Promise<Item[]> {
  const res = await mbGet<{
    data: { model: string; id: number; name: string; description: string | null; display?: string }[];
  }>(ctx.tenant, `/api/collection/${ctx.tenant.collectionId}/items?models=card&models=dashboard&models=dataset`);
  return res.data.map((i) => ({
    kind: i.model === "dashboard" ? "dashboard" : i.model === "dataset" ? "model" : "card",
    id: i.id,
    name: i.name,
    description: i.description,
    display: i.display ?? null,
  }));
}

export async function cardData(ctx: TenantContext, cardId: number) {
  const card = await assertCard(ctx, cardId);
  const ds = await mbPost<EngineDataset>(ctx.tenant, `/api/card/${cardId}/query`);
  return {
    card: { id: card.id, name: card.name, description: card.description, display: card.display },
    result: toQueryResult(ds),
    drillable: card.query_type === "query" && card.table_id != null,
  };
}

// ── Dashboards & filters ─────────────────────────────────────────────────────

/** Filter values from the URL, keyed by parameter slug. Date: "YYYY-MM-DD~YYYY-MM-DD"; category: one or more values. */
export type Filters = Record<string, string[]>;

export interface PublicParameter {
  slug: string;
  name: string;
  kind: "date" | "category";
}

export interface Widget {
  id: number;
  cardId: number;
  title: string;
  display: string;
  row: number;
  col: number;
  sizeX: number;
  sizeY: number;
}

const DATE_RANGE = /^\d{4}-\d{2}-\d{2}~\d{4}-\d{2}-\d{2}$/;

function publicParams(d: EngineDashboard): PublicParameter[] {
  return d.parameters.map((p) => ({
    slug: p.slug,
    name: p.name,
    kind: p.type.startsWith("date") ? "date" : "category",
  }));
}

function widgets(d: EngineDashboard): Widget[] {
  return d.dashcards
    .filter((dc): dc is EngineDashcard & { card_id: number; card: NonNullable<EngineDashcard["card"]> } =>
      dc.card_id != null && dc.card != null,
    )
    .sort((a, b) => a.row - b.row || a.col - b.col)
    .map((dc) => ({
      id: dc.id,
      cardId: dc.card_id,
      title: dc.card.name,
      display: dc.card.display,
      row: dc.row,
      col: dc.col,
      sizeX: dc.size_x,
      sizeY: dc.size_y,
    }));
}

/** Validate URL filters against the dashboard's parameters and build engine parameter values. */
function engineParameters(d: EngineDashboard, filters: Filters) {
  const out: { id: string; type: string; value: string | string[] }[] = [];
  for (const p of d.parameters) {
    const vals = (filters[p.slug] ?? []).filter(Boolean);
    if (!vals.length) continue;
    if (p.type.startsWith("date")) {
      if (!DATE_RANGE.test(vals[0])) throw new GatewayError(400, "Geçersiz tarih aralığı.");
      out.push({ id: p.id, type: p.type, value: vals[0] });
    } else {
      out.push({ id: p.id, type: p.type, value: vals.slice(0, 50) });
    }
  }
  return out;
}

export async function dashboard(ctx: TenantContext, dashboardId: number) {
  const d = await assertDashboard(ctx, dashboardId);
  return { id: d.id, name: d.name, description: d.description, parameters: publicParams(d), widgets: widgets(d) };
}

export async function dashboardData(ctx: TenantContext, dashboardId: number, filters: Filters) {
  const d = await assertDashboard(ctx, dashboardId);
  const parameters = engineParameters(d, filters);
  const ws = widgets(d);
  const results = await Promise.all(
    ws.map(async (w) => {
      try {
        const ds = await mbPost<EngineDataset>(
          ctx.tenant,
          `/api/dashboard/${d.id}/dashcard/${w.id}/card/${w.cardId}/query`,
          { parameters },
        );
        return { id: w.id, result: toQueryResult(ds) as QueryResult | null, error: null as string | null };
      } catch (e) {
        return { id: w.id, result: null, error: e instanceof GatewayError ? e.publicMessage : "Hata" };
      }
    }),
  );
  return { widgets: results };
}

export async function parameterValues(ctx: TenantContext, dashboardId: number, slug: string) {
  const d = await assertDashboard(ctx, dashboardId);
  const p = d.parameters.find((x) => x.slug === slug);
  if (!p || p.type.startsWith("date")) throw new GatewayError(404, "Filtre bulunamadı.");
  const res = await mbGet<{ values: unknown[][] }>(
    ctx.tenant,
    `/api/dashboard/${d.id}/params/${encodeURIComponent(p.id)}/values`,
  );
  return res.values.map((v) => String(v[0]));
}

// ── Drill-down ───────────────────────────────────────────────────────────────

const DRILL_LIMIT = 500;

type FieldRef = [string, number | string, Record<string, unknown> | null];

function isFieldRef(x: unknown): x is FieldRef {
  return Array.isArray(x) && x[0] === "field";
}

/**
 * Detail rows behind one bar: the card's source table, filtered to the clicked
 * category (+ the dashboard filters currently applied to that widget).
 */
export async function drill(
  ctx: TenantContext,
  cardId: number,
  column: string,
  value: string,
  scope?: { dashboardId: number; dashcardId: number; filters: Filters },
): Promise<QueryResult> {
  const card = await assertCard(ctx, cardId);
  if (card.query_type !== "query" || card.table_id == null) {
    throw new GatewayError(400, "Bu grafik için detay görünümü yok.");
  }
  const base = await mbPost<EngineDataset>(ctx.tenant, `/api/card/${cardId}/query`);
  const ref = columnRefs(base).get(column);
  if (!isFieldRef(ref) || (ref[2] && "temporal-unit" in ref[2])) {
    throw new GatewayError(400, "Bu kırılım için detay görünümü yok.");
  }
  const clauses: unknown[] = [["=", ref, value]];

  if (scope) {
    const d = await assertDashboard(ctx, scope.dashboardId);
    const dc = d.dashcards.find((x) => x.id === scope.dashcardId && x.card_id === cardId);
    if (!dc) throw new GatewayError(404, "Kayıt bulunamadı.");
    for (const p of engineParameters(d, scope.filters)) {
      const m = dc.parameter_mappings.find((x) => x.parameter_id === p.id);
      const target = Array.isArray(m?.target) ? m.target[1] : null;
      if (!isFieldRef(target)) continue;
      if (typeof p.value === "string") {
        const [from, to] = p.value.split("~");
        clauses.push(["between", target, from, to]);
      } else {
        clauses.push(["=", target, ...p.value]);
      }
    }
  }

  const ds = await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", {
    database: card.database_id,
    type: "query",
    query: {
      "source-table": card.table_id,
      filter: clauses.length === 1 ? clauses[0] : ["and", ...clauses],
      limit: DRILL_LIMIT,
    },
  });
  return toQueryResult(ds);
}

// ── Export ───────────────────────────────────────────────────────────────────

export type ExportFormat = "csv" | "xlsx";

export async function exportCard(
  ctx: TenantContext,
  cardId: number,
  format: ExportFormat,
  scope?: { dashboardId: number; dashcardId: number; filters: Filters },
): Promise<{ body: ArrayBuffer; filename: string; contentType: string }> {
  const card = await assertCard(ctx, cardId);
  const opts = { format_rows: false, pivot_results: false };
  let body: ArrayBuffer;
  if (scope) {
    const d = await assertDashboard(ctx, scope.dashboardId);
    if (!d.dashcards.some((x) => x.id === scope.dashcardId && x.card_id === cardId)) {
      throw new GatewayError(404, "Kayıt bulunamadı.");
    }
    body = await mbBinary(
      ctx.tenant,
      `/api/dashboard/${d.id}/dashcard/${scope.dashcardId}/card/${cardId}/query/${format}`,
      { ...opts, parameters: engineParameters(d, scope.filters) },
    );
  } else {
    body = await mbBinary(ctx.tenant, `/api/card/${cardId}/query/${format}`, opts);
  }
  const date = new Date().toISOString().slice(0, 10);
  return {
    body,
    filename: `dima-${slugify(card.name)}-${date}.${format}`,
    contentType:
      format === "csv"
        ? "text/csv; charset=utf-8"
        : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  };
}

export function slugify(s: string): string {
  const map: Record<string, string> = { ç: "c", ğ: "g", ı: "i", ö: "o", ş: "s", ü: "u" };
  return (
    s
      .toLocaleLowerCase("tr-TR")
      .replace(/[çğıöşü]/g, (c) => map[c])
      .normalize("NFKD")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 60) || "rapor"
  );
}

// ── Ad-hoc SQL (owner/admin) ─────────────────────────────────────────────────

const SQL_MAX_ROWS = 2000;

function nativeQuery(ctx: TenantContext, sql: string) {
  const check = checkSelectOnly(sql);
  if (!check.ok) throw new GatewayError(400, check.reason);
  return { database: ctx.tenant.databaseId, type: "native", native: { query: check.sql } };
}

export async function runSql(ctx: TenantContext, sql: string): Promise<QueryResult> {
  requireAnalyst(ctx);
  const ds = await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", {
    ...nativeQuery(ctx, sql),
    constraints: { "max-results": SQL_MAX_ROWS, "max-results-bare-rows": SQL_MAX_ROWS },
  });
  return toQueryResult(ds);
}

export async function saveSql(ctx: TenantContext, name: string, sql: string) {
  requireAnalyst(ctx);
  const dataset_query = nativeQuery(ctx, sql);
  // Validate it runs before saving it as a shared card.
  toQueryResult(await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", dataset_query));
  const card = await mbPost<{ id: number }>(ctx.tenant, "/api/card", {
    name,
    dataset_query,
    display: "table",
    visualization_settings: {},
    collection_id: ctx.tenant.collectionId,
  });
  return { id: card.id };
}
