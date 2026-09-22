"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronRight, Eye, EyeOff, Tag } from "lucide-react";
import { toast } from "sonner";
import { gateway, type ModelField, type ModelTable } from "@/lib/gateway";
import { cn } from "@dima/ui/utils";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Skeleton } from "@dima/ui/primitives/skeleton";

/**
 * Data model: rename columns, mark which are categories, hide the ones nobody
 * should see. The engine stores this per column, so the same settings feed the
 * break-out list and the chat's schema.
 */
export function DataModel() {
  const tables = useQuery({ queryKey: ["model"], queryFn: gateway.dataModel });
  const [open, setOpen] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Veri modeli</h1>
        <p className="text-sm text-muted-foreground">
          Sütunlara anlaşılır adlar verin, kategori olanları işaretleyin, gerekmeyenleri gizleyin. Bu ayarlar kırılım
          seçeneklerinde ve sohbetin veri şemasında da kullanılır.
        </p>
      </header>

      {tables.isPending && <Skeleton className="h-40 w-full" />}
      {tables.isError && (
        <p role="alert" className="text-sm text-destructive">
          {tables.error.message}
        </p>
      )}

      <div className="space-y-2">
        {tables.data?.map((t) => (
          <TableRow key={t.id} table={t} open={open === t.id} onToggle={() => setOpen(open === t.id ? null : t.id)} />
        ))}
      </div>
    </div>
  );
}

function TableRow({ table, open, onToggle }: { table: ModelTable; open: boolean; onToggle: () => void }) {
  const visible = table.fields.filter((f) => !f.hidden).length;
  return (
    <section className="surface overflow-hidden">
      <button
        type="button"
        aria-expanded={open}
        onClick={onToggle}
        className="flex w-full items-center gap-2 px-4 py-3 text-left transition-colors hover:bg-accent/40"
      >
        <ChevronRight className={cn("size-4 text-muted-foreground transition-transform", open && "rotate-90")} aria-hidden />
        <span className="font-medium">{table.name}</span>
        <span className="ml-auto text-xs text-muted-foreground tabular-nums">
          {visible}/{table.fields.length} sütun görünür
        </span>
      </button>
      {open && (
        <ul className="divide-y divide-[var(--surface-edge)] border-t border-[var(--surface-edge)]">
          {table.fields.map((f) => (
            <FieldRow key={f.id} field={f} />
          ))}
        </ul>
      )}
    </section>
  );
}

function FieldRow({ field }: { field: ModelField }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState(field.displayName);
  const patch = useMutation({
    mutationFn: (p: { displayName?: string; category?: boolean; hidden?: boolean }) =>
      gateway.updateField(field.id, p),
    onSuccess: () => {
      // Column settings change break-out options and the chat schema too.
      void queryClient.invalidateQueries({ queryKey: ["model"] });
      void queryClient.invalidateQueries({ queryKey: ["breakouts"] });
      void queryClient.invalidateQueries({ queryKey: ["tables"] });
    },
    onError: (e) => {
      setName(field.displayName);
      toast.error(e.message);
    },
  });

  const rename = () => {
    const next = name.trim();
    if (!next || next === field.displayName) {
      setName(field.displayName);
      return;
    }
    patch.mutate({ displayName: next });
  };

  return (
    <li className={cn("flex flex-wrap items-center gap-3 px-4 py-2.5", field.hidden && "opacity-60")}>
      <span className="w-44 shrink-0 truncate font-mono text-xs text-muted-foreground" title={field.name}>
        {field.name}
      </span>
      <Input
        value={name}
        onChange={(e) => setName(e.target.value)}
        onBlur={rename}
        onKeyDown={(e) => {
          if (e.key === "Enter") e.currentTarget.blur();
          if (e.key === "Escape") setName(field.displayName);
        }}
        aria-label={`${field.name} görünen adı`}
        className="h-8 max-w-56 flex-1"
      />
      <span className="w-20 shrink-0 text-xs text-muted-foreground">{field.type}</span>
      <div className="ml-auto flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          aria-pressed={field.category}
          title="Kategori: kırılım seçeneklerinde çıkar"
          onClick={() => patch.mutate({ category: !field.category })}
          disabled={patch.isPending}
          className={cn("gap-1.5", field.category && "bg-brand/10 text-foreground")}
        >
          <Tag className={cn("size-3.5", field.category && "text-brand")} aria-hidden />
          Kategori
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-pressed={field.hidden}
          aria-label={field.hidden ? "Sütunu göster" : "Sütunu gizle"}
          title={field.hidden ? "Sütunu göster" : "Sütunu gizle"}
          onClick={() => patch.mutate({ hidden: !field.hidden })}
          disabled={patch.isPending}
        >
          {field.hidden ? <EyeOff className="size-4" aria-hidden /> : <Eye className="size-4" aria-hidden />}
        </Button>
      </div>
    </li>
  );
}
