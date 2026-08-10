# Stage 10 — Quality, Analytics, Performance, Visual QA, and Release

## Objective

Prove that the marketing site is production-ready and has not regressed auth, product, accessibility, SEO, or security behavior.

## Functional QA

Run the scripts that actually exist in dima-frontend/package.json:

~~~bash
pnpm lint
pnpm typecheck
pnpm test
pnpm quality:ui
pnpm e2e
~~~

Run targeted route smoke for all launch pages. Record baseline failures separately from new failures.

## Visual QA matrix

Check:

- 320×568;
- 375×812;
- 768×1024;
- 1024×768;
- 1440×900;
- 1920×1080.

For each relevant route, inspect:

- light and dark theme;
- Turkish and English;
- keyboard navigation;
- mobile menu open/close;
- reduced motion;
- 200% zoom;
- no horizontal overflow;
- sticky header/focus offset;
- form loading/success/error.

## Accessibility gate

Verify:

- one H1 and logical heading order;
- landmarks and skip link;
- visible focus;
- keyboard-operable menu, accordion, CTA, proof, and form;
- labels/errors/status announcements;
- meaningful alt text and decorative image semantics;
- color is not the only meaning;
- contrast;
- 44px practical primary targets;
- reduced-motion final state;
- 320px reflow and 200% zoom.

## Performance gate

Inspect:

- marketing route does not boot product providers;
- hero media dimensions reserve layout space;
- images are optimized/lazy where appropriate;
- client islands are small;
- no unnecessary third-party script;
- no layout-property animation;
- no anonymous network calls from proof UI;
- route-level loading and error behavior.

Target outcomes, subject to the repository baseline:

- LCP ≤ 2.5s at p75;
- INP ≤ 200ms;
- CLS ≤ 0.1;
- Lighthouse mobile performance/accessibility/best practices/SEO ≥ 90/95/95/95 where tooling is available.

## SEO and analytics gate

- Check title, description, canonical, OG, sitemap, robots, JSON-LD, and 404 status.
- Keep /app, auth, API, and internal routes out of the public index.
- Use provider-independent events only for approved marketing interactions.
- Never send name, email, company, free-form message, SQL, schema, tenant, or query content to analytics.
- Apply consent/privacy rules for the chosen provider.

## Security/regression gate

- public marketing remains public;
- logged-out /app redirects correctly;
- logged-in auth redirects correctly;
- expired-cookie handling remains intact;
- product /app and its query/report/session behavior still work;
- API proxy and backend origin secrecy are unchanged;
- admin routes are not linked;
- no secrets or PII are in the diff.

## Release handoff

Provide:

1. stage completion report;
2. route/metadata table;
3. visual screenshots or a reproducible screenshot command;
4. test command results;
5. claim review and known limitations;
6. deferred pages/content dependencies;
7. rollback-safe diff summary;
8. recommended post-launch monitoring events.

Do not mark release ready when a legal, product-claim, endpoint, or authentication dependency is unresolved.

