"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { startOAuth, type OAuthProvider } from "@dima/api-client";

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="size-4" aria-hidden>
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1Z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.65l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23Z" />
      <path fill="#FBBC05" d="M5.84 14.11a6.6 6.6 0 0 1 0-4.22V7.05H2.18a11 11 0 0 0 0 9.9l3.66-2.84Z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.05l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38Z" />
    </svg>
  );
}
function GitHubIcon() {
  return (
    <svg viewBox="0 0 24 24" className="size-4 fill-foreground" aria-hidden>
      <path d="M12 1C5.92 1 1 5.92 1 12c0 4.86 3.15 8.98 7.52 10.44.55.1.75-.24.75-.53v-1.85c-3.06.67-3.7-1.48-3.7-1.48-.5-1.27-1.22-1.6-1.22-1.6-1-.69.08-.67.08-.67 1.1.08 1.68 1.14 1.68 1.14.98 1.68 2.57 1.2 3.2.92.1-.71.38-1.2.7-1.47-2.44-.28-5.01-1.22-5.01-5.43 0-1.2.43-2.18 1.13-2.95-.11-.28-.49-1.4.11-2.9 0 0 .92-.3 3.02 1.13a10.5 10.5 0 0 1 5.5 0c2.1-1.43 3.02-1.13 3.02-1.13.6 1.5.22 2.62.11 2.9.7.77 1.13 1.75 1.13 2.95 0 4.22-2.58 5.15-5.03 5.42.4.34.74 1 .74 2.02v3c0 .29.2.63.76.52A11 11 0 0 0 23 12c0-6.08-4.92-11-11-11Z" />
    </svg>
  );
}
function AppleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="size-4 fill-foreground" aria-hidden>
      <path d="M16.36 12.68c.02 2.5 2.19 3.33 2.22 3.35-.02.06-.35 1.2-1.15 2.37-.69 1.02-1.4 2.03-2.53 2.05-1.1.02-1.46-.65-2.72-.65-1.26 0-1.66.63-2.7.67-1.09.04-1.92-1.1-2.61-2.11-1.42-2.06-2.5-5.82-1.05-8.36.72-1.26 2.01-2.06 3.41-2.08 1.07-.02 2.07.72 2.72.72.65 0 1.87-.89 3.16-.76.54.02 2.05.22 3.02 1.64-.08.05-1.8 1.05-1.78 3.15M14.3 5.4c.58-.7.97-1.67.86-2.65-.83.03-1.84.55-2.44 1.25-.53.62-1 1.61-.88 2.56.93.07 1.87-.47 2.46-1.16" />
    </svg>
  );
}

const PROVIDERS: { id: OAuthProvider; label: string; icon: React.ReactNode }[] = [
  { id: "google", label: "Google", icon: <GoogleIcon /> },
  { id: "github", label: "GitHub", icon: <GitHubIcon /> },
  { id: "apple", label: "Apple", icon: <AppleIcon /> },
];

export function OAuthButtons({ next = "/" }: { next?: string }) {
  const t = useTranslations("auth");
  return (
    <div className="grid gap-2">
      {PROVIDERS.map((p) => (
        <Button
          key={p.id}
          type="button"
          variant="outline"
          className="w-full gap-2"
          onClick={() => startOAuth(p.id, next)}
        >
          {p.icon}
          {t("continueWith", { provider: p.label })}
        </Button>
      ))}
    </div>
  );
}

export function AuthDivider() {
  const t = useTranslations("auth");
  return (
    <div className="flex items-center gap-3">
      <span className="h-px flex-1 bg-border" />
      <span className="text-[11px] tracking-wide text-muted-foreground uppercase">{t("or")}</span>
      <span className="h-px flex-1 bg-border" />
    </div>
  );
}
