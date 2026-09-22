# FT-005 FAILURE RECEIPT — MODEL_E2E_RED_001

Status: OPEN / COGNITION ROOT CAUSE NOT YET VISIBLE
Date: 2026-09-23

OBSERVED_RUN:
`35786695054`

OBSERVED_SHA:
`68c53f4d1247a1fe813ebaf6bcc901916f6f2660`

MODEL_ROLE:
`THIRD_MODEL_DIAGNOSTIC`

EXACT_MODEL_ID:
`google/gemini-2.5-flash-lite`

PROVIDER:
`openrouter`

## What passed before the RED

Pinned Metabase startup:
`GREEN`

Independent DB oracle:
```text
Q1 last-30-day SUM = 16270
Q2 previous-month SUM = 21994
Q3 previous-month breakdown:
East = 5523
North = 5425
South = 5474
West = 5572
```

Therefore this receipt is not classified as a Metabase, DB, or run-lifecycle failure.

## Observed failure

The E2E stopped before a usable first analytical turn was established:

`FastAskError: COGNITION_UNAVAILABLE: structured cognition failed for dima_fast_followup_resolution`

Receipt had:
- turns = [];
- followup_calls = [];
- gateway_revalidation = [].

Thus no claim is made yet about:
- current metadata revalidation;
- query correctness;
- evidence lineage;
- DB equality for the three-turn chain.

Those gates were never reached.

## Failure class

`MODEL_STRUCTURED_OUTPUT_RELIABILITY / INNER_CAUSE_UNKNOWN`

Do not patch the prompt or product semantics until the eval harness exposes:
- provider transport success/error;
- raw requested structured action JSON or safe digest;
- parse success;
- validation error type/path;
- latency;
- token usage when available.

No chain-of-thought or reasoning text may be recorded.

## Re-proof contract

After diagnostics:
- preserve this RED;
- repeat current Gemini diagnostic;
- run Luna baseline and Sol ceiling with frozen inputs/contracts;
- only after classification may a minimal fix be authorized.

FT-005 remains OPEN.
