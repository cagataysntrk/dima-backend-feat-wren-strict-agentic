import type { Metadata } from "next";
import { Plus_Jakarta_Sans, JetBrains_Mono, Playfair_Display } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale } from "next-intl/server";
import "./globals.css";
import { Providers } from "@/lib/providers";

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
  title: "dima — Veriyle Konuş",
  description: "Doğal dille sor, güvenilir SQL ve rapor al.",
  // OG görseli (app/opengraph-image.tsx) Next tarafından otomatik eklenir.
  openGraph: {
    title: "dima — Veriyle Konuş",
    description: "deterministic · intelligent · modeled · agentic",
    type: "website",
  },
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
      className={`${sans.variable} ${mono.variable} ${display.variable} h-full antialiased`}
    >
      {/* suppressHydrationWarning: browser extensions (Grammarly vb.) <body>'ye
          data-gr-* attribute enjekte eder; bu yalnız o attribute farkını susturur. */}
      <body suppressHydrationWarning className="h-full flex flex-col overflow-hidden">
        <NextIntlClientProvider>
          <Providers>{children}</Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
