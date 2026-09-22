"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import { useTranslations } from "next-intl";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@dima/ui/primitives/dialog";
import { Kbd, KbdGroup } from "@dima/ui/primitives/kbd";

/** macOS writes ⌘; everything else writes Ctrl. Known only on the client. */
function useModKey() {
  return useSyncExternalStore(
    () => () => {},
    () => (navigator.platform.toLowerCase().includes("mac") ? "⌘" : "Ctrl"),
    () => "Ctrl",
  );
}

const SHORTCUTS = [
  { keys: ["mod", "K"], key: "palette" },
  { keys: ["mod", "B"], key: "sidebar" },
  { keys: ["mod", "Enter"], key: "runSql" },
  { keys: ["mod", "/"], key: "shortcuts" },
  { keys: ["Esc"], key: "close" },
] as const;

export function ShortcutsDialog() {
  const t = useTranslations("shortcuts");
  const mod = useModKey();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "/" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>{t("title")}</DialogTitle>
        </DialogHeader>
        <ul className="space-y-2.5">
          {SHORTCUTS.map(({ keys, key }) => (
            <li key={key} className="flex items-center justify-between gap-4 text-sm">
              <span className="text-muted-foreground">{t(key)}</span>
              <KbdGroup>
                {keys.map((k) => (
                  <Kbd key={k}>{k === "mod" ? mod : k}</Kbd>
                ))}
              </KbdGroup>
            </li>
          ))}
        </ul>
      </DialogContent>
    </Dialog>
  );
}
