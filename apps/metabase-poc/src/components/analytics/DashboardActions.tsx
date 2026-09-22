"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LayoutDashboard, LayoutGrid, Plus } from "lucide-react";
import { toast } from "sonner";
import { gateway } from "@/lib/gateway";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

/** Name prompt for a new dashboard (in-app dialog, never window.prompt). */
export function NewDashboardDialog({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  onCreated: (id: number) => void;
}) {
  const [name, setName] = useState("");
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: () => gateway.createDashboard(name.trim()),
    onSuccess: ({ id }) => {
      void queryClient.invalidateQueries({ queryKey: ["items"] });
      setName("");
      onOpenChange(false);
      onCreated(id);
    },
    onError: (e) => toast.error(e.message),
  });
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (name.trim()) create.mutate();
          }}
          className="grid gap-4"
        >
          <DialogHeader>
            <DialogTitle>Yeni pano</DialogTitle>
            <DialogDescription>Pano bir tarih filtresiyle başlar; eklediğiniz grafikler filtreye bağlanır.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-2">
            <Label htmlFor="dashboard-name">Pano adı</Label>
            <Input
              id="dashboard-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={120}
              autoFocus
              placeholder="ör. Haftalık üretim"
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
              Vazgeç
            </Button>
            <Button type="submit" variant="brand" disabled={!name.trim() || create.isPending}>
              {create.isPending ? "Oluşturuluyor…" : "Panoyu oluştur"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

/** Overview button: create a dashboard, then open it. */
export function NewDashboardButton() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
        <Plus className="size-4" aria-hidden />
        Yeni pano
      </Button>
      <NewDashboardDialog open={open} onOpenChange={setOpen} onCreated={(id) => router.push(`/app/dashboards/${id}`)} />
    </>
  );
}

/**
 * "Panoya ekle": pick a dashboard (or create one) for a saved card.
 * `resolveCardId` lets callers save first (chat answers are unsaved SQL).
 */
export function AddToDashboard({
  resolveCardId,
  size = "sm",
}: {
  resolveCardId: () => Promise<number>;
  size?: "sm" | "xs";
}) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [creating, setCreating] = useState(false);
  const dashboards = useQuery({
    queryKey: ["items"],
    queryFn: gateway.items,
    select: (items) => items.filter((i) => i.kind === "dashboard"),
  });
  const add = useMutation({
    mutationFn: async (dashboardId: number) => {
      const cardId = await resolveCardId();
      const res = await gateway.addToDashboard(dashboardId, cardId);
      return { dashboardId, ...res };
    },
    onSuccess: ({ dashboardId, wired }) => {
      void queryClient.invalidateQueries({ queryKey: ["dashboard", dashboardId] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard-data", dashboardId] });
      toast.success(wired ? "Panoya eklendi." : "Panoya eklendi. Pano filtreleri bu grafiğe uygulanmaz.", {
        action: { label: "Panoyu aç", onClick: () => router.push(`/app/dashboards/${dashboardId}`) },
      });
    },
    onError: (e) => toast.error(e.message),
  });

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size={size} disabled={add.isPending}>
            <LayoutDashboard className={size === "xs" ? "size-3.5" : "size-4"} aria-hidden />
            {add.isPending ? "Ekleniyor…" : "Panoya ekle"}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-64">
          <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">Pano seçin</DropdownMenuLabel>
          {dashboards.isPending && <p className="px-2 py-1.5 text-sm text-muted-foreground">Yükleniyor…</p>}
          {dashboards.data?.length === 0 && <p className="px-2 py-1.5 text-sm text-muted-foreground">Henüz pano yok.</p>}
          {dashboards.data?.map((d) => (
            <DropdownMenuItem key={d.id} onSelect={() => add.mutate(d.id)}>
              <LayoutGrid className="size-4 text-muted-foreground" aria-hidden />
              <span className="truncate">{d.name}</span>
            </DropdownMenuItem>
          ))}
          <DropdownMenuSeparator />
          <DropdownMenuItem onSelect={() => setCreating(true)}>
            <Plus className="size-4" aria-hidden />
            Yeni pano…
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <NewDashboardDialog open={creating} onOpenChange={setCreating} onCreated={(id) => add.mutate(id)} />
    </>
  );
}
