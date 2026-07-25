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
}: {
  children: React.ReactNode;
  className?: string;
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

  return (
    <div className="relative min-h-0 flex-1">
      <div ref={viewportRef} onScroll={onScroll} className={cn("h-full overflow-auto", className)}>
        {children}
      </div>
      <AnimatePresence>
        {showJump && (
          <motion.div
            initial={{ opacity: 0, x: "-50%", y: 6, scale: 0.9 }}
            animate={{ opacity: 1, x: "-50%", y: 0, scale: 1 }}
            exit={{ opacity: 0, x: "-50%", y: 6, scale: 0.9 }}
            transition={{ duration: 0.18, ease: [0.23, 1, 0.32, 1] }}
            className="absolute bottom-3 left-1/2"
          >
            <Button
              variant="outline"
              size="icon-sm"
              aria-label="En alta git"
              onClick={jump}
              className="rounded-full shadow-md"
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
          ? "max-w-[85%] rounded-2xl rounded-br-sm bg-secondary px-4 py-2 text-sm text-secondary-foreground"
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
