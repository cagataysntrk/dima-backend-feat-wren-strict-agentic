"use client";

/**
 * 🔴 G2 — DİYALOG DURUMU: *"bekleyen: dönem"*
 *
 * ## Neden bu satır var
 *
 * JPMorgan (arXiv 2605.26394): çok-turlu text-to-SQL'de **tur-3 durumsuz koşulduğunda
 * beş modelin beşi de %0**; iki turluk pencereyle **%87,6–100**. Durum taşımak bir
 * iyileştirme değil, **var olma koşulu**.
 *
 * Kullanıcı tarafındaki karşılığı: sistem bir şey sorduysa, **sorduğunu unutmadığı**
 * görünmeli. Aksi hâlde kullanıcı her turda baştan anlatmak zorunda kalır — şikâyetin
 * kendisi buydu.
 *
 * ## Tasarım sınırları
 *
 * - **Yeni panel YOK** (PK-1): mevcut chip satırının altında tek, soluk bir satır.
 * - **Kalıcı gösterge DEĞİL**: yuva dolunca kaybolur. Sürekli duran bir rozet, bir
 *   bekleyiş değil bir uyarı gibi okunurdu.
 * - `sorulan` varsa o öne çıkar; yoksa açık yuvalar listelenir.
 */

import type { AskItem } from "@/lib/types";

const ETIKET: Record<string, string> = {
  cube: "konu",
  olcu: "ölçü",
  donem: "dönem",
};

export function DiyalogDurumu({ item }: { item: AskItem }) {
  const d = item.diyalog_durumu;
  if (!d) return null;

  const bekleyen = d.sorulan ? [d.sorulan] : d.acik_slotlar ?? [];
  if (bekleyen.length === 0) return null;

  return (
    <div
      className="mt-1 font-mono text-[10px] text-neutral-500"
      title="Sistem bunu sordu ve cevabını bekliyor — bir sonraki mesajın bu yuvayı doldurabilir."
    >
      <span className="text-neutral-400">bekleyen:</span>{" "}
      {bekleyen.map((s) => ETIKET[s] ?? s).join(" · ")}
      {d.dolu && d.dolu.length > 0 && (
        <span className="ml-2 text-neutral-400">
          (dolan: {d.dolu.map((s) => ETIKET[s] ?? s).join(" · ")})
        </span>
      )}
    </div>
  );
}
