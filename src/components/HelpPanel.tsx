"use client";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { BrandMark } from "@/components/BrandMark";
import { Separator } from "@/components/ui/separator";

const EXAMPLES = [
  "Bu ay toplam üretim",
  "Makine bazında ortalama OEE",
  "Vardiya × haftanın günü verimliliği (son 3 ay)",
  "Aşama bazında toplam fire",
  "Müşteri bazında ciro (son 6 ay)",
  "En kârlı müşteriler",
  "Erkek çalışanlar için haftanın günleri bazında OEE",
  "Temmuz ayında makine bazında duruş",
  "Kumaş cinsine göre fire oranı (bu yıl)",
  "Aylık üretim trendi",
  "Renklere göre ortalama renk sapması",
  "Kişilerin aylık verimliliğini önceki dönemle karşılaştır",
  "Reddedilen partileri listele",
  "Su tüketimi aylara göre",
];

/**
 * Yardım paneli — tasarım sistemine hizalandı: gövde Jakarta (mono yalnız
 * teknik terimlerde), köşeler `--radius`, kenarlar hairline token'ı, vurgu
 * `--brand`. Örnek sorular tıklanınca doğrudan sorulur.
 */
export function HelpPanel({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="space-y-6">
      <Link
        href="/brand"
        className="inline-flex opacity-90 transition-opacity hover:opacity-100"
      >
        <BrandMark size="sm" />
      </Link>

      <section className="space-y-2 text-sm leading-relaxed">
        <p className="text-foreground">
          <span className="font-medium text-brand">dima</span> — verinle doğal dille konuş.
          Yaz, Enter&apos;a bas; motor güvenilir SQL üretir, doğrular, çalıştırır ve raporlar.
        </p>
        <p className="text-muted-foreground">
          Bilinen metrikler <span className="font-mono text-xs">deterministik</span> (cube)
          yolla, gerisi denetlenen LLM ile yanıtlanır — her rapor kaynağını (provenance)
          gösterir.
        </p>
      </section>

      <Separator />

      <section className="space-y-2">
        <h3 className="text-xs font-medium tracking-wide text-muted-foreground">Örnekler</h3>
        <ul className="space-y-1">
          {EXAMPLES.map((ex) => (
            <li key={ex}>
              <button
                onClick={() => onPick(ex)}
                className="group flex w-full items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                <span className="min-w-0">{ex}</span>
                <ArrowUpRight className="size-3.5 shrink-0 opacity-0 transition-opacity group-hover:opacity-100" />
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
