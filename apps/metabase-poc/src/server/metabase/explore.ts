import "server-only";
import { randomUUID } from "node:crypto";
import type { QueryResult } from "@dima/contracts";
import { toQueryResult, type EngineDataset } from "./adapter";
import { scopeClauses, type Scope } from "./api";
import { mbGet, mbPost } from "./client";
import { GatewayError } from "./errors";
import { assertCard, type TenantContext } from "./guard";
import { ZOOM_TO, periodRange, toMbql5, type TimeUnit } from "./mbql5";

// Exploration from a chart point (feature 4), built on the card's own MBQL 5
// query so the measure stays exactly what the card defines:
//   zoom      — a time bucket opens at the next finer granularity
//   break out — a category's measure split by another column of the table

type Stage = { breakout?: unknown[][]; filters?: unknown[]; "order-by"?: unknown } & Record<string, unknown>;
type FieldClause = [string, Record<string, unknown>, number | string];

const uuid = () => randomUUID();

/** The card's single-stage query with exactly one breakout, or a 400. */
async function singleBreakoutQuery(ctx: TenantContext, cardId: number) {
  const card = await assertCard(ctx, cardId);
  const q = card.dataset_query;
  const stage = q?.stages?.length === 1 ? (q.stages[0] as Stage) : null;
  const bo = stage?.breakout?.length === 1 ? (stage.breakout[0] as FieldClause) : null;
  if (card.query_type !== "query" || !q || !stage || !bo || bo[0] !== "field" || card.table_id == null) {
    throw new GatewayError(400, "Bu grafik keşfe uygun değil.");
  }
  return { card, query: structuredClone(q), breakout: bo, tableId: card.table_id };
}

async function run(ctx: TenantContext, query: unknown): Promise<QueryResult> {
  return toQueryResult(await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", query));
}

async function withScope(ctx: TenantContext, cardId: number, scope?: Scope): Promise<unknown[]> {
  return scope ? (await scopeClauses(ctx, cardId, scope)).map((c) => toMbql5(c, uuid)) : [];
}

export async function zoom(ctx: TenantContext, cardId: number, value: string, scope?: Scope) {
  const { query, breakout } = await singleBreakoutQuery(ctx, cardId);
  const opts = breakout[1];
  const unit = opts["temporal-unit"] as TimeUnit | undefined;
  const next = unit ? ZOOM_TO[unit] : null;
  if (!unit || !next) throw new GatewayError(400, "Bu dönem daha fazla açılamaz.");
  const range = periodRange(value, unit);
  if (!range) throw new GatewayError(400, "Geçersiz dönem.");

  const stage = query.stages![0] as Stage;
  const { "temporal-unit": _drop, ...plain } = opts;
  void _drop;
  stage.breakout = [["field", { ...opts, "temporal-unit": next, "lib/uuid": uuid() }, breakout[2]]];
  stage.filters = [
    ...(stage.filters ?? []),
    ["between", { "lib/uuid": uuid() }, ["field", { ...plain, "lib/uuid": uuid() }, breakout[2]], ...range],
    ...(await withScope(ctx, cardId, scope)),
  ];
  delete stage["order-by"];
  return { result: await run(ctx, query), unit: next, range };
}

interface TableField {
  id: number;
  name: string;
  display_name: string;
  base_type: string;
  semantic_type: string | null;
  visibility_type: string;
  fingerprint?: { global?: { "distinct-count"?: number } } | null;
}

/**
 * Text/boolean columns are categories. Integers usually are quantities (counts,
 * grams, cm) and the engine gives them no semantic type, so an integer only
 * counts as a category when the engine says so or its name marks it as a code
 * (shift, code, type, class, group, level). Feature 7 (data model) will let
 * admins mark categories explicitly.
 */
const CODE_NAME = /(vardiya|shift|kod|code|tip|type|tur|sinif|class|grup|group|seviye|level)/i;

function isCategory(f: TableField): boolean {
  if (/Text|Boolean/.test(f.base_type)) return true;
  if (!f.base_type.includes("Integer")) return false;
  return f.semantic_type === "type/Category" || CODE_NAME.test(f.name);
}

/** Categorical columns a card's measure can be split by (2–50 distinct values, not dates/keys). */
export async function breakoutOptions(ctx: TenantContext, cardId: number) {
  const { breakout, tableId } = await singleBreakoutQuery(ctx, cardId);
  const meta = await mbGet<{ fields: TableField[] }>(ctx.tenant, `/api/table/${tableId}/query_metadata`);
  return meta.fields
    .filter((f) => {
      const n = f.fingerprint?.global?.["distinct-count"] ?? 0;
      return (
        f.id !== breakout[2] &&
        f.visibility_type === "normal" &&
        !f.base_type.startsWith("type/Date") &&
        !/PK|FK/.test(f.semantic_type ?? "") &&
        isCategory(f) &&
        n >= 2 &&
        n <= 50
      );
    })
    .map((f) => ({ id: f.id, name: f.name, label: f.display_name, baseType: f.base_type }));
}

export async function breakoutBy(
  ctx: TenantContext,
  cardId: number,
  value: string,
  fieldId: number,
  scope?: Scope,
) {
  const { query, breakout } = await singleBreakoutQuery(ctx, cardId);
  const option = (await breakoutOptions(ctx, cardId)).find((f) => f.id === fieldId);
  if (!option) throw new GatewayError(400, "Bu kırılım kullanılamaz.");
  const stage = query.stages![0] as Stage;
  const opts = breakout[1];
  const typed = /Integer|Float|Decimal/.test(String(opts["base-type"] ?? "")) && value.trim() !== "" ? Number(value) : value;
  stage.filters = [
    ...(stage.filters ?? []),
    ["=", { "lib/uuid": uuid() }, ["field", { ...opts, "lib/uuid": uuid() }, breakout[2]], typed],
    ...(await withScope(ctx, cardId, scope)),
  ];
  stage.breakout = [
    ["field", { "lib/uuid": uuid(), "base-type": option.baseType, "effective-type": option.baseType }, option.id],
  ];
  // Largest first, like the source card's categorical order.
  stage["order-by"] = [["desc", { "lib/uuid": uuid() }, ["aggregation", { "lib/uuid": uuid() }, firstAggUuid(stage)]]];
  return { result: await run(ctx, query), by: option.label };
}

/** MBQL 5 aggregation refs point at the aggregation's lib/uuid. */
function firstAggUuid(stage: Stage): string {
  const agg = (stage.aggregation as unknown[][] | undefined)?.[0];
  const opts = agg?.[1] as Record<string, unknown> | undefined;
  const id = opts?.["lib/uuid"];
  if (typeof id !== "string") throw new GatewayError(400, "Bu grafik keşfe uygun değil.");
  return id;
}
