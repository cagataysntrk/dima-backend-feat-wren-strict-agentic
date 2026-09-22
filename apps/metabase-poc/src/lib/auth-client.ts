"use client";

import { createAuthClient } from "better-auth/react";
import { organizationClient } from "better-auth/client/plugins";

// Same-origin: Better Auth is mounted at /api/auth/* in this app.
export const authClient = createAuthClient({
  plugins: [organizationClient()],
});
