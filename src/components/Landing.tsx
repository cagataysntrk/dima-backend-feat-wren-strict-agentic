"use client";

import Link from "next/link";
import { useState } from "react";
import { BrandMark } from "@/components/BrandMark";
import { CaretInput } from "@/components/CaretInput";

// Maksimum-minimalist açılış: boş sayfa, ortada yanıp sönen imleç + ince input çizgisi.
// Header/logo/başlık YOK. Chrome yalnızca sağ üstteki floatlar (page verir) ve
// alt-orta imza: düşük opaklıkta ink wordmark → /brand (filigran, header değil).
export function Landing({ onSubmit }: { onSubmit: (q: string) => void }) {
  const [value, setValue] = useState("");

  const send = () => {
    const t = value.trim();
    if (t) onSubmit(t);
  };

  return (
    <div className="dima-vignette relative flex h-full items-center justify-center px-6">
      <CaretInput value={value} onChange={setValue} onSubmit={send} autoFocus size="hero" />

      <Link
        href="/brand"
        className="absolute inset-x-0 bottom-8 flex justify-center opacity-30 transition-opacity hover:opacity-80"
      >
        <BrandMark size="sm" ink />
      </Link>
    </div>
  );
}
