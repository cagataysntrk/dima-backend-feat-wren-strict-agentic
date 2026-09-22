import { exportCard } from "@/server/metabase/api";
import { GatewayError } from "@/server/metabase/errors";
import { filtersFrom, idParam, withTenant } from "@/server/http";

// GET /api/cards/:id/export?format=csv|xlsx[&dashboardId=&dashcardId=&<filter slug>=…]
export const GET = withTenant<{ id: string }>(async (ctx, req, { id }) => {
  const url = new URL(req.url);
  const format = url.searchParams.get("format");
  if (format !== "csv" && format !== "xlsx") throw new GatewayError(400, "Geçersiz biçim.");
  const d = url.searchParams.get("dashboardId");
  const dc = url.searchParams.get("dashcardId");
  const scope =
    d && dc
      ? {
          dashboardId: idParam(d),
          dashcardId: idParam(dc),
          filters: filtersFrom(url, ["format", "dashboardId", "dashcardId"]),
        }
      : undefined;
  const file = await exportCard(ctx, idParam(id), format, scope);
  return new Response(file.body, {
    headers: {
      "Content-Type": file.contentType,
      "Content-Disposition": `attachment; filename="${file.filename}"`,
      "Cache-Control": "no-store",
    },
  });
});
