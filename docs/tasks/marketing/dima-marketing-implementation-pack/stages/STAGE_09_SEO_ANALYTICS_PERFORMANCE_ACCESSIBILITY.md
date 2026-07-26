# STAGE 09 — SEO, Analytics, Performance and Accessibility Hardening

## Objective

Apply cross-cutting production hardening after all main pages exist.

## SEO tasks

1. Site URL env and metadataBase.
2. Root title template.
3. Unique metadata all public routes.
4. Canonicals.
5. Open Graph/Twitter.
6. 1200×630 Dima OG.
7. `sitemap.ts`.
8. `robots.ts`.
9. `/app`, auth, API noindex/disallow.
10. Organization JSON-LD.
11. Factual SoftwareApplication JSON-LD.
12. Real 404.
13. Internal link audit.
14. No hreflang for cookie-only locale.
15. Preview deployment noindex policy.

## Analytics tasks

1. Confirm provider and consent requirements.
2. Implement provider abstraction.
3. Add approved events.
4. Exclude PII/query/SQL/tenant data.
5. Respect Do Not Track/consent policy as required.
6. Verify events in preview.
7. Document event dictionary.

Do not install analytics provider without approval if none selected.

## Performance tasks

1. Run bundle/build analysis using available tooling.
2. Verify marketing chunks do not include:
   - React Query,
   - Zustand product stores,
   - React Flow,
   - chart libs,
   - product API client.
3. Optimize LCP.
4. Image sizes/formats.
5. Font loading.
6. Dynamic import only where useful.
7. CLS audit.
8. Remove unused effects/dependencies.
9. Test slow network/CPU if tooling permits.

## Accessibility tasks

WCAG 2.2 AA review:
- landmarks,
- headings,
- labels,
- keyboard,
- focus visible/not obscured,
- target size,
- contrast,
- reduced motion,
- zoom/reflow,
- form errors,
- mobile menu,
- accordion,
- diagrams,
- skip link,
- status announcement.

Use axe/Playwright if installed; do not add a large framework solely for one scan without justification.

## Required validation

```bash
pnpm lint
pnpm build
pnpm e2e
```

Plus Lighthouse/axe if available.

## Acceptance criteria

- Indexing surfaces correct.
- No duplicate metadata.
- No misleading structured data.
- No PII analytics.
- Marketing bundle separated from product-heavy code.
- No critical accessibility issue.
- Performance targets met or documented with exact blockers.

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
