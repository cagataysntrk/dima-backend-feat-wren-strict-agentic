"use client";

import type { CSSProperties, PointerEvent, ReactNode, RefObject } from "react";
import { useEffect, useId, useRef, useState, useSyncExternalStore } from "react";
import {
  AnimatePresence,
  m,
  useInView,
  useMotionValue,
  useSpring,
  useTransform,
} from "motion/react";
import { cn } from "@dima/ui/utils";

const reducedMotionQuery = "(prefers-reduced-motion: reduce)";

function subscribeToReducedMotion(onStoreChange: () => void) {
  const media = window.matchMedia(reducedMotionQuery);
  media.addEventListener("change", onStoreChange);
  return () => media.removeEventListener("change", onStoreChange);
}

function useStableReducedMotion() {
  return useSyncExternalStore(
    subscribeToReducedMotion,
    () => window.matchMedia(reducedMotionQuery).matches,
    () => false,
  );
}

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
        // Satır yüksekliği sabitlenmez: `grid-auto-rows: auto` her satırı en uzun
        // öğesine göre boyutlar ve kardeşleri o yüksekliğe stretch eder. `auto-rows-fr`
        // kullanılmaz — v4'te minmax(0,1fr)'e derlenir ve taşan içeriği kırpar.
        "grid grid-cols-1 gap-4 md:grid-cols-6",
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
  tilt = true,
}: {
  children: ReactNode;
  className?: string;
  tilt?: boolean;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const reduceMotion = useStableReducedMotion();
  const pointerX = useMotionValue(50);
  const pointerY = useMotionValue(50);
  const rotateX = useSpring(useTransform(pointerY, [0, 100], [2.4, -2.4]), {
    stiffness: 210,
    damping: 24,
  });
  const rotateY = useSpring(useTransform(pointerX, [0, 100], [-2.4, 2.4]), {
    stiffness: 210,
    damping: 24,
  });
  const [active, setActive] = useState(false);
  const [supportsPointerMotion, setSupportsPointerMotion] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(
      "(min-width: 768px) and (hover: hover) and (pointer: fine)",
    );
    const update = () => setSupportsPointerMotion(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  function onPointerMove(event: PointerEvent<HTMLDivElement>) {
    if (!supportsPointerMotion) return;
    const bounds = cardRef.current?.getBoundingClientRect();
    if (!bounds) return;
    pointerX.set(((event.clientX - bounds.left) / bounds.width) * 100);
    pointerY.set(((event.clientY - bounds.top) / bounds.height) * 100);
    setActive(true);
  }

  function resetPointer() {
    pointerX.set(50);
    pointerY.set(50);
    setActive(false);
  }

  return (
    <m.div
      ref={cardRef}
      className={cn(
        "group relative flex flex-col overflow-hidden rounded-xl border bg-card shadow-sm [transform-style:preserve-3d]",
        "transition-[border-color,box-shadow] duration-300 hover:border-brand/30 hover:shadow-xl hover:shadow-brand/5 focus-visible:border-brand/30 focus-visible:shadow-xl focus-within:border-brand/30 focus-within:shadow-xl focus-within:shadow-brand/5",
        className,
      )}
      onPointerMove={onPointerMove}
      onPointerLeave={resetPointer}
      onBlurCapture={resetPointer}
      style={
        tilt && supportsPointerMotion && !reduceMotion
          ? { rotateX, rotateY, transformPerspective: 900 }
          : undefined
      }
    >
      <m.div
        aria-hidden="true"
        className="pointer-events-none absolute -inset-px z-0"
        animate={{ opacity: active ? 1 : 0 }}
        transition={{ duration: 0.2 }}
        style={{
          background: useTransform(
            [pointerX, pointerY],
            ([x, y]) =>
              `radial-gradient(420px circle at ${x}% ${y}%, color-mix(in oklch, var(--brand) 16%, transparent), transparent 68%)`,
          ),
        }}
      />
      {/* `flex-1` + `flex flex-col`: kart hücresini gerçekten doldurur ve çocukların
          `mt-auto` ile alta sabitlenmesini mümkün kılar. Eskiden buradaki `h-full`
          atıldı — ebeveyn yüksekliği auto olduğu için hiçbir şey yapmıyordu. */}
      <div className="relative z-10 flex min-h-0 flex-1 flex-col [transform:translateZ(0)]">{children}</div>
    </m.div>
  );
}

export function AnimatedGridPattern({ className }: { className?: string }) {
  const reduceMotion = useStableReducedMotion();
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

// Düzen sınıfı ÜRETMEZ: eskiden varsayılan `grid gap-2` basıyordu ve çağıran taraf
// `space-y-*` geçtiğinde tailwind-merge ikisini uzlaştıramadığı için (farklı CSS
// özellikleri) boşluk iki kez uygulanıyordu. Düzeni artık her zaman çağıran verir.
// `as="ul"` gerçek liste semantiği için — çocuklar `<li>` olarak sarılır.
export function AnimatedList({
  children,
  className,
  as = "div",
  itemClassName,
}: {
  children: ReactNode[];
  className?: string;
  as?: "div" | "ul";
  itemClassName?: string;
}) {
  const Root = as === "ul" ? "ul" : "div";
  const Item = as === "ul" ? m.li : m.div;
  return (
    <Root className={className}>
      {children.map((child, index) => (
        <Item
          key={index}
          className={itemClassName}
          initial={{ opacity: 0, x: -12 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.7 }}
          transition={{ duration: 0.32, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
        >
          {child}
        </Item>
      ))}
    </Root>
  );
}

export function WordRotate({
  words,
  className,
  duration = 2400,
}: {
  words: string[];
  className?: string;
  duration?: number;
}) {
  const reduceMotion = useStableReducedMotion();
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (reduceMotion || words.length < 2) return;
    const timer = window.setInterval(
      () => setIndex((value) => (value + 1) % words.length),
      duration,
    );
    return () => window.clearInterval(timer);
  }, [duration, reduceMotion, words]);

  return (
    <span
      className={cn(
        "relative isolate inline-grid overflow-visible pb-[0.12em] align-bottom leading-[1.04]",
        className,
      )}
    >
      {/* Yer tutucu, kelimeleri aynı grid hücresine bindirerek hücreyi gerçek
          RENDER genişliğine göre boyutlar. Eski hâli `word.length` (karakter sayısı)
          ile seçiyordu; orantılı display fontunda kısa ama geniş bir kelime
          (ör. "MODEL") uzun ama dar olandan taşabiliyordu. */}
      {words.map((word) => (
        <span aria-hidden="true" className="invisible col-start-1 row-start-1" key={word}>
          {word}
        </span>
      ))}
      <AnimatePresence mode="wait" initial={false}>
        <m.span
          className="relative z-10 col-start-1 row-start-1"
          key={words[index]}
          initial={reduceMotion ? false : { opacity: 0, y: -18, filter: "blur(6px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={reduceMotion ? undefined : { opacity: 0, y: 18, filter: "blur(6px)" }}
          transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
        >
          {words[index]}
        </m.span>
      </AnimatePresence>
    </span>
  );
}

export function Marquee({
  children,
  className,
  reverse = false,
  pauseOnHover = true,
  repeat = 4,
}: {
  children: ReactNode;
  className?: string;
  reverse?: boolean;
  pauseOnHover?: boolean;
  repeat?: number;
}) {
  const marqueeRef = useRef<HTMLDivElement>(null);
  const inView = useInView(marqueeRef, { margin: "160px" });
  return (
    <div
      ref={marqueeRef}
      className={cn(
        "marketing-marquee group flex overflow-hidden [--duration:42s] [--gap:1rem]",
        className,
      )}
    >
      {Array.from({ length: repeat }, (_, index) => (
        <div
          aria-hidden={index > 0 || undefined}
          className={cn(
            // items-stretch: kartlar içerik uzunluğuna göre 72/92px arasında değişip
            // dikey ortalanmak yerine satırın yüksekliğini paylaşır.
            "flex shrink-0 items-stretch gap-[var(--gap)] pr-[var(--gap)]",
            reverse ? "marketing-marquee-reverse" : "marketing-marquee-track",
            pauseOnHover && "group-hover:[animation-play-state:paused] group-focus-within:[animation-play-state:paused]",
            !inView && "[animation-play-state:paused]",
          )}
          key={index}
        >
          {children}
        </div>
      ))}
    </div>
  );
}

export function NumberTicker({
  value,
  className,
  decimals = 0,
  locale = "en-US",
}: {
  value: number;
  className?: string;
  decimals?: number;
  locale?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const reduceMotion = useStableReducedMotion();
  const motionValue = useMotionValue(reduceMotion ? value : 0);
  const spring = useSpring(motionValue, { damping: 36, stiffness: 90 });
  const display = useTransform(spring, (latest) =>
    new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(latest),
  );

  useEffect(() => {
    if (inView || reduceMotion) motionValue.set(value);
  }, [inView, motionValue, reduceMotion, value]);

  return <m.span className={className} ref={ref}>{display}</m.span>;
}

export function Particles({
  className,
  quantity = 42,
}: {
  className?: string;
  quantity?: number;
}) {
  const reduceMotion = useStableReducedMotion();
  const particlesRef = useRef<HTMLDivElement>(null);
  const inView = useInView(particlesRef, { margin: "160px" });
  return (
    <div aria-hidden="true" className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)} ref={particlesRef}>
      {Array.from({ length: quantity }, (_, index) => {
        const left = (index * 37 + 11) % 100;
        const top = (index * 61 + 7) % 100;
        const size = 1 + (index % 3) * 0.6;
        return (
          <span
            className={cn("marketing-particle absolute rounded-full bg-brand/45", reduceMotion && "animate-none")}
            key={index}
            style={
              {
                left: `${left}%`,
                top: `${top}%`,
                width: `${size}px`,
                height: `${size}px`,
                "--particle-delay": `${-(index % 12) * 0.7}s`,
                "--particle-duration": `${7 + (index % 6)}s`,
                "--particle-drift": `${(index % 2 ? 1 : -1) * (10 + (index % 5) * 4)}px`,
                animationPlayState: reduceMotion || !inView ? "paused" : "running",
              } as CSSProperties
            }
          />
        );
      })}
    </div>
  );
}

export function AnimatedBeam({
  containerRef,
  fromRef,
  toRef,
  className,
  curvature = 0,
  reverse = false,
  duration = 4,
  delay = 0,
}: {
  containerRef: RefObject<HTMLElement | null>;
  fromRef: RefObject<HTMLElement | null>;
  toRef: RefObject<HTMLElement | null>;
  className?: string;
  curvature?: number;
  reverse?: boolean;
  duration?: number;
  delay?: number;
}) {
  const id = useId();
  const reduceMotion = useStableReducedMotion();
  const [path, setPath] = useState({ d: "", width: 0, height: 0 });

  useEffect(() => {
    const update = () => {
      const container = containerRef.current?.getBoundingClientRect();
      const from = fromRef.current?.getBoundingClientRect();
      const to = toRef.current?.getBoundingClientRect();
      if (!container || !from || !to) return;
      const startX = from.left - container.left + from.width / 2;
      const startY = from.top - container.top + from.height / 2;
      const endX = to.left - container.left + to.width / 2;
      const endY = to.top - container.top + to.height / 2;
      setPath({
        width: container.width,
        height: container.height,
        d: `M ${startX},${startY} Q ${(startX + endX) / 2},${startY - curvature} ${endX},${endY}`,
      });
    };
    const observer = new ResizeObserver(update);
    if (containerRef.current) observer.observe(containerRef.current);
    update();
    return () => observer.disconnect();
  }, [containerRef, curvature, fromRef, toRef]);

  return (
    <svg
      aria-hidden="true"
      className={cn("pointer-events-none absolute inset-0", className)}
      fill="none"
      height={path.height}
      viewBox={`0 0 ${path.width} ${path.height}`}
      width={path.width}
    >
      <path d={path.d} stroke="var(--border)" strokeWidth="1.5" />
      {!reduceMotion ? (
        <path
          className={reverse ? "marketing-beam-path-reverse" : "marketing-beam-path"}
          d={path.d}
          pathLength="1"
          stroke={`url(#${id})`}
          strokeLinecap="round"
          strokeWidth="2"
          style={
            {
              "--beam-path-duration": `${duration}s`,
              "--beam-path-delay": `${delay}s`,
            } as CSSProperties
          }
        />
      ) : null}
      <defs>
        <linearGradient id={id}>
          <stop stopColor="var(--brand)" stopOpacity="0" />
          <stop offset="0.45" stopColor="var(--brand)" />
          <stop offset="1" stopColor="var(--brand)" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
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
