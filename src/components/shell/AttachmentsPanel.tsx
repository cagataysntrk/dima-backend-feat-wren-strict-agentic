"use client";

import { Paperclip } from "lucide-react";
import type { AskResponse } from "@/lib/types";
import { attachmentsOf } from "@/lib/attachments";
import { Attachment } from "@/components/ai/attachment";

/**
 * Bu sohbette gönderilen tüm ekler, mesajına göre gruplu.
 *
 * DÜRÜSTLÜK NOTU: backend `/ask` şu an metin-only. Bu dosyalar SUNUCUYA
 * GİTMİYOR — yalnız oturum boyunca istemcide tutuluyor (lib/attachments.ts,
 * WeakMap). Sayfa yenilenince kaybolurlar. Kullanıcı "yükledim" sanmasın diye
 * bunu panelde açıkça yazıyoruz; yükleme ucu eklenince bu not kalkar.
 */
export function AttachmentsPanel({ items }: { items: AskResponse[] }) {
  const groups = items
    .map((item) => ({ item, files: attachmentsOf(item) }))
    .filter((g): g is { item: AskResponse; files: File[] } => !!g.files?.length);

  const total = groups.reduce((n, g) => n + g.files.length, 0);

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
              <Attachment key={`${f.name}-${i}`} file={f} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
