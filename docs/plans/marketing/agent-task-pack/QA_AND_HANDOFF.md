# QA and Handoff Contract

Every stage ends with an evidence-backed report. “Looks good” is not a test result.

## Required stage report

```markdown
# Stage Completion Report

## Scope
- Stage:
- Routes:
- Primary user outcome:

## Files changed
- path — reason

## Decisions
- content:
- visual:
- architecture:

## Validation
- `command` — PASS/FAIL — relevant result

## Visual checks
- 320/375/768/1024/1440:
- light/dark:
- Turkish/English:
- keyboard/mobile menu:

## Security and regression checks
- public route:
- auth route:
- product `/app`:
- API/proxy:

## Known limitations
## Deferred work
## Next stage
```

## Stage acceptance gates

### Code and architecture

- Strict TypeScript and existing lint rules pass.
- Server Components are used by default; client islands have a reason.
- Marketing pages do not import product QueryClient, Zustand, React Flow, chart runtime, or API client without a written justification.
- No backend origin, secret, tenant identifier, customer data, or admin URL leaks into the public page.
- No unrelated refactor or broad formatting churn.

### UX and accessibility

- Semantic landmarks and one `h1` per page.
- Keyboard navigation, visible focus, focus management, and Escape behavior work.
- Primary touch targets are practical 44×44px; icon-only buttons have labels.
- Contrast is checked, not assumed.
- Reduced motion renders a readable final state.
- 320px reflow and 200% zoom do not hide content or create horizontal scroll.
- Form labels, errors, status updates, and menu states are announced semantically.

### Performance

- Hero media reserves space and does not introduce avoidable layout shift.
- Non-critical images and heavy proof UI are lazy or route-split where appropriate.
- No animation of layout properties for decorative motion.
- Marketing route does not boot the authenticated product runtime.

### SEO and content

- Unique title, description, canonical, social metadata, and indexability decision.
- Public routes are in the sitemap only when ready; app/auth/API remain excluded.
- All claims are available/pilot/planned or removed.
- Turkish and English copy are reviewed for meaning, not only syntax.

## Recommended validation order

Run from `frontend` and inspect `package.json` first:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm quality:ui
pnpm e2e
```

If a script is absent or already fails on baseline, report the exact command and failure. Do not weaken configuration or hide the test.
