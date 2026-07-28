"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { refresh } from "./api-client";
import { MotionConfig } from "motion/react";
import { ThemeProvider } from "@/components/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";

// Sayfa yenilenince access token memory'den gider; refresh cookie'den (varsa) sessizce
// geri kur → ilk API çağrısı 401 yemeden token hazır olur. /login'de cookie yoksa no-op.
function AuthBootstrap({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    void refresh();
  }, []);
  return <>{children}</>;
}

export function GlobalProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <MotionConfig reducedMotion="user">{children}</MotionConfig>
    </ThemeProvider>
  );
}

export function ProductProviders({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
      }),
  );
  return (
    <QueryClientProvider client={client}>
      <TooltipProvider delayDuration={200}>
        <AuthBootstrap>{children}</AuthBootstrap>
      </TooltipProvider>
      <Toaster />
    </QueryClientProvider>
  );
}
