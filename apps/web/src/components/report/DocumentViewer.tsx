"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { AlertTriangle, Download, FileText } from "lucide-react";
import { formatBytes } from "@/components/ai/attachment";
import { Button } from "@dima/ui/primitives/button";
import { Skeleton } from "@dima/ui/primitives/skeleton";
import { cn } from "@dima/ui/utils";

/**
 * Ek önizleyici — sağ panelde açılır.
 *
 * TASARIM KISITI: dosyalar YEREL `File` nesneleri, sunucuya yüklenmiyor. Bu
 * yüzden Google/Microsoft online viewer'ları (public URL ister) kullanılamaz;
 * her şey tarayıcıda çözülüyor.
 *
 * Her çözümleyici ayrı ayrı `dynamic()` ile yükleniyor: pdf.js + mammoth + SheetJS
 * toplamı megabaytlarca; sohbet açılışında bunları indirmenin anlamı yok. Ek
 * tıklanana kadar hiçbiri gelmiyor.
 */

const PdfView = dynamic(() => import("./viewers/PdfView"), {
  ssr: false,
  loading: () => <ViewerSkeleton />,
});
const DocxView = dynamic(() => import("./viewers/DocxView"), {
  ssr: false,
  loading: () => <ViewerSkeleton />,
});
const SheetView = dynamic(() => import("./viewers/SheetView"), {
  ssr: false,
  loading: () => <ViewerSkeleton />,
});
const TextView = dynamic(() => import("./viewers/TextView"), {
  ssr: false,
  loading: () => <ViewerSkeleton />,
});

type Kind = "pdf" | "image" | "docx" | "sheet" | "text" | "unsupported";

function kindOf(file: File): Kind {
  const name = file.name.toLowerCase();
  const ext = name.slice(name.lastIndexOf(".") + 1);
  if (file.type === "application/pdf" || ext === "pdf") return "pdf";
  if (file.type.startsWith("image/")) return "image";
  if (ext === "docx") return "docx";
  if (["xlsx", "xlsm", "xls", "csv"].includes(ext)) return "sheet";
  if (["txt", "md", "json", "sql", "csv", "log", "yaml", "yml"].includes(ext)) return "text";
  if (file.type.startsWith("text/")) return "text";
  return "unsupported";
}

export function DocumentViewer({ file, className }: { file: File; className?: string }) {
  const kind = useMemo(() => kindOf(file), [file]);
  // Object URL EFFECT İÇİNDE üretilir, memo/lazy-state ile değil: StrictMode
  // dev'de effect'i mount→unmount→mount olarak iki kez çalıştırıyor. Memo'lanmış
  // bir URL ilk temizlikte iptal ediliyor ve ikinci mount ölü tutamacı yeniden
  // kullanıyordu. Effect'te üretince her çalışma kendi URL'ini alıp kendi
  // temizliğinde bırakıyor. (Yalnız görsel önizleme + indirme bağlantısı için;
  // PDF dosyayı doğrudan alıyor.)
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    const objectUrl = URL.createObjectURL(file);
    // Dış kaynak (object URL) yaşam döngüsü effect'e ait; tek seferlik atama,
    // zincirleme render yok — kuralın hedeflediği durum bu değil.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  return (
    <div className={cn("flex min-h-0 flex-col gap-3", className)}>
      <header className="flex items-center gap-2">
        <FileText className="size-4 shrink-0 text-muted-foreground" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-foreground">{file.name}</p>
          <p className="text-xs text-muted-foreground">{formatBytes(file.size)}</p>
        </div>
        <Button variant="outline" size="sm" asChild disabled={!url} className="gap-1.5">
          <a href={url ?? undefined} download={file.name}>
            <Download className="size-3.5" />
            İndir
          </a>
        </Button>
      </header>

      <div className="min-h-0 flex-1">
        {kind === "pdf" && <PdfView file={file} />}
        {kind === "image" && url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={url}
            alt={file.name}
            className="max-h-full w-full rounded-lg border border-border object-contain"
          />
        )}
        {kind === "docx" && <DocxView file={file} />}
        {kind === "sheet" && <SheetView file={file} />}
        {kind === "text" && <TextView file={file} />}
        {kind === "unsupported" && <Unsupported name={file.name} />}
      </div>
    </div>
  );
}

function ViewerSkeleton() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-5 w-1/3" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

/**
 * PowerPoint ve eski Office biçimleri: tarayıcıda güvenilir biçimde çizen açık
 * kaynak bir çözüm YOK (var olanlar animasyon/düzeni bozuyor). Yarım yamalak
 * göstermektense indirme sunuyoruz — yanlış render, render etmemekten kötüdür.
 */
function Unsupported({ name }: { name: string }) {
  const ext = name.slice(name.lastIndexOf(".") + 1).toUpperCase();
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-12 text-center">
      <AlertTriangle className="size-5 text-muted-foreground" />
      <p className="text-sm text-foreground">{ext} önizlemesi yok</p>
      <p className="max-w-xs text-xs text-muted-foreground">
        Bu biçim tarayıcıda güvenilir biçimde gösterilemiyor. Dosyayı indirip
        kendi uygulamanda açabilirsin.
      </p>
    </div>
  );
}
