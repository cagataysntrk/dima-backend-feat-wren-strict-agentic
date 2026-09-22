import { describe, expect, it } from "vitest";
import { insightTitle } from "./insight-title";

describe("insightTitle", () => {
  it("rephrases the engine's English titles", () => {
    expect(insightTitle("Makineler by Kapasite Kg", "makineler")).toBe("Kapasite Kg kırılımı");
    expect(insightTitle("Total Makineler", "makineler")).toBe("Toplam makineler");
    expect(insightTitle("Count of rows", "makineler")).toBe("makineler adedi");
    expect(insightTitle("Makineler per Hat", "makineler")).toBe("Hat kırılımı");
  });

  it("leaves anything else as it is", () => {
    expect(insightTitle("Özet", "makineler")).toBe("Özet");
  });
});
