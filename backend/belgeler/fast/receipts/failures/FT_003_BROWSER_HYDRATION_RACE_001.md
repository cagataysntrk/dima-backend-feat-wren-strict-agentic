# FT-003 FAILURE RECEIPT — BROWSER_HYDRATION_RACE_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

OBSERVED_RUN:
`35776518579`

OBSERVED_SHA:
`2635ecc26f8093b67636ba581e705a4ed132be6f`

FAILED_STEP:
`Browser proof over real Fast Ask + Metabase`

FAILURE_CLASS:
`EVAL_ORACLE_TIMING`

## Already passed in the same run

- pinned Metabase OSS boot;
- Fast-only Ask backend boot;
- Dima test access token;
- frozen frontend install;
- Next production build;
- isolated frontend start.

## Observed failure

```text
Error: timeout: loading state
```

The E2E saw the server-rendered FT-003 heading and immediately mutated/submitted the form.

Backend diagnostics contain:
- Fast health request;
- expected global-shell 404s for legacy auth/schema endpoints;
- no `POST /fast/ask` before the timeout.

Therefore the failed first submit did not reach the Fast Ask backend.

## Root cause

The oracle treated server-rendered page visibility as proof that the client React event handlers were already hydrated.

The heading can be visible before hydration is complete.

The first `form.requestSubmit()` can therefore race client hydration, causing:
- no Fast Ask request;
- no loading state;
- timeout.

This is not:
- a FastAskService defect;
- a Metabase defect;
- a retrieval defect;
- an evidence defect;
- a frontend product-state defect.

Previous real browser proof on the same product flow is GREEN.

## Authorized patch

Test-only E2E stabilization:
- after the FT-003 heading is observed, allow a bounded client-hydration settle interval before the first interaction;
- retain browser network latency so the loading state remains observable;
- do not change production UI/backend timing.

## Forbidden patches

- add artificial production UI delay;
- add production backend delay;
- remove loading-state proof;
- weaken real /fast/ask proof;
- replace real response with fixture;
- alter auth or Metabase behavior.

## Focused proof

Re-run FT-003 browser workflow.

Required:
- real `POST /fast/ask` observed;
- loading PASS;
- COUNT/SUM/BREAKDOWN PASS;
- chart/table PASS;
- clarification/unsupported/failed PASS;
- desktop PASS;
- 390x844 mobile PASS.
