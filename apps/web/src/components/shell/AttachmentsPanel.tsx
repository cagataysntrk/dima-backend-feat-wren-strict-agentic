"use client";

import { useMemo } from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import type { AskResponse } from "@dima/contracts";
import { attachmentsOf } from "@/lib/attachments";
import { DocumentList } from "@/components/shell/DocumentList";
import { useDocuments, type DocumentEntry } from "@/stores/documents";

/**
 * BELGELER — bu sohbetin dosyaları: eklenenler ve buradan üretilen çıktılar.
 *
 * Hesabın TÜM belgeleri sol taraftaki /documents sayfasında; burada yalnız açık
 * sohbete ait olanlar var (sağ panelin kapsam kuralı). Aynı liste bileşeni ve
 * aynı ÜRETİLEN/YÜKLENEN rozeti kullanılıyor — iki yerde iki farklı görünüm
 * öğrenmek zorunda kalmayasın.
 *
 * DÜRÜSTLÜK NOTU: backend `/ask` hâlâ metin-only ve dosya ucu yok. Mesaja
 * iliştirilen dosyalar SUNUCUYA GİTMİYOR, oturum boyunca istemcide duruyor
 * (lib/attachments.ts, WeakMap). Üretilen CSV'ler de tarayıcıda yazılıyor.
 * Yükleme/dışa aktarma uçları eklendiğinde bu not kalkar.
 */
export function AttachmentsPanel({
  items,
  conversationId,
}: {
  items: AskResponse[];
  conversationId?: string;
}) {
  const documents = useDocuments((s) => s.documents);

  // Mesaja iliştirilen dosyalar belge modeline çevrilir — böylece ekler ve
  // üretilen çıktılar TEK listede, tek rozet dilinde görünür.
  const uploaded = useMemo<DocumentEntry[]>(
    () =>
      items.flatMap((item, gi) =>
        (attachmentsOf(item) ?? []).map((f, i) => ({
          id: `att-${gi}-${i}-${f.name}`,
          name: f.name,
          origin: "uploaded" as const,
          kind: f.type || "dosya",
          size: f.size,
          createdAt: f.lastModified,
          conversationId,
          question: item.question,
          contractId: null,
          blob: f,
        })),
      ),
    [items, conversationId],
  );

  // Üretilenlerden yalnız BU sohbete ait olanlar (kapsam kuralı).
  const generated = documents.filter(
    (d) => d.origin === "generated" && (!conversationId || d.conversationId === conversationId),
  );

  const all = [...generated, ...uploaded].sort((a, b) => b.createdAt - a.createdAt);

  return (
    <div className="space-y-3">
      <DocumentList
        documents={all}
        emptyHint={
          <p className="max-w-xs text-xs text-muted-foreground/80">
            Komut satırındaki + ile dosya ekleyebilir, bir cevabın altındaki{" "}
            <span className="font-medium">dışa aktar</span> ile çıktı üretebilirsin.
          </p>
        }
      />

      {all.length > 0 && (
        <p className="rounded-lg border border-border bg-muted/40 px-3 py-2 text-xs leading-relaxed text-muted-foreground">
          Belgeler şu an yalnız bu oturumda tutuluyor — sunucuya yüklenmiyor ve
          sayfa yenilenince kayboluyor.
        </p>
      )}

      <Link
        href="/documents"
        className="inline-flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
      >
        Hesaptaki tüm belgeler
        <ArrowUpRight className="size-3.5" />
      </Link>
    </div>
  );
}
