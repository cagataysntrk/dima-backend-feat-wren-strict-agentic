import { z } from "zod";
import { drill } from "@/server/metabase/api";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

const Body = z.object({
  column: z.string().min(1).max(200),
  value: z.string().max(500),
  scope: z
    .object({
      dashboardId: z.number().int().positive(),
      dashcardId: z.number().int().positive(),
      filters: z.record(z.string(), z.array(z.string())),
    })
    .optional(),
});

export const POST = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  const { column, value, scope } = body.data;
  return { result: await drill(ctx, idParam(id), column, value, scope) };
});
