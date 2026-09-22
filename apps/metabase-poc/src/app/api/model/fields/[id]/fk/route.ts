import { z } from "zod";
import { setForeignKey } from "@/server/metabase/model";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

// null clears the relationship; a number points this column at that one.
const Body = z.object({ targetFieldId: z.number().int().positive().nullable() });

export const PUT = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return { field: await setForeignKey(ctx, idParam(id), body.data.targetFieldId) };
});
