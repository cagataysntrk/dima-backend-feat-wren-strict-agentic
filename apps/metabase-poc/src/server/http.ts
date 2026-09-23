import "server-only";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { getTranslations } from "next-intl/server";
import { DEFAULT_LOCALE, LOCALE_COOKIE, isLocale } from "@/i18n/config";
import { ZodError } from "zod";
import { ERROR_KEYS } from "./error-messages";

const UNEXPECTED = "Beklenmeyen bir hata oluştu.";
const INVALID = "Geçersiz istek.";
import { GatewayError } from "./metabase/errors";
import { requireTenant, type TenantContext } from "./metabase/guard";

/**
 * Route-handler wrapper: resolves the tenant from the session, runs the handler,
 * and converts every failure into a Dima-worded JSON error. Engine details are
 * logged server-side only.
 */
/**
 * Gateway errors are thrown as Turkish strings (those are the identifiers in
 * the code); here they become the caller's language. An unmapped message is
 * passed through rather than swallowed — a missing translation should still
 * tell the person what happened.
 */
export async function localizeError(message: string): Promise<string> {
  const key = ERROR_KEYS[message];
  if (!key) return message;
  // The locale is read from the cookie here rather than left to next-intl's
  // request scope: in a Route Handler that scope is not always established,
  // and a silent fallback would ship Turkish to an English reader.
  const store = await cookies();
  const cookieLocale = store.get(LOCALE_COOKIE)?.value;
  const locale = isLocale(cookieLocale) ? cookieLocale : DEFAULT_LOCALE;
  try {
    const t = await getTranslations({ locale, namespace: "gateway" });
    return t(key);
  } catch (e) {
    console.warn("[gateway] could not translate error", e);
    return message;
  }
}

export function withTenant<P>(
  handler: (ctx: TenantContext, req: Request, params: P) => Promise<Response | unknown>,
) {
  return async (req: Request, { params }: { params: Promise<P> }) => {
    try {
      const ctx = await requireTenant();
      const out = await handler(ctx, req, await params);
      return out instanceof Response ? out : NextResponse.json(out);
    } catch (e) {
      if (e instanceof GatewayError) {
        if (e.detail) console.warn(`[gateway] ${e.status} ${e.detail}`);
        return NextResponse.json({ error: await localizeError(e.publicMessage) }, { status: e.status });
      }
      console.error("[gateway] unexpected", e);
      return NextResponse.json({ error: await localizeError(UNEXPECTED) }, { status: 500 });
    }
  };
}

/**
 * Like `withTenant`, but for routes that only need a signed-in session (the
 * settings screens administer the company, they don't query its data). Zod
 * failures become a 400 rather than a 500.
 */
export function withSession(handler: (req: Request) => Promise<unknown>) {
  return async (req: Request) => {
    try {
      const out = await handler(req);
      return out instanceof Response ? out : NextResponse.json(out);
    } catch (e) {
      if (e instanceof GatewayError) {
        if (e.detail) console.warn(`[gateway] ${e.status} ${e.detail}`);
        return NextResponse.json({ error: await localizeError(e.publicMessage) }, { status: e.status });
      }
      if (e instanceof ZodError) return NextResponse.json({ error: await localizeError(INVALID) }, { status: 400 });
      console.error("[gateway] unexpected", e);
      return NextResponse.json({ error: await localizeError(UNEXPECTED) }, { status: 500 });
    }
  };
}

/** Positive integer path id, or a 404-style error. */
export function idParam(v: string): number {
  const n = Number(v);
  if (!Number.isInteger(n) || n <= 0) throw new GatewayError(404, "Kayıt bulunamadı.");
  return n;
}

/** URL search params → {slug: values[]}, ignoring reserved keys. */
export function filtersFrom(url: URL, reserved: string[] = []) {
  const out: Record<string, string[]> = {};
  for (const [k, v] of url.searchParams) {
    if (reserved.includes(k)) continue;
    (out[k] ??= []).push(v);
  }
  return out;
}
