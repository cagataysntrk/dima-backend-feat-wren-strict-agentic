"use client";

import { useMemo, useState } from "react";
import { ArrowLeft, LayoutDashboard, Sparkles } from "lucide-react";
import { Renderer } from "@openuidev/react-lang";
import type { AskResponse } from "@dima/contracts";
import { catalogEntries, composeDashboard } from "@dima/genui";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CatalogProvider } from "@/components/genui/catalog";
import { dashboardLibrary } from "@/components/genui/library";
import { SourceBadge } from "@/components/report/SourceBadge";

/**
 * Paneller — sohbetten üretilen çok karolu panolar.
 *
 * PANOYU ŞU AN DETERMİNİSTİK BİR DÜZENLEYİCİ ÜRETİYOR, model değil.
 *
 * Sebep: pano üretimi için model çağrısı `dima-backend`'e ait (sağlayıcı
 * anahtarı Next sürecinde durmaz) ve o uç henüz yok. Kurallarla üretmek
 * özelliğin bugün çalışmasını sağlıyor; model geldiğinde değişen tek şey bu
 * metni kimin ürettiği olacak — renderer, katalog ve vokabüler aynen kalıyor.
 * Ayrıca kalıcı bir geri düşüş hattı: model erişilemezse ya da geçersiz çıktı
 * verirse pano yine gelir.
 *
 * VERİ MODELDEN GELMEZ. Üretilen metin yalnız `resultId` referansları taşır;
 * satırları renderer katalogdan çeker (components/genui/catalog.tsx).
 */
export function DashboardsPanel({
  items,
  onSelect,
}: {
  items: AskResponse[];
  onSelect: (item: AskResponse) => void;
}) {
  const [open, setOpen] = useState(false);

  const entries = useMemo(() => catalogEntries(items), [items]);
  const source = useMemo(() => composeDashboard(entries), [entries]);
  const candidates = useMemo(() => items.filter((i) => i.cube_query && i.result), [items]);

  if (open && source) {
    return (
      <div className="space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setOpen(false)}
          className="-ml-2 w-fit gap-1.5"
        >
          <ArrowLeft className="size-4" />
          Panellere dön
        </Button>
        <CatalogProvider entries={entries}>
          <Renderer
            response={source}
            library={dashboardLibrary}
            // Boş dizi "hata yok" demek — koşulsuz loglamak yanlış alarm üretir.
            // Dolu dizi, üretim modele geçtiğinde geri beslenecek düzeltme sinyali.
            onError={(errors) => {
              if (errors.length) console.warn("[genui] düzeltilebilir hatalar:", errors);
            }}
          />
        </CatalogProvider>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {entries.length >= 2 ? (
        <Card className="gap-2 p-3">
          <div className="flex items-start gap-2">
            <Sparkles className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden />
            <p className="text-xs leading-relaxed text-muted-foreground">
              Bu sohbetteki {entries.length} sonuçtan bir panel oluşturulabilir.
              Veriler yeniden sorgulanmaz — mevcut sonuçlar düzenlenir.
            </p>
          </div>
          <Button size="sm" onClick={() => setOpen(true)} className="w-full">
            <LayoutDashboard className="size-4" />
            Bu sohbetten panel oluştur
          </Button>
        </Card>
      ) : (
        <div className="flex items-start gap-2 rounded-lg border border-border bg-muted/40 px-3 py-2">
          <Sparkles className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden />
          <p className="text-xs leading-relaxed text-muted-foreground">
            Panel oluşturmak için en az iki sonuç gerekiyor. Birkaç metrik sorusu
            sor — sonuçlar burada birleştirilecek.
          </p>
        </div>
      )}

      {candidates.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
          <LayoutDashboard className="size-5 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Henüz panel adayı yok.</p>
          <p className="max-w-xs text-xs text-muted-foreground/80">
            Bir metrik sorusu sor — cube&apos;dan gelen her sonuç buraya düşer.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {candidates.map((item, i) => (
            <Card
              key={`${item.question}-${i}`}
              className="cursor-pointer gap-2 p-3 transition-colors hover:border-brand/40"
              onClick={() => onSelect(item)}
            >
              <div className="flex items-center gap-2">
                <SourceBadge source={item.source} />
                {item.result && (
                  <span className="text-xs text-muted-foreground">
                    {item.result.row_count} satır
                  </span>
                )}
                {item.contract_id && (
                  <Badge variant="outline" className="ml-auto font-mono text-[10px]">
                    {item.contract_id}
                  </Badge>
                )}
              </div>
              <p className="truncate text-sm text-foreground">{item.question}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
