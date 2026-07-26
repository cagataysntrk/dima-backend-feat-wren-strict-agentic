# STAGE 04 — Homepage

## Objective

Build the complete public homepage at `/` with an original Dima-specific narrative and real product proof.

## Required section order

1. Hero
2. Product proof
3. D-I-M-A pillars
4. How it works
5. Use cases
6. Textile/dyehouse proof
7. Trust/security
8. Integrations/deployment
9. FAQ
10. Final CTA

## Hero content

Preferred:
- Eyebrow: `Güvenilir konuşmalı analitik`
- H1: `İşletme verinizle konuşun. Cevabın nasıl üretildiğini görün.`
- Subhead: modeled context + validation + report
- Primary: `Demo talep et` → `/contact`
- Secondary: `Giriş yap` → `/login`

Copy must live in i18n content, not hardcoded across components.

## Product proof

Build a deterministic public-safe visual:
- sample boyahane question,
- context tags,
- parse/catalog/plan/verify/run steps,
- `DRY-PLAN VERIFIED`,
- chart/table/KPI-like result,
- SQL or trace preview.

Rules:
- no real backend call,
- no auth bypass,
- no real customer data,
- no heavy chart runtime if CSS/SVG/HTML can render it,
- reduced-motion renders final stable state,
- mobile-specific composition.

## Pillars

D/I/M/A each explain a real mechanism.
Status-label Agentic/Beta/Planned if needed.

## Use cases

Each use-case card includes a realistic sample question, not only a noun.

## Textile proof

Link to `/solutions/textile-dyehouse`.
Use only sanitized demo terminology.

## Trust

Explain read-only guard, dry-plan, modeled context, SQL visibility, permissions/audit only to verified extent.

## FAQ

Use visible accessible content. Do not add FAQ schema until Stage 09 and only if policy/visibility match.

## Visual constraints

- no particles/WebGL,
- no rainbow CTA,
- no fake logo cloud,
- no fake stats,
- no fake testimonials,
- one primary visual motif,
- no autoplay carousel,
- avoid excessive client JS.

## Validation

```bash
pnpm lint
pnpm build
```

Checks:
- 320px,
- 375px,
- 768px,
- 1440px,
- light/dark,
- reduced motion,
- keyboard,
- LCP asset,
- no product dependency imports.

## Acceptance criteria

- User understands product, mechanism and target use cases within first screen + first proof.
- Every claim traceable to approved claim matrix.
- CTAs work.
- No public API call.
- Original Dima visual identity.

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
