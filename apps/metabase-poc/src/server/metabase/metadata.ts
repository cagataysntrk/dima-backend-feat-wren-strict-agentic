import "server-only";
import { mbGet } from "./client";
import type { TenantContext } from "./guard";

const SCHEMA_TTL_MS = 10 * 60_000;

export interface TableSchema {
  schema: string;
  name: string;
  columns: { name: string; type: string; label?: string }[];
}

const schemaCache = new Map<string, { at: number; tables: TableSchema[] }>();

/**
 * Tenant-visible table and column metadata.
 *
 * This is a generic product/data-model operation, not chat intelligence.
 * Keep it in the Metabase adapter layer so removing the legacy custom agent
 * cannot break the existing "Tablolar" UI surface.
 */
export async function tenantTables(ctx: TenantContext): Promise<TableSchema[]> {
  const hit = schemaCache.get(ctx.tenant.slug);
  if (hit && Date.now() - hit.at < SCHEMA_TTL_MS) return hit.tables;

  const meta = await mbGet<{
    tables: {
      schema: string;
      name: string;
      visibility_type: string | null;
      fields: {
        name: string;
        display_name: string;
        database_type: string;
        visibility_type: string;
      }[];
    }[];
  }>(ctx.tenant, `/api/database/${ctx.tenant.databaseId}/metadata`);

  const tables: TableSchema[] = meta.tables
    .filter((table) => table.schema === ctx.tenant.schema && !table.visibility_type)
    .map((table) => ({
      schema: table.schema,
      name: table.name,
      columns: table.fields
        .filter(
          (field) =>
            field.visibility_type === "normal" &&
            !/^_mb_/i.test(field.name),
        )
        .map((field) => ({
          name: field.name,
          type: field.database_type,
          label:
            field.display_name &&
            field.display_name.toLowerCase() !==
              field.name.replace(/_/g, " ")
              ? field.display_name
              : undefined,
        })),
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  schemaCache.set(ctx.tenant.slug, { at: Date.now(), tables });
  return tables;
}
