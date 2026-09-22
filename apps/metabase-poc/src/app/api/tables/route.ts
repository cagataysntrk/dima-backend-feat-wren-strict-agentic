import { tenantTables } from "@/server/chat/agent";
import { withTenant } from "@/server/http";

// Table + column names of the caller's company, for the chat composer's "Tablolar" menu.
export const GET = withTenant(async (ctx) => ({
  tables: (await tenantTables(ctx)).map((t) => ({ name: t.name, columns: t.columns.map((c) => c.name) })),
}));
