import { schemaGraph } from "@/server/metabase/model";
import { withTenant } from "@/server/http";

// GET /api/schema — tables, columns and the declared relationships between them.
export const GET = withTenant(async (ctx) => schemaGraph(ctx));
