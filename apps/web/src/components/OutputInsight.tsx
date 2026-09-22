"use client";

import { AlertTriangle, Diamond, Lightbulb, OctagonAlert } from "lucide-react";
import type { Interpretation, Signal } from "@dima/contracts";
import { Badge } from "@dima/ui/primitives/badge";
import { cn } from "@dima/ui/utils";

// EVRENSEL ÇIKTI YORUMU (feature flag: cikti_yorumlama). Backend her tablo/grafik/rapor/KPI
// için DETERMİNİSTİK analiz üretir (en yüksek/düşük, % değişim, trend yönü + lower_is_better
// iyi/kötü çerçevesi, pay); burada yalnız gösterilir. Bayrak kapalıysa yanıtta interpretation
// yok → hiç render edilmez.
//
// K3 PROAKTİF SİNYALLER özetin ALTINDA, ayrı kutularda durur. Nötr özetle aynı
// kutuya girselerdi "dikkat" tonu kaybolurdu — sinyalin işi zaten göze çarpmak:
// anomali (z-score), yön endişesi (kötü yönde %10+ değişim), yoğunlaşma (≥%50 pay).

const SIGNAL_TONE: Record<Signal["severity"], string> = {
  critical: "border-destructive/30 bg-destructive/5 text-destructive",
  warning: "border-amber-500/30 bg-amber-500/5 text-amber-700 dark:text-amber-400",
  info: "border-border bg-muted/30 text-foreground/90",
};

const SIGNAL_ICON: Record<Signal["severity"], typeof AlertTriangle> = {
  critical: OctagonAlert,
  warning: AlertTriangle,
  info: Diamond,
};

export function OutputInsight({ interpretation }: { interpretation?: Interpretation | null }) {
  if (!interpretation?.summary) return null;
  const signals = interpretation.signals ?? [];
  // `facts` özetin YAPISAL hali (en yüksek/en düşük/pay…). Backend bunu hep
  // gönderiyordu ama hiçbir istemci çizmiyordu. Özet zaten cümleye çevirdiği için
  // rozetler TARAMA içindir: göz cümleyi okumadan sayıyı yakalasın.
  const facts = interpretation.facts ?? [];
  return (
    <div className="mt-2 space-y-1.5">
      {/* Yorum, verinin OKUNMASIDIR — sohbetin gövde metniyle aynı okunurlukta
          olmalı. `muted` tonu ikincil metadata için (satır sayısı, rozet), burada
          değil; ayrıca 12px'te muted kontrastı sınırda kalıyordu. */}
      <div className="flex gap-2 rounded-lg border border-border bg-muted/30 px-3 py-2">
        <Lightbulb className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden />
        <p className="text-[13px] leading-relaxed text-foreground/90">{interpretation.summary}</p>
      </div>

      {facts.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {facts.map((f, i) => (
            <Badge key={`${f.type}-${i}`} variant="outline" className="gap-1.5 font-normal">
              <span className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
                {f.type}
              </span>
              {f.text}
            </Badge>
          ))}
        </div>
      )}

      {signals.map((s, i) => {
        const Icon = SIGNAL_ICON[s.severity] ?? SIGNAL_ICON.info;
        return (
          <div
            key={`${s.kind}-${i}`}
            className={cn(
              "flex gap-2 rounded-lg border px-3 py-2",
              SIGNAL_TONE[s.severity] ?? SIGNAL_TONE.info,
            )}
          >
            <Icon className="mt-0.5 size-3.5 shrink-0" aria-hidden />
            <p className="text-[13px] leading-relaxed">{s.text}</p>
          </div>
        );
      })}
    </div>
  );
}
