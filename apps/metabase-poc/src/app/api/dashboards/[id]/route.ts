import { z } from "zod";
import { dashboard } from "@/server/metabase/api";
import { archiveDashboard, updateDashboard } from "@/server/metabase/dashboards";
import { GatewayError } from "@/server/metabase/errors";
import { idParam, withTenant } from "@/server/http";

export const GET = withTenant<{ id: string }>(async (ctx, _req, { id }) => dashboard(ctx, idParam(id)));

const Patch = z
  .object({ name: z.string().trim().min(1).max(120).optional(), description: z.string().max(500).nullable().optional() })
  .refine((b) => b.name !== undefined || b.description !== undefined);

export const PATCH = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const body = Patch.safeParse(await req.json().catch(() => null));
  if (!body.success) throw new GatewayError(400, "Geçersiz istek.");
  await updateDashboard(ctx, idParam(id), body.data);
  return { ok: true };
});

export const DELETE = withTenant<{ id: string }>(async (ctx, _req, { id }) => {
  await archiveDashboard(ctx, idParam(id));
  return { ok: true };
});
