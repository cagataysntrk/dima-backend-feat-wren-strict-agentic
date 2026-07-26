import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hesap",
  robots: { index: false, follow: false },
};

export default function AuthLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
