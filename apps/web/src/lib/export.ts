// Rapor dışa aktarma — İSTEMCİDE üretilir.
//
// dima-backend'de dışa aktarma ucu YOK (HEAD'de doğrulandı: ne /export ne
// indirme). Ama satırlar zaten tarayıcıda: cevabı çizen veri, dosyayı yazmaya
// da yeter. Böylece Belgeler bugün çalışıyor; backend bir uç eklediğinde
// değişen tek şey blob'u kimin ürettiği olur — belge modeli ve yüzey aynı kalır.
//
// Excel uyumu için CSV: BOM + noktalı virgül. Türkçe Excel ondalık ayracı virgül
// olduğu için alan ayracı da virgül olursa sütunlar kayar; UTF-8 BOM olmadan da
// ş/ğ/ı bozulur. İkisi de "dosyayı açınca doğru görünsün" için zorunlu.

import type { QueryResult } from "@dima/contracts";

const SEP = ";";

function cell(v: unknown): string {
  if (v === null || v === undefined) return "";
  const s = String(v);
  // Ayraç, tırnak ya da satır sonu içeren değer tırnaklanır; içteki tırnak ikilenir.
  return /[";\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function resultToCsv(result: QueryResult): Blob {
  const head = result.columns.map(cell).join(SEP);
  const rows = result.rows.map((r) => result.columns.map((c) => cell(r[c])).join(SEP));
  // \r\n: Excel'in beklediği satır sonu.
  const text = "﻿" + [head, ...rows].join("\r\n");
  return new Blob([text], { type: "text/csv;charset=utf-8" });
}

/** Soru metninden dosya adı — Türkçe karakterler sadeleşir, uzunluk sınırlanır. */
export function fileNameFor(question: string, ext: string): string {
  const base =
    question
      .toLocaleLowerCase("tr-TR")
      .replace(/ğ/g, "g")
      .replace(/ü/g, "u")
      .replace(/ş/g, "s")
      .replace(/ı/g, "i")
      .replace(/ö/g, "o")
      .replace(/ç/g, "c")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 60) || "rapor";
  return `${base}.${ext}`;
}
