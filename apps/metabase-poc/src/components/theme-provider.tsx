// POC COPY of apps/web/src/components/theme-provider.tsx — unchanged. Follow-up: extract to packages/ui.
"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ComponentProps } from "react";

/** Runtime light/dark theming via a `.dark` class on <html>, overriding OS. */
export function ThemeProvider({
  children,
  ...props
}: ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
