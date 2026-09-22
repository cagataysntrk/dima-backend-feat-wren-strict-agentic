import { z } from "zod";
import { createDashboard } from "@/server/metabase/dashboards";
import { GatewayError } from "@/server/metabase/errors";
import { withTenant } from "@/server/http";

const Body = z.object({ name: z.string().trim().min(1).max(120) });

export const POST = withTenant(async (ctx, req) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Pano adı gerekli.");
  return createDashboard(ctx, body.data.name);
});
