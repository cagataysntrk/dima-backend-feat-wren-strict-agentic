# FT-003 FAILURE RECEIPT — LIVE_SENTINEL_RED_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

FAILURE_ID:
`FT_003_LIVE_SENTINEL_RED_001`

OBSERVED_RUN:
`35770581158`

OBSERVED_SHA:
`9afe2529e58a28f6ff0be72eb9686f44d50cd224`

METABASE_BOOT:
`PASS`

INDEPENDENT_DB_ORACLE:
`PASS`

FAST_ASK_SENTINEL:
`FAIL`

FAILED_STEP:
`Run real Fast Ask API sentinel`

FAILURE_CLASS:
`EVAL_ORACLE`

## Independent DB oracle

Temporal window:

```text
2026-08-09 <= order_date < 2026-09-08
```

Observed independent values:

```text
COUNT = 20
SUM = 16270.00

BREAKDOWN
East  = 4085.00
North = 4015.00
South = 4050.00
West  = 4120.00
```

## Actual failure

The live test first proved numeric equality:

```python
assert _number(sum_body["result"]["rows"][0]["sum"]) == expected_sum
```

That assertion passed.

The next assertion failed:

```python
assert sum_body["answer"] == f"Sonuç: {expected_sum.normalize()}."
```

Actual traceback:

```text
AssertionError:
'Sonuç: 16270.' != 'Sonuç: 1.627E+4.'
```

Therefore:

```text
PRODUCT RESULT       = CORRECT
PRODUCT FORMATTER    = CORRECT
TEST STRING ORACLE   = WRONG
FAILURE CLASS        = EVAL_ORACLE
```

## Root cause

Python Decimal normalization changes representation:

```python
Decimal("16270.00").normalize()
```

may stringify as:

```text
1.627E+4
```

The product deliberately formats the same numeric value for presentation as:

```text
16270
```

Presentation formatting must not be changed to satisfy a scientific-notation artifact in the test oracle.

## Authorized patch

Patch only the live test oracle.

Required invariant:
- parse the numeric payload from the answer;
- compare its Decimal value to the independent DB Decimal value;
- keep the existing result-row numeric equality;
- do not require a scientific-notation display string.

## Forbidden patches

- change `deterministic_answer()`;
- change `_format_decimal()`;
- alter query builder;
- alter Metabase execution;
- weaken DB oracle;
- change expected business value;
- phrase-patch cognition;
- expand FT-003 scope.

## Focused re-proof

Re-run live workflow on current branch HEAD.

Required:
- COUNT = independent DB oracle;
- SUM = independent DB oracle;
- BREAKDOWN = independent DB oracle;
- exact temporal bounds;
- portable query evidence;
- access fingerprint;
- query fingerprint;
- result digest;
- raw SQL = 0;
- join = 0;
- Wren/V2/V3 = 0.

## Related artifact note

The old RED run did not upload `ft003-live-receipt.json` because the test aborted before receipt creation.
A new GREEN run must produce and upload a replacement receipt.
