"use client";

import { Database, Hash, Table2, Tag, Type } from "lucide-react";
import type { UploadResponse } from "@dima/contracts";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

/**
 * BAĞLANAN VERİ (D1/D2/D36) — "kurulum = konuşma".
 *
 * Excel yüklenince backend kolonları çıkarır (ad, tip, rol) ve örnek sorular
 * döner. Bu kart o çıkarımı KULLANICIYA GÖSTERİR: demonun ilk vay anı "sihirbaz
 * kolonları tanıdı, tip onayı sordu" — çıkarımı gizlersek o an kaybolur.
 *
 * Tip/rol rozetleri okunur adlarla gelir: `ölçü` toplanabilir sayı, `boyut`
 * kırılım, `zaman` tarih ekseni. Kullanıcı yanlış bir çıkarımı burada görür.
 */

// Backend kolon rolünü serbest string veriyor; bilinenleri Türkçeleştirip
// kalanını olduğu gibi gösteriyoruz (yeni rol UI değişikliği istemesin).
const ROLE_LABEL: Record<string, string> = {
  measure: "ölçü",
  dimension: "boyut",
  time: "zaman",
};

const ROLE_ICON: Record<string, typeof Hash> = {
  measure: Hash,
  dimension: Tag,
  time: Type,
};

export function DatasetCard({
  data,
  onPick,
  className,
}: {
  data: UploadResponse;
  /** Örnek soruya tıklama — doğrudan sorulur. */
  onPick?: (q: string) => void;
  className?: string;
}) {
  const columns = (data.columns ?? []) as {
    orig?: string;
    name?: string;
    type?: string;
    role?: string;
  }[];

  return (
    <Card className={cn("gap-3 p-3", className)}>
      <div className="flex items-center gap-2">
        <Database className="size-4 shrink-0 text-brand" aria-hidden />
        <span className="min-w-0 truncate text-sm font-medium text-foreground">
          {data.dataset}
        </span>
        <Badge variant="brand-subtle" className="ml-auto shrink-0 text-[10px]">
          bağlandı
        </Badge>
      </div>

      <div className="flex items-center gap-3 font-mono text-[11px] text-muted-foreground tabular-nums">
        <span className="flex items-center gap-1">
          <Table2 className="size-3" aria-hidden />
          {data.row_count.toLocaleString("tr-TR")} satır
        </span>
        <span>{columns.length} kolon</span>
      </div>

      {/* Çıkarılan kolonlar — demonun "sihirbaz tanıdı" anı. */}
      {columns.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {columns.map((c, i) => {
            const role = c.role ?? "";
            const Icon = ROLE_ICON[role] ?? Tag;
            return (
              <Badge
                key={`${c.name ?? c.orig ?? i}`}
                variant="outline"
                className="gap-1 font-mono text-[10px] font-normal"
                title={`${c.orig ?? c.name} · ${c.type ?? "?"} · ${ROLE_LABEL[role] ?? role}`}
              >
                <Icon className="size-2.5 text-muted-foreground" aria-hidden />
                {c.name ?? c.orig}
                <span className="text-muted-foreground/70">
                  {ROLE_LABEL[role] ?? c.type ?? ""}
                </span>
              </Badge>
            );
          })}
        </div>
      )}

      {/* Backend'in önerdiği açılış soruları — "şimdi ne sorabilirim?" */}
      {data.suggestions && data.suggestions.length > 0 && onPick && (
        <div className="flex flex-wrap gap-1.5 border-t border-border pt-2">
          {data.suggestions.map((s) => (
            <button key={s.label} type="button" onClick={() => onPick(s.query)}>
              <Badge
                variant="outline"
                className="cursor-pointer font-normal transition-colors hover:border-brand/40 hover:bg-brand/5"
              >
                {s.label}
              </Badge>
            </button>
          ))}
        </div>
      )}

      <p className="text-[11px] leading-relaxed text-muted-foreground">
        Veri bu oturuma bağlı — ham dosya buluta ya da modele gitmez, yerel
        motorda sorgulanır.
      </p>
    </Card>
  );
}
