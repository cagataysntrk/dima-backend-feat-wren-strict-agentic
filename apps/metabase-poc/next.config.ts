import type { NextConfig } from "next";

// Metabase is reached ONLY from server code (src/server/metabase/*). Its URL and
// API keys are server-side env vars and never reach the browser.
const nextConfig: NextConfig = {
  transpilePackages: ["@dima/contracts", "@dima/domain", "@dima/ui"],
  // pg is a Node-native driver; keep it out of the server bundle.
  serverExternalPackages: ["pg"],
  poweredByHeader: false,
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },
};

export default nextConfig;
