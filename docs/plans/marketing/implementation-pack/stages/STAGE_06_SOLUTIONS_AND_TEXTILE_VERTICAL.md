# STAGE 06 — Solutions and Textile/Dyehouse Vertical

## Objective

Build `/solutions` and `/solutions/textile-dyehouse` with concrete jobs-to-be-done and sector-specific product proof.

## `/solutions`

Group by outcome, not org chart only:
- Executive visibility
- Production/OEE
- Sales/customer
- Finance/KPI
- Inventory/supply
- Data/IT governance

Each card:
- problem,
- sample question,
- Dima mechanism,
- expected output,
- link/deep CTA.

## `/solutions/textile-dyehouse`

### Required narrative

1. Vertical hero
2. Data landscape
3. Real questions
4. Production/OEE
5. Fire/quality
6. Recipe/chemical
7. Water/energy
8. Orders/deadlines/shipments
9. Integration/onboarding
10. Demo CTA

### Demo model vocabulary

Use only sanitized/public demo terms:
- partiler
- vardiya kayıtları
- siparişler
- sevkiyatlar
- reçete/kimyasal
- makineler
- müşteriler
- personel
- fire
- OEE
- renk sapması
- su/enerji
- termin

### Proof

- data relationship mini-map,
- sample query cards,
- one realistic result visual,
- no real customer data,
- no claim of direct Egemen integration unless actually implemented and approved.

### Industry tone

Avoid pretending Dima is a full MES/ERP. Clearly position it as an analytics/context/reporting layer over operational data.

## SEO/content

- Turkish industrial terminology.
- Unique metadata.
- No keyword stuffing.
- Add internal links to Product, How It Works, Security and Contact.

## Validation

```bash
pnpm lint
pnpm build
```

Check:
- diagram reflow,
- screen-reader alternative,
- claim status,
- no customer trademark misuse,
- mobile.

## Acceptance criteria

- A dyehouse operator can recognize their workflow.
- Dima scope is clear.
- Vertical page contains real proof, not generic factory imagery.

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
