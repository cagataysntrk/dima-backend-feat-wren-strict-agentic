import { previewTable } from "@/server/metabase/browse";
import { idParam, withTenant } from "@/server/http";

// GET /api/browse/:tableId?sort=<fieldId>&dir=asc|desc — first rows of a table.
export const GET = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const url = new URL(req.url);
  const sortField = url.searchParams.get("sort");
  const dir = url.searchParams.get("dir") === "desc" ? "desc" : "asc";
  const sort = sortField ? { fieldId: idParam(sortField), dir: dir as "asc" | "desc" } : undefined;
  return { result: await previewTable(ctx, idParam(id), sort) };
});
