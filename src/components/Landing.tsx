"use client";

import { useState } from "react";
import { CaretInput } from "@/components/CaretInput";

// Maksimum-minimalist açılış: boş sayfa, ortada yanıp sönen imleç + ince input çizgisi.
// Header/logo/başlık YOK. Chrome yalnızca sağ üstteki floatlar (page verir).
export function Landing({ onSubmit }: { onSubmit: (q: string) => void }) {
  const [value, setValue] = useState("");

  const send = () => {
    const t = value.trim();
    if (t) onSubmit(t);
  };

  return (
    <div className="dima-vignette flex h-full items-center justify-center px-6">
      <CaretInput value={value} onChange={setValue} onSubmit={send} autoFocus size="hero" />
    </div>
  );
}
