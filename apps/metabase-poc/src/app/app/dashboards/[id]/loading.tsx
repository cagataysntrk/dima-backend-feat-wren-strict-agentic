import { CardGridSkeleton, LoadingShell, PageHeaderSkeleton } from "@/components/shell/Skeletons";

export default function Loading() {
  return (
    <LoadingShell>
      <PageHeaderSkeleton />
      <div className="mt-6">
        {/* Panolar kart ızgarasıdır — yükleme de öyle görünmeli. */}
        <CardGridSkeleton count={4} />
      </div>
    </LoadingShell>
  );
}
