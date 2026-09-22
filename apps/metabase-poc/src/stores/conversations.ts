"use client";

import { create } from "zustand";
import { createJSONStorage, persist, type StateStorage } from "zustand/middleware";
import type { ChatAnswer } from "@/lib/gateway";

// Chat history for the POC: kept in this browser (localStorage), scoped by
// organization so switching company never shows another tenant's chats.
// Server-side history (dima-backend /conversations) is a later integration.

export interface Step {
  id: number;
  text: string;
  done: boolean;
}

export type Entry = { id: number; question: string } & (
  | { status: "pending"; steps?: Step[]; partial?: string }
  | { status: "done"; reply: ChatAnswer; steps?: string[]; durationMs?: number }
  | { status: "error"; message: string }
);

export interface Conversation {
  id: string;
  orgId: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  entries: Entry[];
}

interface State {
  conversations: Conversation[];
  create: (orgId: string) => string;
  addEntry: (convId: string, question: string) => number;
  /** Live progress of a pending turn (steps + streamed text). */
  progress: (convId: string, entryId: number, patch: { steps?: Step[]; partial?: string }) => void;
  settle: (convId: string, entryId: number, patch: Extract<Entry, { status: "done" | "error" }>) => void;
  rename: (convId: string, title: string) => void;
  remove: (convId: string) => void;
}

const MAX_CONVERSATIONS = 30;
const MAX_PERSISTED_ROWS = 500;

// localStorage can be full, blocked (private mode) or absent; the chat must keep working.
const safeStorage: StateStorage = {
  getItem: (k) => {
    try {
      return localStorage.getItem(k);
    } catch {
      return null;
    }
  },
  setItem: (k, v) => {
    try {
      localStorage.setItem(k, v);
    } catch {
      /* quota / disabled: history just isn't persisted */
    }
  },
  removeItem: (k) => {
    try {
      localStorage.removeItem(k);
    } catch {
      /* ignore */
    }
  },
};

const touch = (c: Conversation, entries: Entry[]): Conversation => ({ ...c, entries, updatedAt: Date.now() });

export const useConversations = create<State>()(
  persist(
    (set, get) => ({
      conversations: [],
      create: (orgId) => {
        const id = crypto.randomUUID();
        const now = Date.now();
        set((s) => ({
          conversations: [{ id, orgId, title: "", createdAt: now, updatedAt: now, entries: [] }, ...s.conversations].slice(
            0,
            MAX_CONVERSATIONS,
          ),
        }));
        return id;
      },
      addEntry: (convId, question) => {
        const conv = get().conversations.find((c) => c.id === convId);
        const entryId = (conv?.entries.at(-1)?.id ?? 0) + 1;
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === convId
              ? {
                  ...touch(c, [...c.entries, { id: entryId, question, status: "pending" }]),
                  title: c.title || question.slice(0, 80),
                }
              : c,
          ),
        }));
        return entryId;
      },
      progress: (convId, entryId, patch) =>
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === convId
              ? touch(
                  c,
                  c.entries.map((e) => (e.id === entryId && e.status === "pending" ? { ...e, ...patch } : e)),
                )
              : c,
          ),
        })),
      settle: (convId, entryId, patch) =>
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === convId ? touch(c, c.entries.map((e) => (e.id === entryId ? patch : e))) : c,
          ),
        })),
      rename: (convId, title) =>
        set((s) => ({
          conversations: s.conversations.map((c) =>
            c.id === convId ? { ...c, title: title.trim().slice(0, 80) || c.title } : c,
          ),
        })),
      remove: (convId) => set((s) => ({ conversations: s.conversations.filter((c) => c.id !== convId) })),
    }),
    {
      name: "dima-poc-conversations",
      version: 1,
      // Rehydrated after mount (AppSidebar) so SSR and the first client render match.
      skipHydration: true,
      storage: createJSONStorage(() => safeStorage),
      // Persist finished turns only (a reload can't resume a pending request),
      // with large results trimmed to stay well inside the storage quota.
      partialize: (s) => ({
        conversations: s.conversations.map((c) => ({
          ...c,
          entries: c.entries
            .filter((e) => e.status !== "pending")
            .map((e) =>
              e.status === "done" && e.reply.result && e.reply.result.rows.length > MAX_PERSISTED_ROWS
                ? {
                    ...e,
                    reply: {
                      ...e.reply,
                      result: { ...e.reply.result, rows: e.reply.result.rows.slice(0, MAX_PERSISTED_ROWS) },
                    },
                  }
                : e,
            ),
        })),
      }),
    },
  ),
);
