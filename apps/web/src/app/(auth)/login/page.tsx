"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { useTranslations } from "next-intl";
import { ArrowLeft } from "lucide-react";
import { apiErrorMessage, login } from "@dima/api-client";
import { AuthShell } from "@/components/auth/AuthShell";
import { AuthDivider, OAuthButtons } from "@/components/auth/OAuthButtons";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Label } from "@dima/ui/primitives/label";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@dima/ui/primitives/input-otp";

function LoginForm() {
  const t = useTranslations();
  const router = useRouter();
  const params = useSearchParams();
  const requestedNext = params.get("next");
  const next =
    requestedNext?.startsWith("/app") && !requestedNext.startsWith("//")
      ? requestedNext
      : "/app";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [otpNeeded, setOtpNeeded] = useState(false); // MFA'lı hesap: parola doğru → OTP iste
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(code?: string) {
    setBusy(true);
    setErr(null);
    try {
      await login(email, password, (code ?? otp) || undefined);
      // Yeni oturum TEMİZ başlasın — token-expiry gibi buton-dışı çıkışlarda da önceki
      // kullanıcının konuşma zinciri sızmasın (çapraz-kullanıcı izolasyon, canlı 2026-07-25).
      const { useConversations } = await import("@/stores/conversations");
      useConversations.getState().reset();
      router.replace(next);
    } catch (error) {
      const msg = apiErrorMessage(error);
      if (msg.includes("OTP")) {
        setOtpNeeded(true);
        setErr(code || otp ? msg : null); // ilk sefer hata değil, alanın açılması yeterli
      } else {
        setErr(msg);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">{t("login.title")}</h1>
        <p className="text-sm text-muted-foreground">
          {otpNeeded ? t("auth.otpHint") : t("login.subtitle")}
        </p>
      </div>

      {otpNeeded ? (
        <div className="space-y-4">
          <div className="flex justify-center py-2">
            <InputOTP maxLength={6} value={otp} onChange={setOtp} onComplete={(v) => submit(v)} autoFocus>
              <InputOTPGroup>
                {[0, 1, 2, 3, 4, 5].map((i) => (
                  <InputOTPSlot key={i} index={i} />
                ))}
              </InputOTPGroup>
            </InputOTP>
          </div>
          {err && (
            <p className="text-center text-sm text-destructive" aria-live="polite">
              {err}
            </p>
          )}
          <Button variant="brand" className="w-full" disabled={busy || otp.length < 6} onClick={() => submit()}>
            {busy ? "…" : t("login.submit")}
          </Button>
          <button
            type="button"
            onClick={() => {
              setOtpNeeded(false);
              setOtp("");
              setErr(null);
            }}
            className="flex w-full items-center justify-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-3.5" /> {t("auth.email")}
          </button>
        </div>
      ) : (
        <>
          <OAuthButtons next={next} />
          <AuthDivider />
          <form onSubmit={(e) => { e.preventDefault(); submit(); }} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">{t("auth.email")}</Label>
              <Input
                id="email"
                type="email"
                autoFocus
                autoComplete="username"
                value={email}
                suppressHydrationWarning
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">{t("auth.password")}</Label>
                <Link href="/forgot-password" className="text-xs text-muted-foreground transition-colors hover:text-brand">
                  {t("login.forgot")}
                </Link>
              </div>
              <PasswordInput id="password" value={password} onChange={setPassword} />
            </div>
            {err && (
              <p className="text-sm text-destructive" aria-live="polite">
                {err}
              </p>
            )}
            <Button
              type="submit"
              variant="brand"
              className="w-full"
              disabled={busy || !email || !password}
              suppressHydrationWarning
            >
              {busy ? "…" : t("login.submit")}
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground">
            {t("login.noAccount")}{" "}
            <Link href="/register" className="font-medium text-brand hover:underline">
              {t("login.signUp")}
            </Link>
          </p>
        </>
      )}
    </div>
  );
}

export default function LoginPage() {
  return (
    <AuthShell>
      <Suspense>
        <LoginForm />
      </Suspense>
    </AuthShell>
  );
}
