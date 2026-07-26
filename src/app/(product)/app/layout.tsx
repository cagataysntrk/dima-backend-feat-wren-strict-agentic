import type { Metadata } from "next";
import { ProductProviders } from "@/lib/providers";

export const metadata: Metadata = {
  title: "Uygulama",
  robots: { index: false, follow: false },
};

export default function ProductLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="h-dvh overflow-hidden">
      <ProductProviders>{children}</ProductProviders>
    </div>
  );
}
