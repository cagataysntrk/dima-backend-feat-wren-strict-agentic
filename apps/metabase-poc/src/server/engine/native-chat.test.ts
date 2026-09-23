import { describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));
import { parseNativeLine } from "./native-chat";

describe("native Metabot stream parser", () => {
  it("parses text/tool/state protocol without exposing reasoning", () => {
    expect(parseNativeLine('0:"Merhaba"')).toEqual({ kind: "text", value: "Merhaba" });
    expect(
      parseNativeLine('9:{"toolCallId":"t1","toolName":"nlq_search","args":"{}"}'),
    ).toEqual({
      kind: "tool_call",
      value: { toolCallId: "t1", toolName: "nlq_search", args: "{}" },
    });
    expect(
      parseNativeLine('2:{"type":"state","version":1,"value":{"query":{"id":"x"}}}'),
    ).toEqual({
      kind: "data",
      value: { type: "state", version: 1, value: { query: { id: "x" } } },
    });
  });

  it("ignores unknown protocol prefixes", () => {
    expect(parseNativeLine('x:{"private":"ignored"}')).toBeNull();
  });
});
