# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

PRE_SEAL_FT004_HEAD:
`5114372fb78049d95a7b4ba763e73817d7052a55`

OBSERVED_BRANCH_HEAD:
`f8018800c773019f0e79907fec3e15edec72dbb0`

CURRENT_PRODUCT_GATE:
`FT-005 — CONVERSATION + FOLLOW-UP CONTEXT / PREDEVELOPMENT`

FT-003_FINAL:
`CLOSED / GREEN`

FT-004_FINAL:
`CLOSED / GREEN`

FT-005:
`OPEN / PREDEVELOPMENT NEXT`

OPEN_RED:
`NONE`

FT-004_POST_SEAL_INVARIANTS:
`CLOSED / GREEN`

POST_SEAL_CORE:
`35781659952 GREEN`

POST_SEAL_LIVE:
`35781660160 GREEN`

POST_SEAL_GATEWAY:
`35781659866 GREEN`

POST_SEAL_BROWSER:
`35781660084 GREEN`

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

## POST-SEAL FT-004 INVARIANTS

```text
cancel-before-RUNNING
-> Ask call = 0

run owner identity
= tenant_id + user_id

retry
= same question + same as_of_date
```

Closed receipts:
- `FT_004_POST_SEAL_CANCEL_START_RACE_001`;
- `FT_004_POST_SEAL_OWNER_IDENTITY_001`;
- `FT_004_POST_SEAL_RETRY_IDENTITY_001`.

## NEXT_EXACT_ACTION

1. Audit legacy conversation surfaces READ-ONLY.
2. Open `FT_005_PREDEVELOPMENT_REVIEW.md`.
3. Decide Fast conversation store strategy before implementation.
4. Freeze conversation / turn / accepted-context authority contracts.
5. Keep every analytical turn as a new immutable run.
6. Keep retry, follow-up, clarification, new turn, and new run as distinct concepts.
7. Do not begin Analyst or Root Cause inside FT-005.
