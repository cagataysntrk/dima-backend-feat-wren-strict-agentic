# Stage 06 — Product and How It Works Pages

## Objective

Turn Dima's product architecture into two different pages: one outcome-led product overview and one mechanism-led trust explanation.

## Product page sections

- Ask: natural-language question input and question examples.
- Understand: modeled context and business definitions.
- Validate: guard and dry-plan.
- Explore: table, chart, KPI, pivot, or report surfaces only when verified.
- Verify: visible SQL/provenance/feedback.
- Reuse: contracts, schedules, or notifications only with capability status.
- Govern: permissions, tenant scope, and audit boundaries.
- Integrate: current/pilot/planned deployment and sources.

## How It Works sections

- Why raw text-to-SQL is not enough.
- What a modeled semantic layer adds.
- How the guard constrains query intent.
- What dry-plan validation checks.
- How execution and result presentation are separated.
- Where session, tenant, and permission controls apply.
- How SQL/provenance is shown.
- What validation does not promise.

## Tasks

1. Reuse the homepage proof primitives where the story is shared.
2. Make each page's hero answer its page intent; do not repeat the homepage verbatim.
3. Use diagrams and traces that can be read in source order by assistive technology.
4. Avoid adding backend calls to make marketing proof “real.”
5. Keep current/pilot/planned states visible wherever an implementation detail is not launch-ready.
6. Add links between the two pages and to Security/Integrations.

## Acceptance criteria

- Product page helps a buyer understand what they can do.
- How It Works page helps a technical buyer understand why the answer is trustworthy.
- Mechanism language is accurate and avoids absolute guarantees.
- Every visual has an accessible text equivalent.
- Deep links and heading hierarchy are correct.

## Verification

Run typecheck/lint/build, inspect desktop/mobile screenshots, check keyboard access to traces/accordions, and verify no product runtime is booted unnecessarily.

