import type { Metadata } from "next";
import { ProductProviders } from "@/lib/providers";
import { SecondaryShell } from "@/components/shell/SecondaryShell";

export const metadata: Metadata = {
  title: "Paneller",
  robots: { index: false, follow: false },
};

export default function DashboardsLayout({
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
