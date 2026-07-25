"use client";

import { useSyncExternalStore } from "react";

const subscribe = () => () => {};

/**
 * True only after client mount (false during SSR + first hydration render).
 * Uses useSyncExternalStore so it never calls setState in an effect — the
 * canonical hydration-safe way to gate client-only, theme/locale-dependent UI.
 */
export function useMounted(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => true, // client snapshot
    () => false, // server snapshot (and first hydration render)
  );
}
