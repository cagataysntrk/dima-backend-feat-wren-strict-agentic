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
  // §B (1 Ağustos 2026): ÖNCEDEN son 20/40 mesajla sınırlıydı — thread modelinde (bir
  // konuyu derinlemesine işleyip başka bir konuya geçip GERİ DÖNME) bu sınır birkaç
  // thread sonra KÖK mesajları sessizce düşürüp o thread'i YENİDEN İNŞA EDİLEMEZ hale
  // getiriyordu (bir oturumluk, istemci-içi liste — sunucu tarafı kalıcılık zaten AYRI
  // ve sınırsız, bkz. /conversations). Sınır KALDIRILDI.
  add: (item) => set((s) => ({ items: [item, ...s.items] })),
  clear: () => set({ items: [] }),
  load: (items) => set({ items }),
}));
