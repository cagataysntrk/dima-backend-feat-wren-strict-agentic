"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LayoutDashboard, Plus, Check } from "lucide-react";
import type { AskResponse } from "@dima/contracts";
import { addDashboardWidget, createDashboard, listDashboards } from "@dima/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

// Karo dönemi GÖRELİ saklanır: pano her açılışta yeniden çözer. Mutlak tarih
// saklamak panoyu bir kereliğine doğru, sonsuza kadar bayat yapardı.
const PERIODS = [
  { value: "", label: "raporun kendi dönemi" },
  { value: "bugün", label: "bugün" },
  { value: "dün", label: "dün" },
  { value: "son 7 gün", label: "son 7 gün" },
  { value: "bu ay", label: "bu ay" },
  { value: "geçen ay", label: "geçen ay" },
];

/**
 * "Panoya ekle" — bir cevabı kalıcı bir pano karosuna çevirir.
 *
 * Kaydedilen şey SONUÇ DEĞİL SORGUdur (`cube_query` + göreli dönem + görünüm
 * ipucu). Böylece pano her açılışta güncel veriyi gösterir; satırlar istemcide
 * saklanmaz. Bu yüzden yalnız cube kaynaklı cevaplarda görünür — LLM cevabının
 * yeniden koşturulabilir bir sorgusu yok.
 */
export function AddToDashboard({
  data,
  label,
  className,
}: {
  data: AskResponse;
  /** Karo başlığı — raporu üreten gerçek soru. */
  label: string;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const [added, setAdded] = useState(false);
  const [target, setTarget] = useState<string>("");
  const [period, setPeriod] = useState<string>("");
  const [newTitle, setNewTitle] = useState("");
  const qc = useQueryClient();

  const { data: list } = useQuery({
    queryKey: ["dashboards"],
    queryFn: listDashboards,
    enabled: open, // panoları yalnız açılınca çek — her cevapta istek atmasın
  });
  const dashboards = list?.dashboards ?? [];
  const ownDashboards = dashboards.filter((d) => d.own);
  const atLimit = list ? ownDashboards.length >= list.max_per_user : false;

  const add = useMutation({
    mutationFn: async () => {
      if (!data.cube_query) throw new Error("cube sorgusu yok");
      // Yeni pano seçiliyse önce onu yarat, sonra karoyu ekle.
      const id =
        target === "__new__" ? (await createDashboard(newTitle.trim() || undefined)).id : target;
      await addDashboardWidget(id, {
        title: label,
        cube_query: data.cube_query,
        view_hint: data.view_hint,
        period: period || null,
      });
      return id;
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dashboards"] });
      setAdded(true);
      setOpen(false);
      setNewTitle("");
    },
  });

  if (!data.cube_query || !data.source) return null;

  // Hiç pano yoksa varsayılan olarak "yeni pano" akışını göster.
  const effectiveTarget = target || (ownDashboards.length ? ownDashboards[0].id : "__new__");
  const creating = effectiveTarget === "__new__";

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <Tooltip>
        <TooltipTrigger asChild>
          <PopoverTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              aria-label="panoya ekle"
              className={cn(
                "h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground",
                added && "text-brand",
                className,
              )}
            >
              {added ? <Check className="size-3.5" /> : <LayoutDashboard className="size-3.5" />}
              {added ? "panoda" : "panoya ekle"}
            </Button>
          </PopoverTrigger>
        </TooltipTrigger>
        <TooltipContent side="bottom">
          Bu raporu bir panoya sabitle — pano her açılışta güncel veriyle koşar
        </TooltipContent>
      </Tooltip>

      <PopoverContent align="start" className="w-80 space-y-3 p-3">
        <div className="space-y-1.5">
          <Label className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
            pano
          </Label>
          <Select value={effectiveTarget} onValueChange={setTarget}>
            <SelectTrigger size="sm" className="h-7 w-full text-xs" aria-label="Hedef pano">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ownDashboards.map((d) => (
                <SelectItem key={d.id} value={d.id} className="text-xs">
                  {d.title} · {d.widget_count} karo
                </SelectItem>
              ))}
              {!atLimit && (
                <SelectItem value="__new__" className="text-xs">
                  + yeni pano
                </SelectItem>
              )}
            </SelectContent>
          </Select>
          {creating && (
            <Input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="pano adı (opsiyonel)"
              className="h-7 text-xs"
            />
          )}
          {atLimit && ownDashboards.length > 0 && (
            <p className="text-[11px] text-muted-foreground">
              Pano sınırına ulaşıldı ({list?.max_per_user}) — mevcut bir panoya ekleyebilirsin.
            </p>
          )}
        </div>

        <div className="space-y-1.5">
          <Label className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
            dönem
          </Label>
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger size="sm" className="h-7 w-full text-xs" aria-label="Karo dönemi">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PERIODS.map((p) => (
                <SelectItem key={p.value} value={p.value} className="text-xs">
                  {p.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-[11px] leading-relaxed text-muted-foreground">
            Dönem göreli saklanır — pano her açılışta yeniden çözer, karo bayatlamaz.
          </p>
        </div>

        <Separator />

        <Button
          variant="brand"
          size="sm"
          onClick={() => add.mutate()}
          disabled={add.isPending}
          className="h-7 w-full gap-1.5 text-xs"
        >
          <Plus className="size-3.5" />
          {add.isPending ? "ekleniyor…" : "panoya ekle"}
        </Button>
        {add.isError && (
          <p className="text-[11px] text-destructive">Eklenemedi — tekrar dene.</p>
        )}
      </PopoverContent>
    </Popover>
  );
}
