import "server-only";
import type { QueryResult } from "@dima/contracts";
import { columnRefs, toQueryResult, type EngineDataset } from "./adapter";
import { mbBinary, mbGet, mbPost, mbPut } from "./client";
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
import { categoryClause, dateClause } from "./filters";
import { widthOf, type Width } from "./layout";
import { isDateFilter } from "@/lib/date-filter";
import { parameterValues as varParameters, parseVariables, templateTags } from "@/lib/sql-vars";

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

/** Goal of a "progress" card (engine visualization setting), if set. */
function goalOf(settings: Record<string, unknown> | undefined): number | null {
  const g = Number(settings?.["progress.goal"]);
  return Number.isFinite(g) && g > 0 ? g : null;
}

export async function cardData(ctx: TenantContext, cardId: number) {
  const card = await assertCard(ctx, cardId);
  const ds = await mbPost<EngineDataset>(ctx.tenant, `/api/card/${cardId}/query`);
  return {
    card: {
      id: card.id,
      name: card.name,
      description: card.description,
      display: card.display,
      goal: goalOf(card.visualization_settings),
    },
    result: toQueryResult(ds),
    drillable: card.query_type === "query" && card.table_id != null,
  };
}

/** Chart types a card may be saved as (engine display names we can render). */
export const CARD_DISPLAYS = [
  "table",
  "pivot",
  "bar",
  "row",
  "line",
  "area",
  "pie",
  "scatter",
  "combo",
  "scalar",
  "smartscalar",
  "progress",
  "funnel",
  "waterfall",
] as const;
export type CardDisplay = (typeof CARD_DISPLAYS)[number];

/** Save a card's chart type, goal or name (owner/admin). */
export async function updateCard(
  ctx: TenantContext,
  cardId: number,
  patch: { display?: CardDisplay; goal?: number | null; name?: string },
) {
  requireAnalyst(ctx);
  const card = await assertCard(ctx, cardId);
  const body: Record<string, unknown> = {};
  if (patch.name) body.name = patch.name.trim().slice(0, 120);
  if (patch.display) body.display = patch.display;
  if (patch.goal !== undefined) {
    const settings = { ...(card.visualization_settings ?? {}) };
    if (patch.goal === null) delete settings["progress.goal"];
    else settings["progress.goal"] = patch.goal;
    body.visualization_settings = settings;
  }
  if (Object.keys(body).length === 0) return { ok: true };
  await mbPut(ctx.tenant, `/api/card/${cardId}`, body);
  return { ok: true };
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
  width: Width;
  /** False when the dashboard filters don't apply to this widget (e.g. native SQL). */
  filtered: boolean;
  goal: number | null;
}

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
      width: widthOf(dc.size_x, dc.card.display),
      filtered: dc.parameter_mappings.length > 0,
      goal: goalOf(dc.card.visualization_settings),
    }));
}

