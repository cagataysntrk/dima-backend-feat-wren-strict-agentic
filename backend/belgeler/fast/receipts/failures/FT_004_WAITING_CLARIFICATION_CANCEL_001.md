# FT-004 FAILURE RECEIPT — WAITING_CLARIFICATION_CANCEL_001

Status: CLOSED / RUN_STATE_MACHINE_IMPLEMENTATION
Date: 2026-09-22

OBSERVED_RUN:
`35778100380`

OBSERVED_SHA:
`c14c60fc2c718212b6a78ab98fe47c34d47e2e40`

FAILED_STEP:
`FT-004 lifecycle tests`

FAILURE_CLASS:
`RUN_STATE_MACHINE_IMPLEMENTATION`

FAILED_TEST:
`test_clarification_waits_then_can_be_cancelled`

## Observed

Expected:

```text
WAITING_CLARIFICATION
-> CANCEL_REQUESTED
-> CANCELLED
```

Actual returned state:

```text
CANCEL_REQUESTED
```

## Root cause

`FastRunManager.cancel_run()` reads the original snapshot and correctly allows
`WAITING_CLARIFICATION -> CANCEL_REQUESTED`.

After that transition, however, the local `snapshot` variable has already become:

`CANCEL_REQUESTED`

The implementation then checks:

```python
snapshot.state == FastRunState.WAITING_CLARIFICATION
```

which can no longer be true.

A completed worker future may also remain briefly present in the manager map because a very fast
worker can finish around future registration/removal timing. Future presence alone is therefore
not valid proof of an active worker.

## Correct lifecycle semantics

WAITING_CLARIFICATION is quiescent:
- there is no analytical work that should continue;
- cancel should become terminal immediately;
- the run must emit CANCEL_REQUESTED then RUN_CANCELLED;
- terminal event exactly once.

For RUNNING:
- cancellation remains cooperative;
- late analytical success may not overwrite CANCEL_REQUESTED/CANCELLED.

## Authorized patch

Owner:
`backend/app/fast/run_manager.py`

Required:
1. preserve the pre-cancel state;
2. WAITING_CLARIFICATION -> immediate CANCELLED after CANCEL_REQUESTED;
3. treat absent/done/cancelled future as no active worker;
4. handle terminal-vs-cancel transition race by returning the already-terminal canonical snapshot;
5. do not change FT-003 Ask/query/evidence code.

## Forbidden

- change state definitions to satisfy the test;
- make WAITING_CLARIFICATION terminal;
- remove CANCEL_REQUESTED event;
- change FastAskService;
- add hard query cancellation;
- weaken terminal exactly-once.

## Re-proof

Required:
- clarification cancel test GREEN;
- running cancel late-success discard GREEN;
- terminal cancel idempotent GREEN;
- API/SSE tests run;
- FT-003 regressions run.


## Closure

Corrective product SHA:
`0e0a948202eac24bbdca05c954764d8a370f3d89`

Core closure run:
`35778574189 GREEN`

Final core/live-test SHA run:
`35778861234 GREEN`

Real pinned-Metabase clarification/cancel proof:
`35778861380 GREEN`

Observed real sequence:
```text
RUN_CREATED
RUN_STARTED
RUN_WAITING_CLARIFICATION
CANCEL_REQUESTED
RUN_CANCELLED
```

Final state:
`CANCELLED`

Terminal event:
exactly one.

This failure is CLOSED.
