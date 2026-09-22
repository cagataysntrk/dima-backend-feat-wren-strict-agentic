import Link from "next/link";
import { BrandMark } from "@dima/ui/brand/BrandMark";
import { Button } from "@dima/ui/primitives/button";

export default function NotFound() {
  return (
    <main className="marketing-grid flex min-h-screen items-center justify-center px-5">
      <div className="max-w-xl text-center">
        <BrandMark size="xl" />
        <p className="mt-10 font-mono text-xs uppercase tracking-[0.2em] text-brand">404</p>
        <h1 className="mt-4 font-display text-5xl">Bu sayfa bulunamadı.</h1>
        <p className="mt-5 text-muted-foreground">Adres değişmiş veya sayfa artık mevcut olmayabilir.</p>
        <Button asChild variant="brand" className="mt-8"><Link href="/">Ana sayfaya dön</Link></Button>
      </div>
    </main>
  );
}
