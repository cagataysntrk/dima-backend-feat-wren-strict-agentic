import { z } from "zod";
import { addCard } from "@/server/metabase/dashboards";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

const Body = z.object({ cardId: z.number().int().positive() });

export const POST = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return addCard(ctx, idParam(id), body.data.cardId);
});
