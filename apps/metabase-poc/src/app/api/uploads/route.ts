import { GatewayError } from "@/server/metabase/errors";
import { uploadFile } from "@/server/metabase/uploads";
import { withTenant } from "@/server/http";

export const POST = withTenant(async (ctx, req) => {
  const form = await req.formData().catch(() => null);
  const file = form?.get("file");
  if (!(file instanceof File)) throw new GatewayError(400, "Dosya bulunamadı.");
  return uploadFile(ctx, file);
});
