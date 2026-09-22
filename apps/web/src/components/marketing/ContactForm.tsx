"use client";

import { useActionState, useState } from "react";
import Link from "next/link";
import { Loader2, Send } from "lucide-react";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Label } from "@dima/ui/primitives/label";
import { Textarea } from "@dima/ui/primitives/textarea";
import type { MarketingLocale } from "@/content/marketing";
import type { ContactState } from "@/lib/marketing/contact";
import { submitContact } from "@/app/(marketing)/contact/actions";

const initialState: ContactState = { status: "idle" };
const text = {
  tr: { name: "Ad soyad", email: "İş e-postası", company: "Şirket", role: "Rol", source: "Veri kaynağı (isteğe bağlı)", need: "Öncelikli rapor veya iş sorusu", send: "Demo talebini gönder", privacy: "Gönderdiğiniz bilgileri demo talebinizi yanıtlamak için işleriz.", consent: "Gizlilik metnini okudum ve bilgilerimin bu amaçla işlenmesini kabul ediyorum.", link: "Gizlilik metnini okuyun." },
  en: { name: "Full name", email: "Work email", company: "Company", role: "Role", source: "Data source (optional)", need: "Priority report or business question", send: "Send demo request", privacy: "We process the information you submit to respond to your demo request.", consent: "I have read the privacy notice and agree to this processing.", link: "Read the privacy notice." },
} as const;

export function ContactForm({ locale }: { locale: MarketingLocale }) {
  const [state, action, pending] = useActionState(submitContact, initialState);
  const [startedAt] = useState(() => Date.now());
  const t = text[locale];
  if (state.status === "success") return <div role="status" aria-live="polite" className="rounded-lg border border-chart-2/40 bg-chart-2/10 p-6 text-sm leading-6">{state.message}</div>;
  const fields = [
    ["fullName", t.name, "text", "name"],
    ["email", t.email, "email", "email"],
    ["company", t.company, "text", "organization"],
    ["role", t.role, "text", "organization-title"],
    ["dataSource", t.source, "text", "off"],
  ] as const;
  return (
    <form action={action} className="space-y-5" noValidate>
      <input type="hidden" name="locale" value={locale} /><input type="hidden" name="startedAt" value={startedAt} />
      <div className="absolute left-[-10000px]" aria-hidden="true"><Label htmlFor="website">Website</Label><Input id="website" name="website" tabIndex={-1} autoComplete="off" /></div>
      <div className="grid gap-5 sm:grid-cols-2">
        {fields.map(([name, label, type, autoComplete], index) => (
          <div className={index === 4 ? "sm:col-span-2" : ""} key={name}>
            <Label htmlFor={name}>{label}{name !== "dataSource" && <span aria-hidden="true"> *</span>}</Label>
            <Input className="mt-2 min-h-11" id={name} name={name} type={type} autoComplete={autoComplete} required={name !== "dataSource"} aria-invalid={!!state.errors?.[name]} aria-describedby={state.errors?.[name] ? `${name}-error` : undefined} />
            {state.errors?.[name] && <p id={`${name}-error`} className="mt-1 text-xs text-destructive">{state.errors[name]}</p>}
          </div>
        ))}
      </div>
      <div><Label htmlFor="need">{t.need} *</Label><Textarea className="mt-2 min-h-32" id="need" name="need" required aria-invalid={!!state.errors?.need} aria-describedby={state.errors?.need ? "need-error" : undefined} />{state.errors?.need && <p id="need-error" className="mt-1 text-xs text-destructive">{state.errors.need}</p>}</div>
      {state.message && <p role="alert" className="text-sm text-destructive">{state.message}</p>}
      <p className="text-xs leading-5 text-muted-foreground">{t.privacy} <Link className="underline hover:text-foreground focus-visible:text-foreground" href="/privacy">{t.link}</Link></p>
      <div className="flex items-start gap-3">
        <input className="mt-1 size-4 shrink-0 accent-brand" id="privacyConsent" name="privacyConsent" type="checkbox" required aria-invalid={!!state.errors?.privacyConsent} aria-describedby={state.errors?.privacyConsent ? "privacyConsent-error" : undefined} />
        <div><Label className="text-xs font-normal leading-5" htmlFor="privacyConsent">{t.consent} <span aria-hidden="true">*</span></Label>{state.errors?.privacyConsent && <p id="privacyConsent-error" className="mt-1 text-xs text-destructive">{state.errors.privacyConsent}</p>}</div>
      </div>
      <Button disabled={pending} type="submit" variant="brand" size="lg" className="min-h-11">{pending ? <Loader2 className="animate-spin" /> : <Send />}{t.send}</Button>
    </form>
  );
}
