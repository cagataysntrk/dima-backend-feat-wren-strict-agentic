import { searchLibrary } from "@/server/metabase/library";
import { withTenant } from "@/server/http";

// GET /api/search?q= — the tenant's analyses and dashboards matching the text.
export const GET = withTenant(async (ctx, req) => ({
  items: await searchLibrary(ctx, new URL(req.url).searchParams.get("q") ?? ""),
}));
