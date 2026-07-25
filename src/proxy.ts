import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Route guard (Next 16 "proxy" convention; eski adı middleware). Refresh cookie
// (same-origin, rewrite-proxy sayesinde) yoksa /login'e yönlendir. Access token
// client'ta (memory); bu katman yalnız SAYFA erişimini kapılar. API token yaşam
// döngüsü api-client'te (Bearer + 401→refresh).
//
// Cookie adı backend DIMA_COOKIE_NAME ile eşleşir; env ile senkron tutulur
// (backend adı değiştirirse kod değil yalnız build config değişir).
const SESSION_COOKIE = process.env.NEXT_PUBLIC_SESSION_COOKIE ?? "dima_refresh";

// Oturum gerektirmeyen genel auth sayfaları.
const AUTH_ROUTES = new Set(["/login", "/register", "/forgot-password"]);

// api-client, refresh de başarısız olduğunda /login?expired=1'e yönlendirir.
// Cookie hâlâ tarayıcıda (HTTP-only, JS silemez) olduğu için bu işaret olmadan
// aşağıdaki "girişliyken /login'e gelme" kuralı /login ↔ / arasında sonsuz
// döngü yaratır. İşaret varsa: bayat cookie'yi burada sil ve login'i göster.
const EXPIRED_FLAG = "expired";

export function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const hasSession = req.cookies.has(SESSION_COOKIE);
  const isAuthPage = AUTH_ROUTES.has(pathname);

  if (isAuthPage && req.nextUrl.searchParams.has(EXPIRED_FLAG)) {
    const res = NextResponse.next();
    if (hasSession) res.cookies.delete(SESSION_COOKIE);
    return res;
  }

  if (!hasSession && !isAuthPage) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }
  // Girişliyken auth sayfalarına gelme → ana uygulamaya dön.
  if (hasSession && isAuthPage) {
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
