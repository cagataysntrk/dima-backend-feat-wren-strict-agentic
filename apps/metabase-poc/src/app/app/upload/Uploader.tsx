"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { FileSpreadsheet, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import { gateway } from "@/lib/gateway";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const ACCEPT = ".csv,.xlsx,.xls";

export function Uploader() {
  const input = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [over, setOver] = useState(false);
  const upload = useMutation({
    mutationFn: (f: File) => gateway.upload(f),
    onSuccess: () => {
      toast.success("Veri yüklendi.");
      setFile(null);
    },
    onError: (e) => toast.error(e.message),
  });

  const pick = (f: File | undefined) => {
    if (f) {
      setFile(f);
      upload.reset();
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Veri yükle</h1>
        <p className="text-sm text-muted-foreground">
          Excel veya CSV dosyası yükleyin; ilk sayfa şirketinizin veri alanına tablo olarak eklenir ve analizlerde
          kullanılabilir.
        </p>
      </header>

      <button
        type="button"
        onClick={() => input.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          pick(e.dataTransfer.files[0]);
        }}
        className={cn(
          "flex w-full flex-col items-center gap-2 rounded-[1.25rem] border-2 border-dashed border-[var(--surface-edge-strong)] bg-card/40 px-6 py-12 text-center transition-colors",
          over ? "border-brand bg-brand/5" : "hover:border-brand/40 hover:bg-accent/40",
        )}
      >
        <UploadCloud className="size-7 text-muted-foreground" aria-hidden />
        <span className="font-medium">Dosyayı sürükleyin ya da seçin</span>
        <span className="text-xs text-muted-foreground">.xlsx · .xls · .csv — en fazla 20 MB</span>
      </button>
      <input
        ref={input}
        type="file"
        accept={ACCEPT}
        className="sr-only"
        aria-label="Dosya seç"
        onChange={(e) => pick(e.target.files?.[0])}
      />

      {file && (
        <div className="surface flex items-center gap-3 p-4">
          <FileSpreadsheet className="size-5 shrink-0 text-brand" aria-hidden />
          <div className="min-w-0 flex-1">
            <div className="truncate text-sm font-medium">{file.name}</div>
            <div className="text-xs text-muted-foreground tabular-nums">
              {(file.size / 1024).toLocaleString("tr-TR", { maximumFractionDigits: 0 })} KB
            </div>
          </div>
          <Button variant="brand" onClick={() => upload.mutate(file)} disabled={upload.isPending}>
            {upload.isPending ? "Yükleniyor…" : "Yükle"}
          </Button>
        </div>
      )}

      {upload.data && (
        <p className="text-sm">
          Yüklendi.{" "}
          <Link href={`/app/cards/${upload.data.id}`} className="text-brand hover:underline">
            Tabloyu aç
          </Link>
        </p>
      )}
    </div>
  );
}
