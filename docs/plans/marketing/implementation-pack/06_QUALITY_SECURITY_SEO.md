# 06 — Quality, Security, SEO and Release Gates

## 1. Definition of Done

Bir marketing stage yalnızca görsel olarak tamamlandığında bitmiş sayılmaz. Aşağıdaki kapılar geçmelidir:

- TypeScript strict compile
- ESLint
- production build
- route/auth regression
- responsive checks
- keyboard navigation
- reduced motion
- metadata/SEO
- no false claims
- no sensitive asset
- no product business logic regression

## 2. Performance budgets

### Mimari bütçe
- Marketing route'ları React Query, Zustand, React Flow ve chart runtime import etmez.
- WebGL/Three/particle canvas yok.
- Hero LCP element tek ve ölçülü.
- Fonts `next/font`.
- Images `next/image`, width/height reserved.
- Below-fold assets lazy.
- Client component adaları küçük.
- Heavy interactive proof dynamic import edilebilir, stable placeholder ile.

### Outcome targets
75. percentile field target:
- LCP ≤ 2.5s
- INP ≤ 200ms
- CLS ≤ 0.1

Lab target:
- Lighthouse mobile Performance ≥ 90
- Accessibility ≥ 95
- Best Practices ≥ 95
- SEO ≥ 95

Skorlar çevreye göre değişebilir; temel amaç stage öncesine göre regresyon yaratmamaktır.

## 3. Accessibility target

WCAG 2.2 AA baseline:

- Semantic landmarks.
- Tek H1.
- Logical heading order.
- Skip link.
- Keyboard-operable nav, menu, accordion, form.
- Visible focus; tercihen 2px solid perimeter ve 3:1 contrast.
- Minimum pointer target 24×24px; primary controls için practical 44×44px.
- Focus sticky header/modal altında kalmaz.
- Body text contrast minimum.
- Color tek bilgi taşıyıcısı değildir.
- Reduced motion.
- Images alt text.
- Decorative SVG `aria-hidden`.
- Form errors field ile programmatically associated.
- Status messages announced.
- No autoplay audio/video.
- 200% zoom ve 320px reflow.

## 4. Security gates

- Public page backend origin göstermemeli.
- Anonymous product query endpoint açılmamalı.
- Contact form server validation.
- Rate limit / honeypot / anti-abuse.
- User-provided content HTML olarak render edilmez.
- External links `rel` policy.
- No API key in `NEXT_PUBLIC_*`.
- No real customer data/screenshots.
- No admin URL/navigation.
- CSP eklenirse önce Report-Only ve Next/Motion inline style compatibility ölçümü.
- Existing security headers korunur.
- Dependency eklenirse license ve vulnerability kontrolü.

## 5. Auth regression matrix

| Durum | URL | Beklenen |
|---|---|---|
| Logged out | `/` | Marketing 200 |
| Logged out | `/product` | Public 200 |
| Logged out | `/app` | `/login?next=/app` |
| Logged in | `/login` | `/app` |
| Expired cookie flag | `/login?expired=1` | Cookie temizlenir, login görünür |
| Logged in | `/app` | Product app |
| Logged out | unknown URL | Public 404, login redirect değil |
| Any | `/api/*` | Existing proxy/backend auth semantics |

## 6. SEO checklist

- Unique title, description.
- Canonical.
- Open Graph 1200×630.
- Social image has safe margins and readable text.
- Sitemap only indexable public routes.
- Robots blocks app/auth/API.
- Product and auth `noindex`.
- JSON-LD validates.
- Internal link graph.
- No empty/duplicate pages.
- Turkish copy spellchecked.
- English copy human-reviewed before indexing.
- Site URL env correct in preview/prod.
- 404 returns real 404 status.

## 7. Analytics policy

Provider bağımsız event schema:

```text
marketing_page_view
marketing_nav_clicked
marketing_cta_clicked
marketing_demo_form_started
marketing_demo_form_submitted
marketing_demo_form_failed
marketing_faq_opened
marketing_product_proof_interacted
```

Event properties:
- page
- placement
- locale
- campaign/utm
- device class

Gönderilmemesi gereken:
- query content
- email/name/company
- database/schema name
- tenant slug
- SQL
- free-form form message

Consent ve privacy metni provider seçimine göre uygulanmalıdır.

## 8. Visual QA matrix

Viewport:
- 320×568
- 375×812
- 768×1024
- 1024×768
- 1440×900
- 1920×1080

Theme:
- light
- dark
- system

Language:
- TR
- EN, mevcutsa

Input:
- keyboard
- pointer
- touch simulation

Browser:
- Chromium
- Safari/WebKit
- Firefox

## 9. Test commands

Mevcut scriptlere göre:

```bash
pnpm lint
pnpm build
pnpm e2e
```

Stage 9/10'da mümkünse:
```bash
# Repo'ya uygun test tooling varsa
pnpm test
pnpm test:e2e
pnpm lighthouse
```

Olmayan script uydurulmaz; agent önce `package.json` kontrol eder.

## 10. Release checklist

- Clean git diff review.
- No debug logs.
- No temporary copy.
- No placeholder link.
- Forms point to production-safe endpoint.
- OG image current.
- Sitemap/robots current.
- Preview smoke.
- Production env.
- Rollback commit/PR identifiable.
- Product login/query/report smoke.
- Changelog entry.
- Owner sign-off on claims.
- Security sign-off on Security page.
- Legal sign-off on privacy/terms.
