import { defineConfig, globalIgnores } from "eslint/config";
import next from "@dima/eslint-config/next";

// Vendored shadcn/ui primitives are upstream code; the rest is ours.
export default defineConfig([...next, globalIgnores(["src/primitives/**", "src/use-mobile.ts"])]);
