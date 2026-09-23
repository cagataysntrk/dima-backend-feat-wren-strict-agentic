import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { ERROR_KEYS } from "./error-messages";
import tr from "../../messages/tr.json";
import en from "../../messages/en.json";

/** Every `new GatewayError(n, "…")` literal in the app. */
function thrownMessages(dir: string, out = new Set<string>()): Set<string> {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) thrownMessages(path, out);
    else if (/\.tsx?$/.test(name)) {
      for (const m of readFileSync(path, "utf8").matchAll(/new GatewayError\(\s*\d+\s*,\s*"([^"]+)"/g)) {
        out.add(m[1]);
      }
    }
  }
  return out;
}

const root = join(import.meta.dirname, "..");

describe("gateway error messages", () => {
  // A new throw site with no key would reach an English-speaking user in
  // Turkish, and nothing else would notice.
  it("has a key for every thrown message", () => {
    const missing = [...thrownMessages(join(root, "server")), ...thrownMessages(join(root, "app", "api"))].filter(
      (m) => !ERROR_KEYS[m],
    );
    expect(missing).toEqual([]);
  });

  it("has both translations for every key", () => {
    const keys = Object.values(ERROR_KEYS);
    expect(keys.filter((k) => !(k in tr.gateway))).toEqual([]);
    expect(keys.filter((k) => !(k in en.gateway))).toEqual([]);
  });

  it("keeps the Turkish text identical to what the code throws", () => {
    for (const [message, key] of Object.entries(ERROR_KEYS)) {
      expect((tr.gateway as Record<string, string>)[key]).toBe(message);
    }
  });
});
