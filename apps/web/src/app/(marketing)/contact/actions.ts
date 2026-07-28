"use server";

import { headers } from "next/headers";
import { Resend } from "resend";
import { checkContactRateLimit, isLikelyBot, type ContactState, validateContactForm } from "@/lib/marketing/contact";

export async function submitContact(_previous: ContactState, formData: FormData): Promise<ContactState> {
  const locale = String(formData.get("locale")) === "en" ? "en" : "tr";
  const tr = locale === "tr";
  if (isLikelyBot(formData)) {
    return { status: "success", message: tr ? "Talebiniz alındı." : "Your request has been received." };
  }
  const requestHeaders = await headers();
  const ip = requestHeaders.get("x-forwarded-for")?.split(",")[0]?.trim() || requestHeaders.get("x-real-ip") || "unknown";
  if (!checkContactRateLimit(ip)) {
    return { status: "error", message: tr ? "Çok fazla deneme yapıldı. Lütfen daha sonra tekrar deneyin." : "Too many attempts. Please try again later." };
  }
  const result = validateContactForm(formData, locale);
  if (!result.valid) return { status: "error", errors: result.errors, message: tr ? "Lütfen işaretli alanları kontrol edin." : "Please review the highlighted fields." };

  const apiKey = process.env.RESEND_API_KEY;
  const to = process.env.CONTACT_TO_EMAIL;
  const from = process.env.CONTACT_FROM_EMAIL;
  if (!apiKey || !to || !from) {
    return { status: "error", message: tr ? "Form şu anda kullanılamıyor. Lütfen contact@upcytech.com adresine yazın." : "The form is currently unavailable. Please email contact@upcytech.com." };
  }
  const resend = new Resend(apiKey);
  const p = result.payload;
  try {
    const { error } = await resend.emails.send({
      from,
      to,
      replyTo: p.email,
      subject: `dima demo request — ${p.company}`,
      text: `Name: ${p.fullName}\nCompany: ${p.company}\nRole: ${p.role}\nData source: ${p.dataSource || "Not provided"}\n\nNeed:\n${p.need}`,
    });
    if (error) throw new Error("Delivery rejected");
    return { status: "success", message: tr ? "Teşekkürler. Talebiniz ekibimize ulaştı." : "Thank you. Your request reached our team." };
  } catch {
    return { status: "error", message: tr ? "Mesaj gönderilemedi. Lütfen contact@upcytech.com adresine yazın." : "We could not send your message. Please email contact@upcytech.com." };
  }
}
