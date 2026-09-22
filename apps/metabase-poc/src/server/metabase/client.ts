import "server-only";
import { GatewayError, fromUpstream } from "./errors";
import { adminApiKey, metabaseUrl, type Tenant } from "./tenants";

/** Who the call is made as: a tenant (its own API key / permission group) or the admin key. */
export type Caller = Tenant | "admin";

const TIMEOUT_MS = 60_000;

async function raw(caller: Caller, path: string, init: RequestInit = {}): Promise<Response> {
  const key = caller === "admin" ? adminApiKey() : caller.apiKey;
  const headers = new Headers(init.headers);
  headers.set("X-API-Key", key);
  if (init.body && typeof init.body === "string") headers.set("Content-Type", "application/json");
  let res: Response;
  try {
    res = await fetch(metabaseUrl() + path, {
      ...init,
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (e) {
    throw new GatewayError(502, "Analiz servisine bağlanılamadı.", String(e));
  }
  if (!res.ok) {
    throw fromUpstream(res.status, `${init.method ?? "GET"} ${path} -> ${res.status}: ${(await res.text()).slice(0, 500)}`);
  }
  return res;
}

export async function mbJson<T>(caller: Caller, path: string, init: RequestInit = {}): Promise<T> {
  const res = await raw(caller, path, init);
  const text = await res.text();
  return (text ? JSON.parse(text) : null) as T;
}

export const mbGet = <T>(caller: Caller, path: string) => mbJson<T>(caller, path);

export const mbPost = <T>(caller: Caller, path: string, body?: unknown) =>
  mbJson<T>(caller, path, { method: "POST", body: JSON.stringify(body ?? {}) });

export const mbPut = <T>(caller: Caller, path: string, body?: unknown) =>
  mbJson<T>(caller, path, { method: "PUT", body: JSON.stringify(body ?? {}) });

/** Binary responses (exports). */
export async function mbBinary(caller: Caller, path: string, body: unknown): Promise<ArrayBuffer> {
  const res = await raw(caller, path, { method: "POST", body: JSON.stringify(body) });
  return res.arrayBuffer();
}

/** Multipart form posts (uploads). */
export const mbForm = <T>(caller: Caller, path: string, form: FormData) =>
  mbJson<T>(caller, path, { method: "POST", body: form });
