# STAGE 05 — Product and How It Works Pages

## Objective

Build `/product` and `/how-it-works` as complementary deep pages: one product-led, one mechanism-led.

## `/product` structure

1. Product hero
2. Ask
3. Modeled context
4. Validate
5. Explore (table/chart/KPI/pivot)
6. Verify/trace
7. Reuse/schedule, status-labeled
8. Govern
9. CTA

Every section should use real Dima surfaces or sanitized coded mockups.

## `/how-it-works` structure

1. Why raw text-to-SQL is insufficient
2. Connection and schema/model onboarding
3. Business semantics / MDL
4. NL interpretation
5. SELECT guard
6. Dry-plan
7. Execution
8. Result/provenance
9. Verify/reuse
10. Security boundary
11. Planned architecture, clearly labeled

## Technical accuracy rules

- Do not say dry-plan proves business correctness; it validates planning/semantic executability.
- Do not say SELECT-only eliminates all risk.
- Do not imply LLM directly executes arbitrary SQL.
- Distinguish model definitions from raw schema.
- Distinguish engine connector capability from Dima production-tested connector support.
- On-prem/thin agent must be status-labeled.

## Components

Prefer shared:
- workflow timeline,
- architecture diagram,
- product surface frame,
- capability status,
- code/SQL block,
- source/context callout.

Architecture diagram must have text alternative.

## SEO

Unique copy and metadata; do not duplicate homepage paragraphs.

## Validation

```bash
pnpm lint
pnpm build
```

Plus links, heading hierarchy, diagram accessibility, mobile reflow.

## Acceptance criteria

- Product page answers “What can I do?”
- How It Works answers “Why should I trust it?”
- Claims are nuanced and accurate.
- No heavy duplicated runtime.

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
