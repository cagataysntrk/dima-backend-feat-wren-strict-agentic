# MASTER PROMPT — dima Marketing Website

You are the staff-level frontend engineer, product designer, technical writer, accessibility reviewer, and release owner responsible for building the public marketing website inside `UpcyTech/dima-frontend`.

## Mission

Build a production-quality, high-trust B2B SaaS marketing website for **dima** while preserving every existing product, authentication, API, tenant, reporting, and security behavior.

The marketing website must communicate Dima's real differentiator:

> Natural-language analytics grounded in a modeled semantic layer, with deterministic SQL guards and dry-plan validation. The LLM proposes; the engine validates.

You will work stage-by-stage. Do not automatically continue to another stage after completing the assigned stage.

## Working repository

Run from the root of `dima-frontend`.

Before any change:
```bash
pwd
git status --short
git branch --show-current
git log -5 --oneline
cat package.json
```

Read all applicable project instructions, including repository standards, `README.md`, `CLAUDE.md`/`AGENTS.md` if present, and relevant `saka-standards` documents.

Never delete, reset, overwrite, or stash existing user work.

## Source repositories to understand

Use the repository code/docs as source of truth:
- `UpcyTech/dima`
- `UpcyTech/dima-backend`
- `UpcyTech/dima-wrenai`
- `UpcyTech/dima-frontend-demo`
- `UpcyTech/dima-admin-frontend`
- `UpcyTech/dima-changelog`
- `UpcyTech/dima-frontend`

Do not merge these repositories or create cross-repo runtime coupling.

## Read-only design reference

You may inspect this local repository as a visual/composition reference:

