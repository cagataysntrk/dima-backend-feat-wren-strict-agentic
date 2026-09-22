"use client";

import { AnimatePresence, motion } from "motion/react";
import { Check, Copy } from "lucide-react";
import { cn } from "../utils";

/**
 * Kopyala → tik geçişi (Emil Kowalski deseni).
 *
 * İlkeler:
 * - Hareket ANLAM taşır: ikon yerinde DÖNEREK takas olur — "aynı nesne durum
 *   değiştirdi", "biri gidip başkası geldi" değil. Bu yüzden ikisi de aynı
 *   merkezde üst üste (`absolute inset-0`), çapraz kayma yok.
 * - Kısa ve asimetrik: giriş 0.2s yumuşak-çıkışlı eğri, çıkış 0.12s. Çıkışlar
 *   her zaman daha hızlı olmalı, yoksa arayüz ağır hissettirir.
 * - Dönüş küçük (±90°) ve ölçek 0.6'dan başlar: fark edilir ama dikkat çalmaz.
 * - `MotionConfig reducedMotion="user"` global olduğu için hareket kısıtlı
 *   kullanıcılarda kendiliğinden sade bir geçişe düşer.
 */
export function CopyIcon({
  copied,
  className,
}: {
  copied: boolean;
  className?: string;
}) {
  return (
    <span className={cn("relative inline-flex size-3.5 shrink-0", className)} aria-hidden="true">
      <AnimatePresence initial={false} mode="popLayout">
        {copied ? (
          <motion.span
            key="check"
            initial={{ opacity: 0, scale: 0.6, rotate: -90 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            exit={{ opacity: 0, scale: 0.6, rotate: 90, transition: { duration: 0.12 } }}
            transition={{ duration: 0.2, ease: [0.32, 0.72, 0, 1] }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <Check className="size-full text-emerald-600 dark:text-emerald-400" strokeWidth={2.5} />
          </motion.span>
        ) : (
          <motion.span
            key="copy"
            initial={{ opacity: 0, scale: 0.6, rotate: 90 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            exit={{ opacity: 0, scale: 0.6, rotate: -90, transition: { duration: 0.12 } }}
            transition={{ duration: 0.2, ease: [0.32, 0.72, 0, 1] }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <Copy className="size-full" />
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  );
}
