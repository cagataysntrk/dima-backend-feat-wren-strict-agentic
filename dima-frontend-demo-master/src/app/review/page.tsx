"use client";

// /review — Discovery→Promote reviewer sayfası (Faz 2e). Sayfa erişimi zaten `src/proxy.ts`
// ile oturuma bağlı (login şart); BURADAKİ ek kapı `measure:read` iznidir (analyst+) —
// izinsiz kullanıcı (viewer) sayfayı görebilir ama boş bir bilgi mesajıyla karşılaşır,
// buton görünürlüğü değil SAYFA İÇERİĞİ bu izne bağlıdır (backend zaten her uçta ayrıca
// zorluyor — bu yalnız kullanıcı deneyimi, güvenlik sınırı DEĞİL).

import Link from "next/link";
import { ReviewPanel } from "@/components/ReviewPanel";
import { usePermission } from "@/lib/usePermission";

export default function ReviewPage() {
  const canView = usePermission("measure:read");

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-hairline px-4">
        <div>
          <h1 className="font-mono text-[13px] uppercase tracking-wide text-foreground">
            Ölçü inceleme
          </h1>
          <p className="font-mono text-[10px] text-neutral-400">
            Discovery→Promote — ham-SQL yanıtlarından yakalanan ölçü adayları
          </p>
        </div>
        <Link
          href="/"
          className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
        >
          ← sohbete dön
        </Link>
      </header>
      <div className="min-h-0 flex-1">
        {canView ? (
          <ReviewPanel />
        ) : (
          <p className="p-4 font-mono text-[12px] text-neutral-400">
            Bu sayfayı görüntüleme izniniz yok (analyst veya üstü rol gerekir).
          </p>
        )}
      </div>
    </div>
  );
}
