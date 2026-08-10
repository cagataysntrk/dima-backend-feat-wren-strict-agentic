export type ContactState = {
  status: "idle" | "success" | "error";
  message?: string;
  errors?: Partial<Record<keyof ContactPayload, string>>;
};

export type ContactPayload = {
  fullName: string;
  email: string;
  company: string;
  role: string;
  dataSource: string;
  need: string;
  privacyConsent: string;
};

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MAX = { fullName: 120, email: 254, company: 160, role: 120, dataSource: 200, need: 2000, privacyConsent: 2 } as const;

function clean(value: FormDataEntryValue | null, limit: number, multiline = false) {
  if (typeof value !== "string") return "";
  const normalized = multiline ? value : value.replace(/[\r\n\t]+/g, " ");
  return normalized.trim().slice(0, limit + 1);
}

export function validateContactForm(formData: FormData, locale: string) {
  const tr = locale !== "en";
  const payload: ContactPayload = {
    fullName: clean(formData.get("fullName"), MAX.fullName),
    email: clean(formData.get("email"), MAX.email).toLowerCase(),
    company: clean(formData.get("company"), MAX.company),
    role: clean(formData.get("role"), MAX.role),
    dataSource: clean(formData.get("dataSource"), MAX.dataSource),
    need: clean(formData.get("need"), MAX.need, true),
    privacyConsent: formData.get("privacyConsent") === "on" ? "on" : "",
  };
  const errors: Partial<Record<keyof ContactPayload, string>> = {};
  const required = tr ? "Bu alan zorunludur." : "This field is required.";
  for (const key of ["fullName", "email", "company", "role", "need", "privacyConsent"] as const) {
    if (!payload[key]) errors[key] = required;
  }
  if (payload.email && !EMAIL.test(payload.email)) errors.email = tr ? "Geçerli bir e-posta girin." : "Enter a valid email.";
  for (const key of Object.keys(MAX) as (keyof ContactPayload)[]) {
    if (payload[key].length > MAX[key]) errors[key] = tr ? "Bu alan çok uzun." : "This field is too long.";
  }
  return { payload, errors, valid: Object.keys(errors).length === 0 };
}

type Bucket = { count: number; resetAt: number };
const buckets = new Map<string, Bucket>();
const WINDOW_MS = 15 * 60 * 1000;
const LIMIT = 5;

export function checkContactRateLimit(key: string, now = Date.now()) {
  if (buckets.size > 1000) {
    for (const [bucketKey, bucket] of buckets) if (bucket.resetAt <= now) buckets.delete(bucketKey);
  }
  const current = buckets.get(key);
  if (!current || current.resetAt <= now) {
    buckets.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return true;
  }
  if (current.count >= LIMIT) return false;
  current.count += 1;
  return true;
}

export function isLikelyBot(formData: FormData, now = Date.now()) {
  if (clean(formData.get("website"), 200)) return true;
  const startedAt = Number(formData.get("startedAt"));
  return !Number.isFinite(startedAt) || now - startedAt < 2500 || now - startedAt > 24 * 60 * 60 * 1000;
}
