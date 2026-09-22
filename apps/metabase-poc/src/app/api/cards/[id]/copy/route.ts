import { duplicateCard } from "@/server/metabase/library";
import { idParam, withTenant } from "@/server/http";

// POST /api/cards/:id/copy — duplicate an analysis into the same collection.
export const POST = withTenant<{ id: string }>(async (ctx, _req, { id }) => duplicateCard(ctx, idParam(id)));
