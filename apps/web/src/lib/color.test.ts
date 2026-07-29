import { describe, expect, it } from "vitest";
import {
  contrastRatio,
  gradeContrast,
  oklchToHex,
  oklchToSrgb,
  parseOklch,
  relativeLuminance,
  resolveCssColor,
} from "./color";

/**
 * Stil kılavuzu bu matematiğin çıktısını SAYI olarak gösteriyor ("4.8:1 · AA").
 * Yanlış bir dönüşüm sessizce yanlış bir güvence üretir — o yüzden bilinen
 * değerlerle sabitlenir: sRGB primaries, beyaz/siyah = 21:1, ve globals.css'te
 * hex'i zaten yazılı olan dima jetonları.
 */

const ok = (s: string) => {
  const v = parseOklch(s);
  if (!v) throw new Error(`ayrıştırılamadı: ${s}`);
  return v;
};

/** Kontrast/parlaklık sRGB alır — testlerde oklch metninden tek adımda geç. */
const rgb = (s: string) => oklchToSrgb(ok(s));

describe("parseOklch", () => {
  it("sayısal biçimi okur", () => {
    expect(parseOklch("oklch(0.551 0.260 292.1)")).toEqual({
      l: 0.551,
      c: 0.26,
      h: 292.1,
    });
  });

  it("yüzde biçimini de okur", () => {
    expect(parseOklch("oklch(55.1% 65% 292.1)")).toEqual({
      l: 0.551,
      c: 0.26,
      h: 292.1,
    });
  });

  it("negatif ton açısını kabul eder", () => {
    expect(parseOklch("oklch(0.7 0.1 -20)")?.h).toBe(-20);
  });

  // Tahmin etmektense null dönmeli: yanlış bir renk, eksik renkten kötüdür.
  it("tanınmayan biçimde null döner", () => {
    expect(parseOklch("#7e38f8")).toBeNull();
    expect(parseOklch("rgb(126 56 248)")).toBeNull();
    expect(parseOklch("")).toBeNull();
  });
});

describe("oklchToHex", () => {
  it("uçları tam verir", () => {
    expect(oklchToHex(ok("oklch(1 0 0)"))).toBe("#FFFFFF");
    expect(oklchToHex(ok("oklch(0 0 0)"))).toBe("#000000");
  });

  // sRGB primaries — matris ve gama fonksiyonunun tek doğrulanabilir referansı.
  it("sRGB primaries'i vurur", () => {
    expect(oklchToHex(ok("oklch(0.62796 0.25768 29.234)"))).toBe("#FF0000");
    expect(oklchToHex(ok("oklch(0.86644 0.29483 142.495)"))).toBe("#00FF00");
    expect(oklchToHex(ok("oklch(0.45201 0.31321 264.052)"))).toBe("#0000FF");
  });

  /**
   * globals.css marka morunu "#7e38f8" diye yazıyor ve jetonu oklch olarak
   * tanımlıyor. Bu test o İKİSİNİN aynı rengi söylediğini kanıtlar — biri
   * değişip diğeri unutulursa burada patlar.
   */
  it("dima marka morunu üretir", () => {
    expect(oklchToHex(ok("oklch(0.551 0.260 292.1)"))).toBe("#7E38F8");
  });

  it("gamut dışını kırpar (taşma değil)", () => {
    const hex = oklchToHex({ l: 0.7, c: 0.9, h: 30 });
    expect(hex).toMatch(/^#[0-9A-F]{6}$/);
  });
});

describe("contrastRatio", () => {
  it("beyaz/siyah = 21:1", () => {
    expect(contrastRatio(rgb("oklch(1 0 0)"), rgb("oklch(0 0 0)"))).toBeCloseTo(21, 4);
  });

  it("aynı renk = 1:1", () => {
    const c = rgb("oklch(0.551 0.260 292.1)");
    expect(contrastRatio(c, c)).toBeCloseTo(1, 6);
  });

  it("sıradan bağımsızdır", () => {
    const a = rgb("oklch(0.22 0.006 65)");
    const b = rgb("oklch(0.985 0.003 95)");
    expect(contrastRatio(a, b)).toBeCloseTo(contrastRatio(b, a), 10);
  });

  /**
   * Açık temanın ana metin ikilisi. Sayı düşerse palet regresyona girmiştir —
   * bu testin işi o düşüşü sessiz bırakmamak.
   */
  it("açık tema gövde metni AAA taşır", () => {
    const ratio = contrastRatio(rgb("oklch(0.22 0.006 65)"), rgb("oklch(0.985 0.003 95)"));
    expect(ratio).toBeGreaterThan(15);
    expect(gradeContrast(ratio)).toBe("AAA");
  });

  it("ikincil metin AA eşiğini geçer", () => {
    const ratio = contrastRatio(rgb("oklch(0.52 0.008 65)"), rgb("oklch(0.985 0.003 95)"));
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });
});

describe("relativeLuminance", () => {
  it("0–1 aralığında ve monotondur", () => {
    expect(relativeLuminance(rgb("oklch(0 0 0)"))).toBeCloseTo(0, 6);
    expect(relativeLuminance(rgb("oklch(1 0 0)"))).toBeCloseTo(1, 6);
    expect(relativeLuminance(rgb("oklch(0.7 0 0)"))).toBeGreaterThan(
      relativeLuminance(rgb("oklch(0.4 0 0)")),
    );
  });
});

describe("resolveCssColor", () => {
  /**
   * Tarayıcı yokken (SSR / test) çalışmaz — ama PATLAMAMALI ve sahte renk
   * uydurmamalı. Sayfa bu null'ı "—" olarak gösterir.
   */
  it("canvas olmayan ortamda null döner", () => {
    expect(resolveCssColor("oklch(0.551 0.260 292.1)")).toBeNull();
    expect(resolveCssColor("")).toBeNull();
  });
});

describe("gradeContrast", () => {
  it("WCAG eşiklerini uygular", () => {
    expect(gradeContrast(21)).toBe("AAA");
    expect(gradeContrast(7)).toBe("AAA");
    expect(gradeContrast(4.5)).toBe("AA");
    expect(gradeContrast(3)).toBe("AA-large");
    expect(gradeContrast(2.9)).toBe("fail");
  });
});
