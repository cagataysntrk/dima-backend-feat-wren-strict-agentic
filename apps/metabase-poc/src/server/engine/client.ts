import "server-only";
import { GatewayError, fromUpstream } from "@/server/metabase/errors";
import { metabaseUrl, type Tenant } from "@/server/metabase/tenants";

const TIMEOUT_MS = 120_000;

export function engineConfigured(): boolean {
  return Boolean(process.env.DIMA_ENGINE_URL && process.env.DIMA_ENGINE_TENANTS);
}

export async function engineFetch(
  tenant: Tenant,
  path: string,
  init: RequestInit = {},
  signal?: AbortSignal,
): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set("X-API-Key", tenant.apiKey);
  if (init.body && typeof init.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  headers.set("Accept", init.headers && new Headers(init.headers).get("Accept") ? new Headers(init.headers).get("Accept")! : "application/json");

  const timeout = AbortSignal.timeout(TIMEOUT_MS);
  const combined = signal ? AbortSignal.any([signal, timeout]) : timeout;

  let res: Response;
  try {
    res = await fetch(metabaseUrl() + path, {
      ...init,
      headers,
      cache: "no-store",
      signal: combined,
    });
  } catch (e) {
    if (signal?.aborted) throw e;
    throw new GatewayError(502, "Analiz servisine bağlanılamadı.", String(e));
  }

  if (!res.ok) {
    const detail = `${init.method ?? "GET"} ${path} -> ${res.status}: ${(await res.text()).slice(0, 800)}`;
    throw fromUpstream(res.status, detail);
  }
  return res;
}

export async function engineJson<T>(
  tenant: Tenant,
  path: string,
  body: unknown,
  signal?: AbortSignal,
): Promise<T> {
  const res = await engineFetch(
    tenant,
    path,
    { method: "POST", body: JSON.stringify(body) },
    signal,
  );
  const text = await res.text();
  return (text ? JSON.parse(text) : null) as T;
}
