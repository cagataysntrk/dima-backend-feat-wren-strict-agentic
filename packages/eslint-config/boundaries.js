import { defineConfig } from "eslint/config";

/**
 * Monorepo bağımlılık yönü — DOKÜMANDA DEĞİL, LINT'TE.
 *
 * Bir mimari kural yalnız yazıldığı yerde yaşarsa ölür. Bunlar CI'da patlar.
 *
 *   apps/*  →  ui-*  →  tokens
 *      ↓
 *   domain · api-client · contracts     ← React yok, DOM yok, Node yok
 *
 * DİKKAT — burada `files` globu YOK, bilerek. ESLint `files` desenlerini
 * çalıştığı dizine göre çözer; her paket kendi dizininde lint olduğu için
 * "packages/domain/**" gibi kök-göreli bir desen HİÇ eşleşmez (sessizce
 * devre dışı kalır). Bunun yerine kurallar katman olarak dışa verilir ve
 * her paket hangi katmanı istediğini kendi config'inde seçer.
 */

/** Her yerde geçerli: workspace sınırını delen import'lar. */
export const crossWorkspace = defineConfig([
  {
    name: "dima/cross-workspace-imports",
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              // 1. packages → apps import edemez (paket tüketicisine bağımlı olamaz)
              // 2. app → app import edemez (göreli sıçrama build sınırını deler)
              group: ["**/apps/*/src/**", "../../*/src/**", "../../../*/**"],
              message:
                "Workspace sınırını göreli yolla geçme. Ortak parçayı packages/ altına çıkar ve @dima/* olarak import et.",
            },
            {
              // 3. Derin import: paketin yüzeyi package.json exports ile sınırlı
              group: ["@dima/*/src/*", "@dima/*/dist/*"],
              message:
                "Derin import yapma. Paketin dışarı açtığı yüzey package.json exports ile sınırlıdır.",
            },
          ],
        },
      ],
    },
  },
]);

/**
 * Yalnız platformdan bağımsız paketlerin (contracts, domain) açtığı katman.
 *
 * Bu katmanı kullanmak "ben React/DOM/Node tanımıyorum" beyanıdır. Mobil
 * (React Native) tarafı bu paketleri birebir alacak; içine `window` girdiği
 * an alamaz. api-client BU KATMANI KULLANMAZ — o bir taşıma katmanı ve
 * tarayıcı API'lerine erişmesi meşru.
 */
export const platformFree = defineConfig([
  {
    name: "dima/platform-free",
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["react", "react-dom", "react/*", "next", "next/*"],
              message:
                "Bu paket platformdan bağımsız — React Native tarafı da kullanacak.",
            },
            {
              group: ["fs", "path", "node:*"],
              message:
                "Bu paket Node API'si kullanamaz — tarayıcıda ve RN'de de çalışmalı.",
            },
          ],
        },
      ],
      "no-restricted-globals": [
        "error",
        { name: "window", message: "Bu paket DOM tanımaz." },
        { name: "document", message: "Bu paket DOM tanımaz." },
        { name: "localStorage", message: "Bu paket DOM tanımaz." },
        { name: "navigator", message: "Bu paket DOM tanımaz." },
      ],
    },
  },
]);
