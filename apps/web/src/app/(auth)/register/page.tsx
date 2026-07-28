"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { apiErrorMessage, register } from "@/lib/api-client";
import { AuthShell } from "@/components/auth/AuthShell";
import { AuthDivider, OAuthButtons } from "@/components/auth/OAuthButtons";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { PasswordStrength, scorePassword } from "@/components/auth/PasswordStrength";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

function RegisterForm() {
  const t = useTranslations();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const mismatch = confirm.length > 0 && confirm !== password;
  const valid = !!email && password.length >= 8 && scorePassword(password) >= 2 && confirm === password;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!valid) return;
    setBusy(true);
    setErr(null);
    try {
      await register(email, password);
      router.replace("/app");
    } catch (error) {
      setErr(apiErrorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">{t("register.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("register.subtitle")}</p>
      </div>

      <OAuthButtons />
      <AuthDivider />

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
        <div className="space-y-1.5">
          <Label htmlFor="password">{t("auth.password")}</Label>
          <PasswordInput id="password" autoComplete="new-password" value={password} onChange={setPassword} />
          <PasswordStrength value={password} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="confirm">{t("auth.confirmPassword")}</Label>
          <PasswordInput
            id="confirm"
            autoComplete="new-password"
            value={confirm}
            onChange={setConfirm}
            aria-invalid={mismatch}
          />
          {mismatch && <p className="text-[11px] text-destructive">{t("auth.passwordsNoMatch")}</p>}
        </div>
        {err && (
          <p className="text-sm text-destructive" aria-live="polite">
            {err}
          </p>
        )}
        <Button type="submit" variant="brand" className="w-full" disabled={busy || !valid}>
          {busy ? "…" : t("register.submit")}
        </Button>
        <p className="text-center text-[11px] leading-snug text-muted-foreground">{t("register.terms")}</p>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        {t("register.haveAccount")}{" "}
        <Link href="/login" className="font-medium text-brand hover:underline">
          {t("register.signIn")}
        </Link>
      </p>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <AuthShell>
      <RegisterForm />
    </AuthShell>
  );
}
