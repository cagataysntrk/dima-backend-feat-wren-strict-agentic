"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { BrandMark } from "@/components/BrandMark";
import { CaretInput } from "@/components/CaretInput";
import { useQuery } from "@tanstack/react-query";
import { getStarters } from "@/lib/api-client";

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
  // ⚠ En çok **altı** örnek: yediden fazlası bir davet değil bir menüdür ve boş durumun
  // amacı (bir yön göstermek) bir seçim yüküne dönüşür.
  const { data: starters } = useQuery({ queryKey: ["starters"], queryFn: getStarters });
  const baslangiclar = (starters ?? []).slice(0, 6);
  const fileRef = useRef<HTMLInputElement>(null);

  const send = () => {
    const t = value.trim();
    if (t) onSubmit(t);
  };

  return (
    <div className="dima-vignette relative flex h-full flex-col items-center justify-center gap-4 px-6">
      <CaretInput
        value={value}
        onChange={setValue}
        onSubmit={send}
        autoFocus
        size="hero"
        ipucu="bir soru yaz — örneğin: bu yıl ciro nedir?"
      />

      {/* 🔴 FAZ 7.3/b — **boş durum bir yön göstermeli.** Bugüne kadar landing yalnız bir
          imleç gösteriyordu: kullanıcı ne sorabileceğini **tahmin etmek** zorundaydı ve
          ilk soru bir deneme-yanılmaydı.

          ⚠ Örnekler `/starters`'tan gelir — `HelpPanel`'in **aynı kaynağı**. İkinci bir
          liste yazmak, aynı ürünün iki farklı yeteneği varmış gibi görünmesine yol
          açardı: *aynı kuralın iki sahibi ayrışır.*
          ⚠ Boşsa **hiçbir şey gösterilmez**: uydurma bir örnek, olmayan bir yeteneği
          vaat eder ve ilk soru bir hayal kırıklığı olur. */}
      {baslangiclar.length > 0 && (
        <div className="flex max-w-2xl flex-col items-center gap-2">
          <p className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            ne sorabilirim
          </p>
          <div className="flex flex-wrap justify-center gap-1.5">
            {baslangiclar.map((b) => (
              <button
                key={b.query}
                onClick={() => onSubmit(b.query)}
                title={b.grup ? `${b.grup} — ${b.query}` : b.query}
                className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-500 transition-colors hover:border-accent/50 hover:text-foreground"
              >
                {/* Grup adı **taşınır**: hangi departmanın sorusu olduğunu bilmek,
                    sorunun kendisi kadar bilgidir. Taşımıyorsa uydurulmaz. */}
                {b.grup && <span className="mr-1.5 text-neutral-400">{b.grup}</span>}
                {b.query}
              </button>
            ))}
          </div>
        </div>
      )}

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
