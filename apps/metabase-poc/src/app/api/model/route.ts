import { dataModel } from "@/server/metabase/model";
import { withTenant } from "@/server/http";

// GET /api/model — the tenant's tables and columns with their data-model settings.
export const GET = withTenant(async (ctx) => ({ tables: await dataModel(ctx) }));
