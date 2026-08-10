#!/usr/bin/env node
/**
 * Backend sözleşmesini TypeScript'e çevirir.
 *
 * SORUN: `types.ts` bugüne kadar backend'in `app/schemas.py`'siyle ELLE
 * hizalandı. Bu canlı bir kayma kaynağı — bu oturumda backend'e eklenen
 * `ConversationOut`, `NextStep`, `Recommendation`, `UploadRequest` gibi
 * modeller frontend'de hiç yoktu ve kimse fark etmemişti.
 *
 * İKİ KİPİ VAR:
 *   codegen         şemayı çıkarır + TS üretir (geliştirici çalıştırır)
 *   codegen --check ürettiğini commit'lenmişle karşılaştırır, farklıysa PATLAR
 *
 * İkincisi asıl değer: CI'da çalışınca "backend değişti, frontend güncellenmedi"
 * durumu sessiz kalmaz.
 *
 * ŞEMA NEREDEN:
 *   1. DIMA_BACKEND_URL verilmişse → GET <url>/openapi.json (backend çalışıyorsa
 *      en doğru kaynak; tüm yollar dahil)
 *   2. Yoksa DIMA_BACKEND_PATH (varsayılan ../backend) → app/schemas.py'den
 *      python ile çıkarılır. DB bağımlılıkları gerekmez.
 */

import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SCHEMA = resolve(root, "schema/openapi.json");
const OUTPUT = resolve(root, "src/generated.ts");
const check = process.argv.includes("--check");

/**
 * Backend kaynağı AÇIKÇA verilir — varsayılan bir komşu-dizin yolu YOK.
 *
 * Başta komşu backend yolu varsayılanı vardı ve yanlış alarm üretti:
 * geliştiricinin yerel backend kopyası herhangi bir dalda ya da commit'te
 * olabilir (bu makinede 100 commit geriydi), dolayısıyla ona göre "kaymış"
 * demek doğru bilgi taşımıyor. Karşılaştırma ancak referansın ne olduğunu
 * bilerek anlamlı.
 */
const backendUrl = process.env.DIMA_BACKEND_URL;
const backendPath = process.env.DIMA_BACKEND_PATH
  ? resolve(process.cwd(), process.env.DIMA_BACKEND_PATH)
  : null;

// --- 1. Şemayı al -----------------------------------------------------------

/**
 * Şemayı backend'den alır. Erişilemiyorsa `null` döner.
 *
 * `--check` kipinde bu ayrım önemli: CI'da backend repo'su yoktur. Orada
 * "atla ve geç" demek, savaştığımız sessiz başarısızlık biçimi olurdu; bunun
 * yerine iki kademeli kontrol yapıyoruz (aşağıya bak).
 */
async function fetchSchema() {
  if (backendUrl) {
    const res = await fetch(new URL("/openapi.json", backendUrl));
    if (!res.ok) throw new Error(`openapi.json alınamadı: ${res.status}`);
    return JSON.stringify(await res.json(), null, 2) + "\n";
  }

  if (!backendPath || !existsSync(backendPath)) {
    if (check) return null; // kademe 2'ye düş
    throw new Error(
      `Backend kaynağı verilmedi.\n\n` +
        `  DIMA_BACKEND_PATH=../../backend bun run codegen\n` +
        `  DIMA_BACKEND_URL=http://localhost:8000 bun run codegen\n\n` +
        `Backend deposu güncel bir dalda olmalı — eski bir kopyadan üretmek\n` +
        `sözleşmeyi geriye alır.`,
    );
  }

  return execFileSync(
    "python3",
    [resolve(root, "scripts/extract-schema.py"), backendPath],
    { encoding: "utf8", maxBuffer: 32 * 1024 * 1024 },
  );
}

// --- 2. TS üret -------------------------------------------------------------

function generateTypes() {
  const generated = execFileSync(
    "bunx",
    ["openapi-typescript", SCHEMA, "--root-types", "--root-types-no-schema-prefix"],
    { cwd: root, encoding: "utf8", maxBuffer: 32 * 1024 * 1024 },
  );

  return (
    `// ÜRETİLMİŞ DOSYA — ELLE DÜZENLEME.\n` +
    `//\n` +
    `// Kaynak: dima-backend app/schemas.py → schema/openapi.json\n` +
    `// Yenile: bun run --filter @dima/contracts codegen\n` +
    `// CI, bu dosyanın güncel olduğunu 'codegen:check' ile doğrular.\n` +
    `//\n` +
    `// SINIRI BİL: backend bazı alanları \`dict[str, Any]\` olarak tiplemiş\n` +
    `// (kpi, interpretation, cube_query). Onlar burada Record<string, unknown>\n` +
    `// olarak çıkar — işe yaramaz. O alanların KULLANILABİLİR şekilleri\n` +
    `// src/types.ts'te elle yazılıdır ve orada kalmalıdır. Codegen ancak\n` +
    `// backend'in tiplediği kadar iyidir.\n` +
    `\n` +
    generated
  );
}

// --- 3. Yaz ya da karşılaştır ------------------------------------------------

const schema = await fetchSchema();
const previousSchema = existsSync(SCHEMA) ? readFileSync(SCHEMA, "utf8") : "";
const previousTypes = existsSync(OUTPUT) ? readFileSync(OUTPUT, "utf8") : "";

if (check) {
  /**
   * İKİ KADEME:
   *
   *   1. Backend erişilebilirse — commit'lenmiş şema backend'le uyuşuyor mu?
   *      Asıl kontrol bu: "backend değişti, frontend güncellenmedi" burada
   *      yakalanır.
   *
   *   2. Erişilemiyorsa (CI) — commit'lenmiş ŞEMADAN üretilen TS, commit'lenmiş
   *      TS ile aynı mı? Backend kaymasını göremez ama `generated.ts`'in elle
   *      düzenlenmiş olmasını yakalar. Kontrolün neyi KAPSAMADIĞI açıkça
   *      yazdırılır — sessizce geçmek, kontrolü hiç koymamaktan kötüdür.
   */
  const types = generateTypes(); // commit'lenmiş şemadan
  if (previousTypes !== types) {
    throw new Error(
      `generated.ts, commit'lenmiş şemayla uyuşmuyor — elle düzenlenmiş olabilir.\n\n` +
        `  bun run --filter @dima/contracts codegen\n\n` +
        `çalıştırıp sonucu commit'le.`,
    );
  }

  if (schema === null) {
    console.log(
      "✓ generated.ts commit'lenmiş şemayla tutarlı\n" +
        "! backend KONTROL EDİLMEDİ (repo/URL yok). Backend kayması bu koşuda\n" +
        "  görülmez; DIMA_BACKEND_PATH veya DIMA_BACKEND_URL verilirse görülür.",
    );
  } else if (schema !== previousSchema) {
    throw new Error(
      `Sözleşme KAYMIŞ: backend değişmiş ama commit'lenmiş şema eski.\n\n` +
        `  bun run --filter @dima/contracts codegen\n\n` +
        `çalıştırıp sonucu commit'le.`,
    );
  } else {
    console.log("✓ sözleşme backend ile güncel");
  }
} else {
  if (schema === null) throw new Error("şema alınamadı");
  writeFileSync(SCHEMA, schema);
  writeFileSync(OUTPUT, generateTypes());
  const count = Object.keys(JSON.parse(schema).components?.schemas ?? {}).length;
  console.log(`✓ ${count} şema → ${OUTPUT.replace(root + "/", "")}`);
}
