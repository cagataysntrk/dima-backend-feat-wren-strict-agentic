"use client";

// Feature flags (ADR-0009) + permissions (/auth/me) — module-level singletons read
// once and shared across surfaces (sidebar, report, artifact). Kept out of React Query
// deliberately: tiny, read-once, and permissions default to ALLOWED until loaded so
// there's no UI regression on first paint (the backend enforces every action anyway).

import { useEffect, useState } from "react";
import { getFeatures, getMe, type AuthUser } from "@/lib/api-client";

let _me: AuthUser | null = null;
/** The signed-in user (for the account entry). Null until /auth/me resolves. */
export function useMe(): AuthUser | null {
  const [me, setMe] = useState<AuthUser | null>(_me);
  useEffect(() => {
    if (_me) return;
    getMe()
      .then((u) => {
        _me = u;
        setMe(u);
      })
      .catch(() => {});
  }, []);
  return me;
}

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
