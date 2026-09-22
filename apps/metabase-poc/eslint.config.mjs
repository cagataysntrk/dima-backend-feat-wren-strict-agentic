import { defineConfig, globalIgnores } from "eslint/config";
import next from "@dima/eslint-config/next";

const eslintConfig = defineConfig([
  ...next,
  // Vendored shadcn/ui primitives (copied from apps/web) — upstream code, not linted.
  globalIgnores(["src/components/ui/**"]),
]);

export default eslintConfig;
