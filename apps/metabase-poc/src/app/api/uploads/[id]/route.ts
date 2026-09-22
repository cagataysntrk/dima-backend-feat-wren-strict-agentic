import { amendUpload } from "@/server/metabase/uploads";
import { setArchived } from "@/server/metabase/library";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

// POST /api/uploads/:cardId?mode=append|replace — add rows to, or replace, an uploaded table.
export const POST = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const mode = new URL(req.url).searchParams.get("mode");
  if (mode !== "append" && mode !== "replace") throw new GatewayError(400, "Geçersiz istek.");
  const form = await req.formData().catch(() => null);
  const file = form?.get("file");
  if (!(file instanceof File)) throw new GatewayError(400, "Dosya bulunamadı.");
  return amendUpload(ctx, idParam(id), file, mode);
});

// DELETE /api/uploads/:cardId — move the uploaded table's analysis to the trash.
// The table itself stays in the company's schema (the engine has no delete for it).
export const DELETE = withTenant<{ id: string }>(async (ctx, _req, { id }) =>
  setArchived(ctx, "card", idParam(id), true),
);
