import type { LucideIcon } from "lucide-react";
import { cn } from "@dima/ui/utils";

/**
 * The "nothing here yet" panel. An empty page should say what belongs here and
 * offer the one action that fills it — never just "no data".
 */
export function EmptyState({
  icon: Icon,
  title,
  hint,
  action,
  className,
}: {
  icon?: LucideIcon;
  title: string;
  /** One sentence: what goes here, or what to do next. */
  hint?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center gap-2 px-6 py-10 text-center", className)}>
      {Icon && (
        <span className="mb-1 flex size-10 items-center justify-center rounded-full bg-muted/60 text-muted-foreground">
          <Icon className="size-5" aria-hidden />
        </span>
      )}
      <p className="text-sm font-medium">{title}</p>
      {hint && <p className="max-w-sm text-sm text-muted-foreground">{hint}</p>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
