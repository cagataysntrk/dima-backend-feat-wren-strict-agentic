import { breakoutOptions } from "@/server/metabase/explore";
import { idParam, withTenant } from "@/server/http";

// GET /api/cards/:id/breakouts — columns this card's measure can be split by.
export const GET = withTenant<{ id: string }>(async (ctx, _req, { id }) => ({
  fields: (await breakoutOptions(ctx, idParam(id))).map(({ id: fid, name, label }) => ({ id: fid, name, label })),
}));
