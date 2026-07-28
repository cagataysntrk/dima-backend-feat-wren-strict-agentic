"use client";

import { useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Kbd, KbdGroup } from "@/components/ui/kbd";

/**
 * Klavye kısayolları — Claude'daki modalın karşılığı, ⌘/ ile açılır.
 *
 * Buradaki liste GERÇEKTEN bağlı olan kısayolları gösterir. Bir satır eklemeden
 * önce kısayolun çalıştığından emin ol: çalışmayan bir kısayolu listelemek,
 * kullanıcıyı olmayan bir özelliği aramaya gönderir.
 */
const GROUPS: { title: string; items: { label: string; keys: string[] }[] }[] = [
  {
    title: "Genel",
    items: [
      { label: "Ara / komut paleti", keys: ["⌘", "K"] },
      { label: "Kenar çubuğunu aç/kapa", keys: ["⌘", "B"] },
      { label: "Klavye kısayolları", keys: ["⌘", "/"] },
    ],
  },
  {
    title: "Sohbette",
    items: [
      { label: "Mesajı gönder", keys: ["⏎"] },
      { label: "Satır atla", keys: ["⇧", "⏎"] },
      { label: "Dosya ekle", keys: ["⌘", "U"] },
    ],
  },
];

export function ShortcutsDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "/" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onOpenChange(!open);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onOpenChange]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Klavye kısayolları</DialogTitle>
        </DialogHeader>

        <div className="space-y-5">
          {GROUPS.map((g) => (
            <section key={g.title} className="space-y-1">
              <h3 className="text-xs font-medium text-muted-foreground">{g.title}</h3>
              <ul>
                {g.items.map((it) => (
                  <li
                    key={it.label}
                    className="flex items-center justify-between gap-4 border-b border-border py-2.5 last:border-0"
                  >
                    <span className="text-sm text-foreground">{it.label}</span>
                    <KbdGroup>
                      {it.keys.map((k) => (
                        <Kbd key={k}>{k}</Kbd>
                      ))}
                    </KbdGroup>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
