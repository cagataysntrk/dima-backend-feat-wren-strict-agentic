import { describe, expect, it } from "vitest";
import { frameData, mergeToolCalls, splitFrames, sseFrame, usableToolCalls, type StreamedToolCall } from "./sse";

describe("splitFrames", () => {
  it("returns complete frames and keeps the unfinished tail", () => {
    expect(splitFrames("data: a\n\ndata: b\n\ndata: par")).toEqual({
      frames: ["data: a", "data: b"],
      rest: "data: par",
    });
  });

  it("handles CRLF and keep-alive blank frames", () => {
    expect(splitFrames("data: a\r\n\r\n\r\n\r\n").frames).toEqual(["data: a"]);
  });
});

describe("frameData", () => {
  it("reads the payload and joins multi-line data", () => {
    expect(frameData("data: {\"x\":1}")).toBe('{"x":1}');
    expect(frameData("data: one\ndata: two")).toBe("one\ntwo");
  });

  it("ignores comments", () => {
    expect(frameData(": ping")).toBeNull();
  });
});

describe("mergeToolCalls", () => {
  it("re-assembles arguments streamed across chunks", () => {
    let acc: StreamedToolCall[] = [];
    acc = mergeToolCalls(acc, [{ index: 0, id: "c1", function: { name: "run_sql", arguments: '{"sql":"sel' } }]);
    acc = mergeToolCalls(acc, [{ index: 0, function: { arguments: 'ect 1","final":true}' } }]);
    expect(acc).toEqual([{ id: "c1", name: "run_sql", arguments: '{"sql":"select 1","final":true}' }]);
  });

  it("keeps parallel calls apart by index", () => {
    const acc = mergeToolCalls(
      [],
      [
        { index: 0, id: "a", function: { name: "run_sql", arguments: "{}" } },
        { index: 1, id: "b", function: { name: "run_sql", arguments: "{}" } },
      ],
    );
    expect(acc.map((c) => c.id)).toEqual(["a", "b"]);
  });

  it("is a no-op without deltas", () => {
    const acc: StreamedToolCall[] = [{ id: "a", name: "run_sql", arguments: "{}" }];
    expect(mergeToolCalls(acc, undefined)).toBe(acc);
  });
});

describe("usableToolCalls", () => {
  it("drops calls whose JSON has not finished arriving", () => {
    const calls: StreamedToolCall[] = [
      { id: "a", name: "run_sql", arguments: '{"sql":"select 1"}' },
      { id: "b", name: "run_sql", arguments: '{"sql":"sel' },
      { id: "", name: "run_sql", arguments: "{}" },
    ];
    expect(usableToolCalls(calls).map((c) => c.id)).toEqual(["a"]);
  });
});

describe("sseFrame", () => {
  it("writes one event per frame", () => {
    expect(sseFrame({ type: "step", text: "a" })).toBe('data: {"type":"step","text":"a"}\n\n');
  });
});
