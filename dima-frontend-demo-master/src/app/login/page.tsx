"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { BrandMark } from "@/components/BrandMark";
import { apiErrorMessage, login } from "@/lib/api-client";

function EyeIcon({ off }: { off: boolean }) {
  return off ? (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.9 4.24A9 9 0 0 1 12 4c6.5 0 10 7 10 7a13 13 0 0 1-2 2.7" />
      <path d="M6.6 6.6A13 13 0 0 0 2 11s3.5 7 10 7a9 9 0 0 0 4.5-1.2" />
      <path d="M3 3l18 18" />
      <path d="M9.5 9.5a3 3 0 0 0 4.2 4.2" />
    </svg>
  ) : (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/";
  // 🔴🔴 `§K3` — Ölçüldü (canlı Playwright kampanyası): 20+ dk açık kalan bir sekmede
  // oturum sessizce düşüyordu, kullanıcı hiç uyarı görmüyordu. `api-client.ts`'in
  // 401→refresh-başarısız yolu artık `?sebep=oturum_suresi` taşıyor — bu nazik not
  // o sinyali okuyup gösteriyor. Kırmızı bir HATA değil (kullanıcı yanlış bir şey
  // yapmadı, zaman geçti) — nötr bir bilgi notu.
  const sebep = params.get("sebep");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [otp, setOtp] = useState("");
  const [otpNeeded, setOtpNeeded] = useState(false); // MFA'lı hesap: parola doğru → OTP iste
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      await login(email, password, otp || undefined);
      // Yeni oturum TEMİZ başlasın — token-expiry gibi buton-dışı çıkışlarda da önceki
      // kullanıcının konuşma zinciri sızmasın (çapraz-kullanıcı izolasyon, canlı 2026-07-25).
      const { useHistory } = await import("@/stores/history");
      useHistory.getState().clear();
      router.replace(next);
    } catch (error) {
      const msg = apiErrorMessage(error);
      if (msg.includes("OTP")) {
        setOtpNeeded(true);
        setErr(otp ? msg : null); // ilk sefer hata değil, alanın açılması yeterli
      } else {
        setErr(msg);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-[min(360px,86vw)]">
      <div className="mb-8 flex justify-center">
        <BrandMark size="xl" animate />
      </div>

      {sebep === "oturum_suresi" && (
        <p className="mb-4 rounded-md border border-hairline bg-neutral-500/[0.04] px-3 py-2 text-xs text-neutral-500">
          Oturumunun süresi doldu — güvenlik için tekrar giriş yapman gerekiyor.
        </p>
      )}

      <label
        htmlFor="email"
        className="mb-1 block font-mono text-[0.7rem] uppercase tracking-wide text-muted"
      >
        e-posta
      </label>
      <input
        id="email"
        type="email"
        autoFocus
        autoComplete="username"
        suppressHydrationWarning
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="mb-3 w-full rounded-md border border-hairline bg-transparent px-3 py-2 text-sm text-foreground outline-none focus:border-accent"
      />

      <label
        htmlFor="password"
        className="mb-1 block font-mono text-[0.7rem] uppercase tracking-wide text-muted"
      >
        parola
      </label>
      <div className="relative mb-4">
        <input
          id="password"
          type={showPw ? "text" : "password"}
          autoComplete="current-password"
          suppressHydrationWarning
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md border border-hairline bg-transparent py-2 pl-3 pr-10 text-sm text-foreground outline-none focus:border-accent"
        />
        <button
          type="button"
          onClick={() => setShowPw((v) => !v)}
          aria-label={showPw ? "Parolayı gizle" : "Parolayı göster"}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted transition-colors hover:text-foreground"
        >
          <EyeIcon off={showPw} />
        </button>
      </div>

      {otpNeeded && (
        <>
          <label
            htmlFor="otp"
            className="mb-1 block font-mono text-[0.7rem] uppercase tracking-wide text-muted"
          >
            doğrulama kodu (otp)
          </label>
          <input
            id="otp"
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            maxLength={6}
            autoFocus
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            className="mb-4 w-full rounded-md border border-hairline bg-transparent px-3 py-2 text-sm text-foreground outline-none focus:border-accent"
          />
        </>
      )}

      {err && (
        <p className="mb-3 text-xs" style={{ color: "var(--danger, #b42318)" }}>
          {err}
        </p>
      )}

      <button
        disabled={busy || !email || !password || (otpNeeded && otp.length < 6)}
        suppressHydrationWarning
        className="w-full rounded-md bg-accent py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
      >
        {busy ? "…" : "Giriş"}
      </button>
    </form>
  );
}

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <Suspense>
        <LoginForm />
      </Suspense>
    </main>
  );
}
