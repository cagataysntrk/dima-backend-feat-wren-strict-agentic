# FT-004 FAILURE RECEIPT — ASK_COMPATIBILITY_TEST_FIXTURE_001

Status: CLOSED / EVAL_ORACLE_FIXTURE_CONTRACT
Date: 2026-09-22

OBSERVED_RUN:
`35778348082`

OBSERVED_SHA:
`0e0a948202eac24bbdca05c954764d8a370f3d89`

FAILED_STEP:
`FT-004 API and SSE tests`

FAILURE_CLASS:
`EVAL_ORACLE_FIXTURE_CONTRACT`

FAILED_TEST:
`test_fast_ask_compatibility_endpoint_remains_available`

## Evidence

In the same run:
- compile = PASS;
- Fast boundary static = PASS;
- FT-004 lifecycle tests = 8 PASS;
- run API auth/ownership test = PASS;
- run snapshot/SSE replay test = PASS.

Failure:

```text
RuntimeError: FastAskService is not configured
app/fast/router.py:19
```

## Root cause

The existing sealed `/fast/ask` router intentionally requires:

```python
isinstance(app.state.fast_ask_service, FastAskService)
```

The new FT-004 API test supplied a standalone `ApiStubService` that did not inherit
`FastAskService`.

This is a test fixture contract violation. It is not evidence that:
- /fast/ask broke;
- run routing broke;
- SSE broke;
- lifecycle code should weaken the sealed Ask type boundary.

## Authorized patch

Test owner only:
`backend/tests/test_fast_run_api.py`

Make the API test double satisfy the existing `FastAskService` owner type while overriding
`ask()` so this focused HTTP test remains provider-free.

## Forbidden

- remove/relax `isinstance(..., FastAskService)` in production router;
- modify FT-003 Ask behavior;
- duplicate Ask implementation;
- change run state machine to satisfy compatibility test.

## Re-proof

Required:
- API/auth/SSE tests GREEN;
- /fast/ask compatibility test GREEN;
- FT-003 regressions execute and GREEN.


## Closure

Test-only corrective SHA:
`f8807c793db239fb23108346a8b615de5da4e00d`

Core closure run:
`35778574189 GREEN`

Final core run on live-sentinel SHA:
`35778861234 GREEN`

Production `FastAskService` type guard changed:
`NO`

`/fast/ask` compatibility:
`GREEN`

This failure is CLOSED.
