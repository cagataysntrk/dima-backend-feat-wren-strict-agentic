# Stage 02 — Content Model, i18n, Metadata, and SEO Foundations

## Objective

Create one typed, reviewable content system so page copy, capability status, metadata, and locale behavior do not drift across routes.

## Tasks

1. Inspect the existing locale implementation, translation files, next-intl configuration, and route strategy.
2. Preserve existing URLs unless a migration is explicitly approved. Do not invent locale-prefixed URLs or hreflang if the site does not support them.
3. Add a marketing namespace or typed content module following repository conventions.
4. Define capability statuses: available, pilot, and planned.
5. Store page titles, descriptions, navigation labels, CTA labels, FAQ, proof labels, capability notes, and claim source notes in one reviewable source.
6. Create route metadata for every launch page:
   - title;
   - description;
   - canonical;
   - Open Graph/Twitter fields;
   - indexability decision.
7. Define sitemap/robots behavior so public marketing is indexable and /app, auth, API, preview-only, and internal routes are not.
8. Add only evidence-backed JSON-LD. Do not add fake aggregate ratings, reviews, prices, or organization facts.
9. Check Turkish copy for natural phrasing and English copy for meaning and completeness.

## Content rules

- Homepage is broad but specific to trusted analytics.
- Product and How It Works explain mechanisms.
- Solutions starts with real questions.
- Textile page uses domain terminology without customer claims.
- Security and Integrations distinguish current, pilot, and planned.
- Pricing, blog, docs, and case studies remain deferred unless approved content exists.

## Acceptance criteria

- No marketing page contains scattered unverifiable feature literals.
- Every launch route has unique metadata and a clear indexability state.
- Locale switching does not break auth/product links or create false hreflang.
- Claims can be reviewed without reading component implementation.
- Long Turkish strings do not overflow navigation, cards, buttons, or metadata templates.

## Verification

Check route metadata in a production-like render, inspect sitemap/robots output, and run typecheck/lint. Include a claim review table in the stage report.

