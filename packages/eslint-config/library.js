import js from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

import { crossWorkspace } from "./boundaries.js";

/**
 * TS paketleri için taban. React/Next kuralları YOK.
 *
 * Platformdan bağımsızlık (React/DOM/Node yasağı) BU KATMANDA DEĞİL —
 * `platform-free` ayrı bir katman, çünkü api-client bu tabanı kullanıyor
 * ama tarayıcı API'lerine erişmesi meşru.
 */
export const library = defineConfig([
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...crossWorkspace,
  globalIgnores(["dist/**"]),
]);

export default library;
