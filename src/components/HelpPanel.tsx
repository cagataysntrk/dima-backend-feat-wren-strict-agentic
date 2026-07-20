"use client";

import Link from "next/link";
import { BrandMark } from "@/components/BrandMark";

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

export function HelpPanel({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="space-y-6 text-sm">
      <Link
        href="/brand"
        className="inline-flex opacity-90 transition-opacity hover:opacity-100"
      >
        <BrandMark size="sm" interpunct />
      </Link>

      <section className="space-y-2">
        <p className="text-neutral-600 dark:text-neutral-300">
          <span className="font-mono text-accent">dima</span> — verinle doğal dille konuş.
          Yaz, Enter&apos;a bas; motor güvenilir SQL üretir, doğrular, çalıştırır ve raporlar.
        </p>
        <p className="text-neutral-500">
          Bilinen metrikler <span className="font-mono">deterministik</span> (cube) yolla,
          gerisi denetlenen LLM ile yanıtlanır — her rapor kaynağını (provenance) gösterir.
        </p>
      </section>

      <section>
        <h3 className="mb-2 font-mono text-[11px] uppercase tracking-wider text-neutral-400">
          Örnekler
        </h3>
        <ul className="space-y-1.5">
          {EXAMPLES.map((ex) => (
            <li key={ex}>
              <button
                onClick={() => onPick(ex)}
                className="w-full border border-hairline px-3 py-2 text-left font-mono text-[13px] text-neutral-600 transition-colors hover:border-neutral-400 hover:text-foreground dark:text-neutral-300 dark:hover:border-neutral-600"
              >
                {ex}
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
