"use client";

import type { Interpretation } from "@/lib/types";

// EVRENSEL ÇIKTI YORUMU (feature flag: cikti_yorumlama). Backend her tablo/grafik/rapor/KPI
// için DETERMİNİSTİK analiz üretir (en yüksek/düşük, % değişim, trend yönü + lower_is_better
// iyi/kötü çerçevesi, pay); burada yalnız gösterilir. Bayrak kapalıysa yanıtta interpretation
// yok → hiç render edilmez. Demo lucide kullanmıyor → inline SVG ampul.
// K3 sinyal önem → renk. warning=amber, critical=kırmızı, info=nötr.
const SIGNAL_TONE: Record<string, string> = {
  critical: "border-red-500/30 bg-red-500/[0.06] text-red-600 dark:text-red-400",
  warning: "border-amber-500/30 bg-amber-500/[0.06] text-amber-700 dark:text-amber-400",
  info: "border-hairline bg-neutral-500/[0.04] text-neutral-500 dark:text-neutral-400",
};

export function OutputInsight({ interpretation }: { interpretation?: Interpretation | null }) {
  if (!interpretation?.summary) return null;
  const signals = interpretation.signals ?? [];
  return (
    <div className="mt-3 space-y-2">
      <div className="flex gap-2 border border-hairline bg-neutral-500/[0.04] px-3 py-2">
        <svg
          className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden
        >
          <path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.1h6c0-.8.4-1.6 1-2.1A7 7 0 0 0 12 2Z" />
        </svg>
        <p className="text-[12px] leading-relaxed text-neutral-500 dark:text-neutral-400">
          {interpretation.summary}
        </p>
      </div>

      {/* K3 proaktif sinyaller — anomali/yön/yoğunlaşma; önem rengiyle vurgulu. */}
      {signals.map((s, i) => (
        <div
          key={`${s.kind}-${i}`}
          className={`flex gap-2 border px-3 py-2 text-[12px] leading-relaxed ${
            SIGNAL_TONE[s.severity] ?? SIGNAL_TONE.info
          }`}
        >
          <span className="mt-px shrink-0" aria-hidden>
            {s.severity === "critical" ? "⛔" : s.severity === "warning" ? "⚠" : "◇"}
          </span>
          <p>{s.text}</p>
        </div>
      ))}
    </div>
  );
}
