import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "dima — Veriyle Konuş",
  description: "Doğal dille sor, güvenilir SQL ve rapor al.",
  // OG görseli (app/opengraph-image.tsx) Next tarafından otomatik eklenir.
  openGraph: {
    title: "dima — Veriyle Konuş",
    description: "deterministic · intelligent · modeled · agentic",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="tr"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="h-full flex flex-col overflow-hidden">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
