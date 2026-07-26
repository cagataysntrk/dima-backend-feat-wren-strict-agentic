"use client";

import { useState, useSyncExternalStore } from "react";
import { Check, ChevronDown, MoreHorizontal, X } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

// İlerleme yalnız bir kullanım ipucudur — localStorage yeterli (token DEĞİL,
// bkz. CLAUDE.md: access token asla localStorage'a yazılmaz).
const KEY = "dima_onboarding_done";
const DISMISS = "dima_onboarding_hidden";

interface Step {
  id: string;
  title: string;
}

const STEPS: Step[] = [
  { id: "ask", title: "İlk soruyu sor" },
  { id: "chart", title: "Görünümü değiştir" },
  { id: "chips", title: "Yorum chip'leriyle oyna" },
  { id: "verify", title: "Cevabı doğrula" },
  { id: "schedule", title: "Rapor zamanla" },
  { id: "schema", title: "Veri modelini gör" },
];

// localStorage üstünde küçük bir dış store — useSyncExternalStore ile okunur,
// böylece effect içinde setState çağırmadan (cascading render) senkron kalır.
const EMPTY: string[] = [];
let cache: string[] | null = null;
let hidden: boolean | null = null;
const listeners = new Set<() => void>();

function read<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}
const subscribe = (cb: () => void) => {
  listeners.add(cb);
  return () => void listeners.delete(cb);
};
const getSnapshot = () => (cache ??= read<string[]>(KEY, EMPTY));
const getServerSnapshot = () => EMPTY;
const getHidden = () => (hidden ??= read<boolean>(DISMISS, false));
const getServerHidden = () => false;

function persist(key: string, value: unknown) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* özel mod / kota — ilerleme kaydedilmezse sorun değil */
  }
  listeners.forEach((l) => l());
}
function writeDone(next: string[]) {
  cache = next;
  persist(KEY, next);
}
function writeHidden(next: boolean) {
  hidden = next;
  persist(DISMISS, next);
}

/** Circular progress ring — sayacın görsel karşılığı (0'da boş halka). */
function Ring({ value, total }: { value: number; total: number }) {
  const r = 6.5;
  const c = 2 * Math.PI * r;
  const pct = total ? value / total : 0;
  return (
    <svg viewBox="0 0 18 18" className="size-3.5 shrink-0 -rotate-90" aria-hidden="true">
      <circle cx="9" cy="9" r={r} fill="none" stroke="currentColor" strokeWidth="2" opacity="0.25" />
      <circle
        cx="9"
        cy="9"
        r={r}
        fill="none"
        stroke="var(--brand)"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray={`${c * pct} ${c}`}
        className="transition-[stroke-dasharray] duration-300"
      />
    </svg>
  );
}

/**
 * "Başlangıç" — sidebar'ın altında duran, YERİNDE açılan onboarding kartı
 * (ChatGPT pattern; modal değil). Kapalıyken tek satır + ilerleme; açıkken
 * ince bir progress bar ve tıklanabilir adım listesi. Üçlü nokta menüsünden
 * gizlenebilir; hepsi bitince kendini kaldırır.
 */
export function Onboarding() {
  const [open, setOpen] = useState(false);
  const done = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  const isHidden = useSyncExternalStore(subscribe, getHidden, getServerHidden);

  const toggle = (id: string) =>
    writeDone(done.includes(id) ? done.filter((x) => x !== id) : [...done, id]);

  const count = done.length;
  if (isHidden || count >= STEPS.length) return null;

  return (
    <Collapsible
      open={open}
      onOpenChange={setOpen}
      className="group/ob rounded-lg px-0.5 py-0.5 transition-colors hover:bg-sidebar-accent/40 data-[state=open]:bg-sidebar-accent/40"
    >
      <div className="flex items-center gap-0.5 pr-0.5">
        <CollapsibleTrigger className="flex min-w-0 flex-1 items-center gap-2 rounded-md px-2 py-1.5 text-left outline-none transition-colors hover:bg-sidebar-accent">
          <span className="text-muted-foreground">
            <Ring value={count} total={STEPS.length} />
          </span>
          <span className="min-w-0 flex-1 truncate text-sm text-sidebar-foreground">
            Başlangıç
          </span>
          {/* sayaç normalde görünür; satıra gelince yerini ··· ve ⌄ ikonlarına bırakır */}
          <span className="shrink-0 text-xs text-muted-foreground tabular-nums group-hover/ob:hidden">
            {count}/{STEPS.length}
          </span>
        </CollapsibleTrigger>

        {/* hover'da beliren aksiyonlar (ChatGPT "Recents" davranışı) */}
        <div className="flex shrink-0 items-center opacity-0 transition-opacity group-hover/ob:opacity-100 focus-within:opacity-100">
          <DropdownMenu>
            <DropdownMenuTrigger
              aria-label="Başlangıç seçenekleri"
              className="rounded-md p-0.5 text-muted-foreground outline-none transition-colors hover:bg-sidebar-accent hover:text-foreground"
            >
              <MoreHorizontal className="size-3.5" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" side="top">
              <DropdownMenuItem onSelect={() => writeDone(STEPS.map((s) => s.id))}>
                <Check className="size-4" />
                Tümünü tamamlandı işaretle
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => writeHidden(true)} variant="destructive">
                <X className="size-4" />
                Gizle
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <CollapsibleTrigger
            aria-label={open ? "Kapat" : "Aç"}
            className="rounded-md p-0.5 text-muted-foreground outline-none transition-colors hover:bg-sidebar-accent hover:text-foreground"
          >
            <ChevronDown
              className={cn("size-3.5 transition-transform duration-200", open && "rotate-180")}
            />
          </CollapsibleTrigger>
        </div>
      </div>

      <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
        <ul className="space-y-0.5 pt-0.5 pb-1">
          {STEPS.map((s) => {
            const isDone = done.includes(s.id);
            return (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => toggle(s.id)}
                  className="flex w-full items-center gap-2.5 rounded-lg px-2 py-1.5 text-left transition-colors hover:bg-sidebar-accent"
                >
                  <span
                    className={cn(
                      "flex size-4 shrink-0 items-center justify-center rounded-full border transition-colors",
                      isDone ? "border-brand bg-brand text-brand-foreground" : "border-border",
                    )}
                  >
                    {isDone && <Check className="size-2.5" strokeWidth={3} />}
                  </span>
                  <span
                    className={cn(
                      "min-w-0 truncate text-sm",
                      isDone
                        ? "text-muted-foreground line-through"
                        : "text-sidebar-foreground",
                    )}
                  >
                    {s.title}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </CollapsibleContent>
    </Collapsible>
  );
}
