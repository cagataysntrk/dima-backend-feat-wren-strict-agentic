import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));
import { openEngineContext, sealEngineContext } from "./context";

describe("native engine context token", () => {
  beforeEach(() => {
    process.env.BETTER_AUTH_SECRET = "test-secret-that-is-not-production";
  });
  afterEach(() => {
    delete process.env.BETTER_AUTH_SECRET;
  });

  const value = {
    version: 1 as const,
    tenantSlug: "boyahane",
    productConversationId: "11111111-1111-4111-8111-111111111111",
    engineConversationId: "22222222-2222-4222-8222-222222222222",
    history: [{ role: "user" as const, content: "Q1" }],
    state: { query: { id: "x" } },
  };

  it("round-trips only for the same tenant and product conversation", () => {
    const token = sealEngineContext(value);
    expect(
      openEngineContext(token, {
        tenantSlug: "boyahane",
        productConversationId: value.productConversationId,
      }),
    ).toEqual(value);
  });

  it("rejects cross-tenant replay", () => {
    const token = sealEngineContext(value);
    expect(() =>
      openEngineContext(token, {
        tenantSlug: "other",
        productConversationId: value.productConversationId,
      }),
    ).toThrow();
  });

  it("rejects tampering", () => {
    const token = sealEngineContext(value);
    const changed = token.slice(0, -1) + (token.endsWith("A") ? "B" : "A");
    expect(() =>
      openEngineContext(changed, {
        tenantSlug: "boyahane",
        productConversationId: value.productConversationId,
      }),
    ).toThrow();
  });
});
