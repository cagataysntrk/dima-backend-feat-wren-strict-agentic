import { z } from "zod";
import { updateField } from "@/server/metabase/model";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

const Body = z
  .object({
    displayName: z.string().trim().min(1).max(120).optional(),
    category: z.boolean().optional(),
    hidden: z.boolean().optional(),
  })
  .refine((b) => Object.keys(b).length > 0, "empty patch");

export const PATCH = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return { field: await updateField(ctx, idParam(id), body.data) };
});
