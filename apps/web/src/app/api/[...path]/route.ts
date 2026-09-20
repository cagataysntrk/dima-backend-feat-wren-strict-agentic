// Same-origin backend proxy (ADR-0012 rewrite-proxy, promoted to a Route Handler so
// we can normalize Set-Cookie). The browser talks to /api/*; we forward to
// BACKEND_ORIGIN (server-side only, never exposed). Cookies flow both ways:
// the incoming Cookie header goes to the backend (so /auth/refresh|logout see the
// refresh cookie), and the backend's Set-Cookie is forwarded back.
//
// DEV-ONLY: strip `Secure` and `Domain` from Set-Cookie. In local dev the app is
// served over http, and browsers silently DROP `Secure` cookies (and reject
// Domain mismatches) — which breaks the session (login 200 but no cookie → the
// page guard bounces back to /login). Production keeps the flags untouched.

import type { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND = process.env.BACKEND_ORIGIN;
const DEV = process.env.NODE_ENV !== "production";

// hop-by-hop / encoding headers we must not forward verbatim
const STRIP_REQ = ["host", "connection", "content-length", "accept-encoding"];
const STRIP_RES = ["content-encoding", "content-length", "transfer-encoding", "connection"];

function normalizeSetCookie(cookie: string): string {
  // http dev: drop Secure (would be discarded) and Domain (host-only for this origin).
  return cookie
    .replace(/;\s*Secure/gi, "")
    .replace(/;\s*Domain=[^;]+/gi, "");
}

async function handler(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  // Prod fail-fast: BACKEND_ORIGIN tanımsızsa localhost'a sessizce düşme (prod 502
  // tuzağı) — yanlış yapılandırmayı gürültülü yap. Dev'de localhost serbest.
  if (!BACKEND) {
    if (DEV) {
      return proxyTo(req, ctx, "http://localhost:8000");
    }
    return Response.json({ detail: "BACKEND_ORIGIN is not configured." }, { status: 503 });
  }
  return proxyTo(req, ctx, BACKEND);
}

async function proxyTo(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
  backend: string,
) {
  const { path } = await ctx.params;
  const target = `${backend}/${path.join("/")}${req.nextUrl.search}`;

  const headers = new Headers(req.headers);
  STRIP_REQ.forEach((h) => headers.delete(h));

  const hasBody = req.method !== "GET" && req.method !== "HEAD";
  let res: Response;
  try {
    res = await fetch(target, {
      method: req.method,
      headers,
      body: hasBody ? await req.arrayBuffer() : undefined,
      redirect: "manual",
    });
  } catch {
    // Backend unreachable (e.g. not running in dev) — clean 502, don't crash the route.
    return Response.json(
      { detail: "Backend'e ulaşılamadı. (Backend unreachable.)" },
      { status: 502 },
    );
  }

  const resHeaders = new Headers(res.headers);
  STRIP_RES.forEach((h) => resHeaders.delete(h));

  // Forward Set-Cookie (undici exposes them individually via getSetCookie()).
  const setCookies = res.headers.getSetCookie?.() ?? [];
  if (setCookies.length) {
    resHeaders.delete("set-cookie");
    for (const c of setCookies) {
      resHeaders.append("set-cookie", DEV ? normalizeSetCookie(c) : c);
    }
  }

  return new Response(res.body, { status: res.status, headers: resHeaders });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const OPTIONS = handler;
export const HEAD = handler;
