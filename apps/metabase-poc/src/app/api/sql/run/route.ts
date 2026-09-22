import { z } from "zod";
import { runSql } from "@/server/metabase/api";
import { GatewayError } from "@/server/metabase/errors";
import { withTenant } from "@/server/http";

const Body = z.object({
  sql: z.string().min(1).max(20_000),
  values: z.record(z.string(), z.string().max(500)).optional(),
});

export const POST = withTenant(async (ctx, req) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return { result: await runSql(ctx, body.data.sql, body.data.values ?? {}) };
});
