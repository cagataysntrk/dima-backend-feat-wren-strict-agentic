import { parameterValues } from "@/server/metabase/api";
import { idParam, withTenant } from "@/server/http";

export const GET = withTenant<{ id: string; slug: string }>(async (ctx, _req, { id, slug }) => ({
  values: await parameterValues(ctx, idParam(id), slug),
}));
