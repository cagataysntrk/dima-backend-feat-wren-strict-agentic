import type { Metadata } from "next";
import { NoAccess } from "@/components/analytics/NoAccess";
import { canAnalyze, shellContext } from "@/server/session";
import { DataModel } from "./DataModel";

export const metadata: Metadata = { title: "Veri modeli" };

export default async function ModelPage() {
  const ctx = await shellContext();
  return canAnalyze(ctx.role) ? <DataModel /> : <NoAccess />;
}
