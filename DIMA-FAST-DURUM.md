# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

PRE_SEAL_HEAD:
`9faa65eb8ac830285a55ce93940daf68da13f699`

OBSERVED_BRANCH_HEAD:
`0e0a948202eac24bbdca05c954764d8a370f3d89`

CURRENT_PRODUCT_GATE:
`FT-004 — RUN LIFECYCLE / STREAMING / CANCEL`

FT-003_FINAL:
`CLOSED / GREEN`

FT-004:
`IMPLEMENTING / CORE RE-PROOF IN PROGRESS`

FT-004_INITIAL_CORE_RED:
`35778100380`

FT-004_INITIAL_RED_CLASS:
`WAITING_CLARIFICATION_CANCEL_STATE_MACHINE`

FT-004_CORRECTIVE_SHA:
`0e0a948202eac24bbdca05c954764d8a370f3d89`

FT-004_CORE_RERUN:
`35778348082 — QUEUED/IN_PROGRESS`

OPEN_RED:
`FT-004 core rerun not yet certified`

TARGET:
`Dima-native Intelligence Workspace on Metabase Analytics Substrate`

SELECTED_RENDERING:
`OPTION_A — Dima-native chart/table`

## FT-003 CERTIFIED RUNS

FT-003_CORE:
`GREEN`
run: `35776527074`
tested SHA: `f86475228074530a426542b9f5674ba12cbb7298`

FT-003_REAL_METABASE_LIVE:
`GREEN`
run: `35776518129`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`

FT-003_GATEWAY_REGRESSION:
`GREEN`
run: `35776518246`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`

FT-003_REAL_MODEL_RETRIEVAL:
`GREEN`
run: `35776518107`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`

FT-003_REAL_MODEL_E2E:
`GREEN`
run: `35776518184`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`
artifact digest:
`sha256:14c4ea5e455f15643c46538afaaabad17eef756c93842f9915f523cc94310c5a`

FT-003_BROWSER_REAL_FAST_ASK:
`GREEN`
run: `35777010348`
tested SHA: `9faa65eb8ac830285a55ce93940daf68da13f699`

FT-UI-002:
`SEALED / HISTORICAL / workflow_dispatch only`
freeze commit: `96cb65f2b05d8bc56e1dd86ced7b13b5c0f3fb3a`

## FT-003 PROVEN CHAIN

```text
Turkish question
-> real model bounded cognition
-> real Metabase metadata SEARCH
-> opaque Dima resource/field authority
-> deterministic temporal bounds
-> deterministic portable query
-> real Metabase construct/execute
-> independent DB equality
-> evidence
-> deterministic answer
-> Dima-native browser UI
```

Certified DB oracle:

```text
2026-08-09 <= order_date < 2026-09-08

COUNT = 20
SUM = 16270
East = 4085
North = 4015
South = 4050
West = 4120
```

Authority safety:
- ambiguous resources -> clarification before metadata read/query;
- construct = 0 on ambiguity;
- execute = 0 on ambiguity;
- unsupported AVG -> UNSUPPORTED before Gateway creation;
- invented IDs = 0 in final model diagnostic;
- raw SQL = 0;
- join = 0;
- Wren/V2/V3 runtime dependency = 0.

Browser:
- real `/fast/ask`;
- real pinned Metabase;
- loading PASS;
- COUNT PASS;
- SUM PASS;
- BREAKDOWN PASS;
- chart PASS;
- table PASS;
- clarification PASS;
- unsupported PASS;
- failed PASS;
- desktop 1440x900 PASS;
- mobile 390x844 PASS;
- scrollWidth = 390.

## CLOSED FAILURE FAMILIES

- FT_003_LIVE_SENTINEL_RED_001 -> EVAL_ORACLE -> CLOSED.
- FT_003_REAL_MODEL_SENTINEL_RED_001 -> retrieval/unsupported/ambiguity contract -> CLOSED.
- FT_003_MODEL_RETRIEVAL_RED_002 -> generic metadata retrieval contract -> CLOSED.
- FT_003_BROWSER_HYDRATION_RACE_001 -> E2E hydration timing oracle -> CLOSED.
- duplicate canonical resource candidate -> CLOSED by URI dedupe.
- invented field handle -> fail-closed regression sealed.

## OPEN DEBT / NOT FT-003 BLOCKERS

MULTI_CANDIDATE_RESOLUTION:
`CONSERVATIVE_CLARIFICATION`

CATALOG_FALLBACK:
`BOUNDED_SAFETY_FALLBACK`

The fallback is permission-filtered and bounded. It is not a translation or semantic dictionary.

Pilot-level broader model benchmark is still later roadmap work; the small FT-003 real-model certification is GREEN.

## CURRENT INVARIANTS

- writes only to Fast Track branch;
- source branches read-only;
- Wren/V2/V3 modification = forbidden;
- silent fallback = 0;
- raw SQL = 0;
- joins = 0 for FT-003;
- METABASE_LICENSE_BUDGET = 0;
- paid Metabase core dependency = 0;
- Metabase frontend fork = 0;
- browser Metabase service/admin secret = 0;
- Dima owns user-facing analyst UX;
- Metabase remains hidden OSS analytics substrate.

## FT-004 CURRENT IMPLEMENTATION

Implemented on initial core SHA:
`c14c60fc2c718212b6a78ab98fe47c34d47e2e40`

Current owners:
- `app.fast.run_models`;
- `app.fast.run_store`;
- `app.fast.run_manager`;
- `app.fast.run_router`;
- Fast-only application integration;
- lifecycle/API/SSE provider-free tests;
- dedicated FT-004 core workflow.

First core run:
`35778100380 RED`

Root cause:
`WAITING_CLARIFICATION -> CANCEL_REQUESTED` did not finalize to `CANCELLED` because cancellation logic checked the post-transition state instead of the pre-cancel state.

Failure receipt:
`FT_004_WAITING_CLARIFICATION_CANCEL_001.md`

Corrective SHA:
`0e0a948202eac24bbdca05c954764d8a370f3d89`

## NEXT_EXACT_ACTION

1. Require FT-004 core rerun `35778348082` GREEN.
2. Verify lifecycle/API/SSE and FT-003 regression steps all execute.
3. Add FT-004 live pinned-Metabase lifecycle sentinel.
4. Prove real run creation -> execution -> COMPLETED -> SSE replay.
5. Prove clarification -> WAITING_CLARIFICATION and cancel lifecycle.
6. Recheck FT-003 core/live/browser/Gateway regressions.
7. Seal FT-004 only after live lifecycle receipt is GREEN.
8. Then open FT-005 conversation predevelopment.
9. Do not add new semantic logic, aggregation families, joins, Analyst, Root Cause or conversation semantics in FT-004.
