# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

PRE_SEAL_FT004_HEAD:
`5114372fb78049d95a7b4ba763e73817d7052a55`

CURRENT_PRODUCT_GATE:
`FT-005 — CONVERSATION + FOLLOW-UP CONTEXT`

FT-003_FINAL:
`CLOSED / GREEN`

FT-004_FINAL:
`CLOSED / GREEN`

FT-005:
`OPEN / PREDEVELOPMENT NEXT`

OPEN_RED:
`NONE`

TARGET:
`Dima-native Intelligence Workspace on Metabase Analytics Substrate`

SELECTED_RENDERING:
`OPTION_A — Dima-native chart/table`

## FT-004 CERTIFIED RUNS

FT-004_CORE_API_SSE:
`GREEN`
run: `35778861234`
tested SHA: `5114372fb78049d95a7b4ba763e73817d7052a55`

FT-004_REAL_METABASE_LIFECYCLE:
`GREEN`
run: `35778861380`
tested SHA: `5114372fb78049d95a7b4ba763e73817d7052a55`
artifact digest:
`sha256:0ef6a463b386b4548128cc3dde2d580c6620ca91d851d9bffea042fbca7cb660`

FT-003_BROWSER_REGRESSION:
`GREEN`
run: `35778348522`
tested SHA: `0e0a948202eac24bbdca05c954764d8a370f3d89`

FT-002B_GATEWAY_REGRESSION:
`GREEN`
run: `35778348296`
tested SHA: `0e0a948202eac24bbdca05c954764d8a370f3d89`

FT-003_LIVE_REGRESSION:
`GREEN`
run: `35778100295`
tested SHA: `c14c60fc2c718212b6a78ab98fe47c34d47e2e40`

## FT-004 PROVEN CHAIN

```text
POST /fast/runs
-> opaque run_id
-> CREATED
-> bounded worker
-> RUNNING
-> sealed FastAskService
-> real pinned Metabase
-> real analytics DB
-> evidence + deterministic answer
-> COMPLETED
-> canonical snapshot
-> replayable SSE events
```

Real live COUNT:
`20`

Real answer:
`Sonuç: 20 kayıt.`

Successful event sequence:
```text
RUN_CREATED
RUN_STARTED
RUN_COMPLETED
```

Clarification/cancel live sequence:
```text
RUN_CREATED
RUN_STARTED
RUN_WAITING_CLARIFICATION
CANCEL_REQUESTED
RUN_CANCELLED
```

## FT-004 LIFECYCLE AUTHORITY

Canonical states:
- CREATED;
- RUNNING;
- WAITING_CLARIFICATION;
- PARTIAL;
- COMPLETED;
- FAILED;
- CANCEL_REQUESTED;
- CANCELLED;
- INTERRUPTED.

Terminal states:
- COMPLETED;
- FAILED;
- CANCELLED;
- INTERRUPTED.

Proven:
- terminal exactly once;
- terminal immutable;
- duplicate-event dedupe;
- monotonic event IDs;
- Last-Event-ID replay;
- foreign principal -> 404;
- owner -> allowed;
- retry lineage creates a new run;
- original terminal run never reopens;
- root_run_id preserved;
- attempt increments;
- nonterminal recovery -> INTERRUPTED;
- cooperative cancel discards late success.

## CLOSED FT-004 FAILURE FAMILIES

- `FT_004_WAITING_CLARIFICATION_CANCEL_001`
  - class: RUN_STATE_MACHINE_IMPLEMENTATION;
  - fixed by preserving pre-cancel state and finalizing quiescent cancellation;
  - closed by core runs `35778574189` and `35778861234`.

- `FT_004_ASK_COMPATIBILITY_TEST_FIXTURE_001`
  - class: EVAL_ORACLE_FIXTURE_CONTRACT;
  - production `FastAskService` type guard retained;
  - test fixture corrected;
  - closed by core runs `35778574189` and `35778861234`.

## OPEN DEBT / NOT FT-004 BLOCKERS

```text
PROCESS_RESTART_DURABILITY = NOT YET CERTIFIED
PERSISTENT_RUN_EVENT_STORE = NOT YET IMPLEMENTED
DISTRIBUTED_WORKERS = NOT YET IMPLEMENTED
CROSS_INSTANCE_SSE_FANOUT = NOT YET IMPLEMENTED
HARD_CANCEL_RUNNING_METABASE_QUERY = NOT YET IMPLEMENTED
```

Current run/event store is intentionally in-process behind a Fast-owned store boundary.
These become mandatory before production/external pilot where applicable.

FT-003 deliberate debt remains:
`MULTI_CANDIDATE_RESOLUTION = CONSERVATIVE_CLARIFICATION`

## CURRENT INVARIANTS

- writes only to Fast Track branch;
- source branches read-only;
- Wren/V2/V3 modification = forbidden;
- sealed FT-003 cognition/query/evidence semantics are not duplicated;
- `/fast/ask` remains compatibility/Quick adapter;
- lifecycle ownership belongs to Fast run layer;
- run terminal state exactly once;
- model does not own run state;
- raw SQL = 0;
- joins = 0 in sealed FT-003 family;
- METABASE_LICENSE_BUDGET = 0;
- paid Metabase core dependency = 0;
- browser Metabase service/admin secret = 0.

## NEXT_EXACT_ACTION

1. Open `FT_005_PREDEVELOPMENT_REVIEW.md`.
2. Define Dima-owned conversation/follow-up context without changing sealed FT-003 analytics authority.
3. Build conversation identity and turn lineage above run lifecycle.
4. Resolve follow-up references from explicit prior accepted/evidence context, not hidden heuristic state.
5. Preserve every analytical execution as a separate run.
6. Do not begin Analyst or Root Cause inside FT-005.
