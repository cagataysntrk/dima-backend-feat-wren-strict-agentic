import type { Metadata } from "next";
import { ProductProviders } from "@/lib/providers";
import { SecondaryShell } from "@/components/shell/SecondaryShell";

export const metadata: Metadata = {
  title: "Ayarlar",
  robots: { index: false, follow: false },
};

export default function SettingsLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="h-dvh overflow-hidden">
      <ProductProviders>
        <SecondaryShell>{children}</SecondaryShell>
      </ProductProviders>
    </div>
  );
}
