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
    expect(visibleCopy).not.toMatch(/\b(?:100%|hallucination-free|zero risk|no hallucinations|SOC 2|ISO 27001)\b/i);
    expect(visibleCopy).not.toMatch(/Ayrıntıyı incele|Explore the details|Learn more|Get started/i);
  });

  it("keeps the homepage and page narratives scannable", () => {
    const tr = getMarketingContent("tr");
    const en = getMarketingContent("en");

    expect(tr.home.process).toHaveLength(4);
    expect(tr.home.reasons).toHaveLength(3);
    expect(tr.home.useCases).toHaveLength(5);
    expect(tr.home.faq).toHaveLength(4);
    expect(tr.home.description.length).toBeLessThan(220);
    expect(en.home.description.length).toBeLessThan(260);

    for (const pageKey of Object.keys(tr.pages)) {
      if (pageKey === "privacy" || pageKey === "terms") continue;
      expect(tr.pages[pageKey].sections.length).toBeLessThanOrEqual(6);
      expect(tr.pages[pageKey].cta.length).toBeGreaterThan(8);
      expect(en.pages[pageKey].cta.length).toBeGreaterThan(8);
    }
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
    expect(getMarketingContent("tr").pages.how.sections).toHaveLength(6);
    expect(getMarketingContent("tr").pages.security.sections).toHaveLength(5);
    expect(getMarketingContent("tr").pages.about.sections).toHaveLength(3);
  });
});
