import "server-only";
import type { QueryResult } from "@dima/contracts";
import { toQueryResult, type EngineDataset } from "./adapter";
import { mbGet, mbPost } from "./client";
import { GatewayError } from "./errors";
import type { TenantContext } from "./guard";

// Browse data (feature 13): the company's tables and a preview of their rows.
// Read-only and open to every role; the tenant key already limits what is visible.

const PREVIEW_LIMIT = 100;

export interface BrowseTable {
  id: number;
  name: string;
  displayName: string;
  fields: { id: number; name: string; label: string }[];
}

interface EngineTable {
  id: number;
  name: string;
  display_name: string;
  schema: string;
  fields: { id: number; name: string; display_name: string; visibility_type: string }[];
}

export async function browseTables(ctx: TenantContext): Promise<BrowseTable[]> {
  const meta = await mbGet<{ tables: EngineTable[] }>(ctx.tenant, `/api/database/${ctx.tenant.databaseId}/metadata`);
  return meta.tables
    .filter((t) => t.schema === ctx.tenant.schema)
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((t) => ({
      id: t.id,
      name: t.name,
      displayName: t.display_name,
      fields: t.fields
        .filter((f) => f.visibility_type === "normal" && !/^_mb_/i.test(f.name))
        .map((f) => ({ id: f.id, name: f.name, label: f.display_name })),
    }));
}

/** First rows of one table, optionally sorted by a column. */
export async function previewTable(
  ctx: TenantContext,
  tableId: number,
  sort?: { fieldId: number; dir: "asc" | "desc" },
): Promise<QueryResult> {
  const table = (await browseTables(ctx)).find((t) => t.id === tableId);
  if (!table) throw new GatewayError(404, "Tablo bulunamadı.");
  if (sort && !table.fields.some((f) => f.id === sort.fieldId)) throw new GatewayError(400, "Geçersiz sıralama.");
  const ds = await mbPost<EngineDataset>(ctx.tenant, "/api/dataset", {
    database: ctx.tenant.databaseId,
    type: "query",
    query: {
      "source-table": tableId,
      limit: PREVIEW_LIMIT,
      ...(sort ? { "order-by": [[sort.dir, ["field", sort.fieldId, null]]] } : {}),
    },
  });
  return toQueryResult(ds);
}
