# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

PRE_SEAL_FT004_HEAD:
`5114372fb78049d95a7b4ba763e73817d7052a55`

OBSERVED_BRANCH_HEAD:
`68c53f4d1247a1fe813ebaf6bcc901916f6f2660`

CURRENT_PRODUCT_GATE:
`FT-005 — CONVERSATION + FOLLOW-UP / IMPLEMENTATION + CERTIFICATION`

FT-003_FINAL:
`CLOSED / GREEN`

FT-004_FINAL:
`CLOSED / GREEN`

FT-005_CORE:
`GREEN`
run: `35784476690`

FT-005_REAL_MODEL:
`RED`
run: `35786550995`
tested SHA: `19628e973b6ceee3b50620a7a544903364823e77`

FT-005_REAL_METABASE_FOLLOWUP:
`RED`
run: `35786695054`
tested SHA: `68c53f4d1247a1fe813ebaf6bcc901916f6f2660`

FT-005_FINAL:
`OPEN`

OPEN_RED:
`FT-005 COGNITION CERTIFICATION`

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

## FT-005 CURRENT IMPLEMENTATION

Implemented and provider-free GREEN:
- FastConversationStore;
- FastConversationService;
- StructuredJsonFastFollowupCognition;
- ContextBoundFastCognition;
- authenticated conversation HTTP surface;
- typed accepted context;
- turn lineage;
- explicit older-turn reply;
- self-contained topic switch isolation;
- active-run conflict;
- clarification continuation with new child turn/new run;
- accepted USER-question lineage;
- owner isolation;
- retry/follow-up separation.

Current core proof:
`35784476690 GREEN`

Current audited implementation SHA:
`d88e599ec702c4a3edaaecbaeba236af30a92139`

Hard debt:
`CONVERSATION_DURABILITY = NOT YET CERTIFIED`

## NEXT_EXACT_ACTION

1. Add focused real-model follow-up sentinel.
2. Add real-model + pinned-Metabase 3-turn follow-up sentinel.
3. Compute independent DB oracle for every executed follow-up result.
4. Require distinct run/evidence identities for every analytical turn.
5. Prove current resource/field authority is revalidated on each turn.
6. Prove assistant prose authority = 0 and prior request-local handles are not reused as authority.
7. Re-run FT-003 and FT-004 regressions.
8. Seal all FT-005 failure receipts.
9. Seal FT-005 only after all certification gates are GREEN.
10. Keep `CONVERSATION_DURABILITY = NOT YET CERTIFIED`.
11. Only after seal, add Research Doctrine docs-only reconciliation.
12. Do not begin Analyst, Research, Root Cause, or new analytical algorithms inside FT-005.


## FT-005 CURRENT CERTIFICATION RED

Provider-free core:
`35784476690 GREEN`

Focused current third-model diagnostic:
`35786550995 RED`

Real-model + pinned-Metabase three-turn E2E:
`35786695054 RED`

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

Current classification:
- A: EVAL_ORACLE_OVERCONSTRAINT;
- B: MODEL_STRUCTURED_OUTPUT_RELIABILITY;
- C: RETRIEVAL_CONTRACT_DRIFT candidate.

No product prompt patch is authorized yet.

Next:
1. open RED receipts;
2. add eval-only structured-output diagnostics;
3. separate HARD vs DIAGNOSTIC oracle;
4. repeat current Gemini diagnostic;
5. run Luna baseline and Sol ceiling on the frozen corpus;
6. classify model dependency;
7. only then authorize minimal fixes.
