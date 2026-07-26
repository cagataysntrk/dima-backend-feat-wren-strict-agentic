# 01 — Repository Architecture Audit

## A. Mevcut teknoloji tabanı

| Alan | Mevcut durum | Marketing kararı |
|---|---|---|
| Framework | Next.js 16 App Router | Korunacak |
| Runtime UI | React 19 | Korunacak |
| Styling | Tailwind CSS 4 + CSS variables | Yeni design system bunun üzerine kurulacak |
| State | TanStack Query + Zustand | Marketing'e taşınmayacak |
| i18n | next-intl, cookie-locale, URL prefix yok | İlk fazda korunacak; marketing namespace eklenecek |
| Theme | next-themes | Marketing shell ile uyumlu kullanılacak |
| Motion | `motion/react` + shared presets | Sınırlı ve reduced-motion uyumlu |
| Icons | Lucide | Tek ikon sistemi olarak korunacak |
| API | Axios, same-origin `/api/*` route handler | Marketing public demo backend çağırmayacak |
| Auth | memory access token + HTTP-only refresh cookie | Aynen korunacak |
| E2E | custom browser/CDP test | Route migrasyonuna göre güncellenecek |

## B. Kritik korunacak business logic

Aşağıdaki alanlar marketing çalışması sırasında refactor bahanesiyle yeniden yazılmamalıdır:

- `src/lib/api-client.ts`
- auth refresh/retry zinciri
- session cookie adı ve normalization
- `src/stores/conversations.ts`
- logout/login sırasında conversation reset güvenlik düzeltmesi
- ask / cube / verify / schedule / notification çağrıları
- report/chart/table/KPI/pivot analiz davranışı
- `/api/[...path]` route handler
- permission-based UI görünürlüğü
- tenant/session semantiği
- feature flags
- product E2E'nin API doğrulama bölümü

## C. Route kaynaklı riskler

### Risk 1 — `/` ürün route'u
Marketing'in `/` olması için product page taşınmalıdır. Dosyanın kopyalanıp eski route'un bırakılması iki farklı state entrypoint oluşturur. Doğru çözüm, tek product entrypoint'i `/app` altına taşımaktır.

### Risk 2 — Proxy
Mevcut proxy “auth dışındaki her şeyi koru” yaklaşımındadır. Marketing için çok sayıda public route eklemek, büyüyen allowlist'i hata eğilimli hale getirir. Önerilen konvansiyon:

- Tüm protected product route'ları `/app/**` altında.
- Proxy matcher yalnızca `/app/:path*` ve session-aware auth route'larını kapsar.
- Marketing route'ları proxy auth logic'ine girmez.
- `/api/**` güvenliği backend/token katmanında kalır.
- Unknown public route, login redirect yerine gerçek 404 gösterebilir.

### Risk 3 — Root layout overflow
Root body marketing için:
`min-h-screen bg-background text-foreground`

Product layout:
`h-dvh overflow-hidden`

Bu ayrım route-group layout'unda yapılmalıdır.

### Risk 4 — Root providers
Public marketing route'larında otomatik refresh çağrısı ve product QueryClient bootstrap istemiyoruz. Provider'lar iki gruba ayrılmalıdır:

- **Global/lightweight:** locale, theme, reduced-motion gibi tüm siteye gerekenler.
- **Product runtime:** QueryClient, AuthBootstrap, product Tooltip/Toaster ve diğer app runtime ihtiyaçları.

Bu refactor sırasında hydration ve theme flash test edilmelidir.

## D. Önerilen klasör sınırları

```text
src/
├── app/
│   ├── layout.tsx
│   ├── sitemap.ts
│   ├── robots.ts
│   ├── manifest.ts
│   ├── (marketing)/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── product/page.tsx
│   │   ├── how-it-works/page.tsx
│   │   ├── solutions/page.tsx
│   │   ├── solutions/textile-dyehouse/page.tsx
│   │   ├── security/page.tsx
│   │   ├── integrations/page.tsx
│   │   ├── about/page.tsx
│   │   ├── changelog/page.tsx
│   │   ├── contact/page.tsx
│   │   ├── privacy/page.tsx
│   │   └── terms/page.tsx
│   ├── (product)/
│   │   └── app/
│   │       ├── layout.tsx
│   │       └── page.tsx
│   └── (auth)/
│       ├── login/page.tsx
│       ├── register/page.tsx
│       └── forgot-password/page.tsx
├── components/
│   ├── marketing/
│   │   ├── layout/
│   │   ├── sections/
│   │   ├── proof/
│   │   └── ui/
│   ├── shell/
│   └── ui/
├── content/
│   └── marketing/
├── lib/
│   ├── marketing/
│   └── ...
└── i18n/
```

Route group adları URL'e girmez.

## E. Dependency politikası

### Öncelik sırası
1. Mevcut component ve dependency ile çöz.
2. Küçük bir component'i local ve dependency-free yaz.
3. Resmi shadcn/MagicUI kaynağından lisansı doğrulanmış minimal primitive ekle.
4. Yeni ağır dependency yalnızca ölçülmüş gerekçeyle.

### Marketing route'larına import edilmemesi gerekenler
- `@tanstack/react-query`
- Zustand product stores
- `@xyflow/react`
- Recharts/ECharts gibi chart runtime'ları, gerçek ihtiyaç yoksa
- product API client
- auth bootstrap
- WebGL / Three / canvas particle dependency'leri

Bir görsel proof için statik HTML/CSS mockup veya optimize screenshot yeterliyse chart runtime gönderilmemelidir.

## F. İ18n kararı

Mevcut yapı locale'i cookie'den çözüyor ve URL prefix kullanmıyor. İlk marketing release için:

- Türkçe canonical içerik.
- `messages/tr.json` ve `messages/en.json` altında `marketing` namespace.
- Dil switch mevcut mekanizmayla çalışabilir.
- Aynı URL'de cookie ile değişen dil için `hreflang` üretilmez.
- İngilizcenin ayrıca indexlenmesi istenirse, route-based locale migration ayrı bir ADR/stage olmalıdır.

## G. E2E migrasyonu

Mevcut test:
- `/` açar,
- product H1 arar,
- example query butonuna tıklar,
- ürün akışını doğrular.

Yeni test seti:
1. `/` public marketing smoke.
2. `/app` no-session → `/login?next=/app`.
3. Login/session sonrası `/app`.
4. Product browser flow artık `/app` üzerinde.
5. `/product`, `/how-it-works`, `/security`, `/solutions/textile-dyehouse` 200.
6. Marketing nav keyboard test.
7. 404 public kalır.
8. `/api` behavior değişmez.

## H. Güvenli migrasyon sırası

1. Baseline test çıktısını kaydet.
2. `/app` route'unu ekle fakat `/` geçici olarak product redirect olabilir.
3. Login/proxy/E2E'yi `/app` semantiğine geçir.
4. Product smoke test geçince `/` marketing page olsun.
5. Root/provider/layout ayrımını yap.
6. Marketing shell ve sayfaları ekle.
7. SEO ve production release.

Bu sıra, “önce marketing'i yazıp sonra auth kırığını çözme” riskini azaltır.
