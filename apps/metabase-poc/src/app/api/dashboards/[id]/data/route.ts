import { dashboardData } from "@/server/metabase/api";
import { filtersFrom, idParam, withTenant } from "@/server/http";

// GET /api/dashboards/:id/data?<filter slug>=<value>…  (date: YYYY-MM-DD~YYYY-MM-DD)
export const GET = withTenant<{ id: string }>(async (ctx, req, { id }) =>
  dashboardData(ctx, idParam(id), filtersFrom(new URL(req.url))),
);
