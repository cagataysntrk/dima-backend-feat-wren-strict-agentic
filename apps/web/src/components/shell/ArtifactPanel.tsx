"use client";

import { BarChart3, Database, Maximize2, Minimize2, Paperclip, X } from "lucide-react";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { useIsMobile } from "@/hooks/use-mobile";
import { cn } from "@/lib/utils";

/**
 * Sağ panel — YALNIZ AÇIK SOHBET hakkında.
 *
 * Kapsam kuralı: sol kenar çubuğu HESAP geneli (tüm veri kaynakları, tüm
 * paneller, tüm belgeler), sağ panel BU sohbet. Bu yüzden veri kataloğu,
 * kayıtlı panolar ve yardım buradan çıktı; geriye sohbete özgü iki yüzey kaldı:
 *   Paneller  — bu sohbetin ürettiği sonuçlar (içindekiler; tıklayınca karta gider)
 *   Kaynaklar — bu sohbet veriyi nereden aldı (küp, ölçü, SQL, mühür)
 *   Belgeler  — bu sohbetin ekleri ve ürettiği dosyalar
 * Rapor sekmesi kalktı: bir rapor aslında bir PANEL'dir, o yüzden Paneller'in
 * içinde yaşıyor — sohbetteki kart zaten raporun kendisi.
 *
 * ÜST BAR TEK ŞERİT: eskiden bir başlık bandı + ayrı bir sekme şeridi vardı,
 * yani iki bant ve arada boş yükseklik. Şimdi sekmeler, genişlet ve kapat aynı
 * h-12 barda — panelin dikey alanı içeriğe kalıyor.
 */
export const PANEL_TABS = [
  { id: "panels", label: "Paneller", icon: BarChart3 },
  { id: "sources", label: "Kaynaklar", icon: Database },
  { id: "attachments", label: "Belgeler", icon: Paperclip },
] as const;

export type PanelTab = (typeof PANEL_TABS)[number]["id"];

/**
 * Panel genişliği — SOHBETE TABAN BIRAKARAK.
 *
 * `calc(100vw - 46rem)` terimi şart: panel genişletilince (900px) 1440px'lik bir
 * ekranda sohbet sütunu ~250px'e düşüyor, kart kontrolleri sığmıyor ve yatay
 * kaydırma doğuyordu (canlı ölçüm 2026-07-29). 46rem ≈ sol kenar çubuğu + okunur
 * bir sohbet sütunu; panel bundan fazlasını alamaz.
 */
const PANEL_W = {
  normal: "w-[min(46vw,600px,calc(100vw-46rem))]",
  expanded: "w-[min(70vw,900px,calc(100vw-46rem))]",
} as const;

export function ArtifactPanel({
  open,
  tab,
  onTabChange,
  onClose,
  children,
}: {
  open: boolean;
  tab: PanelTab;
  onTabChange: (tab: PanelTab) => void;
  onClose: () => void;
  children: React.ReactNode;
}) {
  const t = useTranslations("common");
  const isMobile = useIsMobile();
  const [expanded, setExpanded] = useState(false);

  if (isMobile) {
    return (
      <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
        <SheetContent side="right" className="w-full gap-0 p-0 sm:max-w-lg">
          {/* Sheet'in erişilebilir adı zorunlu; görsel başlık sekmelerin kendisi. */}
          <SheetTitle className="sr-only">Sohbet paneli</SheetTitle>
          <PanelNav tab={tab} onTabChange={onTabChange} />
          <div className="min-h-0 flex-1 overflow-auto p-4">{children}</div>
        </SheetContent>
      </Sheet>
    );
  }

  // Panel HER ZAMAN mount'lu kalır; açılıp kapanma genişlik geçişiyle olur — sol
  // sidebar ile aynı davranış (shadcn `transition-[width]`). Unmount edilseydi
  // genişlik anında sıçrardı; şimdi içerik yumuşakça itilip geri alınıyor.
  return (
    <aside
      data-state={open ? "open" : "closed"}
      aria-hidden={!open}
      className={cn(
        "flex min-h-0 shrink-0 flex-col overflow-hidden border-border bg-card/40",
        "transition-[width,border-left-width] duration-300 ease-[var(--ease-drawer)]",
        "motion-reduce:transition-none",
        open
          ? cn("border-l", expanded ? PANEL_W.expanded : PANEL_W.normal)
          : "w-0 border-l-0",
      )}
    >
      {/* İç sarmalayıcı sabit genişlikte: panel daralırken içerik yeniden akmasın
          (aksi halde kapanışta metin sıkışıp titriyor). */}
      <div
        className={cn(
          "flex min-h-0 flex-1 flex-col transition-opacity duration-200",
          expanded ? PANEL_W.expanded : PANEL_W.normal,
          open ? "opacity-100" : "opacity-0",
        )}
      >
        <PanelNav
          tab={tab}
          onTabChange={onTabChange}
          actions={
            <>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={expanded ? "Daralt" : "Genişlet"}
                className="text-muted-foreground hover:text-foreground"
                onClick={() => setExpanded((e) => !e)}
              >
                {expanded ? <Minimize2 className="size-4" /> : <Maximize2 className="size-4" />}
              </Button>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={t("close")}
                className="text-muted-foreground hover:text-foreground"
                onClick={onClose}
              >
                <X className="size-4" />
              </Button>
            </>
          }
        />
        <div className="min-h-0 flex-1 overflow-auto p-4">{children}</div>
      </div>
    </aside>
  );
}

/**
 * Panelin tek üst şeridi: solda sekmeler, sağda pencere aksiyonları.
 * Yüksekliği ana bardaki (h-12) ile aynı — iki taraf aynı yatay eksende otursun.
 */
function PanelNav({
  tab,
  onTabChange,
  actions,
}: {
  tab: PanelTab;
  onTabChange: (tab: PanelTab) => void;
  actions?: React.ReactNode;
}) {
  return (
    <div className="flex h-12 shrink-0 items-center justify-between gap-2 border-b border-border pr-2 pl-2">
      <div role="tablist" aria-label="Panel bölümleri" className="flex min-w-0 items-center gap-0.5">
        {PANEL_TABS.map(({ id, label, icon: Icon }) => {
          const active = id === tab;
          return (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => onTabChange(id)}
              className={cn(
                "inline-flex shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs transition-colors",
                "focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:outline-none",
                active
                  ? "bg-accent font-medium text-foreground"
                  : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
              )}
            >
              <Icon className="size-3.5" />
              {label}
            </button>
          );
        })}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-0.5">{actions}</div>}
    </div>
  );
}
