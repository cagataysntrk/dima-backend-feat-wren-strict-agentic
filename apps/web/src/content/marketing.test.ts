import { describe, expect, it } from "vitest";
import { getMarketingContent, publicRoutes } from "./marketing";

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

  it("keeps the launch route and capability contracts explicit", () => {
    expect(publicRoutes).toEqual([
      "/",
      "/product",
      "/how-it-works",
      "/solutions",
      "/solutions/textile-dyehouse",
      "/security",
      "/integrations",
      "/about",
      "/contact",
      "/privacy",
      "/terms",
    ]);
    const statuses = JSON.stringify(getMarketingContent("tr"));
    expect(statuses).not.toContain('"beta"');
    expect(getMarketingContent("tr").pages.textile.sections).toHaveLength(6);
    expect(getMarketingContent("en").pages.solutions.sections).toHaveLength(6);
  });
});
