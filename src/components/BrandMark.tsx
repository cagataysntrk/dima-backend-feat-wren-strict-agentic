// dima wordmark — Plus Jakarta Sans, 400. Sade tipografik kilit: çizilen monoline
// SVG harfler ve draw-in animasyonları kaldırıldı. Tek marka motifi kaldı: i'nin
// noktası accent'tir — bu yüzden "i" noktasız "ı" olarak dizilip nokta ayrı bir
// öğe olarak konur. Açılım gerekçesi: docs/branding.md (kök repo).

type PillarKey = "d" | "i" | "m" | "a";

interface Pillar {
  letter: PillarKey;
  word: string;
  tr: string;
  en: string;
}

export const PILLARS: Pillar[] = [
  {
    letter: "d",
    word: "deterministic",
    tr: "Her SQL çalıştırılmadan önce dry-plan'dan geçer; SELECT-only guard.",
    en: "Every SQL query passes a dry plan before execution, with a SELECT-only guard.",
  },
  {
    letter: "i",
    word: "intelligent",
    tr: "Doğal dil → SQL: bilinen metrik cube'dan, gerisi denetlenen LLM ile.",
    en: "Natural language to SQL, grounded in known metrics and bounded LLM proposals.",
  },
  {
    letter: "m",
    word: "modeled",
    tr: "MDL semantik katman tek doğruluk kaynağıdır; şema uydurma yok.",
    en: "The MDL semantic layer is the source of truth; schemas are not invented.",
  },
  {
    letter: "a",
    word: "agentic",
    tr: "Planlanan ince ajan mimarisi ve kontrollü, yeniden kullanılabilir analitik akışları.",
    en: "Planned thin-agent architecture and controlled, reusable analytical workflows.",
  },
];

const SIZES = {
  sm: { text: "text-base", gap: "gap-[0.02em]", sep: "size-[2px]" },
  md: { text: "text-2xl", gap: "gap-[0.02em]", sep: "size-[3px]" },
  xl: { text: "text-5xl md:text-6xl", gap: "gap-[0.02em]", sep: "size-[4px]" },
} as const;

interface BrandMarkProps {
  size?: keyof typeof SIZES;
  /** One-shot reveal on mount: letters rise in sequence, then the i-dot drops. */
  animate?: boolean;
  /** Monochrome variant: i-dot inherits currentColor, hover accents off. */
  ink?: boolean;
  /** Show the per-letter pillar words on hover. Off by default — in app chrome
   *  (sidebar, auth, help) the wordmark is a logo, not an explainer. */
  pillars?: boolean;
  /** Pixel-dot separators between letters: d·i·m·a. */
  interpunct?: boolean;
  className?: string;
}

/** Delay of the i-dot: after the last letter has landed. */
const DOT_DELAY = "0.6s";

/** The dotless-ı + separate accent dot that carries the brand motif. */
function DottedI({ ink, animate }: { ink?: boolean; animate?: boolean }) {
  return (
    <span className="relative inline-block">
      {/* U+0131 — noktasız ı (latin-ext altkümesi zaten Türkçe için yükleniyor) */}
      {"ı"}
      <span
        aria-hidden="true"
        className={`absolute left-1/2 top-[0.14em] size-[0.14em] -translate-x-1/2 rounded-full ${
          ink ? "bg-current" : "bg-brand"
        } ${animate ? "brand-dot-drop" : ""}`}
        style={animate ? { ["--brand-delay" as string]: DOT_DELAY } : undefined}
      />
    </span>
  );
}

export function BrandMark({
  size = "md",
  animate = false,
  ink = false,
  pillars = false,
  interpunct = false,
  className = "",
}: BrandMarkProps) {
  const s = SIZES[size];
  return (
    <span
      role="img"
      aria-label="dima — deterministic, intelligent, modeled, agentic"
      // ink varyantı currentColor'ı miras alır (koyu zeminli lockup'lar için).
      className={`inline-flex items-end font-sans font-normal leading-none tracking-tight ${
        ink ? "" : "text-foreground"
      } ${s.gap} ${s.text} ${className}`}
    >
      {PILLARS.map((pillar, idx) => (
        <span key={pillar.letter} className="contents">
          {interpunct && idx > 0 && (
            <span
              aria-hidden="true"
              className={`${s.sep} mb-[0.42em] shrink-0 rounded-full bg-neutral-400 dark:bg-neutral-600`}
            />
          )}
          <span className="group relative inline-flex flex-col items-center">
            <span
              aria-hidden="true"
              className={`${ink ? "" : "transition-colors group-hover:text-brand"} ${
                animate ? "brand-rise" : ""
              }`}
              style={
                animate ? { ["--brand-delay" as string]: `${idx * 0.08}s` } : undefined
              }
            >
              {pillar.letter === "i" ? <DottedI ink={ink} animate={animate} /> : pillar.letter}
            </span>

            {pillars && (
              <span
                lang="en"
                className="pointer-events-none absolute top-full z-10 mt-2 translate-y-1 whitespace-nowrap border border-hairline bg-background px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-neutral-500 opacity-0 transition-all duration-200 group-hover:translate-y-0 group-hover:opacity-100"
              >
                {pillar.word}
              </span>
            )}
          </span>
        </span>
      ))}
    </span>
  );
}

/** Four pillar cards — the letter-by-letter expansion of the wordmark. */
export function BrandLockup({ locale = "tr" }: { locale?: "tr" | "en" }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {PILLARS.map((pillar, idx) => (
        <div
          key={pillar.letter}
          className="group border border-hairline p-4 transition-colors hover:border-brand/40"
        >
          <span
            aria-hidden="true"
            className="inline-block font-sans text-4xl font-normal leading-none tracking-tight text-neutral-400 transition-colors group-hover:text-brand dark:text-neutral-600"
          >
            {pillar.letter === "i" ? <DottedI ink /> : pillar.letter}
          </span>
          <p
            lang="en"
            className="mt-3 font-mono text-[11px] uppercase tracking-wider text-foreground"
          >
            <span className="mr-1.5 text-brand">
              {String(idx + 1).padStart(2, "0")}
            </span>
            {pillar.word}
          </p>
          <p className="mt-1.5 text-xs leading-relaxed text-neutral-600 dark:text-neutral-400">
            {pillar[locale]}
          </p>
        </div>
      ))}
    </div>
  );
}
