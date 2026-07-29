"use client";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getStarters } from "@dima/api-client";
import { BrandMark } from "@/components/BrandMark";
import { Separator } from "@/components/ui/separator";

// K1 (rehberli analitik) — asıl liste backend'in `/starters` küratöründen gelir:
// rol ve sektör paketine göre filtrelenmiş sorular. Buradaki sabit liste YEDEK,
// yani küratör boşsa ya da uca erişilemezse panel boş kalmasın diye. Yedeği
// kısa tutuyoruz: uzun bir yerel liste, küratörün sessizce düştüğünü gizler.
const FALLBACK = [
  "Bu ay toplam üretim",
  "Makine bazında ortalama OEE",
  "Vardiya × haftanın günü verimliliği (son 3 ay)",
  "Aşama bazında toplam fire",
  "Müşteri bazında ciro (son 6 ay)",
  "Kumaş cinsine göre fire oranı (bu yıl)",
  "Aylık üretim trendi",
  "Su tüketimi aylara göre",
].map((q) => ({ label: q, query: q }));

/**
 * Yardım paneli — tasarım sistemine hizalandı: gövde Jakarta (mono yalnız
 * teknik terimlerde), köşeler `--radius`, kenarlar hairline token'ı, vurgu
 * `--brand`. Örnek sorular tıklanınca doğrudan sorulur.
 */
export function HelpPanel({ onPick }: { onPick: (q: string) => void }) {
  // Hata da boş liste gibi ele alınır (`FALLBACK`) — yardım paneli, küratör
  // ucu düştü diye kullanıcıya hata göstermesi gereken bir yüzey değil.
  const { data: starters } = useQuery({ queryKey: ["starters"], queryFn: getStarters });
  const examples = starters?.length ? starters : FALLBACK;

  return (
    <div className="space-y-6">
      <Link
        href="/app/brand"
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
          {examples.map((ex) => (
            <li key={ex.label}>
              <button
                onClick={() => onPick(ex.query)}
                className="group flex w-full items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                <span className="min-w-0">{ex.label}</span>
                <ArrowUpRight className="size-3.5 shrink-0 opacity-0 transition-opacity group-hover:opacity-100" />
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
