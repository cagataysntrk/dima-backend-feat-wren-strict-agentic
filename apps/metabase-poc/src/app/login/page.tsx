import type { Metadata } from "next";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { BrandMark } from "@dima/ui/brand/BrandMark";
import { LoginForm } from "./LoginForm";

export const metadata: Metadata = { title: "Giriş" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const session = await auth.api.getSession({ headers: await headers() });
  const { next } = await searchParams;
  const target = next?.startsWith("/app") ? next : "/app";
  if (session) redirect(target);
  return (
    <main className="grid min-h-screen place-items-center px-4">
      <div className="w-full max-w-sm space-y-8">
        <div className="space-y-2 text-center">
          <BrandMark size="md" className="justify-center" />
          <p className="text-sm text-muted-foreground">Panolarınıza erişmek için giriş yapın.</p>
        </div>
        <LoginForm next={target} />
      </div>
    </main>
  );
}
