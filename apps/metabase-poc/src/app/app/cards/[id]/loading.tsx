import { LoadingShell, PageHeaderSkeleton, TableSkeleton } from "@/components/shell/Skeletons";

export default function Loading() {
  return (
    <LoadingShell>
      <PageHeaderSkeleton />
      <div className="mt-6">
        <TableSkeleton />
      </div>
    </LoadingShell>
  );
}
