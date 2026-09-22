"use client";

import Link from "next/link";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { ArrowLeft, MailCheck } from "lucide-react";
import { apiErrorMessage, requestPasswordReset } from "@dima/api-client";
import { AuthShell } from "@/components/auth/AuthShell";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Label } from "@dima/ui/primitives/label";

function ForgotForm() {
  const t = useTranslations();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (error) {
      setErr(apiErrorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <div className="space-y-4 text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-brand/10 text-brand">
          <MailCheck className="size-6" />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">{t("forgot.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("forgot.sent")}</p>
        <Button asChild variant="outline" className="w-full">
          <Link href="/login">
            <ArrowLeft className="size-4" /> {t("forgot.back")}
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">{t("forgot.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("forgot.subtitle")}</p>
      </div>
      <form onSubmit={submit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="email">{t("auth.email")}</Label>
          <Input
            id="email"
            type="email"
            autoFocus
            autoComplete="email"
            value={email}
            suppressHydrationWarning
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        {err && (
          <p className="text-sm text-destructive" aria-live="polite">
            {err}
          </p>
        )}
        <Button type="submit" variant="brand" className="w-full" disabled={busy || !email}>
          {busy ? "…" : t("forgot.submit")}
        </Button>
      </form>
      <Link
        href="/login"
        className="flex items-center justify-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-3.5" /> {t("forgot.back")}
      </Link>
    </div>
  );
}

export default function ForgotPasswordPage() {
  return (
    <AuthShell>
      <ForgotForm />
    </AuthShell>
  );
}
