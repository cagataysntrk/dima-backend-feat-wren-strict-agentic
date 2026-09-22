"use client";

import { useState } from "react";
import { Download, FileText, Sparkles, Trash2, Upload } from "lucide-react";
import {
  downloadDocument,
  useDocuments,
  type DocumentEntry,
  type DocumentOrigin,
} from "@/stores/documents";
import { DocumentViewer } from "@/components/report/DocumentViewer";
import { Badge } from "@dima/ui/primitives/badge";
import { Button } from "@dima/ui/primitives/button";
import { Card } from "@dima/ui/primitives/card";
import { Tooltip, TooltipContent, TooltipTrigger } from "@dima/ui/primitives/tooltip";
import { cn } from "@dima/ui/utils";

/**
 * Belge listesi — YÜKLENEN ve ÜRETİLEN dosyalar tek akışta.
 *
 * İkisini ayrı sayfalara bölmek kullanıcıyı "o dosya hangi kategorideydi?"
 * sorusuna zorlardı; oysa aradığı şey dosyanın kendisi. Kaynak farkı bir rozete
 * indirgeniyor: ÜRETİLEN (bizim yazdığımız rapor çıktısı) · YÜKLENEN (kullanıcının
 * verdiği dosya). Rozet sadece renk değil METİN de taşıyor — renk körlüğünde de
 * ayrım okunabilir kalmalı.
 */

const ORIGIN_META: Record<DocumentOrigin, { label: string; icon: typeof Upload; cls: string }> = {
  generated: {
    label: "ÜRETİLEN",
    icon: Sparkles,
    cls: "border-brand/30 bg-brand/[0.06] text-brand",
  },
  uploaded: {
    label: "YÜKLENEN",
    icon: Upload,
    cls: "border-border bg-muted/50 text-muted-foreground",
  },
};

const fmtSize = (n: number) =>
  n < 1024
    ? `${n} B`
    : n < 1024 * 1024
      ? `${(n / 1024).toFixed(0)} KB`
      : `${(n / 1024 / 1024).toFixed(1)} MB`;

const fmtDate = (ts: number) =>
  new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeStyle: "short" }).format(ts);

export function DocumentList({
  documents,
  emptyHint,
  className,
}: {
  documents: DocumentEntry[];
  emptyHint?: React.ReactNode;
  className?: string;
}) {
  const remove = useDocuments((s) => s.remove);
  const [preview, setPreview] = useState<DocumentEntry | null>(null);

  if (preview) {
    // DocumentViewer bir File bekliyor; blob'u adıyla birlikte sarıyoruz.
    const file = new File([preview.blob], preview.name, { type: preview.blob.type });
    return (
      <div className={cn("flex h-full min-h-0 flex-col gap-3", className)}>
        <div className="flex items-center justify-between gap-2">
          <Button variant="ghost" size="sm" onClick={() => setPreview(null)} className="-ml-2 gap-1.5">
            Belgelere dön
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => downloadDocument(preview)}
            className="h-7 gap-1.5 text-xs"
          >
            <Download className="size-3.5" />
            indir
          </Button>
        </div>
        <DocumentViewer file={file} className="min-h-0 flex-1" />
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-10 text-center",
          className,
        )}
      >
        <FileText className="size-5 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Henüz belge yok.</p>
        {emptyHint}
      </div>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {documents.map((d) => {
        const meta = ORIGIN_META[d.origin];
        const Icon = meta.icon;
        return (
          <Card key={d.id} className="group gap-1.5 p-3">
            <div className="flex items-start gap-2">
              <button
                type="button"
                onClick={() => setPreview(d)}
                className="min-w-0 flex-1 text-left"
              >
                <p className="truncate text-sm text-foreground" title={d.name}>
                  {d.name}
                </p>
              </button>
              <Badge
                variant="outline"
                className={cn("shrink-0 gap-1 text-[10px] font-medium", meta.cls)}
                title={
                  d.origin === "generated"
                    ? "Bu dosyayı dima üretti (rapor çıktısı)"
                    : "Bu dosyayı sen yükledin"
                }
              >
                <Icon className="size-2.5" aria-hidden />
                {meta.label}
              </Badge>
            </div>

            {d.question && (
              <p className="truncate text-xs text-muted-foreground" title={d.question}>
                {d.question}
              </p>
            )}

            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] text-muted-foreground/80 tabular-nums">
                {fmtSize(d.size)} · {fmtDate(d.createdAt)}
              </span>
              <div className="ml-auto flex items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label="İndir"
                      onClick={() => downloadDocument(d)}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <Download className="size-3.5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">İndir</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label="Kaldır"
                      onClick={() => remove(d.id)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Kaldır</TooltipContent>
                </Tooltip>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
