import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const src = join(import.meta.dirname, "../..");
const appRoot = join(src, "..");

function read(path: string): string {
  return readFileSync(path, "utf8");
}

describe("native-first chat architecture", () => {
  it("keeps the chat hot path on the native engine adapter with no legacy fallback", () => {
    const route = read(join(src, "app/api/chat/route.ts"));
    expect(route).toContain("@/server/engine/native-chat");
    expect(route).not.toContain("@/server/chat/agent");
    expect(route).not.toContain("@/server/chat/openrouter");
    expect(route).not.toContain("OPENROUTER");
  });

  it("removes the legacy custom OpenRouter analytics engine from the product tree", () => {
    expect(existsSync(join(src, "server/chat/agent.ts"))).toBe(false);
    expect(existsSync(join(src, "server/chat/openrouter.ts"))).toBe(false);
    expect(existsSync(join(src, "server/chat/prompt.ts"))).toBe(false);
  });

  it("keeps provider credentials out of the frontend runtime configuration", () => {
    const env = read(join(appRoot, ".env.local.example"));
    expect(env).toContain("DIMA_ENGINE_URL");
    expect(env).toContain("DIMA_ENGINE_TENANTS");
    expect(env).not.toMatch(/^OPENROUTER_(?:API_KEY|MODEL)=/m);
    expect(env).not.toMatch(/^METABASE_URL=/m);
  });

  it("pins the canonical Dima engine release contract in workspace docs", () => {
    const env = read(join(appRoot, ".env.local.example"));
    const workspace = read(join(appRoot, "../../docs/NATIVE_ENGINE_WORKSPACE.md"));
    const digest = "sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9";
    for (const content of [env, workspace]) {
      expect(content).toContain("0.63.18-dima.0");
      expect(content).toContain(digest);
    }
  });
});
