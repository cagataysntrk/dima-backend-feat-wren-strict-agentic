"use client";

import { useEffect } from "react";

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
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <div className={`fixed inset-0 z-40 ${open ? "" : "pointer-events-none"}`} aria-hidden={!open}>
      <div
        onClick={onClose}
        className={`absolute inset-0 bg-black/40 backdrop-blur-[1px] transition-opacity duration-200 ${
          open ? "opacity-100" : "opacity-0"
        }`}
      />
      {/* İkon şeridinin zemini: kapalıyken sayfa rengi (görünmez), açıkken PANEL
          rengini alır — panel + şerit tek yüzey gibi okunur (ikonlar üstte yüzer). */}
      <div
        className={`absolute right-0 top-0 h-full w-12 bg-background transition-opacity duration-200 ${
          open ? "opacity-100" : "opacity-0"
        }`}
      />
      <aside
        className={`absolute right-12 top-0 flex h-full w-[22rem] max-w-[80vw] flex-col border-l border-hairline bg-background shadow-2xl transition-transform duration-200 ${
          open ? "translate-x-0" : "translate-x-[calc(100%+3rem)]"
        }`}
      >
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-hairline px-4">
          <h2 className="font-mono text-[13px] tracking-wide">{title}</h2>
          <button
            onClick={onClose}
            aria-label="Kapat"
            className="p-1.5 text-neutral-400 transition-colors hover:text-foreground"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </header>
        <div className="flex-1 overflow-auto p-4">{children}</div>
      </aside>
    </div>
  );
}
