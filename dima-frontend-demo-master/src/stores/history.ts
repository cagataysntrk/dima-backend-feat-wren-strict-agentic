// Client-side session state: recent questions asked in this demo run.

import { create } from "zustand";
import type { AskResponse } from "@/lib/types";

interface HistoryState {
  items: AskResponse[];
  add: (item: AskResponse) => void;
  clear: () => void;
  // Resume: kayıtlı sohbeti yükle (items YENİDEN üstte sıralı — store newest-first tutar).
  load: (items: AskResponse[]) => void;
}

export const useHistory = create<HistoryState>((set) => ({
  items: [],
  add: (item) => set((s) => ({ items: [item, ...s.items].slice(0, 20) })),
  clear: () => set({ items: [] }),
  load: (items) => set({ items: items.slice(0, 40) }),
}));
