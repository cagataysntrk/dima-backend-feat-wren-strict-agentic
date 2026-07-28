import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

import { crossWorkspace } from "./boundaries.js";

/**
 * Next.js uygulamaları için ortak ESLint yapılandırması.
 *
 * Uygulamaya özel yok saymalar (vendor'lanmış shadcn primitifleri gibi) burada
 * DEĞİL, uygulamanın kendi eslint.config.mjs'inde tanımlanır — her uygulamanın
 * vendor'ladığı şey farklı.
 */
export const next = defineConfig([
  ...nextVitals,
  ...nextTs,
  ...crossWorkspace,
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);

export default next;
