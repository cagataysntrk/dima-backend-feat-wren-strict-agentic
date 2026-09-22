import type { Metadata } from "next";
import { NoAccess } from "@/components/analytics/NoAccess";
import { canAnalyze, shellContext } from "@/server/session";
import { Uploader } from "./Uploader";

export const metadata: Metadata = { title: "Veri yükle" };

export default async function UploadPage() {
  const ctx = await shellContext();
  return canAnalyze(ctx.role) ? <Uploader /> : <NoAccess />;
}
