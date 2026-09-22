"use client";

import { ArrowRight, Clock, Columns3, Sigma } from "lucide-react";
import type { CubeQuery, NextStep, Recommendation } from "@dima/contracts";
import { Badge } from "@dima/ui/primitives/badge";
import { Button } from "@dima/ui/primitives/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@dima/ui/primitives/tooltip";

/**
 * K2 — cevabın ALTINDAKİ "sonraki adım" chip'leri (rehberli analitik).
 *
 * Backend her chip'i TAM bir `cube_query` ile gönderir, yani tıklama LLM'e
 * gitmez: mevcut deterministik `/cube` yolundan koşar (yorum çubuğundaki chip
 * düzenlemesiyle aynı mekanizma). Bu yüzden ucuz ve tekrarlanabilir — kullanıcı
 * "peki ya makine bazında?" diye yeniden yazmak zorunda kalmıyor.
 *
 * `kind` üç eksenden hangisinde ilerlediğini söyler: kırılım (boyut ekle),
 * ölçek (başka ölçüye bak), zaman (granülerliği değiştir). İkon o eksenin
 * kısayolu — etiketi okumadan da nereye gittiğin belli olsun.
 */

const KIND_ICON: Record<string, typeof Columns3> = {
  dimension: Columns3,
  measure: Sigma,
  time: Clock,
};

const KIND_HINT: Record<string, string> = {
  dimension: "Kırılım — bu boyutta ayrıştırır",
  measure: "Ölçek — başka bir ölçüye bakar",
  time: "Zaman — granülerliği değiştirir",
};

export function NextSteps({
  steps,
  onDrill,
}: {
  steps?: NextStep[];
  onDrill: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  if (!steps?.length) return null;
  return (
    <div className="space-y-1.5 pt-1">
      <div className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
        sonraki adım
      </div>
      <div className="flex flex-wrap gap-1.5">
        {steps.map((step, i) => {
          const Icon = KIND_ICON[step.kind] ?? Columns3;
          return (
            <Tooltip key={`${step.kind}-${i}`}>
              <TooltipTrigger asChild>
                <button type="button" onClick={() => onDrill({ cq: step.cube_query, label: step.label })}>
                  <Badge
                    variant="outline"
                    className="cursor-pointer gap-1.5 font-normal transition-colors hover:border-brand/40 hover:bg-brand/5"
                  >
                    <Icon className="size-3 text-muted-foreground" aria-hidden />
                    {step.label}
                  </Badge>
                </button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                {KIND_HINT[step.kind] ?? "Bu kırılımla yeniden çalıştır"} · deterministik, LLM yok
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>
    </div>
  );
}

/**
 * K4 — sinyalden (K3) türetilen ÖNERİ: "neye bakmalısın" + opsiyonel tek-tık drill.
 *
 * Sinyal durumu bildirir ("fire %18 arttı"), öneri ne yapılacağını söyler
 * ("makine bazında kır"). Aksiyonu olan öneri K2'nin mekanizmasını yeniden
 * kullanır — içgörü → öneri → AKSİYON tek tıkla kapanır.
 */
export function Recommendations({
  items,
  onDrill,
}: {
  items?: Recommendation[];
  onDrill: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  if (!items?.length) return null;
  return (
    <div className="space-y-1.5 pt-1">
      {items.map((rec, i) => (
        <div
          key={i}
          className="flex items-center justify-between gap-2 rounded-lg border border-brand/20 bg-brand/[0.04] px-3 py-2"
        >
          <p className="flex min-w-0 gap-2 text-[13px] leading-relaxed text-foreground/90">
            <ArrowRight className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden />
            {rec.text}
          </p>
          {rec.action && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    onDrill({ cq: rec.action!.cube_query, label: rec.action!.label })
                  }
                  className="h-7 shrink-0 px-2 text-xs"
                >
                  {rec.action.label}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">Deterministik koşar — LLM yok</TooltipContent>
            </Tooltip>
          )}
        </div>
      ))}
    </div>
  );
}
