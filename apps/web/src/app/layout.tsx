import type { Metadata } from "next";
import { Plus_Jakarta_Sans, JetBrains_Mono, Playfair_Display } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale } from "next-intl/server";
import "./globals.css";
import { GlobalProviders } from "@/lib/providers";

const sans = Plus_Jakarta_Sans({
  variable: "--font-sans",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

const display = Playfair_Display({
  variable: "--font-display",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ??
      (process.env.NODE_ENV === "production"
        ? "https://dima.upcytech.com"
        : "http://localhost:3000"),
  ),
  title: {
    default: "dima — Güvenilir konuşmalı analitik",
    template: "%s | dima",
  },
  description:
    "İşletme verinize doğal dilde sorun; modellenmiş bağlam ve doğrulanmış SQL ile açıklanabilir rapor alın.",
  openGraph: {
    title: "dima — Güvenilir konuşmalı analitik",
    description:
      "İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.",
    type: "website",
    siteName: "dima",
  },
  twitter: { card: "summary_large_image" },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  return (
    <html
      lang={locale}
      suppressHydrationWarning
      className={`${sans.variable} ${mono.variable} ${display.variable} antialiased`}
    >
      {/* suppressHydrationWarning: browser extensions (Grammarly vb.) <body>'ye
          data-gr-* attribute enjekte eder; bu yalnız o attribute farkını susturur. */}
      <body suppressHydrationWarning className="min-h-screen bg-background text-foreground">
        <NextIntlClientProvider>
          <GlobalProviders>{children}</GlobalProviders>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
