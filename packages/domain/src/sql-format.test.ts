import { describe, expect, it } from "vitest";
import { formatSql, tokenizeSql } from "./sql-format";

describe("formatSql", () => {
  it("puts each clause on its own line", () => {
    expect(formatSql("select a, b from t where a = 1 order by b desc")).toBe(
      ["SELECT a,", "  b", "FROM t", "WHERE a = 1", "ORDER BY b DESC"].join("\n"),
    );
  });

  it("keeps a line comment from swallowing the code after it", () => {
    const out = formatSql("-- not\nselect 1");
    expect(out).toBe("-- not\nSELECT 1");
    expect(out.split("\n")[1]).not.toMatch(/^--/);
  });

  it("leaves template variables intact", () => {
    // {{x}} split into "{ { x } }" would stop the query from running at all.
    expect(formatSql("select a from t where a = {{makine}}")).toContain("a = {{makine}}");
  });

  it("keeps an optional block on one line with its condition", () => {
    expect(formatSql("select a from t where 1 = 1 [[and a = {{m}}]]")).toBe(
      ["SELECT a", "FROM t", "WHERE 1 = 1", "  [[AND a = {{m}}]]"].join("\n"),
    );
  });

  it("keeps the cast operator tight", () => {
    expect(formatSql("select round(avg(x)::numeric, 1) from t")).toContain("ROUND(AVG(x)::numeric, 1)");
  });

  it("is idempotent", () => {
    const once = formatSql("select a from t where 1 = 1 [[and a = {{m}}]] -- son\n");
    expect(formatSql(once)).toBe(once);
  });
});

describe("tokenizeSql", () => {
  it("emits a template variable as a single token", () => {
    expect(tokenizeSql("{{makine}}")).toEqual([{ type: "ident", text: "{{makine}}" }]);
  });

  it("emits optional-block brackets as single tokens", () => {
    expect(tokenizeSql("[[x]]").map((t) => t.text)).toEqual(["[[", "x", "]]"]);
  });

  it("still tokenizes an unclosed brace as punctuation", () => {
    expect(tokenizeSql("{{oops").map((t) => t.type)).toEqual(["punct", "punct", "ident"]);
  });
});
