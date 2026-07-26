# STAGE 10 — Testing, Release and Handoff

## Objective

Complete regression, release readiness, documentation and maintainable handoff.

## Automated tests

Expand/update tests for:

### Public routes
- `/`
- `/product`
- `/how-it-works`
- `/solutions`
- `/solutions/textile-dyehouse`
- `/security`
- `/integrations`
- `/about`
- `/contact`
- legal pages

### Auth
- logged out `/app`
- logged in auth redirect
- expired cookie
- logout/login conversation reset
- unknown route 404

### Product
- existing ask flow at `/app`
- schema/report UI
- no API proxy regression

### UI
- nav/mobile menu
- CTA links
- contact validation
- reduced motion where testable
- metadata/robots/sitemap basic assertions

## Visual QA

Capture/review:
- mobile,
- tablet,
- desktop,
- light/dark,
- TR/EN,
- long translations,
- 200% zoom,
- keyboard.

Do not approve screenshots containing real credentials/data.

## Content/claim review

Create final checklist:
- available/beta/planned,
- security claims,
- connector claims,
- customer proof permissions,
- legal approval,
- pricing omission/approval,
- contact owner.

## Documentation

Update:
- repo README route map,
- marketing architecture,
- content editing guide,
- asset guide,
- claim status guide,
- analytics events,
- deployment env,
- run/test commands.

## Release

1. Preview deployment.
2. Smoke.
3. Production env review.
4. Domain/canonical.
5. robots/sitemap.
6. form destination.
7. rollback plan.
8. release note.
9. monitoring owner.

## Required validation

```bash
pnpm lint
pnpm build
pnpm e2e
```

Run every available relevant test. Review final diff for:
- debug logs,
- TODO copy,
- dead links,
- placeholders,
- unexpected dependencies,
- broad formatting churn.

## Acceptance criteria

- Full route/auth/product regression passes.
- Production release checklist signed.
- Documentation sufficient for another developer.
- Known limitations explicit.
- Rollback path identified.

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
