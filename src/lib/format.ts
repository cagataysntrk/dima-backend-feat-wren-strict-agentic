// Kolon adından birim çıkarımı + Türkçe sayı biçimlendirme.
// Hem tabloda hem grafiklerde (eksen/tooltip/KPI/heatmap) kullanılır.

export interface Unit {
  suffix: string;
  scale?: number; // değeri gösterime çevirirken çarpan (oran 0-1 → %)
}

// Sıra önemli: parasal/özel kontroller genel eklerden ÖNCE gelir.
export function unitFor(col: string): Unit | null {
  if (!col) return null; // ölçü yok (ör. 0 satır) → birim yok, çökme
  const c = col.toLowerCase();
  if (c.includes("yil")) return null; // yıl (kurulum_yili) — grupsuz tam sayı
  if (c === "kar" || /(tutar|ciro|maliyet|fiyat|katki|gelir|kazanc)/.test(c)) return { suffix: "₺" };
  if (/_kwh$/.test(c) || c.includes("enerji")) return { suffix: "kWh" };
  if (/_lt$|_litre$/.test(c) || c.includes("su_") || c.includes("_su")) return { suffix: "L" };
  if (/_dakika$/.test(c) || /(durus|calisma|planlanan)/.test(c)) return { suffix: "dk" };
  if (/_gl$/.test(c) || c.includes("konsantrasyon")) return { suffix: "g/L" };
  if (c === "gramaj") return { suffix: "g/m²" };
  if (/_cm$/.test(c)) return { suffix: "cm" };
  if (/yuzde|orani/.test(c)) return { suffix: "%" }; // zaten yüzde ölçeğinde
  if (/(^oee$|oee|kullanilabilirlik|performans|kalite)/.test(c)) return { suffix: "%", scale: 100 }; // oran 0-1
  if (/_kg$/.test(c) || c.includes("agirlik") || c.includes("kapasite") || c.includes("tonaj"))
    return { suffix: "kg" };
  return null;
}

function withUnit(s: string, u: Unit | null): string {
  if (!u) return s;
  if (u.suffix === "%") return `%${s}`; // Türkçe: yüzde işareti önde
  if (u.suffix === "₺") return `${s} ₺`;
  return `${s} ${u.suffix}`;
}

// Tam biçim (tablo hücresi, tooltip, KPI).
export function fmtValue(v: unknown, col: string): string {
  if (v === null || v === undefined) return "—";
  const n = typeof v === "number" ? v : Number(v);
  if (Number.isNaN(n)) return String(v);
  if (col.toLowerCase().includes("yil")) return String(Math.round(n));
  const u = unitFor(col);
  const scaled = u?.scale ? n * u.scale : n;
  const s = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 2 }).format(scaled);
  return withUnit(s, u);
}

// Kısa biçim (eksen etiketi) — büyük sayılarda compact (1,2 Mn).
export function fmtAxis(v: unknown, col: string): string {
  const n = typeof v === "number" ? v : Number(v);
  if (Number.isNaN(n)) return String(v ?? "");
  const u = unitFor(col);
  const scaled = u?.scale ? n * u.scale : n;
  const s = new Intl.NumberFormat("tr-TR", {
    notation: Math.abs(scaled) >= 10000 ? "compact" : "standard",
    maximumFractionDigits: 1,
  }).format(scaled);
  return withUnit(s, u);
}

// Sadece birim eki (eksen başlığı vb.).
export function unitSuffix(col: string): string {
  const u = unitFor(col);
  return u ? u.suffix : "";
}
