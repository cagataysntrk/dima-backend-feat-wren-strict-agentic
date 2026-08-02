"use client";

import { useEffect, useRef, useState } from "react";
import { getNotifications, type Notification } from "@/lib/api-client";
import { ContractDetailPanel } from "@/components/ContractDetailPanel";

// Bildirim zili (ADR-0011): zamanlanmış rapor/alarm bildirimleri — 60sn'de bir yoklanır.
// Okunmamış sayacı localStorage'daki son-görülme zamanına göre hesaplanır.
// Buton yalnız rozet taşır; liste, ayarlar/yardım gibi sağ SHEET'te açılır
// (NotificationsPanel, SettingsDrawer içinde render edilir).
const SEEN_KEY = "dima.notifications.seen";

export function NotificationsBell({ onOpen }: { onOpen: () => void }) {
  const [items, setItems] = useState<Notification[]>([]);
  // Lazy initializer (fonksiyon olarak) — yalnız İLK render'da okunur, bir effect
  // İÇİNDE senkron setState ÇAĞIRMAZ (bu oturumda başka yerlerde de düzeltilen
  // "effect gövdesinde setState" antipattern'inin AYNISI burada da vardı).
  const [seenTs, setSeenTs] = useState<string>(() =>
    typeof window === "undefined" ? "" : localStorage.getItem(SEEN_KEY) ?? "");
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const poll = () => getNotifications(20).then(setItems).catch(() => {});
    poll();
    timer.current = setInterval(poll, 60_000);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, []);

  const unread = items.filter((n) => !seenTs || n.ts > seenTs).length;
  const markSeen = () => {
    const latest = items[0]?.ts ?? new Date().toISOString();
    localStorage.setItem(SEEN_KEY, latest);
    setSeenTs(latest);
  };

  const btn =
    "relative flex h-8 w-8 items-center justify-center border border-hairline bg-background/70 text-muted backdrop-blur-sm transition-colors hover:text-foreground hover:border-neutral-400 dark:hover:border-neutral-600";

  return (
    <button
      onClick={() => {
        markSeen();
        onOpen();
      }}
      aria-label="Bildirimler"
      className={btn}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
      {unread > 0 && (
        <span className="absolute -right-1 -top-1 flex h-3.5 min-w-3.5 items-center justify-center bg-accent px-0.5 font-mono text-[9px] leading-none text-white">
          {unread > 9 ? "9+" : unread}
        </span>
      )}
    </button>
  );
}

// Sheet içeriği: açılışta taze liste çeker (rozet yoklaması butonda kalır).
export function NotificationsPanel() {
  const [items, setItems] = useState<Notification[]>([]);
  const [loaded, setLoaded] = useState(false);
  // Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-12): başarısız bir fetch daha önce
  // "hiç bildirim yok" ile AYIRT EDİLEMİYORDU (ikisi de aynı boş listeye düşüyordu).
  const [error, setError] = useState(false);
  const [openContract, setOpenContract] = useState<string | null>(null);
  // NEDEN katmanı (Faz F3) — KAPALI başlar. Bir uyarı önce bir HABERDİR: liste taranabilir
  // kalmalı. Gerekçe bir tık uzakta durur ve AYNI kartın içinde açılır — yeni panel DEĞİL
  // (MIMARI §14.1: "yeni yetenek yeni panel doğurmaz").
  const [acikNeden, setAcikNeden] = useState<ReadonlySet<string | number>>(new Set());
  const nedenAcKapa = (id: string | number) =>
    setAcikNeden((onceki) => {
      const yeni = new Set(onceki);
      if (!yeni.delete(id)) yeni.add(id);
      return yeni;
    });

  useEffect(() => {
    getNotifications(50)
      .then(setItems)
      .catch(() => setError(true))
      .finally(() => setLoaded(true));
  }, []);

  if (loaded && error) {
    return (
      <div className="px-1 py-4 font-mono text-[11px] text-red-500">
        Bildirimler yüklenemedi. Sayfayı yenileyip tekrar dener misin?
      </div>
    );
  }
  if (loaded && items.length === 0) {
    return (
      <div className="px-1 py-4 font-mono text-[11px] text-neutral-400">
        bildirim yok — bir rapora 🔔 zamanla ekleyebilirsin
      </div>
    );
  }
  return (
    <>
      <ul>
        {items.map((n) => {
          const nedenVar = (n.neden?.length ?? 0) > 0 || !!n.neden_not;
          const acik = acikNeden.has(n.id);
          return (
            <li key={n.id} className="border-b border-hairline px-1 py-2 last:border-b-0">
              <div
                className={`font-mono text-[11px] leading-snug ${
                  n.kind === "alert" ? "text-red-500" : "text-neutral-600 dark:text-neutral-300"
                }`}
              >
                {n.message}
              </div>
              <div className="mt-0.5 flex items-center justify-between gap-2 font-mono text-[9px] text-neutral-400">
                <span className="flex items-center gap-2">
                  <span>{n.ts.replace("T", " ").slice(0, 16)}</span>
                  {nedenVar && (
                    <button
                      onClick={() => nedenAcKapa(n.id)}
                      aria-expanded={acik}
                      title="Bu uyarıyı hangi segmentler sürükledi?"
                      className="underline-offset-2 hover:text-foreground hover:underline"
                    >
                      {acik ? "⤴" : "⤵"} neden?
                    </button>
                  )}
                </span>
                {n.contract_id && (
                  <button
                    onClick={() => setOpenContract(n.contract_id ?? null)}
                    title="Kanıt kaydı (Query Contract) — tıkla → incele"
                    className="shrink-0 underline-offset-2 hover:text-foreground hover:underline"
                  >
                    {n.contract_id}
                  </button>
                )}
              </div>
              {nedenVar && acik && (
                // Gerekçe kartın İÇİNDE açılır. Satırlar TIKLANABİLİR DEĞİLDİR ve bu
                // bilinçlidir: backend etiketleri PII-maskeler, maskeli bir değere filtre
                // kuran sorgu boş dönerdi. Kanıt yolu yukarıdaki makbuz kimliğidir.
                <div className="mt-1.5 border-l border-hairline pl-2">
                  {(n.neden ?? []).map((satir, i) => (
                    <div
                      key={i}
                      className="font-mono text-[10px] leading-snug text-neutral-600 dark:text-neutral-300"
                    >
                      ↳ {satir}
                    </div>
                  ))}
                  {n.neden_not && (
                    // Kırpma/tarama sınırı ya da DÜRÜST RED ("bu ölçü toplanabilir değil").
                    // İkisi de aynı yerde görünür: kapsamı daraltan her karar söylenir.
                    <div className="mt-0.5 font-mono text-[9px] text-neutral-400">
                      {n.neden_not}
                    </div>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {openContract && (
        <ContractDetailPanel contractId={openContract} onClose={() => setOpenContract(null)} />
      )}
    </>
  );
}
