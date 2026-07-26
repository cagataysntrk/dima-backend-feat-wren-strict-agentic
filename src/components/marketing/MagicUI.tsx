"use client";

import type { CSSProperties, MouseEvent, ReactNode } from "react";
import { useRef, useState } from "react";
import { m, useReducedMotion } from "motion/react";
import { cn } from "@/lib/utils";

export function BentoGrid({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "grid auto-rows-[15rem] grid-cols-1 gap-4 md:grid-cols-6",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function MagicCard({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [pointer, setPointer] = useState({ x: 0, y: 0, visible: false });

  function onPointerMove(event: MouseEvent<HTMLDivElement>) {
    const bounds = cardRef.current?.getBoundingClientRect();
    if (!bounds) return;
    setPointer({
      x: event.clientX - bounds.left,
      y: event.clientY - bounds.top,
      visible: true,
    });
  }

  return (
    <div
      ref={cardRef}
      className={cn(
        "group relative overflow-hidden rounded-xl border bg-card shadow-sm",
        className,
      )}
      onMouseMove={onPointerMove}
      onMouseLeave={() => setPointer((value) => ({ ...value, visible: false }))}
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 z-0 opacity-0 transition-opacity duration-200"
        style={
          {
            background: `radial-gradient(360px circle at ${pointer.x}px ${pointer.y}px, color-mix(in oklch, var(--brand) 12%, transparent), transparent 70%)`,
            opacity: pointer.visible ? 1 : 0,
          } as CSSProperties
        }
      />
      <div className="relative z-10 h-full">{children}</div>
    </div>
  );
}

export function AnimatedGridPattern({ className }: { className?: string }) {
  const reduceMotion = useReducedMotion();
  return (
    <div
      aria-hidden="true"
      className={cn(
        "marketing-grid pointer-events-none absolute inset-0 overflow-hidden [mask-image:linear-gradient(to_bottom,black,transparent_90%)]",
        className,
      )}
    >
      <m.div
        className="absolute left-[12%] top-[22%] size-1.5 rounded-full bg-brand"
        animate={reduceMotion ? undefined : { opacity: [0.25, 0.9, 0.25] }}
        transition={
          reduceMotion
            ? undefined
            : { duration: 3.2, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }
        }
      />
      <m.div
        className="absolute right-[18%] top-[48%] size-1 rounded-full bg-brand"
        animate={reduceMotion ? undefined : { opacity: [0.2, 0.75, 0.2] }}
        transition={
          reduceMotion
            ? undefined
            : {
                duration: 3.8,
                delay: 0.6,
                repeat: Number.POSITIVE_INFINITY,
                ease: "easeInOut",
              }
        }
      />
    </div>
  );
}

export function BorderBeam({
  className,
  duration = 7,
}: {
  className?: string;
  duration?: number;
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "marketing-border-beam pointer-events-none absolute inset-0 rounded-[inherit]",
        className,
      )}
      style={{ "--beam-duration": `${duration}s` } as CSSProperties}
    />
  );
}

export function AnimatedList({
  children,
  className,
}: {
  children: ReactNode[];
  className?: string;
}) {
  return (
    <div className={cn("grid gap-2", className)}>
      {children.map((child, index) => (
        <m.div
          key={index}
          initial={{ opacity: 0, x: -12 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.7 }}
          transition={{ duration: 0.32, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
        >
          {child}
        </m.div>
      ))}
    </div>
  );
}

export function ProgressiveBlur({
  className,
  direction = "bottom",
}: {
  className?: string;
  direction?: "top" | "bottom";
}) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "pointer-events-none absolute inset-x-0 z-10 h-24 backdrop-blur-[2px]",
        direction === "bottom" ? "bottom-0" : "top-0",
        className,
      )}
      style={{
        maskImage:
          direction === "bottom"
            ? "linear-gradient(to bottom, transparent, black)"
            : "linear-gradient(to top, transparent, black)",
      }}
    />
  );
}
