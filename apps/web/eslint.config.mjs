import { defineConfig, globalIgnores } from "eslint/config";
import next from "@dima/eslint-config/next";

const eslintConfig = defineConfig([
  ...next,
  globalIgnores([
    // Vendored shadcn/ui primitives + generated hooks — upstream code, not linted
    // (they trip the strict React-Compiler rules; we don't hand-maintain them).
    "src/components/ui/**",
    "src/hooks/use-mobile.ts",
  ]),
]);

export default eslintConfig;
