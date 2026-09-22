import { z } from "zod";
import { breakoutBy } from "@/server/metabase/explore";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

const Scope = z.object({
  dashboardId: z.number().int().positive(),
  dashcardId: z.number().int().positive(),
  filters: z.record(z.string(), z.array(z.string())),
});
const Body = z.object({
  value: z.string().max(500),
  fieldId: z.number().int().positive(),
  scope: Scope.optional(),
});

// POST /api/cards/:id/breakout — the clicked category split by another column.
export const POST = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return breakoutBy(ctx, idParam(id), body.data.value, body.data.fieldId, body.data.scope);
});
