import { tenantTables } from "@/server/metabase/metadata";
import { withTenant } from "@/server/http";

// Table + column names of the caller's company, for the chat composer's "Tablolar" menu.
export const GET = withTenant(async (ctx) => ({
  tables: (await tenantTables(ctx)).map((table) => ({
    name: table.name,
    columns: table.columns.map((column) => column.name),
  })),
}));
