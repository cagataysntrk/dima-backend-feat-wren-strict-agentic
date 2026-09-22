import Link from "next/link";
import { BrandMark } from "@dima/ui/brand/BrandMark";
import { Button } from "@dima/ui/primitives/button";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center px-5">
      <div className="max-w-md text-center">
        <BrandMark size="md" />
        <p className="mt-8 font-mono text-xs tracking-[0.2em] text-brand">404</p>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight">Bu sayfa bulunamadı.</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          Adres değişmiş, içerik çöp kutusuna taşınmış ya da başka bir şirkete ait olabilir.
        </p>
        <Button asChild variant="brand" className="mt-7">
          <Link href="/app">Panolara dön</Link>
        </Button>
      </div>
    </main>
  );
}
