"use client";

import { usePathname, useRouter } from "next/navigation";
import { logout } from "@/lib/api-client";
import { useHistory } from "@/stores/history";

// Sağ ikon KOLONUNUN (rail, w-12) EN ALTI — FloatingControls ile aynı stil;
// right-2 = 8px → 32px'lik buton 48px'lik kolonda ortalanır.
/** ⚠ `gomulu` — **FAZ 3.** Bu öge iki yerde yaşayabilir:
 *
 * | yer | ne zaman |
 * |---|---|
 * | `YanCubuk` içinde, **gömülü** | ana sayfada (`/`) — kabuk artık çubuktur |
 * | `layout.tsx`'te, **sabit konumlu** | öteki sayfalarda (`/review`, `/brand`) |
 *
 * 🔴 Neden iki yer değil de **tek yer, iki kip**: ikisini ayrı ayrı render etmek
 * ana sayfada **çift gösterim** üretirdi. `gomulu` olmayan kopya `/` yolunda
 * **susar** — böylece her sayfada tam olarak bir tane çizilir.
 *
 * ⚠ Ve konum düzeltmesi zorunluydu: `fixed right-2` değeri artık **var olmayan**
 * ikon şeridinin içini işaret ediyordu (FAZ 2'de şerit kalktı). Sabit konumlu bir
 * ögenin dayandığı yüzey kaldırılınca, öge kaybolmaz — **öksüz kalır**. */
export function LogoutButton({ gomulu = false }: { gomulu?: boolean } = {}) {
  const pathname = usePathname();
  const router = useRouter();
  if (pathname === "/login") return null;
  if (!gomulu && pathname === "/") return null;

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
      className={gomulu ? btn : `fixed bottom-4 right-2 z-50 ${btn}`}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
        <path d="M16 17l5-5-5-5" />
        <path d="M21 12H9" />
      </svg>
    </button>
  );
}
