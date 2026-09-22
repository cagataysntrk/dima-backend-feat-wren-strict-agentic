import { defineConfig, globalIgnores } from "eslint/config";
import next from "@dima/eslint-config/next";

const eslintConfig = defineConfig([
  ...next,
  // Vendored shadcn/ui primitives + generated hook (copied from apps/web, which
  // ignores the same paths) — upstream code, not linted.
  globalIgnores(["src/components/ui/**", "src/hooks/use-mobile.ts"]),
]);

export default eslintConfig;
