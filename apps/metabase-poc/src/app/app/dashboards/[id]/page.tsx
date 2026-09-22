import { Suspense } from "react";
import { DashboardView } from "./DashboardView";

export default async function DashboardPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <Suspense>
      <DashboardView id={Number(id)} />
    </Suspense>
  );
}
