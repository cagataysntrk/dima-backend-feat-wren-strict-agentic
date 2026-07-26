# STAGE 08 — Company, Resources, Legal and Contact

## Objective

Complete the supporting marketing surface: `/about`, optional `/changelog`, `/contact`, `/privacy`, `/terms`.

## `/about`

Include only verified facts:
- Dima product purpose.
- UpcyTech relationship.
- Product principles.
- Why modeled/deterministic analytics.
- Team/company details only if approved.
- No fabricated office, customer or investor claims.

## `/changelog` — conditional

Build only if there is a safe publishing source.

Private `dima-changelog` must not be streamed directly to public users.

Public entry should:
- be curated,
- omit SHAs/internal hosts/credentials/operational details,
- use user-facing Added/Changed/Fixed language,
- have date and version,
- be static at build or imported from a public-safe content file.

If safe source does not exist, defer page and remove nav link.

## `/contact`

Implement:
- typed validation,
- accessible labels/errors,
- success/error/retry,
- server-side processing,
- anti-abuse,
- privacy acknowledgement,
- no PII analytics.

Do not fake successful submission if endpoint is missing. Use an explicit development-safe state and document backend requirement.

## `/privacy` and `/terms`

Do not invent legal commitments. Use:
- approved legal copy,
- clearly marked review status,
- effective date,
- contact channel.

If legal text is unavailable, create structurally complete placeholders marked `LEGAL REVIEW REQUIRED` in non-production content and block production release.

## Metadata

Unique titles and descriptions.

## Validation

```bash
pnpm lint
pnpm build
```

Contact:
- keyboard,
- server validation,
- rate limit behavior,
- error messages,
- network failure,
- success state.

## Acceptance criteria

- No empty/dead page.
- Contact submission is honest.
- Legal review status explicit.
- Private changelog data not exposed.

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
