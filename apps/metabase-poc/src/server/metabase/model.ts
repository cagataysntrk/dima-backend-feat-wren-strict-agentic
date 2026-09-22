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
}

const toField = (f: EngineField): ModelField => ({
  id: f.id,
  name: f.name,
  displayName: f.display_name,
  type: f.base_type.replace("type/", ""),
  category: f.semantic_type === "type/Category",
  hidden: f.visibility_type !== "normal",
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
