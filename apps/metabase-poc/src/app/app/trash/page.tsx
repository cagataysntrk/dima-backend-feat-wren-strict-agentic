import type { Metadata } from "next";
import { NoAccess } from "@/components/analytics/NoAccess";
import { canAnalyze, shellContext } from "@/server/session";
import { TrashView } from "./TrashView";

export const metadata: Metadata = { title: "Çöp kutusu" };

export default async function TrashPage() {
  const ctx = await shellContext();
  return canAnalyze(ctx.role) ? <TrashView /> : <NoAccess />;
}
