"use client";

import { useOdakTuzagi } from "@/lib/odakTuzagi";

// Sağdan açılan sheet (ayarlar/yardım/bildirimler). Sağ ikon KOLONUNU (rail,
// w-12) örtmez: right-12'de durur — kolon her zaman görünür ve tıklanabilir.
export function SettingsDrawer({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) {
  // 🔴 FAZ 7.5 · A11Y-3: `open` tuzağa DOĞRUDAN geçilir — çekmece kapalıyken odak
  // tuzağa DÜŞMEMELİ, yoksa arkadaki sayfa klavyeyle gezilemez hâle gelir.
  const cekmeceRef = useOdakTuzagi<HTMLElement>(open, onClose);

  return (
    <div className={`fixed inset-0 z-40 ${open ? "" : "pointer-events-none"}`} aria-hidden={!open}>
      <div
        onClick={onClose}
        className={`absolute inset-0 bg-black/40 backdrop-blur-[1px] transition-opacity duration-200 ${
          open ? "opacity-100" : "opacity-0"
        }`}
      />
      <aside
        ref={cekmeceRef}
        role="dialog"
        aria-modal={open || undefined}
        // 🔴 FAZ 7.6 — mobilde şerit ALT çubuğa döndüğü için `right-12` payı ARTIK YANLIŞTIR:
        // olmayan bir kolona 3rem bırakır. Ayrıca `max-w-[80vw]` 375px'te 300px'lik bir
        // çekmece demektir; dar ekranda çekmece **tam genişlik** olur ve alt çubuğun
        // üstünde biter (`bottom-12`).
        className={`absolute right-12 top-0 flex h-full w-[22rem] max-w-[80vw] flex-col border-l border-hairline bg-background shadow-2xl transition-transform duration-200 max-md:right-0 max-md:bottom-12 max-md:h-auto max-md:w-full max-md:max-w-none ${
          open ? "translate-x-0" : "translate-x-[calc(100%+3rem)]"
        }`}
      >
        <header className="flex h-14 shrink-0 items-center border-b border-hairline px-4">
          <h2 className="font-mono text-[13px] tracking-wide">{title}</h2>
        </header>
        <div className="flex-1 overflow-auto p-4">{children}</div>
      </aside>
      {/* İkon şeridinin zemini: kapalıyken sayfa rengi (görünmez), açıkken PANELLE
          AYNI renk. aside'dan SONRA render edilir ki panelin gölgesi (shadow-2xl)
          şeridi karartmasın — panel + şerit tek yüzey gibi okunur. İçindeki h-14
          bölme, panel başlığının alt çizgisini ekranın sağ kenarına kadar uzatır. */}
      <div
        className={`absolute right-0 top-0 h-full w-12 bg-background transition-opacity duration-200 ${
          open ? "opacity-100" : "opacity-0"
        }`}
      >
        {/* Kapatma (✕): şeridin başlık bandında, rail ikonlarıyla AYNI hizada ve stilde. */}
        <div className="flex h-14 items-center justify-center border-b border-hairline">
          <button
            onClick={onClose}
            aria-label="Kapat"
            className="flex h-8 w-8 items-center justify-center border border-hairline bg-background/70 text-muted transition-colors hover:border-neutral-400 hover:text-foreground dark:hover:border-neutral-600"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