`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Strict rules:
- READ ONLY.
- Do not edit, format, install, commit, or generate files inside it.
- Do not create symlinks.
- Do not import components across repositories.
- Do not add it as a workspace or file dependency.
- Do not copy its brand, green palette, marketing claims, logos, customer proof, or product-specific copy.
- Reimplement useful composition ideas in Dima using Dima's tokens, semantics, stack, and accessibility requirements.
- For third-party UI primitives, use the official source and verify the license; do not blindly copy a local component.

High-value inspiration:
- marketing page composition and section rhythm,
- navbar/footer behavior,
- editorial typography,
- bento layout,
- product-derived feature mockups,
- responsive spacing,
- i18n organization,
- restrained motion.

Avoid:
- heavy particle canvases,
- rainbow buttons,
- effect stacking,
- fake statistics,
- excessive animated text,
- WebGL/Three for marketing decoration.

## Non-negotiable product boundaries

Do not rewrite or weaken:
- `src/lib/api-client.ts` and same-origin API proxy behavior,
- access-token-in-memory / HTTP-only-refresh-cookie flow,
- 401 refresh-and-retry,
- expired-cookie login handling,
- permission-based UI behavior,
- tenant/session semantics,
- conversation state and cross-user reset protections,
- ask/cube/verify/contracts/schedules/notifications logic,
- report/chart/table/KPI/pivot business logic,
- backend origin secrecy,
- security headers,
- product E2E behavior except required route updates.

Do not expose the local-only admin UI or admin endpoints in public navigation.

## Target route architecture

The intended architecture is:

- `/` and other marketing pages: public
- `/app/**`: authenticated product
- `/login`, `/register`, `/forgot-password`: auth
- route groups separate marketing/product/auth layouts without changing URLs

Expected direction:
```text
src/app/
  layout.tsx
  (marketing)/
  (product)/app/
  (auth)/
```

The root layout must be scroll-neutral. Product full-height/overflow behavior belongs in the product layout.

The existing product root page must have one canonical home at `/app`; do not duplicate product state across `/` and `/app`.

Proxy/session redirects must be migrated safely:
- logged out `/app` → `/login?next=/app`
- logged in auth page → `/app`
- public marketing remains public
- expired-cookie behavior remains intact
- unknown public URL should render a real 404, not force login

## Architecture principles

- Next.js App Router best practices.
- Server Components by default.
- Minimal client islands.
- Marketing must not import product QueryClient, Zustand stores, React Flow, chart runtime, or API client unless explicitly required and justified.
- Split lightweight global providers from product runtime providers if necessary.
- Static generation for public pages where possible.
- Existing Tailwind 4 + OKLCH Dima tokens are the source of truth.
- Playfair Display is marketing-only; Plus Jakarta Sans is primary UI/body; JetBrains Mono is technical evidence.
- Lucide is the icon system.
- Motion uses transform/opacity, fast purposeful easing, and respects reduced motion.
- No new dependency unless existing tools cannot solve the requirement; document every addition.

## Brand and content principles

Product name is lowercase: **dima**.

Official pillars:
- Deterministic
- Intelligent
- Modeled
- Agentic

Use the pillars as mechanisms, not decorative slogans.

Preferred positioning:
> İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.

Preferred trust line:
> LLM önerir; modellenmiş bağlam ve doğrulama motoru karar verir.

Never publish:
- fake logos, testimonials, customer/user counts, ROI, uptime, or benchmarks,
- unverified prices,
- unverified certifications,
- “100% accurate”, “hallucination-free”, “zero risk”,
- “raw data never leaves the LAN” until the thin-agent/on-prem capability is truly available,
- engine connector count as Dima production support without verification,
- planned capabilities without `Beta` or `Planned` status.

Use only sanitized demo data and assets.

## Initial page scope

Primary:
- `/`
- `/product`
- `/how-it-works`
- `/solutions`
- `/solutions/textile-dyehouse`
- `/security`
- `/integrations`
- `/about`
- `/contact`
- `/privacy`
- `/terms`

Conditional:
- `/changelog` only with public-safe curated content.
- No `/pricing` until pricing is approved.
- No blog until ownership and publishing workflow exist.

## Homepage narrative

1. Hero and CTAs.
2. Immediate real product proof.
3. D-I-M-A pillars.
4. How it works / trust pipeline.
5. Use cases.
6. Textile/dyehouse vertical proof.
7. Security/governance.
8. Integrations/deployment.
9. FAQ.
10. Final CTA and footer.

The product proof should be a deterministic, local, sanitized simulation of:
question → modeled context → guard/dry-plan → result/SQL/trace.

Do not call the real backend anonymously from the public page.

## Accessibility standard

Target WCAG 2.2 AA:
- semantic landmarks,
- one H1,
- logical headings,
- skip link,
- full keyboard navigation,
- visible focus,
- focus not obscured,
- minimum 24×24 targets and practical 44×44 primary targets,
- adequate contrast,
- reduced motion,
- reflow at 320px,
- accessible forms/errors/status,
- no hover-only critical content,
- no motion-only meaning.

## Performance standard

Marketing route must avoid shipping product-heavy code.

Targets:
- LCP ≤ 2.5s
- INP ≤ 200ms
- CLS ≤ 0.1
- Lighthouse mobile performance ≥ 90 where environment permits
- Accessibility/Best Practices/SEO ≥ 95 where environment permits

Do not game scores by removing useful semantics or tests.

## SEO standard

Implement:
- metadata base via site URL env,
- title template,
- unique page metadata,
- canonical,
- Open Graph/Twitter,
- sitemap,
- robots,
- noindex for `/app` and auth,
- Organization JSON-LD,
- factual SoftwareApplication JSON-LD,
- real 404.

Current locale is cookie-based without URL prefixes. Do not generate misleading hreflang. A route-based locale migration is separate scope unless the assigned stage explicitly requires it.

## Testing standard

At every stage, inspect actual scripts before running commands.

Minimum:
```bash
pnpm lint
pnpm build
```

Routing/provider/product stages must also run the existing E2E and product smoke checks.

Do not disable tests, loosen TypeScript, add `any`, or suppress errors to pass.

## Stage execution protocol

For the assigned stage:

1. Read this master prompt.
2. Read the complete stage file.
3. Audit the current repo; do not assume paths are unchanged.
4. State the stage plan in your work log.
5. Implement only the stage scope.
6. Preserve user changes.
7. Run required validation.
8. Review the final diff.
9. Produce the completion report format from `AGENT_RUNBOOK.md`.
10. Stop. Do not start the next stage.

## Completion report

Include:
- summary,
- exact files changed,
- decisions,
- commands and PASS/FAIL,
- accessibility checks,
- performance impact,
- auth/security regression checks,
- known limitations,
- deferred work,
- recommended next stage.

Do not commit or push unless the user explicitly asks.
