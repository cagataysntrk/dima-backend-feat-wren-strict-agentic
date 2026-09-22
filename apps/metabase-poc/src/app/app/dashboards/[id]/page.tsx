import { Suspense } from "react";
import { canAnalyze, shellContext } from "@/server/session";
import { DashboardView } from "./DashboardView";

export default async function DashboardPage({ params }: { params: Promise<{ id: string }> }) {
  const [{ id }, ctx] = await Promise.all([params, shellContext()]);
  return (
    <Suspense>
      <DashboardView id={Number(id)} canEdit={canAnalyze(ctx.role)} />
    </Suspense>
  );
}
