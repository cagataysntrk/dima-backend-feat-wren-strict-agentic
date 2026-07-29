/**
 * OKLCH → sRGB dönüşümü ve WCAG kontrast oranı.
 *
 * NEDEN VAR: tasarım jetonları globals.css'te oklch olarak yazılı. Stil kılavuzu
 * bunları OKUYUP hex'e çevirebilirse, sayfa bir poster olmaktan çıkıp ÖLÇEN bir
 * alete dönüşür — "bu ikili AA geçiyor mu?" sorusu göz kararı değil hesap olur.
 *
 * Sayı gösteren her şey doğrulanabilir olmalı: `color.test.ts` bilinen değerlerle
 * (beyaz/siyah = 21:1, sRGB primaries) matematiği sabitler.
 */

/** Kanal başına 0–1, gama KODLANMIŞ sRGB (ekranda görünen değer). */
export type Srgb = [number, number, number];

export interface Oklch {
  /** Algısal açıklık, 0–1. */
  l: number;
  /** Kroma, 0–~0.4. */
  c: number;
  /** Ton açısı, derece. */
  h: number;
}

/** `oklch(0.551 0.260 292.1)` → nesne. Tanınmayan biçimde null (sessiz tahmin yok). */
export function parseOklch(input: string): Oklch | null {
  const m = /^oklch\(\s*([\d.]+%?)\s+([\d.]+%?)\s+([-\d.]+)/i.exec(input.trim());
  if (!m) return null;
  const num = (raw: string, pctBase: number): number =>
    raw.endsWith("%") ? (parseFloat(raw) / 100) * pctBase : parseFloat(raw);
  const l = num(m[1], 1);
  const c = num(m[2], 0.4);
  const h = parseFloat(m[3]);
  return Number.isFinite(l) && Number.isFinite(c) && Number.isFinite(h) ? { l, c, h } : null;
}

const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x);

/** sRGB transfer fonksiyonu (doğrusal ışık → kodlanmış). */
function encodeGamma(x: number): number {
  return x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
}

/** Tersi — kodlanmış → doğrusal ışık (parlaklık hesabı doğrusal uzayda yapılır). */
function decodeGamma(x: number): number {
  return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
}

/**
 * OKLCH → sRGB, kanal başına 0–1 (kodlanmış, gamut'a KIRPILMIŞ).
 *
 * Kırpma kasıtlı: gamut dışı bir jeton ekranda zaten kırpılarak gösterilir;
 * kontrast hesabı da kullanıcının gerçekte gördüğü rengi almalı.
 */
export function oklchToSrgb({ l, c, h }: Oklch): Srgb {
  const rad = (h * Math.PI) / 180;
  const a = c * Math.cos(rad);
  const b = c * Math.sin(rad);

  // OKLab → LMS' → LMS (küp)
  const lp = l + 0.3963377774 * a + 0.2158037573 * b;
  const mp = l - 0.1055613458 * a - 0.0638541728 * b;
  const sp = l - 0.0894841775 * a - 1.291485548 * b;
  const L = lp * lp * lp;
  const M = mp * mp * mp;
  const S = sp * sp * sp;

  // LMS → doğrusal sRGB
  const lr = 4.0767416621 * L - 3.3077115913 * M + 0.2309699292 * S;
  const lg = -1.2684380046 * L + 2.6097574011 * M - 0.3413193965 * S;
  const lb = -0.0041960863 * L - 0.7034186147 * M + 1.707614701 * S;

  return [
    clamp01(encodeGamma(lr)),
    clamp01(encodeGamma(lg)),
    clamp01(encodeGamma(lb)),
  ];
}

/** `#rrggbb` (büyük harf). */
export function srgbToHex(color: Srgb): string {
  const hex = color
    .map((v) => Math.round(clamp01(v) * 255).toString(16).padStart(2, "0"))
    .join("");
  return `#${hex.toUpperCase()}`;
}

/** OKLCH → `#rrggbb`. */
export function oklchToHex(color: Oklch): string {
  return srgbToHex(oklchToSrgb(color));
}

/** WCAG 2.1 bağıl parlaklık. */
export function relativeLuminance(color: Srgb): number {
  const [r, g, b] = color.map(decodeGamma);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** WCAG 2.1 kontrast oranı — 1 (aynı) … 21 (siyah/beyaz). Sıra önemsiz. */
export function contrastRatio(a: Srgb, b: Srgb): number {
  const la = relativeLuminance(a);
  const lb = relativeLuminance(b);
  const [hi, lo] = la > lb ? [la, lb] : [lb, la];
  return (hi + 0.05) / (lo + 0.05);
}

// ── CSS değerini tarayıcıya çözdürme ────────────────────────────────────────

let sharedCtx: CanvasRenderingContext2D | null | undefined;

function scratchContext(): CanvasRenderingContext2D | null {
  if (typeof document === "undefined") return null;
  if (sharedCtx === undefined) {
    sharedCtx =
      document.createElement("canvas").getContext("2d", {
        willReadFrequently: true,
      }) ?? null;
  }
  return sharedCtx;
}

/**
 * HERHANGİ bir CSS renk değerini gerçek sRGB'ye çevirir — sözdizimini KENDİMİZ
 * ayrıştırmadan, tarayıcıya boyattırıp pikseli okuyarak.
 *
 * Bu dolambaç zorunlu: jetonlar globals.css'te `oklch()` yazılı olsa da derleme
 * hattı (Lightning CSS) onları `lab()` gibi başka bir gösterime çevirebiliyor,
 * dolayısıyla `getPropertyValue` çalışma anında ne döneceği garanti olmayan bir
 * metin verir. Elle yazılmış her ayrıştırıcı bir gün sessizce null döner —
 * tarayıcının kendi çözümlemesi dönmez.
 *
 * Geçersiz değerde null (siyaha düşüp sahte kontrast raporlamaz).
 */
export function resolveCssColor(value: string): Srgb | null {
  const input = value.trim();
  if (!input) return null;
  const ctx = scratchContext();
  if (!ctx) return null;

  // Geçersiz atama fillStyle'ı DEĞİŞTİRMEZ. İki farklı başlangıçtan deneyip
  // aynı sonuca varmıyorsa değer okunamamıştır.
  ctx.fillStyle = "#000000";
  ctx.fillStyle = input;
  const fromBlack = ctx.fillStyle;
  ctx.fillStyle = "#ffffff";
  ctx.fillStyle = input;
  if (ctx.fillStyle !== fromBlack) return null;

  ctx.clearRect(0, 0, 1, 1);
  ctx.fillRect(0, 0, 1, 1);
  const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
  return [r / 255, g / 255, b / 255];
}

/** WCAG eşiği: gövde metni 4.5, iri metin/arayüz öğesi 3.0. */
export type ContrastGrade = "AAA" | "AA" | "AA-large" | "fail";

export function gradeContrast(ratio: number): ContrastGrade {
  if (ratio >= 7) return "AAA";
  if (ratio >= 4.5) return "AA";
  if (ratio >= 3) return "AA-large";
  return "fail";
}
