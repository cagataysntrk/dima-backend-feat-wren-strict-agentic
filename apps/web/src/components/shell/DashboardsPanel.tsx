"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, LayoutDashboard, Plus, Sparkles, Trash2 } from "lucide-react";
import { Renderer } from "@openuidev/react-lang";
import type { AskResponse } from "@dima/contracts";
import { catalogEntries, composeDashboard } from "@dima/genui";
import { createDashboard, deleteDashboard, listDashboards } from "@dima/api-client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { CatalogProvider } from "@/components/genui/catalog";
import { dashboardLibrary } from "@/components/genui/library";
import { DashboardView } from "@/components/shell/DashboardView";

/**
 * Paneller — İKİ AYRI ŞEY, tek yüzeyde.
 *
 * 1. KALICI PANOLAR (varsayılan görünüm). Backend'de yaşar (`/dashboards`),
 *    karolar KAYITLI SORGUdur: her açılışta göreli dönem yeniden çözülür ve
 *    cube_query yeniden koşar. "Bir raporu sabitleyip zaman içinde izleme"
 *    ihtiyacını bu karşılar (§9 canlı izleme).
 *
 * 2. ÜRETKEN KOMPOZİSYON (butonla girilir). Bu SOHBETTEKİ sonuçlardan anlık bir
 *    panel düzenler; hiçbir şey kaydedilmez, veri yeniden sorgulanmaz. Keşif
 *    içindir — "elimdekiler birlikte neye benziyor?".
 *
 * İkisi rakip değil: biri kalıcılık, diğeri anlık düzen. Aynı slotta durmaları
 * bu yüzden sorun değil — ama hangisinin ne olduğu görünür olmalı, o yüzden
 * üretken taraf ayrı bir moda giriyor, listeye karışmıyor.
 *
 * ÜRETKEN PANOYU ŞU AN DETERMİNİSTİK BİR DÜZENLEYİCİ ÜRETİYOR, model değil.
 * Sebep: model çağrısı `dima-backend`'e ait (sağlayıcı anahtarı Next sürecinde
 * durmaz) ve o uç henüz yok. Model geldiğinde değişen tek şey bu metni kimin
 * ürettiği olacak — renderer, katalog ve vokabüler aynen kalıyor.
 */
export function DashboardsPanel({
  items,
  onSelect,
}: {
  items: AskResponse[];
  onSelect: (item: AskResponse) => void;
}) {
  const [mode, setMode] = useState<"list" | "genui">("list");
  const [openId, setOpenId] = useState<string | null>(null);
  const qc = useQueryClient();

  const entries = useMemo(() => catalogEntries(items), [items]);
  const source = useMemo(() => composeDashboard(entries), [entries]);
  const candidates = useMemo(() => items.filter((i) => i.cube_query && i.result), [items]);

  const { data: list, isPending } = useQuery({
    queryKey: ["dashboards"],
    queryFn: listDashboards,
  });
  const dashboards = list?.dashboards ?? [];

  const create = useMutation({
    mutationFn: () => createDashboard(),
    onSuccess: (d) => {
      void qc.invalidateQueries({ queryKey: ["dashboards"] });
      setOpenId(d.id);
    },
  });
  const remove = useMutation({
    mutationFn: (id: string) => deleteDashboard(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["dashboards"] }),
  });

  // --- Tek pano (canlı) ------------------------------------------------------
  if (openId) return <DashboardView id={openId} onBack={() => setOpenId(null)} />;

  // --- Üretken kompozisyon (kaydedilmez) -------------------------------------
  if (mode === "genui" && source) {
    return (
      <div className="space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setMode("list")}
          className="-ml-2 w-fit gap-1.5"
        >
          <ArrowLeft className="size-4" />
          Panolara dön
        </Button>
        <div className="flex items-start gap-2 rounded-lg border border-border bg-muted/40 px-3 py-2">
          <Sparkles className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden />
          <p className="text-xs leading-relaxed text-muted-foreground">
            Anlık düzen — kaydedilmez. Kalıcı izleme için bir cevabın altındaki{" "}
            <span className="font-medium">panoya ekle</span>&apos;yi kullan.
          </p>
        </div>
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

  // --- Pano listesi ----------------------------------------------------------
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-medium text-foreground">Panolarım</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => create.mutate()}
          disabled={create.isPending || (list ? dashboards.filter((d) => d.own).length >= list.max_per_user : false)}
          className="h-7 gap-1.5 px-2 text-xs"
        >
          <Plus className="size-3.5" />
          yeni pano
        </Button>
      </div>

      {isPending ? (
        <div className="space-y-2">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </div>
      ) : dashboards.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border py-8 text-center">
          <LayoutDashboard className="size-5 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Henüz pano yok.</p>
          <p className="max-w-xs text-xs text-muted-foreground/80">
            Bir cevabın altındaki <span className="font-medium">panoya ekle</span> ile ilk
            karonu oluştur — pano her açılışta güncel veriyle koşar.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {dashboards.map((d) => (
            <Card
              key={d.id}
              className="group cursor-pointer gap-1 p-3 transition-colors hover:border-brand/40"
              onClick={() => setOpenId(d.id)}
            >
              <div className="flex items-center gap-2">
                <p className="min-w-0 truncate text-sm text-foreground">{d.title}</p>
                {d.visibility === "tenant" && (
                  <Badge variant="outline" className="shrink-0 text-[10px]">
                    şirket
                  </Badge>
                )}
                {d.own && (
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Panoyu sil"
                    onClick={(e) => {
                      e.stopPropagation();
                      remove.mutate(d.id);
                    }}
                    className="ml-auto shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:text-destructive"
                  >
                    <Trash2 className="size-3.5" />
                  </Button>
                )}
              </div>
              <span className="font-mono text-[10px] text-muted-foreground">
                {d.widget_count} karo · {d.updated_at.replace("T", " ")}
              </span>
            </Card>
          ))}
        </div>
      )}

      <Separator />

      {/* Üretken kompozisyon — kalıcı panoların ALTINDA, ayrı bir eylem olarak. */}
      <div className="space-y-2">
        <div className="flex items-start gap-2">
          <Sparkles className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden />
          <p className="text-xs leading-relaxed text-muted-foreground">
            {entries.length >= 2
              ? `Bu sohbetteki ${entries.length} sonuçtan anlık bir panel düzenlenebilir — kaydedilmez, veri yeniden sorgulanmaz.`
              : "Anlık panel için en az iki sonuç gerekiyor. Birkaç metrik sorusu sor."}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          disabled={entries.length < 2 || !source}
          onClick={() => setMode("genui")}
          className="w-full gap-1.5 text-xs"
        >
          <LayoutDashboard className="size-3.5" />
          Bu sohbetten panel oluştur
        </Button>
      </div>

      {candidates.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
            bu sohbetteki sonuçlar
          </h4>
          {candidates.map((item, i) => (
            <Card
              key={`${item.question}-${i}`}
              className="cursor-pointer gap-2 p-3 transition-colors hover:border-brand/40"
              onClick={() => onSelect(item)}
            >
              <p className="truncate text-sm text-foreground">{item.question}</p>
              {item.result && (
                <span className="text-xs text-muted-foreground">
                  {item.result.row_count} satır
                </span>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
