import type { Metadata } from "next";
import { ProductProviders } from "@/lib/providers";

export const metadata: Metadata = {
  title: "Ayarlar",
  robots: { index: false, follow: false },
};

export default function SettingsLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="h-dvh overflow-auto">
      <ProductProviders>{children}</ProductProviders>
    </div>
  );
}
