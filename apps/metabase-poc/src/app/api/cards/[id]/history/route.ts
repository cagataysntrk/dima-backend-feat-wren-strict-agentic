import { z } from "zod";
import { cardHistory, revertCard } from "@/server/metabase/history";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

export const GET = withTenant<{ id: string }>(async (ctx, _req, { id }) => ({
  revisions: await cardHistory(ctx, idParam(id)),
}));

const Body = z.object({ revisionId: z.number().int().positive() });

// POST /api/cards/:id/history — restore the analysis to an earlier version.
export const POST = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Body.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  return revertCard(ctx, idParam(id), body.data.revisionId);
});
