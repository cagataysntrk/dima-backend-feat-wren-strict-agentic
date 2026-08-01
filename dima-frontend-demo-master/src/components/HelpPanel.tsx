"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { getStarters, getStatsToday, type Starter } from "@/lib/api-client";
import { BrandMark } from "@/components/BrandMark";

// Yedek örnekler — /starters küratörü boşsa ya da erişilemezse gösterilir (K1 fallback).
// Grupsuz (katalog otomatiğiyle AYNI ruhta — departman etiketi yalnız küratörlü listede var).
const FALLBACK: Starter[] = [
  "Bu ay toplam üretim",
  "Makine bazında ortalama OEE",
  "Vardiya × haftanın günü verimliliği (son 3 ay)",
  "Aşama bazında toplam fire",
  "Müşteri bazında ciro (son 6 ay)",
  "Kumaş cinsine göre fire oranı (bu yıl)",
  "Aylık üretim trendi",
  "Su tüketimi aylara göre",
].map((q) => ({ label: q, query: q }));

const TUMU = "Tümü";

export function HelpPanel({ onPick }: { onPick: (q: string) => void }) {
  // K1 — rol/sektör bazlı küratörlü başlangıç soruları; boşsa yerel yedeğe düş.
  const { data } = useQuery({ queryKey: ["starters"], queryFn: getStarters });
  const examples = data && data.length > 0 ? data : FALLBACK;
  // Faz 4.13c — meta-güven şeridi ("bugün %X soru LLM'siz cevaplandı"). Etkinlik yoksa
  // (llm_free_pct null) sessizce gösterilmez — uydurma bir yüzde YOK.
  const { data: statsToday } = useQuery({ queryKey: ["stats-today"], queryFn: () => getStatsToday(1) });

  // Faz 4.8 (1 Ağustos 2026) — "Ne sorabilirim?" departman gezinmesi (dış yol haritası
  // 1.13): örnekler `grup` taşıyorsa sekme/bölüm gezinmesi gösterilir; hiçbiri taşımıyorsa
  // (katalog otomatiği ya da eski bir sektör pack'i) ESKİ düz liste davranışı KORUNUR.
  const groups = useMemo(() => {
    const seen: string[] = [];
    for (const ex of examples) {
      if (ex.grup && !seen.includes(ex.grup)) seen.push(ex.grup);
    }
    return seen;
  }, [examples]);
  const [activeGroup, setActiveGroup] = useState<string>(TUMU);
  const visible =
    groups.length === 0 || activeGroup === TUMU
      ? examples
      : examples.filter((ex) => ex.grup === activeGroup);

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
        {statsToday?.llm_free_pct !== null && statsToday?.llm_free_pct !== undefined && (
          <p className="font-mono text-[11px] text-accent">
            ◆ Bugün %{statsToday.llm_free_pct} soru yapay zekaya hiç gitmeden cevaplandı.
          </p>
        )}
      </section>

      <section>
        <h3 className="mb-2 font-mono text-[11px] uppercase tracking-wider text-neutral-400">
          Örnekler
        </h3>
        {groups.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-1">
            {[TUMU, ...groups].map((g) => (
              <button
                key={g}
                onClick={() => setActiveGroup(g)}
                className={`rounded-full border px-2.5 py-1 text-[11px] transition-colors ${
                  activeGroup === g
                    ? "border-accent bg-accent text-white"
                    : "border-hairline text-neutral-500 hover:border-neutral-400 hover:text-foreground"
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        )}
        <ul className="space-y-1.5">
          {visible.map((ex) => (
            <li key={ex.label}>
              <button
                onClick={() => onPick(ex.query)}
                className="w-full border border-hairline px-3 py-2 text-left font-mono text-[13px] text-neutral-600 transition-colors hover:border-neutral-400 hover:text-foreground dark:text-neutral-300 dark:hover:border-neutral-600"
              >
                {ex.label}
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
