import { tableInsights } from "@/server/metabase/xray";
import { idParam, withTenant } from "@/server/http";

// GET /api/browse/:tableId/insights — automatic charts the engine proposes for a table.
export const GET = withTenant<{ id: string }>(async (ctx, _req, { id }) => tableInsights(ctx, idParam(id)));
