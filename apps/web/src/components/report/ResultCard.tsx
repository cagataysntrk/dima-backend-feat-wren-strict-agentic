"use client";

import { useState } from "react";
import { Maximize2, Minimize2, Expand, Shrink } from "lucide-react";
import type { QueryResult } from "@dima/contracts";
import { ResultView } from "@/components/ResultView";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

/**
 * Genişlemenin YAN BAŞINA miktarı — iki yana AYNI değer verildiği için simetri
 * hesaba değil yapıya bağlı: genişliği hesaplayıp ortalamaya çalışmak, kartın
 * kabı (asistan balonu) avatar/dolgu yüzünden zaten asimetrik oturduğu için
 * bir yana daha çok taşırıyordu.
 *
 * `max(0px, (100cqw - 2rem - 100%) / 2)` = o an SOLDA/SAĞDA gerçekten boş olan
 * yer. `min(4.5rem, …)` onu tavanlar. Yani kart hem tam simetrik büyür hem de
 * kabı asla aşamaz.
 *
 * `2rem` OLUK PAYI, keyfi değil: turun kendi `px-4`'ü (2×1rem) kadar. Onsuz kart
 * tam olarak `100cqw` oluyordu — kabın son pikseline kadar — ve sağ panel açıkken
 * (sohbet sütunu ~254px) dolgu için yer kalmayıp 119px yatay taşma doğuruyordu
 * (canlı ölçüm 2026-07-29). DESIGN.md: sayfa gövdesi yatay kaymaz.
 */
const WIDE_GAIN = "calc(-1 * min(4.5rem, max(0px, (100cqw - 2rem - 100%) / 2)))";

/**
 * Sonuç kartı — grafiğin/tablonun yaşadığı yüzey, boyut denetimiyle birlikte.
 *
 * ÜÇ BOYUT, iki denetim:
 *   normal  dar sohbet sütunu (varsayılan)
 *   geniş   sütun taşar, kart nefes alır  → ⤢ düğmesi
 *   tam     ekranı kaplayan diyalog        → ⛶ düğmesi
 *
 * Genişlik SOHBET SÜTUNUNU büyüterek elde edilir, negatif kenar boşluğuyla değil:
 * kaydırma alanı `overflow-auto`, taşan bir kart yatay kaydırma çubuğu doğururdu
 * (DESIGN.md: sayfa gövdesi yatay kaymaz). Bu yüzden `wide` durumu YUKARI, turu
 * saran kaba bildirilir — büyüyen kart değil, kolonun kendisidir.
 *
 * Varsayılan boyutu VERİ belirler (`chartDensity`): 12 panelli bir facet ya da
 * 20 kategorili bir sütun grafiği dar sütunda zaten okunmuyor; kullanıcıyı her
 * seferinde genişlet'e basmaya zorlamak, bilinen bir sorunu ona havale etmek olur.
 */
export function ResultCard({
  result,
  viewHint,
  meta,
  wide = false,
  onWideChange,
  className,
  children,
}: {
  result: QueryResult;
  viewHint?: string;
  meta?: React.ReactNode;
  /** Geniş mi. `onWideChange` verilmezse genişletme düğmesi HİÇ çizilmez —
   *  sağ panelde kartın genişliği paneli belirler, kullanıcı değil. */
  wide?: boolean;
  onWideChange?: (wide: boolean) => void;
  className?: string;
  /** Kartın içinde, sonucun ALTINDA kalan içerik (ör. SQL bloğu). */
  children?: React.ReactNode;
}) {
  const [full, setFull] = useState(false);

  const actions = (
    <>
      {onWideChange && (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={wide ? "Daralt" : "Genişlet"}
              aria-pressed={wide}
              onClick={() => onWideChange(!wide)}
              className="text-muted-foreground hover:text-foreground"
            >
              {wide ? <Shrink className="size-3.5" /> : <Expand className="size-3.5" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="bottom">{wide ? "Daralt" : "Genişlet"}</TooltipContent>
        </Tooltip>
      )}
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="Tam ekran"
            onClick={() => setFull(true)}
            className="text-muted-foreground hover:text-foreground"
          >
            <Maximize2 className="size-3.5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">Tam ekran</TooltipContent>
      </Tooltip>
    </>
  );

  return (
    <>
      {/* GENİŞLEME YALNIZ BU KARTA AİT — sohbetin geri kalanı (soru balonu, yorum
          çubuğu, aksiyon şeridi) sabit sütunda kalır.

          Kart İKİ YANA EŞİT büyür: genişliğin yarısı kadar negatif sol boşluk,
          kartı kendi merkezinde tutar. Yalnız sağa büyüseydi kart sohbetin
          eksenine göre kayardı.

          `min(...)` güvenlik kilidi: kart ne isterse istesin kabın genişliğini
          (`100cqw`) aşamaz — sağ panel açıkken ya da dar ekranda taşma ve yatay
          kaydırma oluşmaz (DESIGN.md: sayfa gövdesi yatay kaymaz). */}
      <Card
        className={cn(
          "gap-3 p-3",
          className,
        )}
        style={{
          // Geçiş de satır içi: `transition-[width,margin]` arbitrary sınıfına
          // güvenmiyoruz (bkz. ResultView.SIZE_BOX notu).
          transition: "margin 300ms var(--ease-drawer)",
          // Genişlik hesaplanmaz: iki yana AYNI negatif boşluk verilir, kart
          // aradaki yeri kendiliğinden doldurur. Simetri böylece garanti.
          ...(wide ? { marginLeft: WIDE_GAIN, marginRight: WIDE_GAIN } : null),
        }}
      >
        <ResultView
          result={result}
          viewHint={viewHint}
          meta={meta}
          size={wide ? "wide" : "normal"}
          actions={actions}
        />
        {children}
      </Card>

      <Dialog open={full} onOpenChange={setFull}>
        {/* GERÇEK tam ekran: sol-üste sabitlenir, `translate(-50%,-50%)` YOK.
            shadcn'in varsayılan ortalaması yarım piksel kaydırma üretebiliyor
            ve bu, grafiği/yazıyı bulanıklaştırıyordu (canlı 2026-07-29) —
            tek sayı genişlikte %50 tam piksele denk gelmiyor. Ölçüler satır
            içi: `w-[96vw]` gibi arbitrary sınıflar üretilen CSS'e girmeyince
            diyalog `sm:max-w-lg`'ye düşüp küçücük kalıyordu. */}
        <DialogContent
          showCloseButton={false}
          className="top-0 left-0 flex max-w-none translate-x-0 translate-y-0 flex-col gap-3 overflow-auto rounded-none border-0 p-4 sm:max-w-none"
          style={{ width: "100vw", height: "100svh" }}
        >
          {/* Diyalogun erişilebilir adı zorunlu; görsel olarak meta zaten üstte. */}
          <DialogTitle className="sr-only">Sonuç — tam ekran</DialogTitle>
          <div className="flex items-center justify-end">
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label="Tam ekrandan çık"
              onClick={() => setFull(false)}
              className="text-muted-foreground hover:text-foreground"
            >
              <Minimize2 className="size-4" />
            </Button>
          </div>
          {/* Tam ekran KENDİ görünüm durumunu tutar (ayrı ResultView örneği):
              büyütüp pasta seçmek, kapatınca kartın grafik tipini değiştirmesin. */}
          <ResultView result={result} viewHint={viewHint} meta={meta} size="full" />
        </DialogContent>
      </Dialog>
    </>
  );
}
