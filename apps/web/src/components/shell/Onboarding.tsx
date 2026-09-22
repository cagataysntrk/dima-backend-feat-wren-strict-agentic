"use client";

import { useState, useSyncExternalStore } from "react";
import { Check, ChevronDown, ChevronRight, MoreHorizontal, X } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@dima/ui/primitives/collapsible";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@dima/ui/primitives/dropdown-menu";
import { cn } from "@dima/ui/utils";

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

/** Kart şu an gizli mi / bitmiş mi? (hesap menüsündeki "geri getir" için) */
export function useOnboardingDismissed(): boolean {
  const done = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  const hidden = useSyncExternalStore(subscribe, getHidden, getServerHidden);
  return hidden || done.length >= STEPS.length;
}

/** Turu sıfırla ve yeniden göster — "Gizle" tek yönlü bir kapı olmasın. */
export function resetOnboarding() {
  writeHidden(false);
  writeDone([]);
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
      className="group/ob rounded-xl bg-sidebar-accent/70 px-0.5 py-0.5 transition-colors hover:bg-sidebar-accent data-[state=open]:bg-sidebar-accent"
    >
      <div className="flex items-center gap-0.5 pr-0.5">
        <CollapsibleTrigger className="flex min-w-0 flex-1 items-center gap-2 rounded-md px-2 py-1.5 text-left outline-none transition-colors hover:bg-sidebar-accent focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-1 focus-visible:ring-offset-sidebar">
          {/* Halka YALNIZ kapalıyken: açıkken ilerlemeyi yatay şerit anlatıyor,
              iki gösterge aynı anda gereksiz tekrar olurdu. */}
          {!open && (
            <span className="text-muted-foreground">
              <Ring value={count} total={STEPS.length} />
            </span>
          )}
          <span className="min-w-0 flex-1 truncate text-sm text-sidebar-foreground">
            Başlangıç
          </span>
        </CollapsibleTrigger>

        {/* Sağ küme: durağan hâlde sayaç; satıra gelince aksiyonlar.
            Kapalıyken yalnız › (aç), açıkken ··· + ⌄ (seçenekler + kapat). */}
        <div className="flex shrink-0 items-center">
          <span className="px-1 text-xs text-muted-foreground tabular-nums group-hover/ob:hidden">
            {count}/{STEPS.length}
          </span>

          <div className="hidden items-center group-hover/ob:flex focus-within:flex">
            {open && (
              <DropdownMenu>
                <DropdownMenuTrigger
                  aria-label="Başlangıç seçenekleri"
                  className="rounded-md p-1 text-muted-foreground outline-none transition-colors hover:bg-sidebar-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-1 focus-visible:ring-offset-sidebar"
                >
                  <MoreHorizontal className="size-3.5" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" side="top">
                  <DropdownMenuItem onSelect={() => writeDone(STEPS.map((st) => st.id))}>
                    <Check className="size-4" />
                    Tümünü tamamlandı işaretle
                  </DropdownMenuItem>
                  <DropdownMenuItem onSelect={() => writeHidden(true)} variant="destructive">
                    <X className="size-4" />
                    Gizle
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
            <CollapsibleTrigger
              aria-label={open ? "Kapat" : "Aç"}
              className="rounded-md p-1 text-muted-foreground outline-none transition-colors hover:bg-sidebar-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-1 focus-visible:ring-offset-sidebar"
            >
              {open ? (
                <ChevronDown className="size-3.5" />
              ) : (
                <ChevronRight className="size-3.5" />
              )}
            </CollapsibleTrigger>
          </div>
        </div>
      </div>

      <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
        {/* yatay ilerleme — yalnız açıkken (kapalıyken halka bunu anlatıyor) */}
        {/* İlerleme scaleX ile ölçeklenir — width animasyonu layout tetikler,
            transform compositor'da kalır (ui-craft-detect kuralı). */}
        <div
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={STEPS.length}
          aria-valuenow={count}
          aria-label="Başlangıç ilerlemesi"
          className="mx-2 mt-1 mb-2 h-1 overflow-hidden rounded-full bg-sidebar-border"
        >
          <div
            className="h-full origin-left rounded-full bg-brand transition-transform duration-300"
            style={{ transform: `scaleX(${count / STEPS.length})` }}
          />
        </div>
        <ul className="space-y-0.5 pb-1">
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
