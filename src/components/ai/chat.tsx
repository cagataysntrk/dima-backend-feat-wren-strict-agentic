"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ArrowDown, Sparkles, User, X } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { enterUp } from "@/lib/motion";
import { cn } from "@/lib/utils";

/** dima's assistant avatar — brand-tinted mark (icon placeholder). */
export function DimaAvatar({ className }: { className?: string }) {
  return (
    <Avatar className={cn("size-7 border border-brand/20", className)}>
      <AvatarFallback className="rounded-[inherit] bg-brand/10 text-brand">
        <Sparkles className="size-3.5" />
      </AvatarFallback>
    </Avatar>
  );
}

/** User placeholder avatar (generic icon until a real profile image/initials exist). */
export function UserAvatar({ className }: { className?: string }) {
  return (
    <Avatar className={cn("size-7 border border-border", className)}>
      <AvatarFallback className="rounded-[inherit] bg-secondary text-secondary-foreground">
        <User className="size-3.5" />
      </AvatarFallback>
    </Avatar>
  );
}

/**
 * Local AI-chat primitives modeled on the shadcn AI component set
 * (Message Scroller / Message / Bubble / Attachment). Built on our tokens so
 * they stay on-theme; swap for an upstream registry version if you adopt one.
 */

/** MessageScroller — auto-sticks to the bottom as content streams in; shows a
 * "jump to latest" button when the user has scrolled up. */
export function MessageScroller({
  children,
  className,
  /** Alta-git butonunun dipten yüksekliği (üstünde yüzen komut satırını aşmak için). */
  jumpOffset = "bottom-3",
  /** Değeri değişince yukarıda olsan bile en alta ZORLA kaydırır (yeni cevap geldi). */
  scrollKey,
}: {
  children: React.ReactNode;
  className?: string;
  jumpOffset?: string;
  scrollKey?: string | number;
}) {
  const viewportRef = useRef<HTMLDivElement>(null);
  const stick = useRef(true);
  const [showJump, setShowJump] = useState(false);

  const onScroll = () => {
    const el = viewportRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 48;
    stick.current = atBottom;
    setShowJump(!atBottom);
  };

  // Scroll on any content mutation (new message, chart mount) while stuck to bottom.
  useEffect(() => {
    const el = viewportRef.current;
    if (!el) return;
    const obs = new MutationObserver(() => {
      if (stick.current) el.scrollTo({ top: el.scrollHeight });
    });
    obs.observe(el, { childList: true, subtree: true });
    return () => obs.disconnect();
  }, []);

  const jump = () => {
    const el = viewportRef.current;
    el?.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  };

  // Yeni cevap/soru geldiğinde kullanıcı yukarıda okuyor olsa bile oraya götür.
  // (Chip düzenlemesi eski bir mesajın üstünde yapılır; cevap en altta doğar —
  //  kaydırmazsak "hiçbir şey olmadı" hissi veriyordu.)
  const firstRun = useRef(true);
  useEffect(() => {
    if (scrollKey === undefined) return;
    const el = viewportRef.current;
    if (!el) return;
    stick.current = true;
    setShowJump(false);
    el.scrollTo({ top: el.scrollHeight, behavior: firstRun.current ? "auto" : "smooth" });
    firstRun.current = false;
  }, [scrollKey]);

  return (
    <div className="relative min-h-0 flex-1">
      <div ref={viewportRef} onScroll={onScroll} className={cn("h-full overflow-auto [scrollbar-gutter:stable_both-edges]", className)}>
        {children}
      </div>
      {/* Emil kuralları: kısa (~0.22s), yay değil hızlı-yavaşlayan eğri, ve hareket
          ANLAM taşısın — buton aşağı-inişi temsil ettiği için AŞAĞIDAN yukarı süzülüp
          gelir, kaybolurken aşağı döner. Dönüş küçük (-90°→0): fark edilir ama dikkat
          çalmaz. Çıkış girişin yarısı kadar sürer (çıkışlar hızlı olmalı). */}
      <AnimatePresence>
        {showJump && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.85, rotate: -90 }}
            animate={{ opacity: 1, y: 0, scale: 1, rotate: 0 }}
            exit={{ opacity: 0, y: 8, scale: 0.9, rotate: -60, transition: { duration: 0.12 } }}
            transition={{ duration: 0.22, ease: [0.32, 0.72, 0, 1] }}
            style={{ x: "-50%" }}
            className={cn("pointer-events-none absolute left-1/2 z-20", jumpOffset)}
          >
            <Button
              variant="outline"
              size="icon-sm"
              aria-label="En alta git"
              onClick={jump}
              className="pointer-events-auto rounded-full bg-card shadow-lg transition-transform duration-150 hover:-translate-y-px active:translate-y-0"
            >
              <ArrowDown className="size-4" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/** Message — one turn; aligns by author. Animates in on mount (existing turns
 * keep their key, so they never re-animate). */
export function Message({
  from,
  children,
  className,
}: {
  from: "user" | "assistant";
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      data-from={from}
      variants={enterUp}
      initial="hidden"
      animate="show"
      className={cn("flex w-full", from === "user" ? "justify-end" : "justify-start", className)}
    >
      {children}
    </motion.div>
  );
}

/** Bubble — the message body. User turns get a chat bubble; assistant turns are
 * full-width (so charts/reports can breathe). */
export function Bubble({
  from,
  children,
  className,
}: {
  from: "user" | "assistant";
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        from === "user"
          ? "max-w-[calc(100%-2.5rem)] rounded-2xl rounded-br-sm bg-secondary px-4 py-2 text-sm text-secondary-foreground"
          : "min-w-0 flex-1",
        className,
      )}
    >
      {children}
    </div>
  );
}

/** Attachment — a compact context/file chip (e.g. the carried report context). */
export function Attachment({
  children,
  onRemove,
  title,
  className,
}: {
  children: React.ReactNode;
  onRemove?: () => void;
  title?: string;
  className?: string;
}) {
  return (
    <Badge variant="brand-subtle" title={title} className={cn("gap-1.5 font-mono text-[10px]", className)}>
      {children}
      {onRemove && (
        <button type="button" onClick={onRemove} className="hover:text-foreground" aria-label="Kaldır">
          <X className="size-3" />
        </button>
      )}
    </Badge>
  );
}
