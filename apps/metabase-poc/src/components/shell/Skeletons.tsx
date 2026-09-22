import { Skeleton } from "@dima/ui/primitives/skeleton";

/**
 * Route loading placeholders. They mirror the real page's shape — title, then
 * the grid or table that follows — so nothing jumps when the data arrives.
 * Decorative: screen readers get the one live region below, not 30 boxes.
 */
export function PageHeaderSkeleton({ wide = false }: { wide?: boolean }) {
  return (
    <div className="space-y-2">
      <Skeleton className={wide ? "h-7 w-72" : "h-7 w-40"} />
      <Skeleton className="h-4 w-full max-w-md" />
    </div>
  );
}

export function CardGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className="surface space-y-3 p-5">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-28 w-full" />
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="surface space-y-3 p-5">
      <Skeleton className="h-4 w-40" />
      <div className="space-y-2">
        {Array.from({ length: rows }, (_, i) => (
          // Satırlar hafifçe kısalır: tek tip blok "donmuş" görünüyor.
          <Skeleton key={i} className="h-7 w-full" style={{ opacity: 1 - i * 0.06 }} />
        ))}
      </div>
    </div>
  );
}

/** Wraps a skeleton so assistive tech hears one "yükleniyor", not the boxes. */
export function LoadingShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto w-full max-w-6xl space-y-6 p-6">
      <span className="sr-only" role="status">
        Yükleniyor…
      </span>
      <div aria-hidden>{children}</div>
    </div>
  );
}
