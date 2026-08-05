import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // 🔴 `_` ÖNEKİ BİR NİYET BEYANIDIR — "bunu bilerek kullanmıyorum".
      // Ölçülen kusur: `const { [dim]: _omit, ...rest } = r` (bir alanı DÜŞÜRMENİN
      // kanonik JS deyimi) uyarı üretiyordu. Uyarıyı susturmanın iki yolu vardı:
      // deyimi bozmak ya da niyeti tanımak. İkincisi doğrudur — *bir dil deyimini
      // bir linter kuralı için eğip bükmek, kuralı dilin önüne koymaktır.*
      // ⚠ Kural GEVŞETİLMEDİ: önek TAŞIMAYAN kullanılmayan değişken hâlâ uyarıdır
      // (ve FAZ 6'da tam da öyle bir ölü fonksiyon yakalandı: `dimToFilter`).
      "@typescript-eslint/no-unused-vars": ["warn", {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
        caughtErrorsIgnorePattern: "^_",
        destructuredArrayIgnorePattern: "^_",
        ignoreRestSiblings: true,
      }],
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
