"use client";

import { useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowUp, ChevronDown, Table2 } from "lucide-react";
import { gateway } from "@/lib/gateway";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  busy?: boolean;
  /** Start-screen variant: taller box with the aurora edge light and halo. */
  hero?: boolean;
  autoFocus?: boolean;
}

/**
 * Chat input: text on top, a toolbar row below (data-scope chip left, round
 * send button right). Enter sends, Shift+Enter adds a line.
 */
export function Composer({ value, onChange, onSubmit, disabled, busy, hero, autoFocus }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const canSend = !disabled && !busy && value.trim().length > 0;

  /** Insert a table name at the cursor, then give focus back to the text. */
  const insert = (text: string) => {
    const el = ref.current;
    const at = el?.selectionStart ?? value.length;
    const before = value.slice(0, at);
    const pad = before && !/\s$/.test(before) ? " " : "";
    const next = `${before}${pad}${text} ${value.slice(at)}`;
    onChange(next);
    requestAnimationFrame(() => {
      el?.focus();
      const pos = before.length + pad.length + text.length + 1;
      el?.setSelectionRange(pos, pos);
    });
  };

  return (
    <form
      onSubmit={(ev) => {
        ev.preventDefault();
        if (canSend) onSubmit();
      }}
      className="relative rounded-[1.75rem]"
    >
      {hero && <div aria-hidden className="dima-composer-halo" />}
      <div
        className={cn(
          "relative flex flex-col rounded-[1.75rem] border border-[var(--surface-edge)] bg-card shadow-[var(--surface-shadow)] transition-[border-color,box-shadow]",
          "focus-within:border-brand/40",
        )}
      >
        <label htmlFor="question" className="sr-only">
          Soru
        </label>
        <textarea
          ref={ref}
          id="question"
          value={value}
          autoFocus={autoFocus}
          disabled={disabled}
          rows={hero ? 2 : 1}
          onChange={(ev) => onChange(ev.target.value)}
          onKeyDown={(ev) => {
            if (ev.key === "Enter" && !ev.shiftKey && !ev.nativeEvent.isComposing) {
              ev.preventDefault();
              if (canSend) onSubmit();
            }
          }}
          placeholder={disabled ? "Sohbet servisi yapılandırılmadı" : "Verinize bir soru sorun…"}
          className={cn(
            "field-sizing-content max-h-52 w-full resize-none bg-transparent px-5 text-base outline-none placeholder:text-muted-foreground/70 disabled:cursor-not-allowed md:text-[15px]",
            hero ? "min-h-20 pt-5 pb-2" : "min-h-12 pt-4 pb-1",
          )}
        />
        <div className="flex items-center gap-2 px-3 pb-3">
          <TablesMenu onPick={insert} disabled={disabled} />
          <span className="hidden text-xs text-muted-foreground/70 sm:inline">
            Enter gönder · Shift + Enter yeni satır
          </span>
          <Button
            type="submit"
            size="icon"
            aria-label="Gönder"
            disabled={!canSend}
            className={cn(
              "ml-auto size-9 rounded-full transition-colors",
              canSend ? "bg-brand text-brand-foreground hover:bg-brand/90" : "bg-muted text-muted-foreground",
            )}
          >
            <ArrowUp className="size-4" aria-hidden />
          </Button>
        </div>
      </div>
      {hero && <span aria-hidden className="dima-border-beam dima-border-beam--aurora" />}
    </form>
  );
}

/** "Tablolar" chip: browse the company's tables and drop one into the question. */
function TablesMenu({ onPick, disabled }: { onPick: (name: string) => void; disabled?: boolean }) {
  const q = useQuery({ queryKey: ["tables"], queryFn: gateway.tables, staleTime: 10 * 60_000 });
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild disabled={disabled}>
        <button
          type="button"
          className="inline-flex h-9 items-center gap-1.5 rounded-full border bg-background/60 px-3 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none disabled:opacity-50"
        >
          <Table2 className="size-4" aria-hidden />
          Tablolar
          <ChevronDown className="size-3.5 opacity-70" aria-hidden />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" side="top" className="max-h-80 w-72 overflow-y-auto">
        <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
          Soruya eklemek için bir tablo seçin
        </DropdownMenuLabel>
        {q.isPending && <p className="px-2 py-1.5 text-sm text-muted-foreground">Yükleniyor…</p>}
        {q.isError && <p className="px-2 py-1.5 text-sm text-destructive">Tablolar yüklenemedi.</p>}
        {q.data?.map((t) => (
          <DropdownMenuItem key={t.name} onSelect={() => onPick(t.name)} className="flex-col items-start gap-0.5">
            <span className="text-sm font-medium">{t.name}</span>
            <span className="line-clamp-1 text-xs text-muted-foreground">{t.columns.join(", ")}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
