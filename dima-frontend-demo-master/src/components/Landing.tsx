"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { BrandMark } from "@/components/BrandMark";
import { CaretInput } from "@/components/CaretInput";

// Maksimum-minimalist açılış: boş sayfa, ortada yanıp sönen imleç + ince input çizgisi.
// Header/logo/başlık YOK. Chrome yalnızca sağ üstteki floatlar (page verir) ve
// alt-orta imza: düşük opaklıkta ink wordmark → /brand (filigran, header değil).
export function Landing({
  onSubmit,
  onUpload,
  uploading,
}: {
  onSubmit: (q: string) => void;
  onUpload?: (file: File) => void;
  uploading?: boolean;
}) {
  const [value, setValue] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const send = () => {
    const t = value.trim();
    if (t) onSubmit(t);
  };

  return (
    <div className="dima-vignette relative flex h-full flex-col items-center justify-center gap-4 px-6">
      <CaretInput value={value} onChange={setValue} onSubmit={send} autoFocus size="hero" />

      {onUpload && (
        <>
          <input
            ref={fileRef}
            type="file"
            accept=".csv,.xlsx,.xls,.txt,.tsv"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) onUpload(f);
              e.target.value = "";
            }}
          />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            className="font-mono text-[11px] uppercase tracking-wide text-neutral-400 transition-colors hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
          >
            {uploading ? "⋯ yükleniyor" : "📎 Excel/CSV yükle"}
          </button>
        </>
      )}

      <Link
        href="/brand"
        className="absolute inset-x-0 bottom-8 flex justify-center opacity-30 transition-opacity hover:opacity-80"
      >
        <BrandMark size="sm" ink />
      </Link>
    </div>
  );
}
