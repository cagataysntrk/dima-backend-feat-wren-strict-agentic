"use client";

import { useEffect, useState } from "react";
import { FileText, X } from "lucide-react";
import { cn } from "@dima/ui/utils";

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

/**
 * Attachment chip (modeled on the shadcn AI "Attachment" component, on our
 * tokens): image files show a thumbnail, others a file icon, with name, size,
 * and a hover remove button.
 */
export function Attachment({
  file,
  onRemove,
  className,
}: {
  file: File;
  onRemove?: () => void;
  className?: string;
}) {
  const isImage = file.type.startsWith("image/");
  // Create the object URL once (lazy init — no setState in an effect); revoke on unmount.
  const [url] = useState<string | null>(() =>
    isImage && typeof window !== "undefined" ? URL.createObjectURL(file) : null,
  );
  useEffect(() => () => { if (url) URL.revokeObjectURL(url); }, [url]);

  return (
    <div
      className={cn(
        "group relative flex items-center gap-2 rounded-xl border border-border bg-muted/40 p-1.5 pr-2.5",
        className,
      )}
    >
      <div className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-border bg-background">
        {isImage && url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={url} alt={file.name} className="size-full object-cover" />
        ) : (
          <FileText className="size-4 text-muted-foreground" />
        )}
      </div>
      <div className="min-w-0">
        <div className="max-w-40 truncate text-xs font-medium text-foreground">{file.name}</div>
        <div className="text-[10px] text-muted-foreground">{formatBytes(file.size)}</div>
      </div>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          aria-label="Kaldır"
          className="absolute -top-1.5 -right-1.5 flex size-4 items-center justify-center rounded-full border border-background bg-foreground text-background opacity-0 transition-opacity group-hover:opacity-100"
        >
          <X className="size-2.5" />
        </button>
      )}
    </div>
  );
}
