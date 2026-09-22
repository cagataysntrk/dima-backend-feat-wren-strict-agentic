import type { Metadata } from "next";
import Link from "next/link";
import { BrandLockup, BrandMark } from "@dima/ui/brand/BrandMark";

export const metadata: Metadata = {
  title: "dima — marka",
  description: "dima wordmark: deterministic · intelligent · modeled · agentic.",
};

export default function BrandPage() {
  return (
    <main className="flex-1 overflow-auto">
      <div className="mx-auto max-w-3xl px-6 py-10">
        <Link
          href="/app"
          className="font-mono text-[11px] tracking-wider text-neutral-400 transition-colors hover:text-foreground"
        >
          ← dima
        </Link>

        {/* Hero: animated wordmark */}
        <section className="mt-6 flex flex-col items-center py-16">
          <BrandMark size="xl" animate interpunct pillars />
          <p
            lang="en"
            className="mt-10 font-mono text-[11px] uppercase tracking-[0.25em] text-neutral-400"
          >
            deterministic · intelligent · modeled · agentic
          </p>
          <p className="mt-3 max-w-md text-center text-xs leading-relaxed text-neutral-500">
            Dört harf, dört güvence. Harflerin üzerine gelin — her biri
            mimarideki karşılığını söyler.
          </p>
        </section>

        {/* Letter-by-letter expansion */}
        <section className="mt-8">
          <h2 className="mb-3 font-mono text-[11px] uppercase tracking-wider text-neutral-400">
            Harf Harf
          </h2>
          <BrandLockup />
        </section>

        {/* Variants */}
        <section className="mt-10">
          <h2 className="mb-3 font-mono text-[11px] uppercase tracking-wider text-neutral-400">
            Varyantlar
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="flex flex-col items-center justify-center gap-4 border border-hairline p-8">
              <BrandMark size="md" />
              <span className="font-mono text-[10px] uppercase tracking-wide text-neutral-400">
                varsayılan — accent i-noktası
              </span>
            </div>
            <div className="flex flex-col items-center justify-center gap-4 bg-neutral-950 p-8 text-neutral-100">
              <BrandMark size="md" ink />
              <span className="font-mono text-[10px] uppercase tracking-wide text-neutral-500">
                ink — tek renk, koyu zemin
              </span>
            </div>
            <div className="flex flex-col items-center justify-center gap-4 border border-hairline p-8">
              <BrandMark size="sm" interpunct />
              <span className="font-mono text-[10px] uppercase tracking-wide text-neutral-400">
                kompakt + interpunct — panel / navigasyon
              </span>
            </div>
            <div className="flex flex-col items-center justify-center gap-4 border border-hairline p-8">
              <BrandMark size="md" ink />
              <span className="font-mono text-[10px] uppercase tracking-wide text-neutral-400">
                ink — tek renk, açık zemin
              </span>
            </div>
          </div>
        </section>

        {/* Usage rules */}
        <section className="mt-10 mb-6">
          <h2 className="mb-3 font-mono text-[11px] uppercase tracking-wider text-neutral-400">
            Kullanım
          </h2>
          <ul className="space-y-1.5 text-sm text-neutral-600 dark:text-neutral-400">
            <li>
              Ürün adı her zaman küçük harf: <strong>dima</strong>.
            </li>
            <li>
              Tek vurgu rengi <span className="text-brand">accent</span>{" "}
              (amber)&apos;dır — provenance rozetleri ve imleçle aynı dil;
              i&apos;nin noktası bu renktedir.
            </li>
            <li>
              Tek renk gereken yerlerde (favicon, e-posta altbilgisi){" "}
              <code className="border border-hairline px-1 py-0.5 font-mono text-xs">
                ink
              </code>{" "}
              varyantı kullanılır.
            </li>
            <li>
              Açılım metni interpunct ile yazılır: deterministic · intelligent ·
              modeled · agentic. Ayrıntı:{" "}
              <code className="border border-hairline px-1 py-0.5 font-mono text-xs">
                docs/branding.md
              </code>
              .
            </li>
          </ul>
        </section>
      </div>
    </main>
  );
}
