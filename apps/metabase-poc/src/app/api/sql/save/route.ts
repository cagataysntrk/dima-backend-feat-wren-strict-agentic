import { z } from "zod";
import { saveSql } from "@/server/metabase/api";
import { GatewayError } from "@/server/metabase/errors";
import { withTenant } from "@/server/http";

const Body = z.object({ name: z.string().trim().min(1).max(120), sql: z.string().min(1).max(20_000) });

export const POST = withTenant(async (ctx, req) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return saveSql(ctx, body.data.name, body.data.sql);
});
