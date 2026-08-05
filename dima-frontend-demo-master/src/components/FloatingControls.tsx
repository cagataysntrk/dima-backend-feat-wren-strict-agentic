"use client";

import { useEffect, useState } from "react";

import { NotificationsBell } from "@/components/NotificationsBell";
import { type Tema, temaBaslat, temaOku, temaUygula } from "@/lib/tema";

// Sayfada tek chrome: sağ kenarda GÖRÜNMEZ bir ikon ŞERİDİ (rail) — çizgisi/
// zemini yok, sayfayla bütünleşik; yalnız ikonlar yüzer. Yukarıdan aşağı:
// bildirim 🔔, yardım ?, ayarlar ⚙; yeni ikonlar altta devam eder (çıkış en altta).
// Sheet'ler şeridin SOLUNDA açılır (SettingsDrawer right-12) — üst üste binmez;
// sheet açıkken bile diğer ikonlara tıklanıp içerik değiştirilebilir.
// Keskin köşe, ghost, monospace işaret; "sistem paneli" hissi.
export const RAIL_W = "3rem"; // w-12 — page pr-12 ve drawer right-12 ile eşleşir

export function FloatingControls({
  onHistory,
  onNotifications,
  onDashboards,
  onReview,
  onHelp,
  onSettings,
}: {
  onHistory: () => void;
  onNotifications: () => void;
  // Panolar (dashboards bayrağı) — yalnız verilirse ikon çıkar (flag ile geçitlenir).
  onDashboards?: () => void;
  // Ölçü inceleme (/review, Faz 2e) — yalnız `measure:read` izni varsa çıkar.
  onReview?: () => void;
  onHelp: () => void;
  onSettings: () => void;
}) {
  const btn =
    "flex h-8 w-8 items-center justify-center border border-hairline bg-background/70 text-muted backdrop-blur-sm transition-colors hover:text-foreground hover:border-neutral-400 dark:hover:border-neutral-600";
  return (
    // pt-[4.5rem]: ikonlar panel başlık çizgisinin (h-14) ALTINDA başlar — panel
    // açıkken de kapalıyken de aynı hizada (başlık şeridi sağa kadar uzar).
    // 🔴 FAZ 7.6 — **mobilde (<768) şerit ALT ÇUBUĞA döner.** Sağ kenarda dikey bir
    // 3rem'lik şerit, 375px'lik bir ekranın **%13'ünü** yer ve başparmakla en zor
    // ulaşılan köşededir. Alt çubuk hem erişim mesafesini kısaltır hem genişliği
    // içeriğe bırakır. ⚠ `pt-[4.5rem]` mobilde SIFIRLANIR: alt çubukta üstten boşluk,
    // ikonları ekranın dışına iterdi.
    <div
      data-no-print
      className="pointer-events-none fixed right-0 top-0 z-50 flex h-full w-12 flex-col items-center gap-1.5 pt-[4.5rem] [&>*]:pointer-events-auto max-md:top-auto max-md:bottom-0 max-md:h-12 max-md:w-full max-md:flex-row max-md:justify-center max-md:gap-3 max-md:border-t max-md:border-hairline max-md:bg-background/95 max-md:pt-0 max-md:backdrop-blur-sm"
    >
      <button onClick={onHistory} aria-label="Sohbet geçmişi" title="Sohbet geçmişi" className={btn}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 3v5h5" />
          <path d="M3.05 13A9 9 0 1 0 6 5.3L3 8" />
          <path d="M12 7v5l3 2" />
        </svg>
      </button>
      <NotificationsBell onOpen={onNotifications} />
      {onDashboards && (
        <button onClick={onDashboards} aria-label="Panolar" title="Panolar" className={btn}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="7" height="9" />
            <rect x="14" y="3" width="7" height="5" />
            <rect x="14" y="12" width="7" height="9" />
            <rect x="3" y="16" width="7" height="5" />
          </svg>
        </button>
      )}
      {onReview && (
        <button onClick={onReview} aria-label="Ölçü inceleme" title="Ölçü inceleme" className={btn}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 11l3 3L22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
        </button>
      )}
      {/* 🔴 FAZ 7.2 — TEMA ANAHTARI. Yeni bir PANEL değil: var olan ikon şeridinin bir
          düğmesi (K5 tavanı 13/13 — *bir yetenek bir panel doğurmaz*).
          ⚠ ÜÇ durum: sistem → açık → karanlık → sistem. "Karar vermedim" hâlini yok
          etmek, kullanıcının sistem tercihini sessizce ezmek olurdu. */}
      <TemaDugmesi btn={btn} />
      <button onClick={onHelp} aria-label="Yardım" title="Yardım" className={btn}>
        <span className="font-mono text-[13px]">?</span>
      </button>
      <button onClick={onSettings} aria-label="Ayarlar" title="Ayarlar" className={btn}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      </button>
    </div>
  );
}


/** FAZ 7.2 — tema anahtarı. Üç durumlu: `sistem → light → dark → sistem`.
 *
 * ⚠ İkon **duruma göre** değişir ve `title` o durumu **söyler**: bir toggle'ın hangi
 * konumda olduğunu tahmin ettirmek, onu bir sürprize çevirir.
 */
function TemaDugmesi({ btn }: { btn: string }) {
  const [tema, setTema] = useState<Tema>("sistem");
  useEffect(() => {
    temaBaslat();
    setTema(temaOku());
  }, []);
  const sonraki: Record<Tema, Tema> = { sistem: "light", light: "dark", dark: "sistem" };
  const etiket: Record<Tema, string> = {
    sistem: "Tema: sistem (işletim sistemine uyar)",
    light: "Tema: açık",
    dark: "Tema: karanlık",
  };
  const isaret: Record<Tema, string> = { sistem: "◐", light: "☀", dark: "☾" };
  return (
    <button
      onClick={() => {
        const y = sonraki[tema];
        temaUygula(y);
        setTema(y);
      }}
      aria-label={etiket[tema]}
      title={`${etiket[tema]} — değiştirmek için tıkla`}
      className={btn}
    >
      <span className="font-mono text-[13px]" aria-hidden>{isaret[tema]}</span>
    </button>
  );
}
