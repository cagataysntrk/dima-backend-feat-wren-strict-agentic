import { z } from "zod";
import { CARD_DISPLAYS, updateCard } from "@/server/metabase/api";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

const Body = z
  .object({
    display: z.enum(CARD_DISPLAYS).optional(),
    goal: z.number().positive().nullable().optional(),
    name: z.string().trim().min(1).max(120).optional(),
  })
  .refine((b) => Object.keys(b).length > 0, "empty patch");

// PATCH /api/cards/:id — save the chart type, its goal, or the card's name.
export const PATCH = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return updateCard(ctx, idParam(id), body.data);
});
