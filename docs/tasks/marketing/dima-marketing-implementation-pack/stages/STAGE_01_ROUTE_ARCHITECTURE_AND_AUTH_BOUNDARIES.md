# STAGE 01 — Route Architecture and Authentication Boundaries

## Objective

Make `/` safely available for public marketing and move the single canonical authenticated product entrypoint to `/app`, without changing product behavior.

## Preconditions

- Stage 00 complete.
- Baseline failures, if any, understood.
- No unresolved user changes in route/auth files.

## Target

```text
app/
  layout.tsx
  (marketing)/page.tsx            # temporary minimal public shell
  (product)/app/layout.tsx
  (product)/app/page.tsx          # current product
  (auth)/...
```

The temporary `/` page can be minimal and factual. Full design is Stage 04.

## Tasks

1. Move current product root page to `/app`.
   - Do not duplicate the product component.
   - Preserve imports, state, mutations, report behavior and shell.
   - A shared internal component is acceptable if needed, but there must be one canonical route.

2. Split layout responsibilities:
   - root layout scroll-neutral,
   - product layout full-height/overflow-hidden,
   - marketing layout scrollable.

3. Split providers if root currently causes product runtime on public pages.
   - Keep locale/theme/reduced-motion as needed globally.
   - Keep QueryClient/AuthBootstrap/product runtime in protected product/auth boundary.
   - Do not create theme hydration regressions.

4. Update proxy:
   - protect `/app/:path*`,
   - preserve expired-cookie logic,
   - logged-in auth route → `/app`,
   - no session `/app` → login with `next`,
   - public marketing not gated,
   - unknown route can reach 404.

5. Audit and update exact root redirect/link assumptions.
   - Login success.
   - Logout.
   - Session restore.
   - Auth page redirect.
   - logo/home links.
   - test URLs.
   - docs comments where directly relevant.

6. Add route metadata:
   - `/app` noindex.
   - auth noindex.
   - temporary marketing metadata.

7. Update E2E:
   - product browser flow uses `/app`,
   - public `/` smoke,
   - auth redirect matrix.

8. Preserve API proxy and backend origin secrecy.

## Out of scope

- Full marketing page.
- New marketing design system.
- New analytics.
- Contact form.
- New dependencies.
- Product UI redesign.

## Required validation

```bash
pnpm lint
pnpm build
pnpm e2e
```

Manual/automated matrix:
- logged out `/`
- logged out `/app`
- logged in `/login`
- expired `/login?expired=1`
- unknown route
- product query flow at `/app`

## Acceptance criteria

- `/` public.
- `/app` protected.
- Existing product behavior unchanged.
- Root marketing scroll works.
- Product remains `h-dvh`/overflow-controlled.
- No anonymous backend query.
- No cross-user conversation regression.
- No duplicated product state entrypoint.

## Stage delivery report

At the end, return:

```markdown
# Stage Completion Report
## Summary
## Files changed
## Decisions
## Validation
## Accessibility
## Performance
## Security/auth regression
## Known limitations
## Deferred
## Next recommended stage
```

Do not commit or push unless explicitly requested. Stop after this stage.