/** Validate URL filters against the dashboard's parameters and build engine parameter values. */
function engineParameters(d: EngineDashboard, filters: Filters) {
  const out: { id: string; type: string; value: string | string[] }[] = [];
  for (const p of d.parameters) {
    const vals = (filters[p.slug] ?? []).filter(Boolean);
    if (!vals.length) continue;
    if (p.type.startsWith("date")) {
      if (!isDateFilter(vals[0])) throw new GatewayError(400, "Geçersiz tarih filtresi.");
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

/** Values of a category filter matching a search text (engine-side search, tenant key). */
export async function parameterSearch(ctx: TenantContext, dashboardId: number, slug: string, q: string) {
  const d = await assertDashboard(ctx, dashboardId);
  const p = d.parameters.find((x) => x.slug === slug);
  if (!p || p.type.startsWith("date")) throw new GatewayError(404, "Filtre bulunamadı.");
  const text = q.trim().slice(0, 100);
  if (!text) return parameterValues(ctx, dashboardId, slug);
  const res = await mbGet<{ values: unknown[][] }>(
    ctx.tenant,
    `/api/dashboard/${d.id}/params/${encodeURIComponent(p.id)}/search/${encodeURIComponent(text)}`,
  );
  return res.values.map((v) => String(v[0]));
}

// ── Drill-down ───────────────────────────────────────────────────────────────

const DRILL_LIMIT = 500;

type FieldRef = [string, number | string, Record<string, unknown> | null];

function isFieldRef(x: unknown): x is FieldRef {
  return Array.isArray(x) && x[0] === "field";
}

export type Scope = { dashboardId: number; dashcardId: number; filters: Filters };

/**
 * The dashboard filters currently applied to one widget, as legacy MBQL filter
 * clauses on the fields the widget is wired to (drill, zoom, break out).
 */
export async function scopeClauses(ctx: TenantContext, cardId: number, scope: Scope): Promise<unknown[][]> {
  const d = await assertDashboard(ctx, scope.dashboardId);
  const dc = d.dashcards.find((x) => x.id === scope.dashcardId && x.card_id === cardId);
  if (!dc) throw new GatewayError(404, "Kayıt bulunamadı.");
  const out: unknown[][] = [];
  for (const p of engineParameters(d, scope.filters)) {
    const m = dc.parameter_mappings.find((x) => x.parameter_id === p.id);
    const target = Array.isArray(m?.target) ? m.target[1] : null;
    if (!isFieldRef(target)) continue;
    const clause = typeof p.value === "string" ? dateClause(target, p.value) : categoryClause(target, p.value);
    if (clause) out.push(clause);
  }
  return out;
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

  if (scope) clauses.push(...(await scopeClauses(ctx, cardId, scope)));

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

/** SELECT-only native query plus its {{variables}} as engine template tags. */
function nativeQuery(ctx: TenantContext, sql: string, values: Record<string, string> = {}, asDefaults = false) {
  const check = checkSelectOnly(sql);
  if (!check.ok) throw new GatewayError(400, check.reason);
  const vars = parseVariables(check.sql);
  return {
    vars,
    query: {
      database: ctx.tenant.databaseId,
      type: "native",
      native: {
        query: check.sql,
        ...(vars.length ? { "template-tags": templateTags(vars, values, asDefaults) } : {}),
      },
    },
  };
}

export async function runSql(
  ctx: TenantContext,
  sql: string,
  values: Record<string, string> = {},
): Promise<QueryResult> {
  requireAnalyst(ctx);
  return queryReadOnly(ctx, sql, values);
}

/**
 * SELECT-only query on the tenant's own database, no role check. Used by the SQL
 * runner (after requireAnalyst) and by the chat agent, whose SQL is model output:
 * the same guard + tenant DB role apply to both.
 */
export async function queryReadOnly(
  ctx: TenantContext,
  sql: string,
  values: Record<string, string> = {},
  /** Company's own cap (chat settings); never above the hard SQL_MAX_ROWS. */
  maxRows = SQL_MAX_ROWS,
): Promise<QueryResult> {
  const cap = Math.min(maxRows, SQL_MAX_ROWS);
  const { vars, query } = nativeQuery(ctx, sql, values);
  const ds = await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", {
    ...query,
    parameters: varParameters(vars, values),
    constraints: { "max-results": cap, "max-results-bare-rows": cap },
  });
  return toQueryResult(ds);
}

export async function saveSql(
  ctx: TenantContext,
  name: string,
  sql: string,
  values: Record<string, string> = {},
) {
  requireAnalyst(ctx);
  // Current values are stored as tag defaults, so the saved card runs on its own.
  const { vars, query: dataset_query } = nativeQuery(ctx, sql, values, true);
  // Validate it runs before saving it as a shared card.
  toQueryResult(
    await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", {
      ...dataset_query,
      parameters: varParameters(vars, values),
    }),
  );
  const card = await mbPost<{ id: number }>(ctx.tenant, "/api/card", {
    name,
    dataset_query,
    display: "table",
    visualization_settings: {},
    collection_id: ctx.tenant.collectionId,
  });
  return { id: card.id };
}
