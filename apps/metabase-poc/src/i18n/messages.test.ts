import { describe, expect, it } from "vitest";
import en from "../../messages/en.json";
import tr from "../../messages/tr.json";

/** Every leaf key as a dotted path, so the diff names the offender. */
function paths(value: unknown, prefix = ""): string[] {
  if (typeof value !== "object" || value === null) return [prefix];
  return Object.entries(value as Record<string, unknown>).flatMap(([k, v]) =>
    paths(v, prefix ? `${prefix}.${k}` : k),
  );
}

const trKeys = paths(tr).sort();
const enKeys = paths(en).sort();

describe("messages", () => {
  // An untranslated string should fail here, not in front of a user.
  it("has the same keys in both locales", () => {
    expect(enKeys.filter((k) => !trKeys.includes(k))).toEqual([]);
    expect(trKeys.filter((k) => !enKeys.includes(k))).toEqual([]);
  });

  it("has no empty strings", () => {
    const empty = (obj: unknown, prefix = ""): string[] => {
      if (typeof obj === "string") return obj.trim() ? [] : [prefix];
      if (typeof obj !== "object" || obj === null) return [];
      return Object.entries(obj as Record<string, unknown>).flatMap(([k, v]) =>
        empty(v, prefix ? `${prefix}.${k}` : k),
      );
    };
    expect([...empty(tr), ...empty(en)]).toEqual([]);
  });

  it("uses the same placeholders in both locales", () => {
    const vars = (s: string) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
    const get = (obj: unknown, path: string) =>
      path.split(".").reduce<unknown>((o, k) => (o as Record<string, unknown>)?.[k], obj);
    for (const key of trKeys) {
      const a = get(tr, key);
      const b = get(en, key);
      if (typeof a === "string" && typeof b === "string") {
        expect(vars(b), `placeholders differ at ${key}`).toEqual(vars(a));
      }
    }
  });
});
