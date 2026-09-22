import { cardData } from "@/server/metabase/api";
import { idParam, withTenant } from "@/server/http";

export const GET = withTenant<{ id: string }>(async (ctx, _req, { id }) => cardData(ctx, idParam(id)));
