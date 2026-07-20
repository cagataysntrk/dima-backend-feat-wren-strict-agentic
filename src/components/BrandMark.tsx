// dima wordmark — monoline letterforms drawn from a shared geometric grammar
// (bowl + stem + arch). Terminal-minimal dili izler: tek vurgu rengi accent,
// keskin köşeler, mono chip'ler. i'nin noktası accent'tir (imleç göndermesi).
// Açılım gerekçesi: docs/branding.md (kök repo).

type PillarKey = "d" | "i" | "m" | "a";

interface Pillar {
  letter: PillarKey;
  word: string;
  tr: string;
}

export const PILLARS: Pillar[] = [
  {
    letter: "d",
    word: "deterministic",
    tr: "Her SQL çalıştırılmadan önce dry-plan'dan geçer; SELECT-only guard.",
  },
  {
    letter: "i",
    word: "intelligent",
    tr: "Doğal dil → SQL: bilinen metrik cube'dan, gerisi denetlenen LLM ile.",
  },
  {
    letter: "m",
    word: "modeled",
    tr: "MDL semantik katman tek doğruluk kaynağıdır; şema uydurma yok.",
  },
  {
    letter: "a",
    word: "agentic",
    tr: "İnce ajan müşteri tarafında; zamanlanmış, otonom raporlama.",
  },
];

// Shared metrics: viewBox height 56, baseline y=46, x-height y=22, ascender y=8.
const GLYPHS: Record<PillarKey, { width: number; paths: string[] }> = {
  d: {
    width: 34,
    paths: ["M29 34 A12 12 0 1 1 5 34 A12 12 0 1 1 29 34", "M29 8 L29 46"],
  },
  i: {
    width: 10,
    paths: ["M5 22 L5 46"],
  },
  m: {
    width: 42,
    paths: [
      "M5 46 L5 22",
      "M5 31 C5 21.5 21 21.5 21 31 L21 46",
      "M21 31 C21 21.5 37 21.5 37 31 L37 46",
    ],
  },
  a: {
    width: 34,
    paths: ["M29 34 A12 12 0 1 1 5 34 A12 12 0 1 1 29 34", "M29 22 L29 46"],
  },
};

const SIZES = {
  sm: { letter: "h-5", gap: "gap-1.5", dot: "size-[2px]", stroke: 5.5 },
  md: { letter: "h-9", gap: "gap-2", dot: "size-[3px]", stroke: 5 },
  xl: {
    letter: "h-16 md:h-20",
    gap: "gap-3 md:gap-4",
    dot: "size-[4px]",
    stroke: 5,
  },
} as const;

interface BrandMarkProps {
  size?: keyof typeof SIZES;
  /** Draw-in animation on mount (stroke reveal + dot pop). */
  animate?: boolean;
  /** Monochrome variant: i-dot inherits currentColor, hover accents off. */
  ink?: boolean;
  /** Pixel-dot separators between letters: d·i·m·a. */
  interpunct?: boolean;
  className?: string;
}

export function BrandMark({
  size = "md",
  animate = false,
  ink = false,
  interpunct = false,
  className = "",
}: BrandMarkProps) {
  const s = SIZES[size];
  return (
    <span
      role="img"
      aria-label="dima — deterministic, intelligent, modeled, agentic"
      className={`inline-flex items-end ${s.gap} ${className}`}
    >
      {PILLARS.map((pillar, idx) => {
        const glyph = GLYPHS[pillar.letter];
        const delay = `${idx * 0.15}s`;
        return (
          <span key={pillar.letter} className="contents">
            {interpunct && idx > 0 && (
              <span
                aria-hidden="true"
                className={`${s.dot} mb-[0.35em] self-center bg-neutral-400 dark:bg-neutral-600 ${animate ? "brand-pop" : ""}`}
                style={
                  animate
                    ? { ["--brand-delay" as string]: `${0.55 + idx * 0.08}s` }
                    : undefined
                }
              />
            )}
            <span className="group relative flex flex-col items-center">
              <svg
                viewBox={`0 0 ${glyph.width} 56`}
                style={{ aspectRatio: `${glyph.width} / 56` }}
                className={`${s.letter} w-auto text-foreground transition-colors ${ink ? "" : "group-hover:text-accent"}`}
                fill="none"
                stroke="currentColor"
                strokeWidth={s.stroke}
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                {glyph.paths.map((d) => (
                  <path
                    key={d}
                    d={d}
                    pathLength={1}
                    className={animate ? "brand-draw" : undefined}
                    style={
                      animate ? { ["--brand-delay" as string]: delay } : undefined
                    }
                  />
                ))}
                {pillar.letter === "i" && (
                  <circle
                    cx={5}
                    cy={10.5}
                    r={3.75}
                    stroke="none"
                    className={`${ink ? "fill-current" : "fill-accent"} ${animate ? "brand-pop dima-dot" : ""}`}
                    style={
                      animate
                        ? { ["--brand-delay" as string]: "0.55s" }
                        : undefined
                    }
                  />
                )}
              </svg>

              {!ink && (
                <span
                  lang="en"
                  className="pointer-events-none absolute top-full z-10 mt-2 whitespace-nowrap border border-hairline bg-background px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-neutral-500 opacity-0 translate-y-1 transition-all duration-200 group-hover:opacity-100 group-hover:translate-y-0"
                >
                  {pillar.word}
                </span>
              )}
            </span>
          </span>
        );
      })}
    </span>
  );
}

/** Four pillar cards — the letter-by-letter expansion of the wordmark. */
export function BrandLockup() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {PILLARS.map((pillar, idx) => {
        const glyph = GLYPHS[pillar.letter];
        return (
          <div
            key={pillar.letter}
            className="group border border-hairline p-4 transition-colors hover:border-accent/40"
          >
            <svg
              viewBox={`0 0 ${glyph.width} 56`}
              style={{ aspectRatio: `${glyph.width} / 56` }}
              className="h-8 w-auto text-neutral-400 transition-colors group-hover:text-accent dark:text-neutral-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={5}
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              {glyph.paths.map((d) => (
                <path key={d} d={d} />
              ))}
              {pillar.letter === "i" && (
                <circle
                  cx={5}
                  cy={10.5}
                  r={3.75}
                  stroke="none"
                  className="fill-current"
                />
              )}
            </svg>
            <p
              lang="en"
              className="mt-3 font-mono text-[11px] uppercase tracking-wider text-foreground"
            >
              <span className="mr-1.5 text-accent">
                {String(idx + 1).padStart(2, "0")}
              </span>
              {pillar.word}
            </p>
            <p className="mt-1.5 text-xs leading-relaxed text-neutral-500">
              {pillar.tr}
            </p>
          </div>
        );
      })}
    </div>
  );
}
