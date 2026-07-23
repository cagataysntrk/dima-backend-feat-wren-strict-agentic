import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Route guard (Next 16 "proxy" convention; eski adı middleware). Refresh cookie
// (same-origin, rewrite-proxy sayesinde) yoksa /login'e yönlendir. Access token
// client'ta (memory); bu katman yalnız SAYFA erişimini kapılar. API token yaşam
// döngüsü api-client'te (Bearer + 401→refresh).
//
// Cookie adı backend DIMA_ ayarıyla eşleşir (varsayılan "dima_refresh").
const SESSION_COOKIE = "dima_refresh";

export function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const hasSession = req.cookies.has(SESSION_COOKIE);
  const isLogin = pathname === "/login";

  if (!hasSession && !isLogin) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }
  if (hasSession && isLogin) {
    const url = req.nextUrl.clone();
    url.pathname = "/";
    url.search = "";
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

// api (proxy), _next, statik dosyalar ve ikonlar hariç her route korunur.
export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|icon.svg|opengraph-image|.*\\.(?:png|jpg|jpeg|svg|ico|webp)$).*)",
  ],
};
