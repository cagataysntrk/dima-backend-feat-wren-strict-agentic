// Client-side conversation state: named chat sessions in the left sidebar.
// Memory-only for now; the shape allows a later `zustand/persist` without a rewrite.

import { create } from "zustand";
import type { AskResponse } from "@/lib/types";

export interface Conversation {
  id: string;
  title: string;
  sessionId: string;
  items: AskResponse[]; // newest first (matches the old history store)
  createdAt: number;
}

interface ConversationsState {
  conversations: Conversation[];
  activeId: string | null;
  /** Create a fresh conversation and make it active; returns its id. */
  newConversation: () => string;
  select: (id: string) => void;
  /** Append an answer to the active conversation (creating one if needed). */
  add: (item: AskResponse) => void;
  clearActive: () => void;
  /** Sohbeti yeniden adlandır (başlık kullanıcı tarafından sabitlenir). */
  rename: (id: string, title: string) => void;
  /** Sohbeti sil; aktifse aktiflik bir sonrakine geçer. */
  remove: (id: string) => void;
  /** Wipe ALL conversations (cross-user isolation on logout/login). */
  reset: () => void;

  // ── Gizli sohbet ────────────────────────────────────────────────────────
  // Açıkken konuşma listeye HİÇ yazılmaz: geçmişte iz bırakmaz, sidebar'da
  // görünmez, kapanınca da silinir. (Sunucu tarafı ayrı bir mesele — backend
  // yine session_id görür; burada söz verdiğimiz şey YEREL geçmiş.)
  incognito: boolean;
  incognitoItems: AskResponse[];
  setIncognito: (on: boolean) => void;
}

// crypto.randomUUID yalnız güvenli bağlamda (https/localhost) var; http://*.localtld'de yok.
function makeId(prefix: string): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return `${prefix}-${crypto.randomUUID()}`;
    }
  } catch {
    /* güvenli bağlam değil */
  }
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

function freshConversation(): Conversation {
  return {
    id: makeId("c"),
    title: "",
    sessionId: makeId("s"),
    items: [],
    createdAt: Date.now(),
  };
}

// chip düzenlemeleri gerçek soru değildir — başlık için ilk GERÇEK kullanıcı sorusunu al.
const titleFrom = (item: AskResponse) =>
  item.question.startsWith("chip:") ? "" : item.question.slice(0, 60);

export const useConversations = create<ConversationsState>((set) => ({
  conversations: [],
  activeId: null,
  incognito: false,
  incognitoItems: [],
  setIncognito: (on) =>
    // Moda girerken de çıkarken de gizli mesajları temizle — mod kapanınca
    // içerik kalıcı geçmişe SIZMAMALI.
    set({ incognito: on, incognitoItems: [] }),
  newConversation: () => {
    const conv = freshConversation();
    set((s) => ({ conversations: [conv, ...s.conversations], activeId: conv.id }));
    return conv.id;
  },
  select: (id) => set({ activeId: id }),
  add: (item) =>
    set((s) => {
      // gizli mod: kalıcı listeye dokunma
      if (s.incognito) return { incognitoItems: [item, ...s.incognitoItems].slice(0, 40) };
      let conversations = s.conversations;
      let activeId = s.activeId;
      if (!activeId || !conversations.some((c) => c.id === activeId)) {
        const conv = freshConversation();
        conversations = [conv, ...conversations];
        activeId = conv.id;
      }
      conversations = conversations.map((c) =>
        c.id === activeId
          ? {
              ...c,
              title: c.title || titleFrom(item),
              items: [item, ...c.items].slice(0, 40),
            }
          : c,
      );
      return { conversations, activeId };
    }),
  rename: (id, title) =>
    set((s) => ({
      conversations: s.conversations.map((c) => (c.id === id ? { ...c, title } : c)),
    })),
  remove: (id) =>
    set((s) => {
      const conversations = s.conversations.filter((c) => c.id !== id);
      // Aktif sohbet silindiyse aktiflik listedeki ilkine geçer (null kalırsa
      // ekran boş bir "sohbet yok" durumuna düşerdi).
      const activeId = s.activeId === id ? (conversations[0]?.id ?? null) : s.activeId;
      return { conversations, activeId };
    }),
  clearActive: () =>
    set((s) => ({
      conversations: s.conversations.map((c) =>
        c.id === s.activeId ? { ...c, items: [], title: "" } : c,
      ),
      incognitoItems: [],
    })),
  // ÇAPRAZ-KULLANICI İZOLASYON (güvenlik, canlı 2026-07-25): store modül-seviyesi global,
  // SPA login/logout round-trip'inde (hard reload yok) yaşar. Temizlenmezse LOGOUT sonrası
  // BAŞKA kullanıcı önceki kullanıcının tüm konuşma/rapor zincirini görürdü. reset hepsini siler.
  reset: () => set({ conversations: [], activeId: null }),
}));

/** The active conversation object (or null). */
export const selectActive = (s: ConversationsState): Conversation | null =>
  s.conversations.find((c) => c.id === s.activeId) ?? null;
