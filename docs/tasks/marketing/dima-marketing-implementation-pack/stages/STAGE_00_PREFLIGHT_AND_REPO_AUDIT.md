# STAGE 00 — Preflight, Baseline and Repository Audit

## Objective

Create a verified baseline before any marketing implementation. This stage produces documentation and, only if necessary, non-behavioral test helpers. It must not redesign pages.

## Required reading

- `MASTER_PROMPT.md`
- `AGENT_RUNBOOK.md`
- repo `README.md`
- `package.json`
- all repo instruction files
- `src/app/**`
- `src/proxy.ts`
- `src/lib/providers.tsx`
- `src/lib/api-client.ts`
- auth pages
- `messages/*.json`
- `e2e/**`
- `next.config.ts`
- `vercel.json`

Read-only reference:
`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

## Tasks

1. Record:
   - branch,
   - HEAD SHA,
   - uncommitted files,
   - Node/pnpm versions,
   - available scripts,
   - current route tree,
   - current provider tree,
   - current proxy matcher,
   - current auth redirect targets,
   - current metadata/robots/sitemap state.

2. Build a route/auth dependency map:
   - every exact `/` redirect or link,
   - every `router.push("/")`, `replace("/")`, `redirect("/")`,
   - every test assuming `/`,
   - all page access decisions.

3. Build a client-bundle risk map:
   - which root providers are client-side,
   - which heavy product dependencies could leak into marketing,
   - which page/component is `"use client"`.

4. Run baseline:
   ```bash
   pnpm lint
   pnpm build
   pnpm e2e
   ```
   Use actual scripts only.

5. Create/update a repo-local planning document such as:
   `docs/marketing/00-baseline-audit.md`
   Include exact findings; do not duplicate the entire external pack.

6. Identify files that are likely to be touched in Stage 01 and mark risk level.

## Out of scope

- No route move.
- No marketing components.
- No visual design.
- No dependency changes.
- No auth logic rewrite.
- No broad formatting.

## Acceptance criteria

- Baseline commands and results documented.
- All root-route assumptions identified.
- All protected/public routes identified.
- Product business logic boundaries listed.
- UpcyMan reviewed read-only; no modifications.
- Working tree preservation confirmed.

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
