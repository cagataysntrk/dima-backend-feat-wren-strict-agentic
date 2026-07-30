"use client";

import { usePathname, useRouter } from "next/navigation";
import { logout } from "@/lib/api-client";
import { useHistory } from "@/stores/history";

// Sağ ikon KOLONUNUN (rail, w-12) EN ALTI — FloatingControls ile aynı stil;
// right-2 = 8px → 32px'lik buton 48px'lik kolonda ortalanır.
export function LogoutButton() {
  const pathname = usePathname();
  const router = useRouter();
  if (pathname === "/login") return null;

  async function onClick() {
    // ÇIKIŞTA KONUŞMA DURUMUNU TEMİZLE (güvenlik/izolasyon, canlı 2026-07-25): geçmiş global
    // Zustand store'da tutulur — temizlenmezse LOGOUT sonrası BAŞKA kullanıcı önceki
    // kullanıcının soru/rapor zincirini + bağlam cube_query'sini görürdü (çapraz-kullanıcı sızıntı).
    useHistory.getState().clear();
    await logout();
    router.replace("/login");
  }

  const btn =
    "flex h-8 w-8 items-center justify-center border border-hairline bg-background/70 text-muted backdrop-blur-sm transition-colors hover:text-foreground hover:border-neutral-400 dark:hover:border-neutral-600";

  return (
    <button
      onClick={onClick}
      aria-label="Çıkış"
      title="Çıkış"
      className={`fixed bottom-4 right-2 z-50 ${btn}`}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
        <path d="M16 17l5-5-5-5" />
        <path d="M21 12H9" />
      </svg>
    </button>
  );
}
