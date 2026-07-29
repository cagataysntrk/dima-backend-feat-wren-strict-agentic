"use client";

import { Database } from "lucide-react";
import { SchemaPanel } from "@/components/SchemaPanel";

/**
 * Veri kaynakları — HESAP GENELİ veri modeli (tüm küpler, tablolar, ilişkiler).
 *
 * Sağ panelden buraya taşındı: katalog hiçbir zaman "açık sohbete ait" bir şey
 * değildi, hesabın tamamına aitti. Sağ panelde durduğu sürece bir sohbet açmadan
 * bakılamıyordu ve dar bir sütuna sıkışıyordu — ERD diyagramı için en kötü yer.
 */
export default function DataSourcesPage() {
  return (
    <main className="dima-page-in mx-auto max-w-6xl space-y-6 px-6 py-10">
      <header className="space-y-1.5">
        <h1 className="flex items-center gap-2 text-xl font-medium tracking-tight text-foreground">
          <Database className="size-5 text-brand" />
          Veri kaynakları
        </h1>
        <p className="text-sm text-muted-foreground">
          Bu hesabın bağlı olduğu veri modeli — küpler, tablolar ve aralarındaki
          ilişkiler. Sorular bu katalog üzerinden yanıtlanır.
        </p>
      </header>

      <SchemaPanel />
    </main>
  );
}
