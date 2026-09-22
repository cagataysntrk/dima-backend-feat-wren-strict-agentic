import { z } from "zod";
import { zoom } from "@/server/metabase/explore";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

const Scope = z.object({
  dashboardId: z.number().int().positive(),
  dashcardId: z.number().int().positive(),
  filters: z.record(z.string(), z.array(z.string())),
});
const Body = z.object({ value: z.string().min(4).max(40), scope: Scope.optional() });

// POST /api/cards/:id/zoom — a time bucket at the next finer granularity.
export const POST = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return zoom(ctx, idParam(id), body.data.value, body.data.scope);
});
