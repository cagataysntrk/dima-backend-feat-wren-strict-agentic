import { defineConfig } from "eslint/config";

import { library } from "./library.js";
import { platformFree } from "./boundaries.js";

/**
 * Platformdan bağımsız paketler için: library tabanı + React/DOM/Node yasağı.
 * Kullananlar: @dima/contracts, @dima/domain.
 */
export default defineConfig([...library, ...platformFree]);
