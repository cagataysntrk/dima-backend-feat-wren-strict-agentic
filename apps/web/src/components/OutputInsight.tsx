"use client";

import { Lightbulb } from "lucide-react";
import type { Interpretation } from "@/lib/types";

// EVRENSEL ÇIKTI YORUMU (feature flag: cikti_yorumlama). Backend her tablo/grafik/rapor/KPI
// için DETERMİNİSTİK analiz üretir (en yüksek/düşük, % değişim, trend yönü + lower_is_better
// iyi/kötü çerçevesi, pay); burada yalnız gösterilir. Bayrak kapalıysa yanıtta interpretation
// yok → hiç render edilmez.
export function OutputInsight({ interpretation }: { interpretation?: Interpretation | null }) {
  if (!interpretation?.summary) return null;
  return (
    <div className="mt-2 flex gap-2 rounded-lg border border-border bg-muted/30 px-3 py-2">
      <Lightbulb className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden />
      <p className="text-xs leading-relaxed text-muted-foreground">{interpretation.summary}</p>
    </div>
  );
}
