"use client";

/** **AYARLAR BÖLÜMÜ** — dört sekmeli ayar yüzeyi.
 *
 * ## 🔴 Neden ayrı bir dosya
 *
 * `page.tsx` **büyüme tavanına dayandı** (534 kod satırı) ve büyüme kapısı doğru
 * cevabı kendi mesajında yazıyor: *"yeni davranışı bir bileşene çıkar, tavanı
 * yükseltme."*
 *
 * > ⚠ *Bir tavanı yükseltmek, onu kaldırmaktır — çünkü bir kez yükselen tavan,
 * > ikinci kez de yükselir ve üçüncüde kimse gerekçesini hatırlamaz.*
 *
 * Bu bileşen **yeni bir yetenek getirmiyor**: `page.tsx`'te duran JSX buraya taşındı.
 * Sekme durumu da buraya indi — `page.tsx`'in onu bilmesi için hiçbir sebep yoktu
 * (dışarıdan kimse okumuyordu).
 *
 * ## `…Panel` DEĞİL
 *
 * Panel tavanı dolu (13/13). Bu bir **bölüm**: kendi çekmecesini açmıyor, var olan
 * çekmecenin içeriğini taşıyor.
 */

import { useState } from "react";

import { ConnectionReviewPanel } from "@/components/ConnectionReviewPanel";
import { SchedulesPanel } from "@/components/SchedulesPanel";
import { SchemaPanel } from "@/components/SchemaPanel";
import TercihlerPanel from "@/components/TercihlerPanel";

type Sekme = "sema" | "baglanti" | "zamanlamalar" | "tercihler";

const SEKMELER: ReadonlyArray<readonly [Sekme, string]> = [
  ["sema", "Şema"],
  ["baglanti", "Veri Kaynağı Bağla"],
  ["zamanlamalar", "Zamanlamalar"],
  ["tercihler", "Tercihler"],
];

export function AyarlarBolumu({ kapsam }: { kapsam: "departman" | "genel" | "portfoy" | null }) {
  const [sekme, setSekme] = useState<Sekme>("sema");
  return (
    <div>
      <div
        role="tablist"
        aria-label="Ayarlar"
        className="mb-4 flex gap-1 border-b border-[var(--surface-kenar)] text-xs"
      >
        {SEKMELER.map(([k, etiket]) => (
          <button
            key={k}
            role="tab"
            aria-selected={sekme === k}
            onClick={() => setSekme(k)}
            className={`px-3 py-2 transition-colors ${
              sekme === k ? "border-b-2 border-accent text-foreground" : "text-muted hover:text-foreground"
            }`}
          >
            {etiket}
          </button>
        ))}
      </div>
      {sekme === "sema" ? (
        // ⚠ `kapsam` merceği şemaya da geçer: kullanıcının sohbette seçtiği kapsam,
        // şema görünümünde de aynı olmalı — iki yerde iki farklı kapsam, aynı
        // kataloğun iki farklı hâlini gösterirdi.
        <SchemaPanel kapsam={kapsam} />
      ) : sekme === "baglanti" ? (
        <ConnectionReviewPanel />
      ) : sekme === "zamanlamalar" ? (
        <SchedulesPanel />
      ) : (
        <TercihlerPanel />
      )}
    </div>
  );
}
