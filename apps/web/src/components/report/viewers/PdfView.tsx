"use client";

import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@dima/ui/primitives/button";
import { Skeleton } from "@dima/ui/primitives/skeleton";

// pdf.js worker'ı paketle birlikte gelen dosyadan verilir — CDN'den çekmek hem
// çevrimdışı çalışmayı bozar hem de CSP'de dış script gerektirirdi.
//
// `pdfjs-dist` doğrudan bağımlılık olarak KURULU olmalı (react-pdf'in içinde
// yuvalı hâli pnpm'de çözülmüyor) ve sürümü react-pdf'in beklediğiyle AYNI
// olmalı: API ile worker farklı major sürümlerse pdf.js hata verir.
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

// react-pdf `file` olarak doğrudan Blob/File alır; object URL üretmiyoruz —
// URL üretmek StrictMode'un çift-mount'unda iptal edilmiş bir tutamaç bırakıyordu
// ("Unexpected server response (0)").
export default function PdfView({ file }: { file: File }) {
  const [pages, setPages] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);

  if (error) {
    return (
      <p className="rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-xs text-destructive">
        PDF açılamadı: {error}
      </p>
    );
  }

  return (
    <div className="flex min-h-0 flex-col gap-2">
      <div className="min-h-0 flex-1 overflow-auto rounded-lg border border-border bg-muted/30 p-2">
        <Document
          file={file}
          onLoadSuccess={({ numPages }) => setPages(numPages)}
          onLoadError={(e) => setError(e.message)}
          loading={<Skeleton className="h-72 w-full" />}
        >
          <Page
            pageNumber={page}
            width={520}
            renderAnnotationLayer={false}
            renderTextLayer={false}
            className="mx-auto [&>canvas]:!h-auto [&>canvas]:!w-full [&>canvas]:rounded"
          />
        </Document>
      </div>

      {pages > 1 && (
        <div className="flex shrink-0 items-center justify-center gap-2">
          <Button
            variant="outline"
            size="icon-sm"
            aria-label="Önceki sayfa"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            <ChevronLeft className="size-4" />
          </Button>
          <span className="text-xs text-muted-foreground tabular-nums">
            {page} / {pages}
          </span>
          <Button
            variant="outline"
            size="icon-sm"
            aria-label="Sonraki sayfa"
            disabled={page >= pages}
            onClick={() => setPage((p) => p + 1)}
          >
            <ChevronRight className="size-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
