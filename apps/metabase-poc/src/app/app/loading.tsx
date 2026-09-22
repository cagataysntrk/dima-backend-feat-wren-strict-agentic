import { CardGridSkeleton, LoadingShell, PageHeaderSkeleton } from "@/components/shell/Skeletons";

export default function Loading() {
  return (
    <LoadingShell>
      <PageHeaderSkeleton wide />
      <div className="mt-6">
        <CardGridSkeleton />
      </div>
    </LoadingShell>
  );
}
