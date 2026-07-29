# STAGE 03 — Shared Marketing Shell

## Objective

Build the reusable public navigation, mobile menu, footer, skip link and route-level shell.

## Tasks

1. Create typed navigation source.
2. Build desktop navbar:
   - wordmark,
   - Product,
   - How it works,
   - Solutions,
   - Security,
   - Integrations,
   - language,
   - Login,
   - Demo CTA.
3. Build accessible mobile menu:
   - semantic trigger,
   - focus management,
   - Escape,
   - close on navigation,
   - scroll lock,
   - 44px primary targets.
4. Build footer:
   - product links,
   - solutions,
   - company,
   - legal,
   - login/demo,
   - factual copyright/company.
5. Add skip-to-content.
6. Add active/hover/focus states.
7. Ensure sticky header never obscures focused content.
8. Ensure marketing layout has one `<main id="main-content">`.
9. Add minimal factual 404 using the shell.
10. Create typed nav/footer translation namespaces in TR and EN.
11. Do not link admin.
12. Do not create empty routes in navigation.

## Design requirements

- Header may be subtly floating or bordered, but not visually detached from Dima tokens.
- No glass with unreadable contrast.
- Header layout stable on scroll.
- Logo click → `/`.
- Login → `/login`.
- Demo → `/contact`.
- Product app link is “Giriş yap”, not an anonymous `/app` CTA.

## Out of scope

- Full homepage.
- Contact form backend.
- Mega-menu unless content truly requires it.
- Announcement banner without a real announcement.

## Validation

```bash
pnpm lint
pnpm build
```

Manual:
- keyboard tab order,
- screen-reader names,
- mobile open/close,
- no horizontal scroll,
- dark/light,
- TR/EN.

## Acceptance criteria

- Shell used by all marketing pages.
- No nav dead link.
- Mobile menu accessible.
- Product/auth layout unaffected.
- Focus never hidden.

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
