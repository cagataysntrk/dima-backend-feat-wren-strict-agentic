"use client";

/** **ÇEKMECE** — dört yan bölümün **tek yönlendiricisi**. (FAZ 6)
 *
 * ## Neden ayrı bir bileşen
 *
 * `page.tsx` bir **büyüme kapısı** taşıyor ve FAZ 6'da kırmızı verdi (513 → 525).
 * Kapının kendi talimatı açık: *"yeni davranışı bir bileşene çıkar, tavanı yükseltme."*
 *
 * ⚠ Ve çıkarılacak doğru şey yeni davranış değil, **eskisiydi**: `page.tsx` içinde
 * çekmecenin **başlığı** bir üçlü koşul zinciri, **gövdesi** ikinci bir üçlü koşul
 * zinciriydi — *aynı dört dalın iki ayrı yerde iki kez sıralanması.* Bir beşinci bölüm
 * eklenirse ikisini de düzeltmek gerekirdi ve biri unutulurdu: başlık *"Ayarlar"* derken
 * gövde panoları çizerdi.
 *
 * > *İki paralel koşul zinciri, tek bir tablodan her zaman daha kötüdür — çünkü
 * > senkron kaldıklarını hiçbir şey garanti etmez.*
 *
 * Burada tek bir **tablo** var: dal → (başlık, gövde). Yeni bir bölüm eklemek tek satır.
 *
 * 🔴 Yeni bir **panel** açılmadı (tavan 13/13, pay 0): bu `SettingsDrawer`'ın içeriğini
 * seçen bir yönlendirici, kendi yüzeyi olan bir panel değil.
 */

import { AyarlarBolumu } from "@/components/AyarlarBolumu";
import { DashboardsPanel } from "@/components/DashboardsPanel";
import { HelpPanel } from "@/components/HelpPanel";
import { NotificationsPanel } from "@/components/NotificationsBell";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import type { Kapsam } from "@/components/SoruAlani";

export type CekmeceDali = "settings" | "help" | "notifications" | "dashboards" | null;

export function Cekmece({
  dal,
  onKapat,
  onSoru,
  onPanoAc,
  kapsam,
}: {
  dal: CekmeceDali;
  onKapat: () => void;
  onSoru: (q: string) => void;
  onPanoAc: (id: string) => void;
  kapsam: Kapsam | null;
}) {
  // 🔴 TEK TABLO — başlık ve gövde **aynı satırda** yaşar. Ayrı iki koşul zinciri
  // olsaydı biri güncellenip öteki unutulabilirdi ve kullanıcı başlığı bir şey,
  // içeriği başka bir şey söyleyen bir çekmece görürdü.
  const dallar: Record<Exclude<CekmeceDali, null>, { baslik: string; govde: React.ReactNode }> = {
    help: { baslik: "dima · yardım", govde: <HelpPanel onPick={onSoru} /> },
    notifications: { baslik: "Bildirimler", govde: <NotificationsPanel /> },
    dashboards: {
      baslik: "Panolar",
      govde: <DashboardsPanel onOpen={(id) => { onPanoAc(id); onKapat(); }} />,
    },
    settings: {
      baslik: "Ayarlar · Veri Modeli",
      govde: <AyarlarBolumu kapsam={kapsam} />,
    },
  };
  const secili = dal ? dallar[dal] : null;

  return (
    <SettingsDrawer open={dal !== null} onClose={onKapat} title={secili?.baslik ?? ""}>
      {secili?.govde ?? null}
    </SettingsDrawer>
  );
}
