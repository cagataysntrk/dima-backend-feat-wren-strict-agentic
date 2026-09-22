import "server-only";
import * as XLSX from "xlsx";
import { mbForm, mbGet, mbPut } from "./client";
import { GatewayError } from "./errors";
import { requireAnalyst, type TenantContext } from "./guard";
import { slugify } from "./api";

// Excel/CSV upload → a new table in the tenant's OWN schema + a model card in the
// tenant's collection.
//
// Engine constraint (v0.58): the upload target is ONE global setting
// ("uploads-settings": db + schema). To keep uploads per-tenant we point it at
// the tenant's database/schema, upload, and reset it — serialized by an
// in-process lock. Fine for a single-instance POC; multi-instance would need a
// distributed lock or our own ingestion path.

const MAX_BYTES = 20 * 1024 * 1024;
let lock: Promise<unknown> = Promise.resolve();

function exclusive<T>(fn: () => Promise<T>): Promise<T> {
  const run = lock.then(fn, fn);
  lock = run.catch(() => undefined);
  return run;
}

async function toCsv(file: File): Promise<string> {
  const name = file.name.toLowerCase();
  const buf = await file.arrayBuffer();
  if (name.endsWith(".csv")) return new TextDecoder("utf-8").decode(buf);
  if (name.endsWith(".xlsx") || name.endsWith(".xls")) {
    const wb = XLSX.read(buf, { type: "array", cellDates: true });
    const first = wb.SheetNames[0];
    if (!first) throw new GatewayError(400, "Dosyada sayfa bulunamadı.");
    return XLSX.utils.sheet_to_csv(wb.Sheets[first], { dateNF: "yyyy-mm-dd" });
  }
  throw new GatewayError(400, "Yalnızca .csv, .xlsx veya .xls dosyaları yüklenebilir.");
}

/**
 * Uploaded tables get an engine-generated row-id column. Mark it "sensitive" so the
 * engine leaves it out of query results AND file exports (not just our adapter view).
 */
async function hideEngineColumns(cardId: number): Promise<void> {
  const card = await mbGet<{ table_id: number | null }>("admin", `/api/card/${cardId}`);
  if (card.table_id == null) return;
  const meta = await mbGet<{ fields: { id: number; name: string }[] }>(
    "admin",
    `/api/table/${card.table_id}/query_metadata`,
  );
  await Promise.all(
    meta.fields
      .filter((f) => /^_mb_/i.test(f.name))
      .map((f) => mbPut("admin", `/api/field/${f.id}`, { visibility_type: "sensitive" })),
  );
}

export async function uploadFile(ctx: TenantContext, file: File): Promise<{ id: number }> {
  requireAnalyst(ctx);
  if (file.size === 0) throw new GatewayError(400, "Dosya boş.");
  if (file.size > MAX_BYTES) throw new GatewayError(400, "Dosya 20 MB sınırını aşıyor.");
  const csv = await toCsv(file);
  const base = slugify(file.name.replace(/\.[^.]+$/, "")).replace(/-/g, "_") || "veri";

  return exclusive(async () => {
    await mbPut("admin", "/api/setting/uploads-settings", {
      value: { db_id: ctx.tenant.databaseId, schema_name: ctx.tenant.schema, table_prefix: "yukleme_" },
    });
    try {
      const form = new FormData();
      form.set("collection_id", String(ctx.tenant.collectionId));
      form.set("file", new Blob([csv], { type: "text/csv" }), `${base}.csv`);
      const id = await mbForm<number>(ctx.tenant, "/api/upload/csv", form);
      await hideEngineColumns(id);
      return { id };
    } finally {
      await mbPut("admin", "/api/setting/uploads-settings", {
        value: { db_id: null, schema_name: null, table_prefix: null },
      }).catch(() => undefined);
    }
  });
}
