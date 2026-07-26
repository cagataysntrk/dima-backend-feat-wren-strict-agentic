# 05 — Target Technical Architecture

## 1. Route architecture

```text
app/
  layout.tsx                    # neutral global root
  (marketing)/
    layout.tsx                  # public, scrollable, marketing shell
    page.tsx                    # /
    product/page.tsx
    how-it-works/page.tsx
    ...
  (product)/
    app/
      layout.tsx                # h-dvh, product providers, noindex
      page.tsx                  # moved current product root
  (auth)/
    login/page.tsx
    register/page.tsx
    forgot-password/page.tsx
```

## 2. Root layout responsibilities

Root layout yalnızca:
- `<html lang>`
- global fonts
- global CSS
- lightweight global providers
- metadata defaults
taşımalıdır.

Root body:
- `min-h-screen`
- scroll'u engellemez
- product-specific flex/overflow class taşımaz

## 3. Product layout responsibilities

- `h-dvh`
- `overflow-hidden`
- QueryClient
- AuthBootstrap
- product shell assumptions
- noindex metadata
- any app-only tooltip/toaster runtime
- error boundary if needed

## 4. Marketing layout responsibilities

- Marketing navbar
- main landmark
- footer
- skip-to-content
- scrollable body
- public-safe providers
- optional structured data
- no auth refresh request
- no product store initialization

## 5. Server-first boundary

Pages ve statik sections default Server Components olmalıdır.

Client Components yalnızca:
- mobile navigation
- theme/language interactive control
- FAQ accordion if needed
- contact form state
- deterministic product proof animation
- minimal viewport reveal wrapper

Aşağıdaki pattern'den kaçının:
- tüm homepage'e `"use client"`
- tüm content'i client translation hook ile render etmek
- client component içinden statik metin listeleri üretmek
- marketing route'a QueryClient/Zustand taşımak

## 6. Auth and proxy policy

Protected convention:
- tüm ürün route'ları `/app/**`
- auth pages `/login`, `/register`, `/forgot-password`

Proxy:
- `/app/:path*` için cookie kontrolü
- no session → `/login?next=<path>`
- session + auth page → `/app`
- expired flag logic korunur
- marketing route'ları auth redirect'e girmez

Security note:
- proxy yalnızca page access gate'tir.
- API authorization backend Bearer/tenant/permission katmanında kalır.
- marketing public oluşu API'yi public yapmaz.

## 7. Redirect and link migration

Güncellenecek noktalar:
- login success redirect
- auth-page-with-session redirect
- logout redirect
- logo/home links
- search/new chat assumptions
- any `router.push("/")`
- E2E `FRONTEND_URL`
- docs/readme route descriptions
- metadata canonical
- error pages

Repo genelinde exact search:
- `href="/"`
- `router.push("/")`
- `router.replace("/")`
- `pathname === "/"`
- `redirect("/")`
- `next=/`

Her eşleşme bağlamıyla incelenmeli; kör replace yapılmamalı.

## 8. Content architecture

```ts
type CapabilityStatus = "available" | "beta" | "planned";

type MarketingCapability = {
  id: string;
  title: string;
  summary: string;
  status: CapabilityStatus;
  evidence?: {
    repoPath?: string;
    demoRoute?: string;
  };
};
```

Amaç:
- aynı claim'in farklı sayfalarda farklı status ile görünmesini önlemek,
- roadmap claim'lerini açıkça etiketlemek,
- launch öncesi claim review yapmak.

## 9. Asset architecture

```text
public/marketing/
  brand/
  product/
  industries/textile/
  og/
```

Kurallar:
- SVG logolar optimize.
- Screenshot'lar demo/sanitized.
- `next/image`.
- Dimensions sabit.
- Alt text content source'ta.
- Filenames semantic ve kebab-case.
- Büyük video gerekiyorsa poster + user initiated playback.
- LCP hero visual tek ve optimize.

## 10. SEO architecture

- `NEXT_PUBLIC_SITE_URL` veya server env ile `metadataBase`.
- Root title template.
- Her sayfada unique title/description.
- canonical.
- Open Graph/Twitter.
- `sitemap.ts`.
- `robots.ts`.
- `/app`, `/api`, auth noindex/disallow.
- Organization JSON-LD.
- SoftwareApplication JSON-LD yalnızca factual fields.
- FAQ structured data yalnızca görünür içerikle birebir ve policy uygunsa.
- Cookie-based TR/EN için hreflang yok.

## 11. Error and loading states

Marketing:
- custom 404.
- contact form validation.
- no skeleton needed for static content.
- optional dynamic content için stable dimensions.

Product:
- mevcut loading/error behavior korunur.
- route migration nedeniyle yeni hydration flash oluşmamalı.

## 12. Deployment

- Vercel config korunur.
- Backend origin server-side kalır.
- Marketing build backend erişimi gerektirmemeli.
- Static generation mümkün olan tüm public pages için.
- Contact endpoint/network unavailable olsa bile homepage build'i bozulmamalı.
- Preview deployment'ta robots noindex kararı değerlendirilmeli.
