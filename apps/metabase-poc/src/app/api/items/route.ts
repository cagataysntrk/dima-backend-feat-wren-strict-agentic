import { listItems } from "@/server/metabase/api";
import { withTenant } from "@/server/http";

export const GET = withTenant(async (ctx) => ({ items: await listItems(ctx) }));
