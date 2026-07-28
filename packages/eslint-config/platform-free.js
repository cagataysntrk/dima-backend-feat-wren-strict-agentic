import { defineConfig } from "eslint/config";

import { library } from "./library.js";
import { platformFree } from "./boundaries.js";

/**
 * Platformdan bağımsız paketler için: library tabanı + React/DOM/Node yasağı.
 * Kullananlar: @dima/contracts, @dima/domain.
 *
 * KAPSAM `src/**` — yalnız yayınlanan kod. Paketin `scripts/` altındaki
 * geliştirici araçları (codegen gibi) Node API'lerine meşru şekilde ihtiyaç
 * duyar; onlar paketin dışa açtığı yüzeyin parçası değil, hiçbir zaman
 * tarayıcıya veya React Native'e gitmez.
 *
 * NOT — glob PAKETE GÖRELİ, kök-göreli DEĞİL. ESLint desenleri çalıştığı
 * dizine göre çözer ve her paket kendi dizininde lint olur; "packages/x/**"
 * gibi kök-göreli bir desen sessizce hiçbir şeyle eşleşmez. "src/**" doğru
 * olan.
 */
export default defineConfig([
  ...library,
  ...platformFree.map((config) => ({ ...config, files: ["src/**/*.{ts,tsx}"] })),
  {
    name: "dima/package-scripts",
    files: ["scripts/**/*.{js,mjs}"],
    languageOptions: {
      globals: {
        process: "readonly",
        console: "readonly",
        fetch: "readonly",
        URL: "readonly",
        Buffer: "readonly",
      },
    },
  },
]);
