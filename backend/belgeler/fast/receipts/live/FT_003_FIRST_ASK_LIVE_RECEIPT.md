# FT-003 — FIRST ASK LIVE METABASE RECEIPT

Status: GREEN / BACKEND LIVE GATE
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Certified run

RUN:
`35772731613`

TESTED_SHA:
`82471af5c34ed1d47b4d2e9d066a9dc1bbcaea7e`

ARTIFACT:
`dima-fast-ft003-live-82471af5c34ed1d47b4d2e9d066a9dc1bbcaea7e`

ARTIFACT_DIGEST:
`sha256:5360c4392afe0956d14c1eadfce1c62e89275a05df3964a76d8462b8d4593eef`

METABASE_RUNTIME:
`v0.63.18`

## Independent DB oracle

Window:

```text
2026-08-09 <= order_date < 2026-09-08
```

Oracle:

```text
COUNT = 20
SUM   = 16270.00

BREAKDOWN
East  = 4085.00
North = 4015.00
South = 4050.00
West  = 4120.00
```

## Real Fast Ask observations

COUNT:
- status = SUCCESS
- answer = `Sonuç: 20 kayıt.`
- result count = 20
- DB oracle equality = PASS

SUM:
- status = SUCCESS
- answer = `Sonuç: 16270.`
- result sum = 16270.0
- DB oracle numeric equality = PASS

BREAKDOWN:
- status = SUCCESS
- West = 4120.0
- East = 4085.0
- South = 4050.0
- North = 4015.0
- DB oracle map equality = PASS

## Evidence invariants

For all three live requests:
- exact temporal bounds present and correct;
- portable query present;
- access fingerprint present;
- query fingerprint present;
- result digest present;
- Metabase runtime version present;
- raw SQL/native query = 0;
- join = 0.

Fast-only architecture remains:
- Wren runtime dependency = 0;
- V2 runtime dependency = 0;
- V3 runtime dependency = 0.

## Field portable-FK upstream contract

Table:
`metabase://table/1`

Observed:

```text
amount:
  Metabase direct portable_fk = YES
  FieldRegistry fallback used = NO

order_date:
  Metabase direct portable_fk = YES
  FieldRegistry fallback used = NO

region:
  Metabase direct portable_fk = YES
  FieldRegistry fallback used = NO
```

For every selected field in this run:
- construct-query accepted = YES;
- execute accepted = YES;
- independent DB oracle matched = YES.

The same-table fallback remains implemented and provider-free tested, but it was not exercised by this pinned Metabase response because upstream supplied direct portable FKs.

## Prior RED closure

Old RED:
- run `35770581158`
- SHA `9afe2529e58a28f6ff0be72eb9686f44d50cd224`
- class `EVAL_ORACLE`

Cause:
`Decimal("16270.00").normalize()` produced scientific notation in the test expected string.

Fix:
- test answer is compared using Decimal numeric semantics;
- product `deterministic_answer()` unchanged;
- product `_format_decimal()` unchanged.

First corrected live run:
`35772434074` = GREEN.

Final current-line live run with safety/provenance work:
`35772731613` = GREEN.

## Gate decision

FT-003 LIVE BACKEND = GREEN.

FT-003 FINAL remains OPEN until:
- real-model cognition sentinel is classified;
- isolated frontend is connected to real `/fast/ask`;
- desktop/mobile browser proof is GREEN;
- final living status and seal are written.
