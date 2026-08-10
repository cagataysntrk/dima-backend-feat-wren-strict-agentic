# Stage 03 — Design Tokens and Marketing Primitives

## Objective

Build the smallest coherent visual grammar that makes every marketing page feel like Dima without creating a parallel design system.

## Visual direction

Use Editorial Industrial Intelligence:

- existing Dima OKLCH tokens as the source of truth;
- warm editorial light surface and near-black inverse surface;
- indigo/violet accent used with restraint;
- Playfair Display for selected display moments;
- Plus Jakarta Sans for UI/body;
- JetBrains Mono for evidence, SQL, and trace details;
- hairline rules, subtle depth, strong reading measure, and controlled density.

## Tasks

1. Inspect existing globals, tokens, Tailwind/theme helpers, fonts, and icon setup.
2. Add only semantic marketing aliases needed for surface, inverse surface, grid, proof glow, section rule, and evidence states.
3. Establish responsive container, section spacing, type ramp, and reading column tokens.
4. Implement reusable primitives only where they express repeated meaning:
   - MarketingSection;
   - EvidenceLabel;
   - MarketingButton or existing CTA primitive;
   - PillarCard;
   - ProofFrame;
   - FeatureCard;
   - StepRail;
   - FAQItem;
   - Logo/wordmark treatment if needed.
5. Use semantic HTML and compose primitives without boolean-prop explosion.
6. Use Lucide or the existing icon system; no emoji icons.
7. Add motion presets for reveal, hover, and status pulse. Motion must use transform/opacity and reduced-motion fallbacks.
8. Make focus, disabled, hover, pressed, and current-link states explicit.

## Anti-patterns

- Generic purple gradient on white.
- Every section as the same card grid.
- Glow, border beam, marquee, and particle effects together.
- Hardcoded raw hex values inside components.
- Unlabeled icon-only controls.
- Animation that changes layout dimensions.

## Acceptance criteria

- Tokens are reusable and theme-aware.
- Primitives have accessible defaults and no page-specific fake data.
- At least one real page can compose the primitives without one-off CSS drift.
- 320px/375px layouts have no horizontal scroll.
- Reduced-motion renders a complete static state.

## Verification

Run UI quality/lint/typecheck. Inspect primitives in the routes that already use them and record any intentionally deferred visual work.

