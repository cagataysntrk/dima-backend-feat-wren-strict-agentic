"use client";

import { useEffect, useState } from "react";
import { Skeleton } from "@dima/ui/primitives/skeleton";

const MAX_CHARS = 200_000;

/** Düz metin / md / json / sql — olduğu gibi, kırpma sınırıyla. */
export default function TextView({ file }: { file: File }) {
  const [text, setText] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    file
      .text()
      .then((t) => alive && setText(t.slice(0, MAX_CHARS)))
      .catch(() => alive && setText(""));
    return () => {
      alive = false;
    };
  }, [file]);

  if (text === null) return <Skeleton className="h-72 w-full" />;

  return (
    <pre className="max-h-full overflow-auto rounded-lg border border-border bg-muted/30 p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap text-foreground">
      {text}
    </pre>
  );
}
