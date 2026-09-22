"use client";

import { useEffect, useState } from "react";
import { Skeleton } from "@dima/ui/primitives/skeleton";

/**
 * DOCX → HTML (mammoth). Mammoth BİÇİMİ değil YAPIYI korur: başlıklar, listeler,
 * tablolar, kalın/italik gelir; sayfa düzeni, font ve renkler gelmez. Bu, bir
 * eki "okumak" için doğru dengedir — birebir kopya isteyen indirsin.
 */
export default function DocxView({ file }: { file: File }) {
  const [html, setHtml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [{ default: mammoth }, buffer] = await Promise.all([
          import("mammoth/mammoth.browser"),
          file.arrayBuffer(),
        ]);
        const res = await mammoth.convertToHtml({ arrayBuffer: buffer });
        if (alive) setHtml(res.value);
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "bilinmeyen hata");
      }
    })();
    return () => {
      alive = false;
    };
  }, [file]);

  if (error) {
    return (
      <p className="rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-xs text-destructive">
        Belge açılamadı: {error}
      </p>
    );
  }
  if (html === null) return <Skeleton className="h-72 w-full" />;

  return (
    <div className="max-h-full overflow-auto rounded-lg border border-border bg-card p-4">
      {/* mammoth çıktısı dosyanın kendi içeriğidir; script taşımaz (yalnız yapısal
          etiketler üretir). Yine de stil sınıflarını biz veriyoruz. */}
      <div
        className="prose-sm max-w-none text-sm leading-relaxed text-foreground [&_a]:text-brand [&_a]:underline [&_h1]:mt-4 [&_h1]:mb-2 [&_h1]:text-lg [&_h1]:font-semibold [&_h2]:mt-3 [&_h2]:mb-1.5 [&_h2]:font-medium [&_li]:ml-4 [&_li]:list-disc [&_p]:mb-2 [&_table]:w-full [&_table]:border-collapse [&_td]:border [&_td]:border-border [&_td]:px-2 [&_td]:py-1 [&_th]:border [&_th]:border-border [&_th]:px-2 [&_th]:py-1 [&_th]:text-left"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}
