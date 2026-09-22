import "server-only";
import { mbGet, mbPut } from "./client";
import { GatewayError } from "./errors";
import { requireAnalyst, type TenantContext } from "./guard";

// Data model (owner/admin): friendly column names, which columns are
// categories, and which are hidden. The engine stores this per field, so it
// also feeds the break-out list (explore.ts) and the chat's schema.

export interface ModelField {
  id: number;
  name: string;
  displayName: string;
  type: string;
  category: boolean;
  hidden: boolean;
  /** Column this one points at, when a relationship has been declared. */
  fkTargetFieldId: number | null;
}

export interface ModelTable {
  id: number;
  name: string;
  displayName: string;
  fields: ModelField[];
}

interface EngineField {
  id: number;
  name: string;
  display_name: string;
  base_type: string;
  semantic_type: string | null;
  visibility_type: string;
  table_id: number;
  fk_target_field_id?: number | null;
}

const toField = (f: EngineField): ModelField => ({
  id: f.id,
  name: f.name,
  displayName: f.display_name,
  type: f.base_type.replace("type/", ""),
  category: f.semantic_type === "type/Category",
  hidden: f.visibility_type !== "normal",
  fkTargetFieldId: f.fk_target_field_id ?? null,
});

/** The tenant's tables with their columns (engine metadata includes hidden fields). */
export async function dataModel(ctx: TenantContext): Promise<ModelTable[]> {
  const meta = await mbGet<{
    tables: { id: number; name: string; display_name: string; schema: string; fields: EngineField[] }[];
  }>(ctx.tenant, `/api/database/${ctx.tenant.databaseId}/metadata?include_hidden=true`);
  return meta.tables
    .filter((t) => t.schema === ctx.tenant.schema)
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((t) => ({
      id: t.id,
      name: t.name,
      displayName: t.display_name,
      fields: t.fields.map(toField).sort((a, b) => a.name.localeCompare(b.name)),
    }));
}

export interface FieldPatch {
  displayName?: string;
  category?: boolean;
  hidden?: boolean;
}

/**
 * Update one column.
 *
 * Ownership is proven with the TENANT key: engine permissions only let a tenant
 * read fields of its own database, so a successful read means the field is
 * theirs. The write itself needs "manage table metadata", which the OSS edition
 * grants to admins only, so it goes out with the admin key — never on the
 * caller's say-so, always after that check.
 */
export async function updateField(ctx: TenantContext, fieldId: number, patch: FieldPatch): Promise<ModelField> {
  requireAnalyst(ctx);
  const field = await mbGet<EngineField & { table?: { db_id?: number } }>(ctx.tenant, `/api/field/${fieldId}`);
  const dbId = field.table?.db_id;
  if (dbId !== undefined && dbId !== ctx.tenant.databaseId) throw new GatewayError(404, "Kayıt bulunamadı.");

  const body: Record<string, unknown> = {};
  if (patch.displayName !== undefined) {
    const name = patch.displayName.trim();
    if (!name) throw new GatewayError(400, "Sütun adı boş olamaz.");
    body.display_name = name.slice(0, 120);
  }
  if (patch.category !== undefined) {
    // Only flip the category flag; never clobber another semantic type the engine inferred.
    if (patch.category) body.semantic_type = "type/Category";
    else if (field.semantic_type === "type/Category") body.semantic_type = null;
  }
  if (patch.hidden !== undefined) body.visibility_type = patch.hidden ? "sensitive" : "normal";
  if (Object.keys(body).length === 0) return toField(field);

  return toField(await mbPut<EngineField>("admin", `/api/field/${fieldId}`, body));
}

// ── Schema graph ─────────────────────────────────────────────────────────────

export interface SchemaColumn {
  id: number;
  name: string;
  type: string;
  /** This column points at another table's column (engine FK or set here). */
  fkTargetFieldId: number | null;
}

export interface SchemaTable {
  id: number;
  name: string;
  displayName: string;
  columns: SchemaColumn[];
}

export interface SchemaEdge {
  id: string;
  from: string;
  fromColumn: string;
  to: string;
  toColumn: string;
}

export interface SchemaGraph {
  tables: SchemaTable[];
  edges: SchemaEdge[];
}

/**
 * Tables, their columns and the relationships between them.
 *
 * Demo tables were loaded from CSV and carry no database-level foreign keys,
 * so the engine knows none until someone sets them in the data model — the
 * graph draws what is actually declared, never a guess from column names.
 */
export async function schemaGraph(ctx: TenantContext): Promise<SchemaGraph> {
  const meta = await mbGet<{
    tables: {
      id: number;
      name: string;
      display_name: string;
      schema: string;
      fields: EngineField[];
    }[];
  }>(ctx.tenant, `/api/database/${ctx.tenant.databaseId}/metadata`);

  const own = meta.tables.filter((t) => t.schema === ctx.tenant.schema);
  const tables: SchemaTable[] = own
    .map((t) => ({
      id: t.id,
      name: t.name,
      displayName: t.display_name,
      columns: t.fields
        .filter((f) => f.visibility_type === "normal" && !/^_mb_/i.test(f.name))
        .map((f) => ({
          id: f.id,
          name: f.name,
          type: f.base_type.replace("type/", ""),
          fkTargetFieldId: f.fk_target_field_id ?? null,
        }))
        .sort((a, b) => a.name.localeCompare(b.name)),
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  // Where each field lives, so an FK target resolves to a table and column.
  const where = new Map<number, { table: string; column: string }>();
  for (const t of own) for (const f of t.fields) where.set(f.id, { table: t.name, column: f.name });

  const edges: SchemaEdge[] = [];
  for (const t of tables) {
    for (const c of t.columns) {
      if (c.fkTargetFieldId === null) continue;
      const target = where.get(c.fkTargetFieldId);
      // A target outside this tenant's schema is not ours to draw.
      if (!target) continue;
      edges.push({
        id: `fk-${c.id}`,
        from: t.name,
        fromColumn: c.name,
        to: target.table,
        toColumn: target.column,
      });
    }
  }
  return { tables, edges };
}

/**
 * Point a column at another column (or clear it). Same two-key dance as
 * updateField: ownership proven with the tenant key, write with the admin key,
 * and the target must belong to the same database.
 */
export async function setForeignKey(
  ctx: TenantContext,
  fieldId: number,
  targetFieldId: number | null,
): Promise<ModelField> {
  requireAnalyst(ctx);
  const field = await mbGet<EngineField & { table?: { db_id?: number } }>(ctx.tenant, `/api/field/${fieldId}`);
  if (field.table?.db_id !== undefined && field.table.db_id !== ctx.tenant.databaseId) {
    throw new GatewayError(404, "Kayıt bulunamadı.");
  }
  if (targetFieldId !== null) {
    const target = await mbGet<EngineField & { table?: { db_id?: number } }>(
      ctx.tenant,
      `/api/field/${targetFieldId}`,
    );
    if (target.table?.db_id !== undefined && target.table.db_id !== ctx.tenant.databaseId) {
      throw new GatewayError(404, "Kayıt bulunamadı.");
    }
    if (targetFieldId === fieldId) throw new GatewayError(400, "Bir sütun kendisine bağlanamaz.");
  }

  return toField(
    await mbPut<EngineField>("admin", `/api/field/${fieldId}`, {
      // The engine only follows fk_target_field_id when the type says FK.
      semantic_type: targetFieldId === null ? null : "type/FK",
      fk_target_field_id: targetFieldId,
    }),
  );
}
