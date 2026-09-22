# FT-004 FAILURE RECEIPT — POST_SEAL_CANCEL_START_RACE_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

OBSERVED_RUN:
`35781293132`

OBSERVED_SHA:
`4849fd9480142e95330a9fc87ffdcd656303090b`

FAILURE_CLASS:
`RUN_START_CANCELLATION_RACE`

## Deterministic setup

A barrier-controlled FastRunStore paused the worker:
- after the worker's CREATED pre-check;
- immediately before the CREATED -> RUNNING transition.

While paused, cancel transitioned:

```text
CREATED -> CANCEL_REQUESTED
```

The worker was then released.

No sleeps were used to create the race.

## Observed

Final lifecycle:
`CANCELLED`

RUN_STARTED events:
`0`

But:

`FastAskService.calls = 1`

Expected:

`FastAskService.calls = 0`

## Root cause

`FastRunManager._execute()` calls generic `_safe_transition(... RUNNING ...)`.

When the state has already become CANCEL_REQUESTED, the RUNNING transition correctly raises
`FastRunTransitionError`, but `_safe_transition()` converts that error to the canonical
snapshot and returns it.

`_execute()` ignores the returned state and calls `FastAskService.ask()` anyway.

Late result authority is discarded, so numeric authority was not violated, but the explicit
FT-004 contract "cancel before execution -> Ask call = 0" is violated.

## Authorized patch

Owner:
`backend/app/fast/run_manager.py`

- create a start-transition path with explicit race semantics;
- if RUNNING transition loses specifically to CANCEL_REQUESTED, finalize CANCELLED and return;
- if already terminal, return;
- only call FastAskService after an actually successful RUNNING transition;
- do not broaden generic `_safe_transition()`;
- unexpected invalid transitions must not be silently classified as expected races.

## Forbidden

- sleep-based fix;
- FT-003 changes;
- changing cancel contract;
- allowing Ask and merely discarding it;
- weakening the focused test.
