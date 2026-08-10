"use client";

import { type ReactNode, useEffect, useState } from "react";
import { domAnimation, LazyMotion, m, useReducedMotion } from "motion/react";
import { cn } from "@/lib/utils";

const revealTransition = {
  duration: 0.48,
  ease: [0.22, 1, 0.36, 1] as const,
};

export function MarketingMotionProvider({ children }: { children: ReactNode }) {
  return (
    <LazyMotion features={domAnimation}>
      {children}
    </LazyMotion>
  );
}

export function Reveal({
  children,
  className,
  delay = 0,
  y = 22,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
  y?: number;
}) {
  return (
    <m.div
      data-marketing-reveal
      data-marketing-reveal-y={y}
      className={className}
      // Motion enhances a visible document. Keeping the server/first paint
      // visible prevents a long blank page when JS or IntersectionObserver is
      // delayed, disabled, or a full-page screenshot is taken.
      initial={false}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.18 }}
      transition={{ ...revealTransition, delay }}
    >
      {children}
    </m.div>
  );
}

export function Stagger({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <m.div
      data-marketing-reveal
      className={className}
      initial={false}
      whileInView="visible"
      viewport={{ once: true, amount: 0.16 }}
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.075 } },
      }}
    >
      {children}
    </m.div>
  );
}

export function StaggerItem({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <m.div
      data-marketing-reveal
      className={className}
      variants={{
        hidden: { opacity: 0, y: 18 },
        visible: { opacity: 1, y: 0, transition: revealTransition },
      }}
    >
      {children}
    </m.div>
  );
}

export function Float({
  children,
  className,
  distance = 8,
  duration = 5.5,
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  distance?: number;
  duration?: number;
  delay?: number;
}) {
  const reduceMotion = useReducedMotion();
  const [supportsAmbientMotion, setSupportsAmbientMotion] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)");
    const update = () => setSupportsAmbientMotion(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  const animate = !reduceMotion && supportsAmbientMotion;

  return (
    <m.div
      className={cn("will-change-transform", className)}
      animate={animate ? { y: [0, -distance, 0] } : undefined}
      transition={
        animate
          ? {
              duration,
              delay,
              repeat: Number.POSITIVE_INFINITY,
              ease: "easeInOut",
            }
          : undefined
      }
    >
      {children}
    </m.div>
  );
}

export function DrawPath({
  d,
  className,
}: {
  d: string;
  className?: string;
}) {
  return (
    <m.path
      d={d}
      className={className}
      fill="none"
      initial={{ pathLength: 0, opacity: 0 }}
      whileInView={{ pathLength: 1, opacity: 1 }}
      viewport={{ once: true, amount: 0.45 }}
      transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
    />
  );
}
