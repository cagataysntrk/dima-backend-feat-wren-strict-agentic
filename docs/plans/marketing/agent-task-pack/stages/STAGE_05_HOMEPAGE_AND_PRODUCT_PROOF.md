# Stage 05 — Homepage and Deterministic Product Proof

## Objective

Build the homepage as a clear conversion narrative where the product mechanism is visible before decorative storytelling.

## Required section order

1. Hero: specific headline, short subhead, primary demo CTA, secondary product/how-it-works link.
2. Immediate proof frame.
3. D-I-M-A pillars.
4. Trust pipeline.
5. Use-case question gallery.
6. Textile/dyehouse wedge.
7. Security/governance.
8. Integrations/deployment status.
9. FAQ.
10. Final CTA and footer.

## Product proof requirements

Create a local, typed, deterministic simulation of:

1. user asks an operational question;
2. modeled tables/definitions appear;
3. SQL is constrained to the intended read-only shape;
4. dry-plan verification completes;
5. result renders as a chart/table/KPI;
6. provenance/SQL/trace can be inspected.

Use sanitized fictional data. Do not query the real API, expose a customer schema, or make a fictional metric look like a Dima benchmark.

The final state must be readable when JavaScript is disabled or reduced motion is enabled, subject to the repository's rendering model. Interactive transitions are an enhancement, not the only information channel.

## Copy requirements

Use real questions such as:

- “Makine bazında OEE ve fire oranı nedir?”
- “Termin riski taşıyan siparişler hangileri?”
- “Reçete bazında kimyasal maliyet nasıl değişiyor?”

Do not use unsupported outcome numbers or fake customer evidence.

## Acceptance criteria

- The first viewport explains who Dima is, why the category problem matters, and what action to take.
- Product proof is visible early and expresses the complete trust pipeline.
- Every large claim has a mechanism or status label nearby.
- CTA hierarchy is clear; there is one primary action.
- Mobile proof reflows into readable steps instead of shrinking a desktop screenshot.
- No anonymous network request is made by the homepage.

## Verification

Test interactive proof with keyboard and reduced motion, inspect network calls, compare Turkish/English line breaks, and run production build/route smoke.

