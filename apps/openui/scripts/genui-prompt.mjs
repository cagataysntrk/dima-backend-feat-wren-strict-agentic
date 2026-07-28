#!/usr/bin/env node
/**
 * Sistem istemini üretir ve dima için DÜZELTİR.
 *
 * OpenUI'ın taban istemi şu kuralı içeriyor:
 *
 *     - When asked about data, generate realistic/plausible data
 *
 * Bu, dima'nın deterministik-önce vaadinin tam tersi. `PromptOptions` yalnız
 * kural EKLEYEBİLİR, yerleşik olanı kaldıramaz — yani biz "asla veri uydurma"
 * dediğimizde üretilen istem modele aynı anda hem uydurmasını hem uydurmamasını
 * söylüyor. Çelişkili istem, en iyi ihtimalle öngörülemez davranış demek.
 *
 * Bu betik o satırı üretimden SONRA siler.
 *
 * SESSİZ BAŞARISIZLIK KORUMASI — asıl değeri burada:
 *   1. Kural satırı bulunamazsa PATLAR. OpenUI ifadeyi değiştirmiş olabilir;
 *      sessizce geçmek, kuralın hâlâ orada olduğunu fark etmemek demektir.
 *   2. dima kuralları isteme girmemişse PATLAR. CLI, istem seçeneklerini
 *      kütüphane modülünden okur; yanlış yere koyulursa hiçbir uyarı vermeden
 *      yok sayar ve model kurallarımızı hiç görmez.
 *
 * İkisi de "çalışıyor gibi görünüp çalışmama" biçimleri. Test edilmezse
 * fark edilmezler.
 */

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const LIBRARY = "./src/lib/library.tsx";
const PROMPT = resolve(root, "src/generated/system-prompt.txt");

// OpenUI'ın kaldıramadığımız yerleşik kuralı.
const FABRICATION_RULE = "- When asked about data, generate realistic/plausible data";
// dima kurallarının isteme geçtiğini kanıtlayan işaret.
const DIMA_MARKER = "ASLA sayı";

execFileSync("bunx", ["@openuidev/cli@latest", "generate", LIBRARY, "--out", PROMPT], {
  cwd: root,
  stdio: "inherit",
});

const original = readFileSync(PROMPT, "utf8");

if (!original.includes(DIMA_MARKER)) {
  throw new Error(
    `dima kuralları üretilen isteme GİRMEMİŞ ("${DIMA_MARKER}" bulunamadı).\n` +
      `CLI istem seçeneklerini kütüphane modülünden okur — ${LIBRARY} dosyasının\n` +
      `\`promptOptions\` dışa aktarımı yaptığını doğrula. Bu sessiz bir hatadır:\n` +
      `üretim çalışır ama model kurallarımızı hiç görmez.`,
  );
}

if (!original.includes(FABRICATION_RULE)) {
  throw new Error(
    `Kaldırılacak kural bulunamadı:\n  ${FABRICATION_RULE}\n\n` +
      `OpenUI ifadeyi değiştirmiş olabilir. Üretilen istemi oku, veri uydurmayı\n` +
      `teşvik eden yeni ifadeyi bul ve bu betikteki sabiti güncelle. Bu kontrolü\n` +
      `atlamak, kuralın sessizce geri gelmesi demektir.`,
  );
}

const patched = original
  .split("\n")
  .filter((line) => line.trim() !== FABRICATION_RULE)
  .join("\n");

writeFileSync(PROMPT, patched);

/**
 * Yamalı istemi TS modülü olarak da yaz.
 *
 * Bu şart: `/api/chat` istemi `generateSystemPrompt()` ile RUNTIME'da yeniden
 * üretirse, silinen kural geri gelir — yamanın hiçbir anlamı kalmaz. Rota
 * yalnız bu modülü okumalı. Ayrıca .txt import etmek Next'te çalışmadığı için
 * TS modülü her runtime'da güvenli.
 */
writeFileSync(
  resolve(root, "src/generated/system-prompt.ts"),
  `// ÜRETİLMİŞ DOSYA — elle düzenleme. Kaynak: scripts/genui-prompt.mjs\n` +
    `//\n` +
    `// Bu, OpenUI'ın ürettiği istemin YAMALANMIŞ halidir: veri uydurmayı\n` +
    `// teşvik eden yerleşik kural çıkarılmıştır. /api/chat istemi runtime'da\n` +
    `// yeniden ÜRETMEZ, bu sabiti okur — aksi halde kural geri gelir.\n` +
    `export const systemPrompt = ${JSON.stringify(patched)};\n`,
);

console.log(
  `✓ istem üretildi · veri-uydurma kuralı silindi · dima kuralları doğrulandı (${patched.split("\n").length} satır)`,
);
