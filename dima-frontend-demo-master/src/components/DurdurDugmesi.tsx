"use client";

// FAZ 1.12 · AI Act Md.14 — **DURDURMA DÜĞMESİ.**
//
// 🔴 *Durdurulamayan bir otomasyon, üzerinde insan denetimi olmayan bir otomasyondur.*
// Uzun bir Discovery işi başlatıldığında kullanıcının elinde bugüne kadar YALNIZCA
// beklemek vardı; `job_id` bilerek "görünmez" tutuluyordu (api-client'ın kendi yorumu:
// *"bileşenlere HİÇ ULAŞMAZ"*) ve durdurmanın bedeli tam olarak buydu.
//
// ⚠ **İş ÖLDÜRÜLMEZ, sonucu YAYIMLANMAZ** (karar backend'de: `app/ask_jobs.py`). Buradaki
// metin bunu **olduğu gibi** söyler; *"iptal edildi"* deyip işin arkada bitmesine izin
// vermek, kullanıcının gördüğüyle sistemin yaptığını ayırırdı.
//
// ⚠ **Zaten bitmiş bir iş durdurulamaz** ve bu sessizce *"durdurdum"* diye gösterilmez —
// sonuç o an zaten yolda olabilir. Backend `bitti` der, düğme de onu söyler.
//
// 🔴 **İkinci bir bileşen değil, TEK sahip:** aynı düğme hem sol panelde (yeni thread)
// hem sağ panelde (takip) kullanılır. İki yere iki metin yazmak, ikisinin ayrışması
// demekti — bu depoda tam olarak *"aynı kuralın iki sahibi"* diye kaydedilen sınıf.

import { useState } from "react";
import { cancelAskJob } from "@/lib/api-client";

export function DurdurDugmesi({ jobId }: { jobId: string | null }) {
  const [durum, setDurum] = useState<"hazir" | "gonderiliyor" | "durduruldu" | "bitti">("hazir");

  // İş yoksa (senkron yol — bugünkü varsayılan) düğme HİÇ görünmez: görünüp
  // çalışmayan bir durdurma düğmesi, hiç olmayanından beterdir.
  if (!jobId) return null;

  if (durum === "durduruldu" || durum === "bitti") {
    return (
      <span className="font-mono text-[11px] text-neutral-400">
        {durum === "durduruldu" ? "durduruldu — sonuç yayımlanmayacak" : "iş zaten bitmişti"}
      </span>
    );
  }

  return (
    <button
      type="button"
      disabled={durum === "gonderiliyor"}
      onClick={async () => {
        setDurum("gonderiliyor");
        try {
          const r = await cancelAskJob(jobId);
          setDurum(r.durum === "bitti" ? "bitti" : "durduruldu");
        } catch {
          // Durdurma BAŞARISIZ olduysa düğme geri gelir: sessizce "durduruldu" göstermek,
          // çalışmayan bir düğmeyi çalışmış gibi anlatmak olurdu.
          setDurum("hazir");
        }
      }}
      className="inline-flex h-[20px] items-center gap-1 border border-hairline px-1.5 font-mono text-[var(--text-etiket)] tracking-wide text-neutral-500 transition-colors hover:border-red-400 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)] dark:hover:text-red-400"
      title="İşi durdur — sonucu yayımlanmaz (AI Act Md.14)"
    >
      <span aria-hidden>■</span>
      {durum === "gonderiliyor" ? "durduruluyor…" : "durdur"}
    </button>
  );
}
