import { z } from "zod";
import { saveLayout } from "@/server/metabase/dashboards";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

const Body = z.object({
  widgets: z.array(z.object({ id: z.number().int(), width: z.enum(["kpi", "half", "full"]) })).max(100),
});

export const PUT = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  await saveLayout(ctx, idParam(id), body.data.widgets);
  return { ok: true };
});
