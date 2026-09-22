// Public error model for the gateway. Nothing from the analytics engine (its
// name, URLs, stack traces, SQL errors verbatim) is ever returned to the browser:
// callers get a Dima-worded message and an HTTP status.

export class GatewayError extends Error {
  constructor(
    readonly status: number,
    readonly publicMessage: string,
    /** Internal detail, logged server-side only. */
    readonly detail?: string,
  ) {
    super(publicMessage);
  }
}

export const notFound = () => new GatewayError(404, "Kayıt bulunamadı.");
export const forbidden = () => new GatewayError(403, "Bu işlem için yetkiniz yok.");
export const unauthorized = () => new GatewayError(401, "Oturum bulunamadı.");

/** Map an upstream (engine) HTTP status to a public error. 403 → 404 so ids of other tenants are not confirmed. */
export function fromUpstream(status: number, detail: string): GatewayError {
  if (status === 401) return new GatewayError(502, "Analiz servisine bağlanılamadı.", detail);
  if (status === 403 || status === 404) return new GatewayError(404, "Kayıt bulunamadı.", detail);
  if (status === 400 || status === 422) return new GatewayError(400, "Sorgu çalıştırılamadı.", detail);
  return new GatewayError(502, "Analiz servisi şu anda yanıt vermiyor.", detail);
}

/**
 * Query failures come back as HTTP 202 with {status:"failed", error}. Postgres
 * permission errors mean a cross-tenant attempt; everything else is a generic failure.
 */
export function fromQueryFailure(error: unknown): GatewayError {
  const text = String(error ?? "");
  if (/permission denied/i.test(text)) {
    return new GatewayError(403, "Bu veriye erişim yetkiniz yok.", text);
  }
  if (/syntax error|does not exist|column .* not found/i.test(text)) {
    // Safe, useful subset for analysts: the database's own message without engine branding.
    return new GatewayError(400, `Sorgu hatası: ${scrub(firstLine(text))}`, text);
  }
  return new GatewayError(400, "Sorgu çalıştırılamadı.", text);
}

const firstLine = (s: string) => s.split("\n")[0].slice(0, 200);

/** Remove any mention of the underlying engine from text we might show. */
export function scrub(s: string): string {
  return s.replace(/metabase/gi, "analiz servisi");
}
