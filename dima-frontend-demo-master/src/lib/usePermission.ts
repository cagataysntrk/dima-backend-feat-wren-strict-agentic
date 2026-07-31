"use client";

// İzinler (/auth/me permissions) — kaynak backend authorize matrisi; rol semantiği
// UI'a KOPYALANMAZ, rol açmak yalnız backend değişikliğidir. Liste yüklenene kadar
// izinli varsayılır (regresyon olmasın); backend her eylemi kendi tarafında da zorlar.
// ReportPanel'in yerel `usePermission`'ıyla AYNI desen (useFeature.ts'in izin karşılığı) —
// page/rail gibi ortak tüketiciler için.

import { useEffect, useState } from "react";
import { getMe } from "@/lib/api-client";

let _perms: string[] | null = null;

export function usePermission(action: string): boolean {
  const [ok, setOk] = useState<boolean>(_perms ? _perms.includes(action) : true);
  useEffect(() => {
    if (_perms) return;
    getMe()
      .then((me) => {
        _perms = me.permissions ?? [];
        setOk(_perms.includes(action));
      })
      .catch(() => {});
  }, [action]);
  return ok;
}
