import { describe, expect, it } from "vitest";
import { getMarketingContent } from "./marketing";

function collectVisibleStrings(value: unknown, key?: string): string[] {
  if (key === "id") return [];
  if (typeof value === "string") return [value];
  if (Array.isArray(value)) {
    return value.flatMap((item) => collectVisibleStrings(item));
  }
  if (value && typeof value === "object") {
    return Object.entries(value).flatMap(([entryKey, entryValue]) =>
      collectVisibleStrings(entryValue, entryKey),
    );
  }
  return [];
}

describe("marketing content", () => {
  it("keeps the public page structure aligned across locales", () => {
    const tr = getMarketingContent("tr");
    const en = getMarketingContent("en");

    expect(Object.keys(tr.pages)).toEqual(Object.keys(en.pages));
    for (const pageKey of Object.keys(tr.pages)) {
      expect(tr.pages[pageKey].sections.map((section) => section.id)).toEqual(
        en.pages[pageKey].sections.map((section) => section.id),
      );
    }
  });

  it("keeps English product jargon out of primary Turkish marketing copy", () => {
    const { footer, common, home, pages } = getMarketingContent("tr");
    const visibleCopy = collectVisibleStrings({ footer, common, home, pages }).join(" ");

    expect(visibleCopy).not.toMatch(
      /\b(?:semantic|dry-plan|provenance|tenant|permission|onboarding|read-only|roadmap|backend|frontend|LLM|KPI)\b/i,
    );
  });
});
