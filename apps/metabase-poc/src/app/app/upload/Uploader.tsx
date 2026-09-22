"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileSpreadsheet, Plus, RefreshCw, Trash2, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import { gateway, type Item } from "@/lib/gateway";
import { cn } from "@dima/ui/utils";
import { Button } from "@dima/ui/primitives/button";

const ACCEPT = ".csv,.xlsx,.xls";

export function Uploader() {
  const input = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [over, setOver] = useState(false);
  const queryClient = useQueryClient();
  const uploads = useQuery({
    queryKey: ["items"],
    queryFn: gateway.items,
    select: (items) => items.filter((i) => i.kind === "model"),
  });
  const upload = useMutation({
    mutationFn: (f: File) => gateway.upload(f),
    onSuccess: () => {
      toast.success("Veri yüklendi.");
      setFile(null);
      void queryClient.invalidateQueries({ queryKey: ["items"] });
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

      {(uploads.data?.length ?? 0) > 0 && (
        <section className="space-y-2" aria-label="Yüklenen veriler">
          <h2 className="text-sm font-medium text-muted-foreground">Yüklenen veriler</h2>
          <ul className="space-y-2">
            {uploads.data?.map((u) => (
              <UploadRow key={u.id} item={u} />
            ))}
          </ul>
          <p className="text-xs text-muted-foreground">
            “Ekle” satırları mevcut tabloya ekler, “Değiştir” tablodaki satırların yerine yenilerini koyar. Sütunlar
            eşleşmelidir.
          </p>
        </section>
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

/** One uploaded table: append rows, replace all rows, or move its analysis to the trash. */
function UploadRow({ item }: { item: Item }) {
  const queryClient = useQueryClient();
  const append = useRef<HTMLInputElement>(null);
  const replace = useRef<HTMLInputElement>(null);
  const done = () => {
    void queryClient.invalidateQueries({ queryKey: ["items"] });
    void queryClient.invalidateQueries({ queryKey: ["card", item.id] });
  };
  const amend = useMutation({
    mutationFn: ({ file, mode }: { file: File; mode: "append" | "replace" }) =>
      gateway.amendUpload(item.id, file, mode),
    onSuccess: (_r, { mode }) => {
      done();
      toast.success(mode === "append" ? "Satırlar eklendi." : "Tablo değiştirildi.");
    },
    onError: (e) => toast.error(e.message),
  });
  const remove = useMutation({
    mutationFn: () => gateway.removeUpload(item.id),
    onSuccess: () => {
      done();
      toast.success("Çöp kutusuna taşındı.");
    },
    onError: (e) => toast.error(e.message),
  });

  return (
    <li className="surface-sm flex flex-wrap items-center gap-3 px-3 py-2.5">
      <FileSpreadsheet className="size-4 shrink-0 text-brand" aria-hidden />
      <Link href={`/app/cards/${item.id}`} className="min-w-0 flex-1 truncate font-medium hover:underline">
        {item.name}
      </Link>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="xs" onClick={() => append.current?.click()} disabled={amend.isPending}>
          <Plus className="size-3.5" aria-hidden />
          Ekle
        </Button>
        <Button variant="ghost" size="xs" onClick={() => replace.current?.click()} disabled={amend.isPending}>
          <RefreshCw className="size-3.5" aria-hidden />
          Değiştir
        </Button>
        <Button
          variant="ghost"
          size="icon-xs"
          aria-label={`${item.name} kaldır`}
          onClick={() => remove.mutate()}
          disabled={remove.isPending}
        >
          <Trash2 className="size-3.5" aria-hidden />
        </Button>
      </div>
      <input
        ref={append}
        type="file"
        accept={ACCEPT}
        className="sr-only"
        aria-label={`${item.name} tablosuna satır ekle`}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) amend.mutate({ file: f, mode: "append" });
          e.target.value = "";
        }}
      />
      <input
        ref={replace}
        type="file"
        accept={ACCEPT}
        className="sr-only"
        aria-label={`${item.name} tablosunu değiştir`}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) amend.mutate({ file: f, mode: "replace" });
          e.target.value = "";
        }}
      />
    </li>
  );
}
