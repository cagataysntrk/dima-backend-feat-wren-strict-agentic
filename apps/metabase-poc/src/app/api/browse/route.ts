import { browseTables } from "@/server/metabase/browse";
import { withTenant } from "@/server/http";

// GET /api/browse — the company's tables and their columns.
export const GET = withTenant(async (ctx) => ({ tables: await browseTables(ctx) }));
