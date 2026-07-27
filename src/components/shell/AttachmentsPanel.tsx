"use client";

import { useState } from "react";
import { ArrowLeft, Paperclip } from "lucide-react";
import type { AskResponse } from "@/lib/types";
import { attachmentsOf } from "@/lib/attachments";
import { Attachment } from "@/components/ai/attachment";
import { DocumentViewer } from "@/components/report/DocumentViewer";
import { Button } from "@/components/ui/button";

/**
 * Bu sohbette gönderilen tüm ekler, mesajına göre gruplu.
 *
 * DÜRÜSTLÜK NOTU: backend `/ask` şu an metin-only. Bu dosyalar SUNUCUYA
 * GİTMİYOR — yalnız oturum boyunca istemcide tutuluyor (lib/attachments.ts,
 * WeakMap). Sayfa yenilenince kaybolurlar. Kullanıcı "yükledim" sanmasın diye
 * bunu panelde açıkça yazıyoruz; yükleme ucu eklenince bu not kalkar.
 */
export function AttachmentsPanel({ items }: { items: AskResponse[] }) {
  const [preview, setPreview] = useState<File | null>(null);
  const groups = items
    .map((item) => ({ item, files: attachmentsOf(item) }))
    .filter((g): g is { item: AskResponse; files: File[] } => !!g.files?.length);

  const total = groups.reduce((n, g) => n + g.files.length, 0);

  if (preview) {
    return (
      <div className="flex h-full min-h-0 flex-col gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setPreview(null)}
          className="-ml-2 w-fit gap-1.5"
        >
          <ArrowLeft className="size-4" />
          Eklere dön
        </Button>
        <DocumentViewer file={preview} className="min-h-0 flex-1" />
      </div>
    );
  }

  if (!total) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
        <Paperclip className="size-5 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Bu sohbette ek yok.</p>
        <p className="max-w-xs text-xs text-muted-foreground/80">
          Komut satırındaki + ile dosya ekleyebilirsin.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <p className="rounded-lg border border-border bg-muted/40 px-3 py-2 text-xs leading-relaxed text-muted-foreground">
        Ekler şu an yalnız bu oturumda tutuluyor — sunucuya yüklenmiyor ve sayfa
        yenilenince kayboluyor. Dosya yükleme ucu eklendiğinde kalıcı olacaklar.
      </p>

      {groups.map(({ item, files }, gi) => (
        <section key={`${item.question}-${gi}`} className="space-y-2">
          <h3 className="truncate text-xs font-medium text-muted-foreground">
            {item.question}
          </h3>
          <div className="flex flex-wrap gap-2">
            {files.map((f, i) => (
              <button
                key={`${f.name}-${i}`}
                type="button"
                onClick={() => setPreview(f)}
                className="rounded-xl text-left transition-transform hover:-translate-y-px focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none"
              >
                <Attachment file={f} />
              </button>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
