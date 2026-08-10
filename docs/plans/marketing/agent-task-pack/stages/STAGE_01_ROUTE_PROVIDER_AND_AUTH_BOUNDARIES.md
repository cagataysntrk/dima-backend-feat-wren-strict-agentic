# Stage 01 — Route, Provider, and Auth Boundaries

## Objective

Make public marketing pages reachable without booting or weakening the authenticated product runtime.

## Likely files to inspect

- apps/web/src/app/layout.tsx
- apps/web/src/app/(marketing)/layout.tsx
- apps/web/src/app/(product)/...
- apps/web/src/app/(auth)/...
- apps/web/src/proxy.ts or current middleware/proxy
- apps/web/src/lib/providers.tsx
- API client/session helpers
- route-dependent E2E tests

Use the actual repository structure; do not assume these paths exist.

## Tasks

1. Create or complete route groups so public marketing, auth, and /app/** product layouts are separate without changing public URLs.
2. Make the root document scroll-neutral for long marketing pages.
3. Keep product full-height/overflow behavior inside the product boundary.
4. Split product-only providers from lightweight marketing providers if the current root provider boots product state globally.
5. Update the proxy/session rules minimally:
   - public marketing routes stay public;
   - logged-out /app redirects to /login?next=/app;
   - logged-in auth routes redirect to /app;
   - expired-cookie behavior remains intact;
   - unknown public routes return a real 404.
6. Preserve backend origin secrecy and existing API proxy behavior.
7. Add or update targeted route tests.

## Acceptance criteria

- / renders a public shell while /app renders the authenticated product shell.
- Marketing pages do not instantiate QueryClient/Zustand/product runtime by default.
- Auth and product smoke tests still pass.
- No anonymous backend request is introduced.
- Route groups do not duplicate product state or redirect public pages to login.

## Verification

Test at minimum:

~~~text
logged out: /, /product, /app, /login, /unknown
logged in: /login, /app
expired cookie: /login?expired=1
~~~

## Handoff

Report exact changed boundaries, provider decisions, and the regression matrix before moving to Stage 02.

