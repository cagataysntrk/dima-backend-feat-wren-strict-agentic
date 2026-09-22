import { NextResponse, type NextRequest } from "next/server";
import { getSessionCookie } from "better-auth/cookies";

// Page guard (Next 16 "proxy"). Optimistic cookie check only — every page and
// API route re-validates the session server-side (server/metabase/guard.ts).
export function proxy(req: NextRequest) {
  const hasSession = Boolean(getSessionCookie(req));
  const { pathname } = req.nextUrl;

  if (!hasSession && pathname.startsWith("/app")) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.search = "";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }
  // "/login while signed in" is handled by the login page with a REAL session
  // check — a stale cookie here would otherwise loop /login ↔ /app.
  return NextResponse.next();
}

export const config = { matcher: ["/app/:path*"] };
