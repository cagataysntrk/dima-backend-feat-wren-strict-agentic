# FT-004 — RUN LIFECYCLE / STREAMING / CANCEL FINAL CERTIFICATION

Status: CLOSED / GREEN
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Certification statement

FT-004 wraps the sealed FT-003 analytical operation in a bounded Dima-owned lifecycle:

```text
POST /fast/runs
-> run_id
-> CREATED
-> RUNNING
-> sealed FastAskService
-> analytics substrate
-> COMPLETED | FAILED | WAITING_CLARIFICATION | CANCELLED
-> canonical run snapshot
-> structured replayable SSE
```

The model does not own run state.

## Certified SHAs

Initial lifecycle implementation:
`c14c60fc2c718212b6a78ab98fe47c34d47e2e40`

Cancellation correction:
`0e0a948202eac24bbdca05c954764d8a370f3d89`

Ask compatibility test-fixture correction:
`f8807c793db239fb23108346a8b615de5da4e00d`

Live lifecycle sentinel:
`5114372fb78049d95a7b4ba763e73817d7052a55`

## GREEN run matrix

| Gate | Run | Tested SHA | Result |
| --- | --- | --- | --- |
| FT-004 core/lifecycle/API/SSE + FT-003 regression | 35778861234 | 5114372fb78049d95a7b4ba763e73817d7052a55 | GREEN |
| FT-004 real pinned-Metabase lifecycle | 35778861380 | 5114372fb78049d95a7b4ba763e73817d7052a55 | GREEN |
| FT-003 browser regression after lifecycle integration | 35778348522 | 0e0a948202eac24bbdca05c954764d8a370f3d89 | GREEN |
| FT-002B Gateway regression after lifecycle integration | 35778348296 | 0e0a948202eac24bbdca05c954764d8a370f3d89 | GREEN |
| FT-003 real-Metabase live regression after lifecycle integration | 35778100295 | c14c60fc2c718212b6a78ab98fe47c34d47e2e40 | GREEN |

## Live artifact

Name:
`dima-fast-ft004-live-5114372fb78049d95a7b4ba763e73817d7052a55`

Digest:
`sha256:0ef6a463b386b4548128cc3dde2d580c6620ca91d851d9bffea042fbca7cb660`

## Real pinned-Metabase proof

Anchor:
`2026-09-07`

Window:
`2026-08-09 <= order_date < 2026-09-08`

Independent DB oracle:
`COUNT = 20`

Real run:
- state = COMPLETED;
- terminal_event_id = 3;
- answer = `Sonuç: 20 kayıt.`;
- result count = 20;
- query fingerprint present;
- access fingerprint present;
- result digest present.

Successful SSE sequence:
```text
RUN_CREATED
RUN_STARTED
RUN_COMPLETED
```

Replay from `Last-Event-ID: 2` returns only the completion event.

## Clarification + cancel proof

Real Metabase metadata search was used with a cognition abstention.

Run reached:
`WAITING_CLARIFICATION`

Then cancel produced:
```text
CANCEL_REQUESTED
RUN_CANCELLED
```

Final event history:
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
exactly once.

## Provider-free lifecycle proof

Covered:
- success mapping;
- clarification mapping;
- failed mapping;
- cancel while bounded work is running;
- late success discarded after cancel;
- cancel after terminal is idempotent;
- terminal immutability;
- event dedupe;
- monotonic event IDs;
- retry/new-run lineage;
- root_run_id preservation;
- attempt increment;
- INTERRUPTED recovery;
- owner-only GET/events/cancel;
- foreign principal 404;
- SSE replay and terminal close;
- `/fast/ask` compatibility remains.

## Public Fast lifecycle API

```text
POST /fast/runs
GET  /fast/runs/{run_id}
GET  /fast/runs/{run_id}/events
POST /fast/runs/{run_id}/cancel
```

Existing:
`POST /fast/ask`

remains a compatibility / Quick adapter.

## Failure history

### WAITING_CLARIFICATION_CANCEL_001
Class:
`RUN_STATE_MACHINE_IMPLEMENTATION`

Root cause:
post-transition state was used where pre-cancel state was required.

Fix:
preserve pre-cancel state; quiescent/no-active-worker cancellation becomes terminal.

Closed.

### ASK_COMPATIBILITY_TEST_FIXTURE_001
Class:
`EVAL_ORACLE_FIXTURE_CONTRACT`

Root cause:
new test double did not satisfy the existing sealed `FastAskService` owner type.

Fix:
test double inherits FastAskService; production router guard retained.

Closed.

## Explicit limitations

```text
PROCESS_RESTART_DURABILITY = NOT YET CERTIFIED
PERSISTENT_RUN_EVENT_STORE = NOT YET IMPLEMENTED
DISTRIBUTED_WORKERS = NOT YET IMPLEMENTED
CROSS_INSTANCE_SSE_FANOUT = NOT YET IMPLEMENTED
HARD_CANCEL_RUNNING_METABASE_QUERY = NOT YET IMPLEMENTED
```

Cancellation of already-started FT-003 work is cooperative:
- CANCEL_REQUESTED is authoritative;
- bounded underlying call may finish;
- its late success is discarded;
- run ends CANCELLED.

This is an explicit FT-004 contract, not a hidden hard-cancel claim.

## Scope integrity

FT-004 changed no:
- Wren/V2/V3 logic;
- FT-003 semantic/retrieval/query authority;
- aggregation families;
- joins;
- Analyst;
- Root Cause;
- conversation semantics.

## Gate decision

`FT-004 = CLOSED / GREEN`

Next:
`FT-005 — CONVERSATION + FOLLOW-UP CONTEXT`
