import { describe, expect, it } from "vitest";
import { guessType, parameterValues, parseVariables, templateTags } from "./sql-vars";

const SQL = "select * from t where 1=1 [[and makine = {{makine}}]] [[and tarih >= {{baslangic}}]] [[and vardiya = {{ vardiya }}]] and x = {{makine}}";

describe("parseVariables", () => {
  it("finds each variable once, in order, and guesses its type from the name", () => {
    expect(parseVariables(SQL)).toEqual([
      { name: "makine", type: "text", label: "Makine" },
      { name: "baslangic", type: "date", label: "Baslangic" },
      { name: "vardiya", type: "number", label: "Vardiya" },
    ]);
  });

  it("ignores things that are not variables", () => {
    expect(parseVariables("select '{{ }}', {{1bad}}, {{}} from t")).toEqual([]);
  });

  it.each([
    ["tarih", "date"],
    ["bitis_tarihi", "date"],
    ["adet", "number"],
    ["min_tutar", "number"],
    ["musteri", "text"],
  ] as const)("guessType(%s) = %s", (name, type) => {
    expect(guessType(name)).toBe(type);
  });
});

describe("templateTags", () => {
  it("declares one tag per variable", () => {
    expect(templateTags(parseVariables(SQL)).makine).toEqual({
      id: "tag-makine",
      name: "makine",
      "display-name": "Makine",
      type: "text",
    });
  });

  it("stores current values as defaults when saving, so the saved card runs on its own", () => {
    const tags = templateTags(parseVariables(SQL), { makine: "RAM-1", vardiya: "2" }, true);
    expect(tags.makine.default).toBe("RAM-1");
    expect(tags.vardiya.default).toBe(2);
    expect(tags.baslangic.default).toBeUndefined();
  });
});

describe("parameterValues", () => {
  it("sends only filled values, typed for the engine", () => {
    expect(parameterValues(parseVariables(SQL), { makine: "RAM-1", vardiya: "2", baslangic: "  " })).toEqual([
      { type: "category", target: ["variable", ["template-tag", "makine"]], value: "RAM-1" },
      { type: "number/=", target: ["variable", ["template-tag", "vardiya"]], value: [2] },
    ]);
  });

  it("drops a number variable that is not a number", () => {
    expect(parameterValues(parseVariables(SQL), { vardiya: "abc" })).toEqual([]);
  });
});
