import type { Metadata } from "next";
import { NoAccess } from "@/components/analytics/NoAccess";
import { canAnalyze, shellContext } from "@/server/session";
import { SqlRunner } from "./SqlRunner";

export const metadata: Metadata = { title: "SQL" };

export default async function SqlPage() {
  const ctx = await shellContext();
  return canAnalyze(ctx.role) ? <SqlRunner /> : <NoAccess />;
}
