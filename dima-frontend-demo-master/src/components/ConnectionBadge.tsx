"use client";

import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getSchema } from "@/lib/api-client";

// Veri kaynağı (tenant DB) çevrimiçi/çevrimdışı durum noktası — ikon rail'in EN ALTINDA,
// çıkış butonunun HEMEN ÜSTÜNDE (bottom-14, logout bottom-4 ile hizalı kolon).
// SchemaPanel ile AYNI ["schema"] query'sini paylaşır (çift-fetch yok); 30sn'de bir
// tazelenir → DB tekrar açıldığında rozet kendiliğinden yeşile döner. db_online backend'in
// TCP erişilebilirlik kontrolünden gelir (ulaşılamaz DB → /schema asılmaz).
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
export function ConnectionBadge({ gomulu = false }: { gomulu?: boolean } = {}) {
  const pathname = usePathname();
  const { data, isError, isLoading } = useQuery({
    queryKey: ["schema"],
    queryFn: () => getSchema(),   // ⚠ doğrudan geçmek React Query context'ini `scope` sanardı
    refetchInterval: 30_000,
    retry: false,
    enabled: pathname !== "/login",
  });
  if (pathname === "/login") return null;
  // Ana sayfada kabuk `YanCubuk`'tur; oradaki **gömülü** kopya çizer.
  if (!gomulu && pathname === "/") return null;

  const online = !isError && data?.db_online !== false;
  // ⚠️ FAZ 1.11 — KADEMELİ DÜŞÜŞ GÖSTERGESİ (üç seviye).
  //
  // 🔴 Seviye 3 bir HATA DEĞİL bir DURUMDUR: sistem çalışıyor ama cevaplar KATEGORİK
  // OLARAK farklı bir yoldan (LLM'siz, kural tabanlı) geliyor. Bu yüzden kırmızı DEĞİL
  // amber gösterilir ve "çevrimdışı" DEMEZ — "çalışıyor ama LLM yok" ile "hiç
  // çalışmıyor" aynı şey değildir; ikisini aynı renkte göstermek kullanıcıyı yanlış
  // eyleme (sistemi yeniden başlatmaya) iterdi.
  //
  // ⚠ Seviye kararı BACKEND'de (`app/kademeli_dusus.py`); burada ikinci bir eşik/etiket
  // kümesi yazmak rozet ile audit'in AYRIŞMASI demekti. Etiket de backend'den gelir.
  const seviye = data?.llm_seviye ?? null;
  const dusuk = online && (seviye === 2 || seviye === 3);
  const label = isLoading
    ? "Veri kaynağı denetleniyor…"
    : !online
      ? "Veri kaynağına ulaşılamıyor — çevrimdışı"
      : seviye === 3
        ? `Sistem çalışıyor ama LLM YOK — cevaplar kural tabanlı (${data?.llm_uretici ?? "?"})`
        : seviye === 2
          ? `Birincil sağlayıcı yanıt vermiyor — yedekten koşuyor (${data?.llm_uretici ?? "?"})`
          : "Veri kaynağı çevrimiçi";
  return (
    <div
      title={label}
      aria-label={label}
      role="status"
      className={`${gomulu ? "" : "fixed bottom-14 right-2 z-50"} flex h-8 w-8 items-center justify-center`}
    >
      <span
        className={`inline-block h-2.5 w-2.5 rounded-full ${
          isLoading
            ? "bg-neutral-400"
            : !online
              ? "animate-pulse bg-red-500"
              : seviye === 3
                ? "bg-amber-500 ring-2 ring-amber-500/30"
                : dusuk
                  ? "bg-amber-400"
                  : "bg-emerald-500"
        }`}
      />
    </div>
  );
}
