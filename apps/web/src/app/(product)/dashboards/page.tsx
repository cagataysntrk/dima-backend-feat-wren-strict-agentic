"use client";

import { useRouter } from "next/navigation";
import { LayoutDashboard } from "lucide-react";
import { DashboardsPanel } from "@/components/shell/DashboardsPanel";
import { selectActive, useConversations } from "@/stores/conversations";

/**
 * Paneller — HESABIN tüm panoları.
 *
 * Raporlar da buraya ait: bir rapor aslında tek karolu bir panodur (kayıtlı
 * sorgu + görünüm). Ayrı bir "Raporlar" yüzeyi açmak, aynı nesneyi iki isimle
 * iki yerde aramak demekti. Bir panoya girip karolarını, grafiklerini ve
 * tablolarını orada geziyorsun.
 */
export default function DashboardsPage() {
  const router = useRouter();
  // Üretken kompozisyon açık sohbetin sonuçlarından beslenir; sohbet yoksa o
  // bölüm kendini kapatır (DashboardsPanel en az iki sonuç ister).
  const active = useConversations(selectActive);

  return (
    <main className="dima-page-in mx-auto max-w-4xl space-y-6 px-6 py-10">
      <header className="space-y-1.5">
        <h1 className="flex items-center gap-2 text-xl font-medium tracking-tight text-foreground">
          <LayoutDashboard className="size-5 text-brand" />
          Paneller
        </h1>
        <p className="text-sm text-muted-foreground">
          Kaydettiğin panolar. Her karo bir sorguyu saklar — pano her açılışta
          güncel veriyle koşar, bakılan sayı bayatlamaz.
        </p>
      </header>

      <DashboardsPanel
        items={active?.items ?? []}
        onSelect={() => router.push("/app")}
      />
    </main>
  );
}
