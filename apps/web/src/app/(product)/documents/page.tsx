"use client";

import { useMemo, useState } from "react";
import { Paperclip } from "lucide-react";
import { useDocuments, type DocumentOrigin } from "@/stores/documents";
import { DocumentList } from "@/components/shell/DocumentList";
import { Input } from "@dima/ui/primitives/input";
import { ToggleGroup, ToggleGroupItem } from "@dima/ui/primitives/toggle-group";

/**
 * Belgeler — HESABIN tüm dosyaları: yüklenenler ve üretilenler bir arada.
 *
 * "Raporlar" ayrı bir sayfa değil: bir rapor çıktısı da dosyadır, tek farkı onu
 * kullanıcının değil bizim üretmiş olmamız — bu fark bir rozete iniyor.
 */
type Filter = "all" | DocumentOrigin;

export default function DocumentsPage() {
  const documents = useDocuments((s) => s.documents);
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  const shown = useMemo(() => {
    const needle = q.trim().toLocaleLowerCase("tr-TR");
    return documents.filter((d) => {
      if (filter !== "all" && d.origin !== filter) return false;
      if (!needle) return true;
      return `${d.name} ${d.question ?? ""}`.toLocaleLowerCase("tr-TR").includes(needle);
    });
  }, [documents, q, filter]);

  return (
    <main className="dima-page-in mx-auto max-w-3xl space-y-6 px-6 py-10">
      <header className="space-y-1.5">
        <h1 className="flex items-center gap-2 text-xl font-medium tracking-tight text-foreground">
          <Paperclip className="size-5 text-brand" />
          Belgeler
        </h1>
        <p className="text-sm text-muted-foreground">
          Yüklediğin dosyalar ve dima&apos;nın ürettiği rapor çıktıları. Rozet
          hangisinin ne olduğunu söyler.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Belgelerde ara…"
          className="h-8 max-w-xs text-sm"
        />
        <ToggleGroup
          type="single"
          size="sm"
          variant="outline"
          value={filter}
          onValueChange={(v) => v && setFilter(v as Filter)}
        >
          <ToggleGroupItem value="all" className="px-2.5 text-xs">
            tümü
          </ToggleGroupItem>
          <ToggleGroupItem value="generated" className="px-2.5 text-xs">
            üretilen
          </ToggleGroupItem>
          <ToggleGroupItem value="uploaded" className="px-2.5 text-xs">
            yüklenen
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <DocumentList
        documents={shown}
        emptyHint={
          <p className="max-w-sm text-xs text-muted-foreground/80">
            Bir cevabın altındaki <span className="font-medium">dışa aktar</span> ile
            rapor çıktısı üretebilir, komut satırındaki + ile dosya
            yükleyebilirsin.
          </p>
        }
      />
    </main>
  );
}
