import { LoadingShell, PageHeaderSkeleton } from "@/components/shell/Skeletons";
import { Skeleton } from "@dima/ui/primitives/skeleton";

export default function Loading() {
  return (
    <LoadingShell>
      <PageHeaderSkeleton />
      <Skeleton className="mt-6 h-[520px] w-full rounded-xl" />
    </LoadingShell>
  );
}
