# STAGE 02 — Marketing Design System and Primitives

## Objective

Create the Dima-specific marketing visual system using existing Tailwind 4/OKLCH tokens and minimal reusable primitives. Do not build full pages yet.

## Design direction

Editorial Industrial Intelligence:
- warm editorial surfaces,
- near-black inverse sections,
- indigo-violet brand accent,
- thin rules,
- technical mono evidence labels,
- product proof over decoration,
- restrained motion.

## Tasks

1. Audit existing tokens and component primitives.
2. Add only missing semantic marketing tokens.
3. Define typography utilities/components:
   - display,
   - section heading,
   - body,
   - eyebrow,
   - mono evidence.
4. Build primitives:
   - `MarketingContainer`
   - `MarketingSection`
   - `SectionHeader`
   - `EvidenceLabel`
   - `MarketingButton` variants or extend existing Button safely
   - `ProofFrame`
   - `PillarCard`
   - `StatusBadge`
   - `SectionRule`
5. Define motion wrappers using existing presets:
   - reveal,
   - stagger,
   - reduced-motion final state.
6. Build a development-only visual showcase route or Storybook story only if the repo already supports that pattern. Do not expose an unfinished public route.
7. Add design documentation:
   `docs/marketing/01-design-system.md`
8. Inspect UpcyMan's design system and marketing primitives read-only; reimplement, do not copy wholesale.
9. Verify both light and dark themes.
10. Verify 320px–1920px behavior.

## Dependency policy

No new dependency by default. A new primitive package requires:
- feature gap,
- bundle impact,
- license,
- exact components imported,
- reason existing Radix/custom components are insufficient.

## Accessibility

- focus ring visible,
- target sizes,
- semantic heading API,
- no div-as-button,
- contrast,
- reduced motion,
- decorative SVG semantics.

## Out of scope

- Navbar/footer.
- Homepage composition.
- Content claims.
- Product route changes.
- New chart libraries.

## Required validation

```bash
pnpm lint
pnpm build
```

Also inspect generated CSS/client boundaries.

## Acceptance criteria

- Existing product tokens not broken.
- Marketing primitives are original and Dima-branded.
- No UpcyMan runtime coupling.
- No effect soup.
- No unnecessary client boundary.
- Dark/light accessible.

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
