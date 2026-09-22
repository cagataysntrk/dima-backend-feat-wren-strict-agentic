"use client";

import Link from "next/link";
import { BrandMark } from "@dima/ui/brand/BrandMark";
import { Button } from "@dima/ui/primitives/button";

// Route-level error boundary: /app içinde çalışan bir şey fırlatırsa boş
// ekrana düşmek yerine kurtarılabilir bir sayfa göster.
export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="marketing-grid flex min-h-screen items-center justify-center px-5">
      <div className="max-w-xl text-center">
        <BrandMark size="xl" />
        <h1 className="mt-10 font-display text-5xl">Bir şeyler ters gitti.</h1>
        <p className="mt-5 text-muted-foreground">
          Beklenmeyen bir hata oluştu. Tekrar deneyebilir veya ana sayfaya dönebilirsiniz.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Button variant="brand" onClick={reset}>
            Tekrar dene
          </Button>
          <Button asChild variant="outline">
            <Link href="/">Ana sayfaya dön</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
