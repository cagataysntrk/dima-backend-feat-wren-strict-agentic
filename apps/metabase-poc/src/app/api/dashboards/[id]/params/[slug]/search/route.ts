import { parameterSearch } from "@/server/metabase/api";
import { idParam, withTenant } from "@/server/http";

// GET /api/dashboards/:id/params/:slug/search?q=RAM — category values matching the text.
export const GET = withTenant<{ id: string; slug: string }>(async (ctx, req, { id, slug }) => ({
  values: await parameterSearch(ctx, idParam(id), slug, new URL(req.url).searchParams.get("q") ?? ""),
}));
