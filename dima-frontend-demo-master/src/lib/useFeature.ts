"use client";

// Özellik bayrakları (ADR-0009) — açılışta bir kez /features okunur, modül düzeyinde
// paylaşılır. ReportPanel'in yerel kopyasıyla aynı; page/pano gibi ortak tüketiciler için.

import { useEffect, useState } from "react";
import { getFeatures } from "@/lib/api-client";

let _features: Record<string, string> | null = null;

export function useFeature(name: string): string | null {
  const [stage, setStage] = useState<string | null>(_features?.[name] ?? null);
  useEffect(() => {
    if (_features) return;
    getFeatures()
      .then((f) => {
        _features = f;
        setStage(f[name] ?? null);
      })
      .catch(() => {});
  }, [name]);
  return stage;
}
