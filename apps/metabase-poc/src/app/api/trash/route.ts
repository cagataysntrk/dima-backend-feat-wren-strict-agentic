import { z } from "zod";
import { setArchived, trashItems } from "@/server/metabase/library";
import { GatewayError } from "@/server/metabase/errors";
import { withTenant } from "@/server/http";

export const GET = withTenant(async (ctx) => ({ items: await trashItems(ctx) }));

const Body = z.object({ kind: z.enum(["card", "dashboard"]), id: z.number().int().positive() });

// POST /api/trash — restore an item from the trash.
export const POST = withTenant(async (ctx, req) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return setArchived(ctx, body.data.kind, body.data.id, false);
});
