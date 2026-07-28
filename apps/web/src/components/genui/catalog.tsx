"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import type { AskResponse } from "@dima/contracts";
import type { CatalogEntry } from "@dima/genui";

/**
 * Üretilen panonun karolarını gerçek `AskResponse`'lara bağlayan bağlam.
 *
 * Model (ya da deterministik düzenleyici) yalnız `resultId` yazar; veri buradan
 * çözülür. Böylece üretilen yerleşim ile veri arasında tek yönlü, denetlenebilir
 * bir bağ kalır — üreten taraf satırlara hiç dokunmaz.
 */

const CatalogContext = createContext<Map<string, AskResponse>>(new Map());

export function CatalogProvider({
  entries,
  children,
}: {
  entries: CatalogEntry[];
  children: ReactNode;
}) {
  const map = useMemo(
    () => new Map(entries.map((e) => [e.id, e.response])),
    [entries],
  );
  return <CatalogContext.Provider value={map}>{children}</CatalogContext.Provider>;
}

export function useResult(resultId: string): AskResponse | null {
  return useContext(CatalogContext).get(resultId) ?? null;
}
